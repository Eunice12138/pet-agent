from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings


def get_llm() -> ChatOpenAI:
    """
    获取 LLM 客户端。
    使用 DashScope 的 OpenAI 兼容接口，模型可插拔：
    - 换供应商：改 QWEN_BASE_URL
    - 换模型：改 QWEN_MODEL
    """
    if not settings.DASHSCOPE_API_KEY:
        raise ValueError(
            "DASHSCOPE_API_KEY 未配置，请检查 .env 或系统环境变量"
        )

    return ChatOpenAI(
        model=settings.QWEN_MODEL,
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        temperature=0.7,
        timeout=60,
        max_retries=2,
    )


def get_embedding() -> OpenAIEmbeddings:
    """获取 Embedding 模型（用 DashScope 兼容接口）"""
    if not settings.DASHSCOPE_API_KEY:
        raise ValueError("DASHSCOPE_API_KEY 未配置")

    return OpenAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.QWEN_BASE_URL,
        check_embedding_ctx_length=False,   # ⚠️ DashScope 兼容关键
    )