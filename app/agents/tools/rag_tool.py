from langchain_core.tools import tool

from app.rag.retriever import retrieve, format_context


@tool
def search_knowledge(query: str) -> str:
    """
    查询宠物护理知识库。适用于：
    - 宠物健康、症状、护理问题（如"金毛掉毛怎么办"）
    - 疫苗、驱虫相关问题
    - 品种养护建议
    - 门店政策、FAQ

    参数:
        query: 用户的自然语言问题

    返回:
        检索到的知识片段（含来源）
    """
    docs = retrieve(query, top_k=3)
    if not docs:
        return "知识库中没有找到相关信息。"

    context, sources = format_context(docs)
    result = f"{context}\n\n【来源】{', '.join(sources)}"
    return result