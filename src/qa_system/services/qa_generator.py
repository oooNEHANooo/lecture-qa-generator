"""
QA Generation service using LangChain and Google Gemini
"""

import logging
from typing import List, Dict, Any, Optional
from enum import Enum
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json

logger = logging.getLogger(__name__)


class QuestionType(str, Enum):
    """質問の種類"""
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    ESSAY = "essay"
    SHORT_ANSWER = "short_answer"


class DifficultyLevel(str, Enum):
    """難易度レベル"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class GeneratedQuestion(BaseModel):
    """生成された質問"""
    question: str = Field(description="質問文")
    question_type: QuestionType = Field(description="質問の種類")
    difficulty: DifficultyLevel = Field(description="難易度")
    choices: Optional[List[str]] = Field(default=None, description="選択肢（選択式の場合）")
    correct_answer: str = Field(description="正解")
    explanation: str = Field(description="解説")
    keywords: List[str] = Field(description="関連キーワード")


class QASet(BaseModel):
    """質問セット"""
    slide_number: int = Field(description="スライド番号")
    slide_title: str = Field(description="スライドタイトル")
    questions: List[GeneratedQuestion] = Field(description="生成された質問リスト")


class QAGenerator:
    """QA生成サービス"""
    
    def __init__(self, google_api_key: str, model_name: str = "gemini-1.5-flash"):
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=google_api_key,
            model=model_name,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        self.parser = PydanticOutputParser(pydantic_object=GeneratedQuestion)
    
    def generate_questions_for_slide(
        self, 
        slide_content: Dict[str, Any], 
        num_questions: int = 2,
        difficulty_distribution: Dict[DifficultyLevel, int] = None
    ) -> QASet:
        """単一スライドの内容から質問を生成"""
        
        if difficulty_distribution is None:
            difficulty_distribution = {
                DifficultyLevel.EASY: 1,
                DifficultyLevel.MEDIUM: 1,
                DifficultyLevel.HARD: 0
            }
        
        questions = []
        
        for difficulty, count in difficulty_distribution.items():
            for _ in range(count):
                question = self._generate_single_question(slide_content, difficulty)
                if question:
                    questions.append(question)
        
        return QASet(
            slide_number=slide_content["slide_number"],
            slide_title=slide_content["title"],
            questions=questions
        )
    
    def generate_questions_for_multiple_slides(
        self,
        slides_content: List[Dict[str, Any]],
        questions_per_slide: int = 2
    ) -> List[QASet]:
        """複数スライドの内容から質問を生成"""
        
        qa_sets = []
        
        for slide_content in slides_content:
            # スライドに十分なコンテンツがある場合のみ質問生成
            if self._has_sufficient_content(slide_content):
                qa_set = self.generate_questions_for_slide(
                    slide_content, 
                    num_questions=questions_per_slide
                )
                qa_sets.append(qa_set)
                logger.info(f"スライド {slide_content['slide_number']} の質問生成完了")
            else:
                logger.warning(f"スライド {slide_content['slide_number']} は内容が不十分なためスキップ")
        
        return qa_sets
    
    def _generate_single_question(
        self, 
        slide_content: Dict[str, Any], 
        difficulty: DifficultyLevel
    ) -> Optional[GeneratedQuestion]:
        """単一の質問を生成"""
        
        try:
            prompt = self._create_question_prompt(slide_content, difficulty)
            
            response = self.llm.invoke(prompt)
            
            # JSONレスポンスをパース
            question_data = self._parse_response(response.content)
            
            if question_data:
                return GeneratedQuestion(**question_data)
            
        except Exception as e:
            logger.error(f"質問生成中にエラーが発生: {e}")
            return None
    
    def _create_question_prompt(
        self, 
        slide_content: Dict[str, Any], 
        difficulty: DifficultyLevel
    ) -> List[BaseMessage]:
        """質問生成用のプロンプトを作成"""
        
        difficulty_instructions = {
            DifficultyLevel.EASY: "基本的な用語や概念の理解を確認する簡単な質問",
            DifficultyLevel.MEDIUM: "概念の応用や関連性を問う中程度の質問", 
            DifficultyLevel.HARD: "深い理解や批判的思考を要求する難しい質問"
        }
        
        system_message = f"""
あなたは教育専門の質問作成者です。提供されたスライドの内容から、学生の理解度を測定するための質問を1つ生成してください。

## 指示:
1. 難易度: {difficulty_instructions[difficulty]}
2. 質問の種類: multiple_choice（4択）、single_choice（2択）、essay（記述式）、short_answer（短答式）のいずれか
3. 内容に基づいた具体的で明確な質問を作成
4. 選択式の場合は紛らわしい選択肢を含める
5. 正解と詳細な解説を提供

## 重要: 
必ずJSON形式のみで回答してください。説明文は含めず、以下の形式の有効なJSONのみを返してください。

JSON形式:
- question: 質問文
- question_type: 質問の種類 (multiple_choice, single_choice, essay, short_answer)
- difficulty: {difficulty.value}
- choices: 選択肢の配列（選択式の場合のみ）またはnull
- correct_answer: 正解
- explanation: 詳細な解説
- keywords: 関連キーワードの配列

注意: 選択式以外の場合はchoicesをnullにしてください。
"""
        
        user_message = f"""
## スライド情報:
- スライド番号: {slide_content['slide_number']}
- タイトル: {slide_content['title']}
- 内容: {slide_content['content']}
- 要点: {', '.join(slide_content['bullet_points'])}
- 全体テキスト: {slide_content['full_text']}

