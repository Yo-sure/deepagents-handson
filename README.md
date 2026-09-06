# AI Agent 개발 · 2026.09

개념 설명 → 함께 실행 → 개인 기본/확장 과제 → 풀이로 구성한 하루 과정입니다.
LangChain, LangGraph, Harness와 Loop Engineering, MCP, A2A 및 ACP의 역할을 배웁니다.

- [교재 목차](https://yo-sure.github.io/deepagents-handson/toc)
- 새 실습: [workshop/README.md](workshop/README.md)
- 원고: `books/workshop/` (웹 페이지는 빌드 시 생성)
- 기존 코드와 교재는 보존하며 웹의 이전 판 목차에서 열람할 수 있습니다.

```bash
cd workshop
uv sync --locked
uv run python -m course.cli langchain --mode fixed
```

fixed는 API 키 없이 실행합니다. 모델 응답은 결정론적이며, MCP/A2A는 실제 로컬 HTTP를 사용합니다.
live는 유효한 API 키와 수업 전 실행 확인이 필요합니다.

---

## 이전 판 안내 (2026.06)

아래 실행 안내는 기존 `ch*/` 및 `analyst/` 예제용입니다. 새 과정에는 위의 workshop 안내를 사용합니다.

# AI Agent 개발 — 인박스 리서치 애널리스트

교재(GitHub Pages): **https://yo-sure.github.io/deepagents-handson/**
