"""
Lecture model for storing lecture information
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Lecture(BaseModel):
    """講義情報を管理するモデル"""
    __tablename__ = "lectures"
    
    # 基本情報
    title = Column(String(255), nullable=False, comment="講義タイトル")
    description = Column(Text, nullable=True, comment="講義の説明")
    
    # ファイル情報
    original_filename = Column(String(255), nullable=False, comment="元のファイル名")
    file_path = Column(String(500), nullable=False, comment="ファイルパス")
    file_size = Column(Integer, nullable=False, comment="ファイルサイズ（バイト）")
    
    # 抽出された内容
    total_slides = Column(Integer, nullable=False, default=0, comment="総スライド数")
    extracted_content = Column(Text, nullable=True, comment="抽出されたコンテンツ（JSON形式）")
    
    # 処理状況
    is_processed = Column(Boolean, default=False, nullable=False, comment="処理完了フラグ")
    processing_status = Column(String(50), default="pending", comment="処理状況")
    error_message = Column(Text, nullable=True, comment="エラーメッセージ")
    
    # メタデータ
    author = Column(String(100), nullable=True, comment="講師名")
    subject = Column(String(100), nullable=True, comment="科目名")
    lecture_date = Column(DateTime, nullable=True, comment="講義日時")
    
    # リレーション
    questions = relationship("Question", back_populates="lecture", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Lecture(id={self.id}, title='{self.title}', slides={self.total_slides})>"
    
    def to_dict(self):
        """辞書形式で返す"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "original_filename": self.original_filename,
            "total_slides": self.total_slides,
            "is_processed": self.is_processed,
            "processing_status": self.processing_status,
            "author": self.author,
            "subject": self.subject,
            "lecture_date": self.lecture_date.isoformat() if self.lecture_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }