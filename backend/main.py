"""POST /chat でストリーミング応答（SSE）。API 仕様は docs/prompts に準拠。"""

import json
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from starlette.responses import ContentStream

from chat import create_chat_model, stream_chat
from config import load_config
from schemas import ChatRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="remake-chatgpt backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = load_config()
chat_model = create_chat_model(config["llm"])


async def sse_chat_stream(body: ChatRequest) -> ContentStream:
    """SSE: data: {"content": "..."} を送り、終了時に data: [DONE] を送る。"""
    try:
        # プロキシ等のバッファリングを防ぐため先頭で1イベント送る
        yield ": stream start\n\n"
        chunk_count = 0
        async for chunk in stream_chat(chat_model, body.messages):
            chunk_count += 1
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        logger.info("stream_chat finished, chunks=%s", chunk_count)
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.exception("stream_chat error")
        msg = str(e)
        if (
            "429" in msg
            or "quota" in msg.lower()
            or "RateLimitError" in type(e).__name__
        ):
            msg = "利用枠（クォータ）を超えています。プラン・請求を確認してください。"
        yield f"data: {json.dumps({'error': msg})}\n\n"


@app.post("/chat")
async def chat(body: ChatRequest):
    return StreamingResponse(
        content=sse_chat_stream(body),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
