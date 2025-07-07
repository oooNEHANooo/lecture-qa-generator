"""
Answer model for storing correct answers and explanations
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Answer(BaseModel):
    """回答情報を管理するモデル"""
    __tablename__ = "answers"
    
    # 基本情報
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, comment="質問ID")
    
    # 回答内容
    answer_text = Column(Text, nullable=False, comment="回答内容")
    is_correct = Column(Boolean, nullable=False, comment="正解フラグ")
    explanation = Column(Text, nullable=True, comment="解説")
    
    # メタデータ
    order_index = Column(Integer, nullable=True, comment="選択肢の順序（選択式の場合）")
    keywords = Column(Text, nullable=True, comment="関連キーワード（カンマ区切り）")
    
    # リレーション
    question = relationship("Question", back_populates="answers")
    
    def __repr__(self):
        return f"<Answer(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})>"
    
    def to_dict(self):
        """辞書形式で返す"""
        return {
            "id": self.id,
            "question_id": self.question_id,
            "answer_text": self.answer_text,
            "is_correct": self.is_correct,
            "explanation": self.explanation,
            "order_index": self.order_index,
            "keywords": self.keywords.split(",") if self.keywords else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }