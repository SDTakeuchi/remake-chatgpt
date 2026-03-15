"""LangChain ChatOpenAI でストリーミング応答（OpenAI / Gemini OpenAI 互換 API 対応）。"""

from collections.abc import AsyncIterator
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from schemas import ChatMessage, ChatRole


def to_langchain_messages(messages: list[ChatMessage]) -> list[BaseMessage]:
    """
    API の messages を LangChain の BaseMessage リストに変換。
    """
    histories: list[BaseMessage] = []
    for m in messages:
        match m.role:
            case ChatRole.USER:
                histories.append(HumanMessage(content=m.content))
            case ChatRole.ASSISTANT:
                histories.append(AIMessage(content=m.content))
    return histories


def create_chat_model(llm_config: dict) -> BaseChatModel:
    """
    OpenAI または OpenAI 互換 API（Gemini 含む）で ChatOpenAI を生成。
    """
    kwargs: dict = {
        "model": llm_config.get("model", "gpt-4o-mini"),
        "temperature": 0.3,
        "api_key": llm_config.get("api_key", ""),
        "streaming": True,
    }
    base_url = (llm_config.get("base_url") or "").strip().rstrip("/")
    if base_url:
        kwargs["openai_api_base"] = base_url
    return ChatOpenAI(**kwargs)


def _chunk_content_to_str(content) -> str:
    """
    チャンク content を str に正規化（str | list[str|dict] | None 対応）。
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
        return "".join(parts)
    return str(content)


async def stream_chat(
    model: BaseChatModel,
    messages: list[ChatMessage],
) -> AsyncIterator[str]:
    """
    メッセージを LangChain 形式に変換し、ストリームでトークンを yield する。
    """
    lc_messages = to_langchain_messages(messages)
    async for chunk in model.astream(lc_messages):
        # astream()は AIMessageChunk 型のオブジェクトを返す
        text: str = _chunk_content_to_str(chunk.content)
        if text != "":
            yield text
