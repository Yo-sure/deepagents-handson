# AI Agent 개발 · 2026.09

개념 설명 → 함께 실행 → 개인 기본/확장 과제 → 풀이로 구성한 하루 과정입니다.
LangChain, LangGraph, Harness와 Loop Engineering, MCP, A2A 및 ACP의 역할을 배웁니다.

- [교재 목차](https://yo-sure.github.io/deepagents-handson/toc)
- 새 실습: [workshop/README.md](workshop/README.md)
- 원고: `books/workshop/` (웹 페이지는 빌드 시 생성)
- 기존 코드와 교재는 보존하며 웹의 이전 판 목차에서 열람할 수 있습니다.

```bash
cd workshop
uv sync --locked --python 3.12
uv run python -m course.cli langchain
```

실행 전에 `workshop/.env.example`을 참고해 `workshop/.env`에 실습용 키를 저장합니다. 모델 호출 예제는 실제 LLM을 사용하며, MCP/A2A는 실제 로컬 HTTP로 연결합니다. 설치부터 시작한다면 [환경 준비](books/workshop/start.md#setup)를 확인합니다.

[코딩 Harness 활용](books/workshop/engineering.md)에서는 실제 Loop·Graph Engineering 담론을 읽고 Codex·Claude Code에 반복 작업을 맡기는 조건과 여러 역할의 의존성을 설계합니다. 도구·Agent·업무 분기·MCP 공개·A2A 수용의 다섯 부분은 직접 구현하며, 전체 그래프와 반복 구조의 재구현은 선택 심화입니다.

---

## 이전 판 안내 (2026.06)

아래 실행 안내는 기존 `ch*/` 및 `analyst/` 예제용입니다. 새 과정에는 위의 workshop 안내를 사용합니다.

# AI Agent 개발 — 인박스 리서치 애널리스트

교재(GitHub Pages): **https://yo-sure.github.io/deepagents-handson/**
