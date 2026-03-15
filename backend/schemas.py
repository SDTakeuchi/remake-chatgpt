"""API リクエスト/レスポンスの Pydantic スキーマ（型とバリデーション）。"""
from enum import StrEnum

from pydantic import BaseModel, Field


class ChatRole(StrEnum):
    """チャットメッセージの役割（OpenAI Chat API 互換）。"""

    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    """1件のチャットメッセージ（OpenAI Chat API 互換）。"""

    role: ChatRole = Field(..., description="送信者")
    content: str = Field(..., min_length=0, description="メッセージ本文")


class ChatRequest(BaseModel):
    """POST /chat のリクエストボディ。"""

    messages: list[ChatMessage] = Field(
        ...,
        min_length=1,
        description="会話履歴（時系列）。最後がユーザー発言である想定。",
    )
