"""
Jグランツ補助金検索チャットシステム - FastAPI バックエンド
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

from api.chat import chat_with_claude, chat_with_openai, chat_with_both
from api.jgrants import search_subsidies, get_subsidy_detail, search_active_subsidies

# 環境変数の読み込み
load_dotenv()

# FastAPIアプリケーションの初期化
app = FastAPI(
    title="Jグランツ補助金検索チャットAPI",
    description="補助金情報をAIチャットで検索できるAPIシステム",
    version="1.0.0"
)

# CORS設定（フロントエンドからのアクセスを許可）
# 環境変数からフロントエンドURLを取得（本番環境対応）
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# リクエストモデル定義
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "both"  # "claude", "openai", "both"


class SubsidySearchRequest(BaseModel):
    keyword: str
    acceptance: Optional[int] = None
    target_area: Optional[str] = None
    sort: str = "created_date"
    order: str = "DESC"


class SubsidyDetailRequest(BaseModel):
    subsidy_id: str


# ルート定義
@app.get("/")
async def root():
    """
    APIのルート - ヘルスチェック
    """
    return {
        "message": "Jグランツ補助金検索チャットAPI",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    チャット処理エンドポイント

    Claude、OpenAI、または両方のモデルでチャット処理を実行
    """
    # メッセージを辞書形式に変換
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

    try:
        if request.model == "claude":
            result = await chat_with_claude(messages)
            return {"responses": {"claude": result}}

        elif request.model == "openai":
            result = await chat_with_openai(messages)
            return {"responses": {"openai": result}}

        elif request.model == "both":
            results = await chat_with_both(messages)
            return {"responses": results}

        else:
            raise HTTPException(status_code=400, detail="Invalid model parameter")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")


@app.post("/api/subsidies/search")
async def search_subsidies_endpoint(request: SubsidySearchRequest) -> Dict[str, Any]:
    """
    補助金検索エンドポイント（直接検索）
    """
    try:
        result = search_subsidies(
            keyword=request.keyword,
            acceptance=request.acceptance,
            target_area_search=request.target_area,
            sort=request.sort,
            order=request.order
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.get("/api/subsidies/active")
async def search_active_subsidies_endpoint(
    keyword: str,
    target_area: Optional[str] = None
) -> Dict[str, Any]:
    """
    募集中の補助金検索エンドポイント
    """
    try:
        result = search_active_subsidies(keyword, target_area)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.post("/api/subsidies/detail")
async def get_subsidy_detail_endpoint(request: SubsidyDetailRequest) -> Dict[str, Any]:
    """
    補助金詳細取得エンドポイント
    """
    try:
        result = get_subsidy_detail(request.subsidy_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detail fetch error: {str(e)}")


@app.get("/api/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    api_keys_status = {
        "anthropic": "configured" if os.getenv("ANTHROPIC_API_KEY") else "missing",
        "openai": "configured" if os.getenv("OPENAI_API_KEY") else "missing"
    }

    return {
        "status": "healthy",
        "api_keys": api_keys_status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