上記の内容から質問を1つ生成してください。
"""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("user", user_message)
        ])
        
        return prompt_template.format_messages()
    
    def _parse_response(self, response_content: str) -> Optional[Dict[str, Any]]:
        """LLMのレスポンスをパース"""
        try:
            # マルチパターンでJSONを抽出
            json_content = self._extract_json_from_response(response_content)
            
            if not json_content:
                logger.error(f"JSONコンテンツが見つかりません。レスポンス: {response_content[:200]}...")
                return None
            
            # JSONをパース
            data = json.loads(json_content)
            
            # 必須フィールドの検証
            required_fields = ["question", "question_type", "difficulty", "correct_answer", "explanation"]
            for field in required_fields:
                if field not in data:
                    logger.error(f"必須フィールド '{field}' が見つかりません")
                    return None
            
            # デフォルト値の設定
            if "keywords" not in data:
                data["keywords"] = []
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSONパースエラー: {e}")
            logger.debug(f"レスポンス内容: {response_content[:500]}...")
            return None
        except Exception as e:
            logger.error(f"レスポンス解析エラー: {e}")
            return None
    
    def _extract_json_from_response(self, response_content: str) -> Optional[str]:
        """レスポンスからJSON部分を抽出"""
        # パターン1: ```json...``` ブロック
        if "```json" in response_content:
            start = response_content.find("```json") + 7
            end = response_content.find("```", start)
            if end != -1:
                return response_content[start:end].strip()
        
        # パターン2: ```...``` ブロック（json指定なし）
        if "```" in response_content:
            start = response_content.find("```") + 3
            end = response_content.find("```", start)
            if end != -1:
                potential_json = response_content[start:end].strip()
                # JSONかどうかチェック
                if potential_json.startswith("{") and potential_json.endswith("}"):
                    return potential_json
        
        # パターン3: { ... } ブロックを直接抽出
        start_brace = response_content.find("{")
        if start_brace != -1:
            # 対応する閉じ括弧を見つける
            brace_count = 0
            for i, char in enumerate(response_content[start_brace:], start_brace):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        return response_content[start_brace:i+1]
        
        # パターン4: 全体をそのまま試す
        content = response_content.strip()
        if content.startswith("{") and content.endswith("}"):
            return content
        
        return None
    
    def _has_sufficient_content(self, slide_content: Dict[str, Any]) -> bool:
        """スライドに十分なコンテンツがあるかチェック"""
        full_text = slide_content.get("full_text", "")
        content = slide_content.get("content", "")
        bullet_points = slide_content.get("bullet_points", [])
        
        # 最小文字数とコンテンツ要素の確認
        min_text_length = 50
        has_meaningful_content = (
            len(full_text) >= min_text_length or
            len(content) >= min_text_length or
            len(bullet_points) >= 2
        )
        
        return has_meaningful_content
    
    def generate_comprehensive_qa(
        self, 
        slides_content: List[Dict[str, Any]],
        total_questions: int = 20,
        difficulty_ratio: Dict[str, float] = None
    ) -> List[QASet]:
        """包括的なQAセットを生成"""
        
        if difficulty_ratio is None:
            difficulty_ratio = {"easy": 0.4, "medium": 0.4, "hard": 0.2}
        
        # 各難易度の質問数を計算
        easy_count = int(total_questions * difficulty_ratio["easy"])
        medium_count = int(total_questions * difficulty_ratio["medium"]) 
        hard_count = total_questions - easy_count - medium_count
        
        # スライドあたりの質問配分を計算
        valid_slides = [s for s in slides_content if self._has_sufficient_content(s)]
        
        if not valid_slides:
            logger.warning("質問生成に適したスライドがありません")
            return []
        
        questions_per_slide = total_questions // len(valid_slides)
        remaining_questions = total_questions % len(valid_slides)
        
        qa_sets = []
        difficulty_counts = {
            DifficultyLevel.EASY: easy_count,
            DifficultyLevel.MEDIUM: medium_count,
            DifficultyLevel.HARD: hard_count
        }
        
        for i, slide_content in enumerate(valid_slides):
            # このスライドの質問数を決定
            slide_questions = questions_per_slide
            if i < remaining_questions:
                slide_questions += 1
            
            # 難易度配分を決定
            slide_difficulty_dist = self._distribute_difficulty_for_slide(
                slide_questions, difficulty_counts
            )
            
            qa_set = self.generate_questions_for_slide(
                slide_content,
                num_questions=slide_questions,
                difficulty_distribution=slide_difficulty_dist
            )
            
            qa_sets.append(qa_set)
        
        return qa_sets
    
    def _distribute_difficulty_for_slide(
        self, 
        questions_count: int, 
        remaining_difficulty_counts: Dict[DifficultyLevel, int]
    ) -> Dict[DifficultyLevel, int]:
        """スライドごとの難易度配分を決定"""
        
        distribution = {
            DifficultyLevel.EASY: 0,
            DifficultyLevel.MEDIUM: 0,
            DifficultyLevel.HARD: 0
        }
        
        # 残りの質問数に応じて配分
        for difficulty in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]:
            available = remaining_difficulty_counts[difficulty]
            if available > 0 and questions_count > 0:
                allocated = min(1, available, questions_count)
                distribution[difficulty] = allocated
                remaining_difficulty_counts[difficulty] -= allocated
                questions_count -= allocated
        
        return distribution