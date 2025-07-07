"""
Base database model configuration
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, DateTime
from src.qa_system.config import settings

# データベースエンジンの作成
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # SQLクエリログの出力
    pool_pre_ping=True
)

# セッションの設定
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# メタデータの設定
metadata = MetaData()

# ベースクラスの作成
Base = declarative_base(metadata=metadata)


class BaseModel(Base):
    """全モデルの基底クラス"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


# データベースセッションの依存性注入
def get_db():
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# データベースの初期化
def init_db():
    """データベースを初期化"""
    Base.metadata.create_all(bind=engine)


# データベースのリセット（開発用）
def reset_db():
    """データベースをリセット（開発用）"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)