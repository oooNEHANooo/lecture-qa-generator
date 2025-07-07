"""
Lectures API router
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import json
from pathlib import Path
import shutil

from src.qa_system.models.base import get_db
from src.qa_system.models.lecture import Lecture
from src.qa_system.services.pptx_extractor import PPTXExtractor
from src.qa_system.services.qa_generator import QAGenerator
from src.qa_system.models.question import Question, QuestionType, DifficultyLevel
from src.qa_system.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_lectures(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """講義一覧を取得"""
    lectures = db.query(Lecture).offset(skip).limit(limit).all()
    return [lecture.to_dict() for lecture in lectures]


@router.get("/{lecture_id}", response_model=dict)
async def get_lecture(lecture_id: int, db: Session = Depends(get_db)):
    """特定の講義を取得"""
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="講義が見つかりません")
    return lecture.to_dict()


@router.post("/upload", response_model=dict)
async def upload_lecture(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """PowerPointファイルをアップロードして講義を作成"""
    
    # ファイル拡張子の確認
    if not file.filename.lower().endswith(('.pptx', '.ppt')):
        raise HTTPException(
            status_code=400, 
            detail="PowerPointファイル（.pptx または .ppt）のみアップロード可能です"
        )
    
    # ファイルサイズの確認
    if file.size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"ファイルサイズが上限（{settings.max_file_size // 1024 // 1024}MB）を超えています"
        )
    
    try:
        # ファイルを保存
        upload_dir = Path(settings.upload_folder)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 講義レコードを作成
        lecture = Lecture(
            title=title,
            description=description,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file.size,
            author=author,
            subject=subject,
            processing_status="uploaded"
        )
        
        db.add(lecture)
        db.commit()
        db.refresh(lecture)
        
        # バックグラウンドでコンテンツ抽出とQA生成を実行
        background_tasks.add_task(
            process_lecture_content,
            lecture.id,
            str(file_path)
        )
        
        logger.info(f"講義がアップロードされました: {lecture.id}")
        
        return {
            "message": "講義がアップロードされました。コンテンツの抽出とQA生成を開始します。",
            "lecture_id": lecture.id
        }
        
    except Exception as e:
        logger.error(f"ファイルアップロードエラー: {e}")
        raise HTTPException(status_code=500, detail=f"ファイルのアップロードに失敗しました: {str(e)}")


async def process_lecture_content(lecture_id: int, file_path: str):
    """講義コンテンツの処理（バックグラウンドタスク）"""
    from src.qa_system.models.base import SessionLocal
    
    db = SessionLocal()
    try:
        lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
        if not lecture:
            logger.error(f"講義が見つかりません: {lecture_id}")
            return
        
        # 処理開始
        lecture.processing_status = "processing"
        db.commit()
        
        # PowerPointコンテンツの抽出
        extractor = PPTXExtractor()
        slides_content = extractor.extract_from_file(Path(file_path))
        
        # 抽出されたコンテンツを保存
        lecture.total_slides = len(slides_content)
        lecture.extracted_content = json.dumps(
            [slide.to_dict() for slide in slides_content], 
            ensure_ascii=False
        )
        
        # QA生成
        if settings.google_api_key:
            qa_generator = QAGenerator(settings.google_api_key, settings.gemini_model)
            
            # スライドごとにQAを生成（処理負荷軽減のため最大数を制限）
            slides_data = [slide.to_dict() for slide in slides_content[:settings.max_slides_for_qa]]
            qa_sets = qa_generator.generate_questions_for_multiple_slides(
                slides_data, 
                questions_per_slide=settings.qa_per_slide
            )
            
            logger.info(f"QA生成対象: {len(slides_data)}スライド（全{len(slides_content)}スライド中）")
            
            # 質問をデータベースに保存
            for qa_set in qa_sets:
                for question_data in qa_set.questions:
                    question = Question(
                        lecture_id=lecture.id,
                        slide_number=qa_set.slide_number,
                        question_text=question_data.question,
                        question_type=QuestionType(question_data.question_type),
                        difficulty=DifficultyLevel(question_data.difficulty),
                        correct_answer=question_data.correct_answer,
                        explanation=question_data.explanation,
                        choices=question_data.choices,
                        keywords=question_data.keywords
                    )
                    db.add(question)
            
            logger.info(f"講義 {lecture_id} のQA生成が完了: {len([q for qa_set in qa_sets for q in qa_set.questions])}問")
        
        # 処理完了
        lecture.is_processed = True
        lecture.processing_status = "completed"
        db.commit()
        
        logger.info(f"講義 {lecture_id} の処理が完了しました")
        
    except Exception as e:
        logger.error(f"講義処理エラー: {e}")
        
        # エラー状態を更新
        if lecture:
            lecture.processing_status = "error"
            lecture.error_message = str(e)
            db.commit()
    
    finally:
        db.close()


@router.delete("/{lecture_id}")
async def delete_lecture(lecture_id: int, db: Session = Depends(get_db)):
    """講義を削除"""
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="講義が見つかりません")
    
    try:
        # ファイルを削除
        file_path = Path(lecture.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # データベースから削除（関連する質問も自動削除される）
        db.delete(lecture)
        db.commit()
        
        logger.info(f"講義が削除されました: {lecture_id}")
        
        return {"message": "講義が削除されました"}
        
    except Exception as e:
        logger.error(f"講義削除エラー: {e}")
        raise HTTPException(status_code=500, detail=f"講義の削除に失敗しました: {str(e)}")


@router.get("/{lecture_id}/questions", response_model=List[dict])
async def get_lecture_questions(
    lecture_id: int,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """特定の講義の質問一覧を取得"""
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="講義が見つかりません")
    
    query = db.query(Question).filter(Question.lecture_id == lecture_id)
    
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    
    if question_type:
        query = query.filter(Question.question_type == question_type)
    
    questions = query.all()
    return [question.to_dict() for question in questions]


@router.get("/{lecture_id}/slides")
async def get_lecture_slides(lecture_id: int, db: Session = Depends(get_db)):
    """講義のスライド内容を取得"""
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="講義が見つかりません")
    
    if not lecture.extracted_content:
        raise HTTPException(status_code=404, detail="スライド内容が見つかりません")
    
    try:
        slides = json.loads(lecture.extracted_content)
        return {"slides": slides}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="スライドデータの解析に失敗しました")