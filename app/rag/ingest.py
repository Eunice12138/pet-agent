from pathlib import Path
from typing import List

from langchain_core.documents import Document

from app.rag.vectorstore import get_vectorstore, get_text_splitter


KNOWLEDGE_DIR = Path("./data/knowledge")


def load_documents() -> List[Document]:
    """加载 knowledge 目录下所有 txt 文件"""
    docs = []
    if not KNOWLEDGE_DIR.exists():
        raise FileNotFoundError(f"知识目录不存在: {KNOWLEDGE_DIR}")

    for file in KNOWLEDGE_DIR.glob("*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            continue

        doc = Document(
            page_content=content,
            metadata={"source": file.name, "path": str(file)},
        )
        docs.append(doc)
        print(f"  ✅ 加载: {file.name} ({len(content)} 字)")

    return docs


def ingest_all(reset: bool = False) -> int:
    """把所有知识文档灌入向量库"""
    print("📚 开始加载知识文档...")
    docs = load_documents()
    print(f"\n共加载 {len(docs)} 个文档")

    print("\n✂️  切块中...")
    splitter = get_text_splitter()
    chunks = splitter.split_documents(docs)
    print(f"切出 {len(chunks)} 个片段")

    print("\n💾 写入向量库...")
    vectorstore = get_vectorstore()

    if reset:
        try:
            vectorstore.delete_collection()
            vectorstore = get_vectorstore()
            print("  已清空旧的向量库")
        except Exception:
            pass

    vectorstore.add_documents(chunks)
    print(f"\n✅ 灌库完成！共 {len(chunks)} 个片段已存入 Chroma")
    return len(chunks)