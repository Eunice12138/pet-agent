from typing import List, Tuple

from langchain_core.documents import Document

from app.core.config import settings
from app.llm.client import get_llm
from app.rag.vectorstore import get_vectorstore


RAG_PROMPT = """你是一个宠物护理顾问。请根据以下知识库片段回答用户问题。

【知识库片段】
{context}

【用户问题】
{question}

【回答要求】
1. 优先使用知识库片段回答
2. 如果知识库没有相关信息，用通用知识回答，并注明"（通用知识）"
3. 回答简洁，200 字以内
4. 最后列出参考来源（如果有）
"""


def retrieve(query: str, top_k: int = None) -> List[Document]:
    """检索相关文档片段"""
    if top_k is None:
        top_k = settings.RAG_TOP_K

    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(query, k=top_k)
    return docs


def format_context(docs: List[Document]) -> Tuple[str, List[str]]:
    """把检索到的片段格式化为上下文 + 来源列表"""
    context_parts = []
    sources = []

    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "未知")
        context_parts.append(f"[片段 {i}] (来源: {source})\n{doc.page_content}")
        if source not in sources:
            sources.append(source)

    return "\n\n".join(context_parts), sources


async def rag_chat(query: str) -> Tuple[str, List[str]]:
    """RAG 完整流程：检索 → 拼 Prompt → LLM 生成"""
    # 1. 检索
    docs = retrieve(query)

    if not docs:
        # 没有检索到，退化为普通对话
        llm = get_llm()
        result = await llm.ainvoke([("human", query)])
        return result.content, []

    # 2. 格式化上下文
    context, sources = format_context(docs)

    # 3. 拼 Prompt
    prompt = RAG_PROMPT.format(context=context, question=query)

    # 4. 调 LLM
    llm = get_llm()
    result = await llm.ainvoke([("human", prompt)])

    return result.content, sources