"""
Student response model for storing student answers and analytics
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel


class StudentResponse(BaseModel):
    """学生の回答情報を管理するモデル"""
    __tablename__ = "student_responses"
    
    # 基本情報
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, comment="質問ID")
    student_id = Column(String(100), nullable=False, comment="学生ID")
    
    # 回答内容
    response_text = Column(Text, nullable=False, comment="学生の回答")
    is_correct = Column(Boolean, nullable=True, comment="正解フラグ")
    score = Column(Float, nullable=True, comment="得点（0-100）")
    
    # 回答時間
    response_time = Column(Integer, nullable=True, comment="回答時間（秒）")
    submitted_at = Column(DateTime, server_default=func.now(), comment="回答提出時刻")
    
    # メタデータ
    attempt_number = Column(Integer, default=1, comment="回答試行回数")
    confidence_level = Column(Integer, nullable=True, comment="確信度（1-5）")
    difficulty_perception = Column(Integer, nullable=True, comment="難易度感（1-5）")
    
    # セッション情報
    session_id = Column(String(100), nullable=True, comment="セッションID")
    ip_address = Column(String(45), nullable=True, comment="IPアドレス")
    user_agent = Column(String(500), nullable=True, comment="ユーザーエージェント")
    
    # リレーション
    question = relationship("Question", back_populates="student_responses")
    
    def __repr__(self):
        return f"<StudentResponse(id={self.id}, student_id='{self.student_id}', is_correct={self.is_correct})>"
    
    def to_dict(self):
        """辞書形式で返す"""
        return {
            "id": self.id,
            "question_id": self.question_id,
            "student_id": self.student_id,
            "response_text": self.response_text,
            "is_correct": self.is_correct,
            "score": self.score,
            "response_time": self.response_time,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "attempt_number": self.attempt_number,
            "confidence_level": self.confidence_level,
            "difficulty_perception": self.difficulty_perception,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calculate_performance_metrics(self):
        """パフォーマンス指標を計算"""
        metrics = {
            "accuracy": 1.0 if self.is_correct else 0.0,
            "response_efficiency": None,
            "confidence_accuracy_ratio": None
        }
        
        # 回答効率（推定時間との比較）
        if self.response_time and hasattr(self.question, 'estimated_time') and self.question.estimated_time:
            metrics["response_efficiency"] = self.question.estimated_time / self.response_time
        
        # 確信度と正確性の比率
        if self.confidence_level and self.is_correct is not None:
            accuracy_score = 1.0 if self.is_correct else 0.0
            metrics["confidence_accuracy_ratio"] = accuracy_score / (self.confidence_level / 5.0)
        
        return metrics