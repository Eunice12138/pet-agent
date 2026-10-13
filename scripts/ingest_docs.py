"""
灌库脚本：把 data/knowledge/ 下的所有 TXT 灌入 Chroma 向量库

使用方法：
    py -3.11 scripts/ingest_docs.py          # 增量灌库
    py -3.11 scripts/ingest_docs.py --reset  # 清空重建
"""
import sys
from pathlib import Path

# 把项目根目录加入 sys.path（这样能 import app.xxx）
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.ingest import ingest_all


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    if reset:
        print("⚠️  --reset 模式：将清空旧的向量库\n")

    count = ingest_all(reset=reset)
    print(f"\n🎉 完成！共 {count} 个片段")