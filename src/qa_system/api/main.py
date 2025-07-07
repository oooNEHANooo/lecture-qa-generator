"""
Main FastAPI application
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path

from src.qa_system.config import settings
from src.qa_system.models.base import init_db
from .routers import lectures, questions, analytics

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPIアプリケーションの作成
app = FastAPI(
    title="QA System",
    description="講義内容の確認QAの作成システム",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルとテンプレートの設定
static_dir = Path(__file__).parent.parent / "static"
templates_dir = Path(__file__).parent.parent / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

templates = Jinja2Templates(directory=str(templates_dir))

# ルーターの登録
app.include_router(lectures.router, prefix="/api/lectures", tags=["lectures"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])


@app.on_event("startup")
async def startup_event():
    """アプリケーション開始時の処理"""
    logger.info("QA System を開始しています...")
    
    # データベースの初期化
    try:
        init_db()
        logger.info("データベースの初期化が完了しました")
    except Exception as e:
        logger.error(f"データベースの初期化に失敗: {e}")
        raise
    
    logger.info("QA System の開始が完了しました")


@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時の処理"""
    logger.info("QA System を終了しています...")


@app.get("/")
async def read_root(request: Request):
    """ホームページ"""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "QA System"}
    )


@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "debug": settings.debug
    }


@app.get("/lectures")
async def lectures_page(request: Request):
    """講義一覧ページ"""
    return templates.TemplateResponse(
        "lectures.html",
        {"request": request, "title": "講義一覧"}
    )


@app.get("/questions")
async def questions_page(request: Request):
    """質問一覧ページ"""
    return templates.TemplateResponse(
        "questions.html",
        {"request": request, "title": "質問一覧"}
    )


@app.get("/analytics")
async def analytics_page(request: Request):
    """分析ページ"""
    return templates.TemplateResponse(
        "analytics.html",
        {"request": request, "title": "理解度分析"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )