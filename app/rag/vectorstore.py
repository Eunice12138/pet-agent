from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings
from app.llm.client import get_embedding


def get_vectorstore() -> Chroma:
    """获取或创建 Chroma 向量库"""
    return Chroma(
        collection_name="pet_knowledge",
        embedding_function=get_embedding(),
        persist_directory=settings.CHROMA_PERSIST_DIR,
    )


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """文档切块器"""
    return RecursiveCharacterTextSplitter(
        chunk_size=300,           # 每块 500 字
        chunk_overlap=50,         # 块之间重叠 50 字
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
    )