"""Create Q&A source documents from allowlisted public course materials."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "workshop/qna_materials"
PAGES = "start agent langchain graph harness mcp a2a wrap engineering build advanced-quiz".split()

def build():
    documents = {}
    for name in PAGES:
        source = ROOT / f"books/workshop/{name}.md"
        documents[f"textbook/{name}.md"] = f"원본: books/workshop/{name}.md\n\n" + source.read_text(encoding="utf-8")
    for source in sorted((ROOT / "workshop/notebooks").glob("*.ipynb")):
        if source.stem == "qna":
            continue
        chunks = [f"# 원본: notebooks/{source.name}\n"]
        for n, cell in enumerate(json.loads(source.read_text(encoding="utf-8"))["cells"], 1):
            body = "".join(cell["source"])
            chunks.append(f"\n## 셀 {n} · ID {cell.get('id', '없음')}\n")
            chunks.append(body if cell["cell_type"] == "markdown" else f"```python\n{body}\n```")
        documents[f"notebooks/{source.stem}.md"] = "\n".join(chunks)
    for folder in ["course", "build_lab"]:
        for source in sorted((ROOT / "workshop" / folder).glob("*.py")):
            documents[f"code/{folder}/{source.stem}.md"] = f"원본: {folder}/{source.name}\n\n```python\n" + source.read_text(encoding="utf-8") + "\n```\n"
    documents["INDEX.md"] = "# Q&A 자료 목록\n\n교재 원문은 textbook/, 실습과 풀이(이름에 solution)는 notebooks/, 실행 모듈은 code/입니다. 교재의 삽입 표시는 build.md 및 실행 모듈에서 확인합니다. 환경 설정과 개인 작성 파일은 포함하지 않습니다.\n\n" + "\n".join(f"- {name}" for name in sorted(documents))
    for name, body in documents.items():
        target = DEST / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    print(f"Q&A materials: {len(documents)}")

if __name__ == "__main__":
    build()
