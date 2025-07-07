"""
QA System の動作テスト用スクリプト
"""

import asyncio
import sys
from pathlib import Path
import json
import logging

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(str(Path(__file__).parent))

from src.qa_system.services.pptx_extractor import PPTXExtractor
from src.qa_system.services.qa_generator import QAGenerator
from src.qa_system.config import settings

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_pptx_extraction():
    """PowerPoint抽出機能のテスト"""
    logger.info("=== PowerPoint抽出機能のテスト開始 ===")
    
    # サンプルファイルのパス
    sample_files = list(Path("LLM2023").glob("*.pptx"))
    
    if not sample_files:
        logger.warning("LLM2023ディレクトリにPowerPointファイルが見つかりません")
        return None
    
    # 最初のファイルでテスト
    sample_file = sample_files[0]
    logger.info(f"テストファイル: {sample_file}")
    
    try:
        extractor = PPTXExtractor()
        slides_content = extractor.extract_from_file(sample_file)
        
        logger.info(f"抽出されたスライド数: {len(slides_content)}")
        
        # 最初のスライドの内容を表示
        if slides_content:
            first_slide = slides_content[0]
            logger.info(f"最初のスライドタイトル: {first_slide.title}")
            logger.info(f"最初のスライドの要点数: {len(first_slide.bullet_points)}")
        
        # サマリー情報を表示
        summary = extractor.get_lecture_summary()
        logger.info(f"講義サマリー: {summary}")
        
        return slides_content
        
    except Exception as e:
        logger.error(f"PowerPoint抽出エラー: {e}")
        return None


async def test_qa_generation(slides_content):
    """QA生成機能のテスト"""
    logger.info("=== QA生成機能のテスト開始 ===")
    
    if not slides_content:
        logger.warning("スライドコンテンツがないため、QA生成をスキップします")
        return
    
    # Google Gemini APIキーの確認
    if not settings.google_api_key:
        logger.warning("GOOGLE_API_KEYが設定されていません。.envファイルを確認してください")
        return
    
    try:
        # QA生成器を初期化
        qa_generator = QAGenerator(settings.google_api_key, settings.gemini_model)
        
        # 最初の3スライドでテスト
        test_slides = slides_content[:3]
        slides_data = [slide.to_dict() for slide in test_slides]
        
        logger.info(f"QA生成対象スライド数: {len(slides_data)}")
        
        # QAを生成
        qa_sets = qa_generator.generate_questions_for_multiple_slides(
            slides_data,
            questions_per_slide=1  # テストなので1問ずつ
        )
        
        logger.info(f"生成されたQAセット数: {len(qa_sets)}")
        
        # 生成された質問を表示
        for qa_set in qa_sets:
            logger.info(f"\n--- スライド {qa_set.slide_number}: {qa_set.slide_title} ---")
            for i, question in enumerate(qa_set.questions, 1):
                logger.info(f"質問 {i}: {question.question}")
                logger.info(f"種類: {question.question_type}, 難易度: {question.difficulty}")
                logger.info(f"正解: {question.correct_answer}")
                if question.choices:
                    logger.info(f"選択肢: {question.choices}")
                logger.info("---")
        
        return qa_sets
        
    except Exception as e:
        logger.error(f"QA生成エラー: {e}")
        return None


async def test_database_operations():
    """データベース操作のテスト"""
    logger.info("=== データベース操作のテスト開始 ===")
    
    try:
        from src.qa_system.models.base import init_db, SessionLocal
        from src.qa_system.models.lecture import Lecture
        from src.qa_system.models.question import Question, QuestionType, DifficultyLevel
        
        # データベースを初期化
        init_db()
        logger.info("データベースの初期化完了")
        
        # テストデータの作成
        db = SessionLocal()
        
        try:
            # テスト講義を作成
            test_lecture = Lecture(
                title="テスト講義",
                description="システムテスト用の講義",
                original_filename="test.pptx",
                file_path="/tmp/test.pptx",
                file_size=1024,
                total_slides=5,
                is_processed=True,
                processing_status="completed"
            )
            
            db.add(test_lecture)
            db.commit()
            db.refresh(test_lecture)
            
            logger.info(f"テスト講義を作成: ID {test_lecture.id}")
            
            # テスト質問を作成
            test_question = Question(
                lecture_id=test_lecture.id,
                slide_number=1,
                question_text="これはテスト質問ですか？",
                question_type=QuestionType.SINGLE_CHOICE,
                difficulty=DifficultyLevel.EASY,
                correct_answer="はい",
                explanation="これはシステムテスト用の質問です。",
                choices=["はい", "いいえ"],
                keywords=["テスト", "質問"]
            )
            
            db.add(test_question)
            db.commit()
            db.refresh(test_question)
            
            logger.info(f"テスト質問を作成: ID {test_question.id}")
            
            # データの取得テスト
            lectures = db.query(Lecture).all()
            questions = db.query(Question).all()
            
            logger.info(f"総講義数: {len(lectures)}")
            logger.info(f"総質問数: {len(questions)}")
            
        finally:
            db.close()
        
        logger.info("データベース操作テスト完了")
        
    except Exception as e:
        logger.error(f"データベース操作エラー: {e}")


async def test_api_endpoints():
    """API エンドポイントのテスト"""
    logger.info("=== API エンドポイントのテスト開始 ===")
    
    try:
        import httpx
        
        # サーバーが起動していることを確認
        async with httpx.AsyncClient() as client:
            # ヘルスチェック
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                logger.info("ヘルスチェック: OK")
                logger.info(f"レスポンス: {response.json()}")
            else:
                logger.warning(f"ヘルスチェック失敗: {response.status_code}")
            
            # 講義一覧の取得
            response = await client.get("http://localhost:8000/api/lectures/")
            if response.status_code == 200:
                lectures = response.json()
                logger.info(f"講義一覧取得成功: {len(lectures)}件")
            else:
                logger.warning(f"講義一覧取得失敗: {response.status_code}")
            
            # 質問統計の取得
            response = await client.get("http://localhost:8000/api/questions/statistics/overview")
            if response.status_code == 200:
                stats = response.json()
                logger.info(f"質問統計取得成功: {stats}")
            else:
                logger.warning(f"質問統計取得失敗: {response.status_code}")
        
    except ImportError:
        logger.warning("httpx がインストールされていません。API テストをスキップします")
    except Exception as e:
        logger.error(f"API テストエラー: {e}")


async def main():
    """メインテスト関数"""
    logger.info("QA System 統合テストを開始します")
    
    # 1. PowerPoint抽出機能のテスト
    slides_content = await test_pptx_extraction()
    
    # 2. QA生成機能のテスト
    if slides_content:
        await test_qa_generation(slides_content)
    
    # 3. データベース操作のテスト
    await test_database_operations()
    
    # 4. API エンドポイントのテスト
    await test_api_endpoints()
    
    logger.info("統合テスト完了")


if __name__ == "__main__":
    asyncio.run(main())