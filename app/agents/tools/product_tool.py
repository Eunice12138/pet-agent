from langchain_core.tools import tool

from app.rag.retriever import retrieve, format_context


@tool
def search_products(query: str) -> str:
    """
    查询店铺商品信息。适用于：
    - "你们店有什么狗粮"
    - "金毛吃什么粮好"
    - "狗粮多少钱"
    - "有什么洗护用品推荐"

    参数:
        query: 用户的自然语言问题

    返回:
        匹配的商品信息
    """
    docs = retrieve(query, top_k=3)
    if not docs:
        return "没有找到相关商品。"

    # 只保留来源是 06_products.txt 的
    product_docs = [d for d in docs if "06_products" in d.metadata.get("source", "")]
    if not product_docs:
        # 没有精确匹配，返回全部
        product_docs = docs

    context, sources = format_context(product_docs)
    return f"{context}\n\n【来源】{', '.join(sources)}"