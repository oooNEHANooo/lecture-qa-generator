"""
Question model for storing generated questions
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from enum import Enum
from .base import BaseModel


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


class Question(BaseModel):
    """質問情報を管理するモデル"""
    __tablename__ = "questions"
    
    # 基本情報
    lecture_id = Column(Integer, ForeignKey("lectures.id"), nullable=False, comment="講義ID")
    slide_number = Column(Integer, nullable=False, comment="スライド番号")
    
    # 質問内容
    question_text = Column(Text, nullable=False, comment="質問文")
    question_type = Column(SQLEnum(QuestionType), nullable=False, comment="質問の種類")
    difficulty = Column(SQLEnum(DifficultyLevel), nullable=False, comment="難易度")
    
    # 正解情報
    correct_answer = Column(Text, nullable=False, comment="正解")
    explanation = Column(Text, nullable=True, comment="解説")
    
    # 選択肢（JSON形式）
    choices = Column(JSON, nullable=True, comment="選択肢（選択式の場合）")
    
    # メタデータ
    keywords = Column(JSON, nullable=True, comment="関連キーワード")
    estimated_time = Column(Integer, nullable=True, comment="推定回答時間（秒）")
    
    # 統計情報
    usage_count = Column(Integer, default=0, comment="使用回数")
    correct_rate = Column(Integer, nullable=True, comment="正答率（%）")
    
    # リレーション
    lecture = relationship("Lecture", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    student_responses = relationship("StudentResponse", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question(id={self.id}, type={self.question_type}, difficulty={self.difficulty})>"
    
    def to_dict(self):
        """辞書形式で返す"""
        return {
            "id": self.id,
            "lecture_id": self.lecture_id,
            "slide_number": self.slide_number,
            "question_text": self.question_text,
            "question_type": self.question_type.value,
            "difficulty": self.difficulty.value,
            "correct_answer": self.correct_answer,
            "explanation": self.explanation,
            "choices": self.choices,
            "keywords": self.keywords,
            "estimated_time": self.estimated_time,
            "usage_count": self.usage_count,
            "correct_rate": self.correct_rate,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_multiple_choice(self) -> bool:
        """複数選択式の質問かどうか"""
        return self.question_type == QuestionType.MULTIPLE_CHOICE
    
    def is_essay_type(self) -> bool:
        """記述式の質問かどうか"""
        return self.question_type in [QuestionType.ESSAY, QuestionType.SHORT_ANSWER]
    
    def get_choices_list(self) -> list:
        """選択肢をリスト形式で取得"""
        if self.choices and isinstance(self.choices, list):
            return self.choices
        return []
    
    def get_keywords_list(self) -> list:
        """キーワードをリスト形式で取得"""
        if self.keywords and isinstance(self.keywords, list):
            return self.keywords
        return []