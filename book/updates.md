---
layout: page
title: 버전 확인과 목적별 참고 자료
sidebar: false
aside: false
pageClass: lec-page
---
<div class="lec workshop-edition"><div class="deck">
<section class="slide">
<div class="eyebrow">참고 자료 · 버전 확인과 수업 후 학습</div>

# 버전 확인과 목적별 참고 자료

실습 중 막혔다면 먼저 해당 장의 선행 셀과 완료 기준을 확인합니다. 공식 문서는 구현을 확장하거나 수업 코드와 다른 예제를 비교할 때 읽습니다. **설치 버전 확인 → 알고 싶은 질문 선택 → 원문 예제와 비교** 순서로 사용합니다.

|지금 필요한 것|바로 갈 곳|
|---|---|
|설치와 첫 모델 호출|[시작 안내](./workshop/start#setup)|
|중간 장부터 재개하거나 풀이와 비교|[실습 전체 모아보기](./workshop/build)|
|배운 개념을 다시 확인|[기본 퀴즈](./workshop/wrap#wrap), [코드·설계 심화 10문항](./workshop/advanced-quiz)|
|다음 작업·검토·중단 규칙을 설계|[Loop·Graph 설계](./workshop/engineering)|

</section>
<nav class="lesson-nav" aria-label="참고 자료 탐색"><a href="#versions">01 수업 버전</a><a href="#reading">02 목적별 원문</a><a href="#compare">03 예제 비교</a></nav>
<section class="slide" id="versions">

## 수업 버전부터 확인합니다

수업은 `workshop/pyproject.toml`과 `uv.lock`에 고정한 조합을 사용합니다. 아래 표는 이 조합의 핵심 패키지입니다. 외부 문서의 최신 예제가 다른 이름이나 동작을 사용한다면 먼저 대상 버전을 확인합니다.

|패키지|수업 버전|주로 확인할 위치|
|---|---|---|
|langchain|1.4.0|create_agent, langchain.mcp의 MCPAdapter|
|langchain-openai|1.6.0|공통 모델 연결|
|langgraph|1.2.11|StateGraph, 분기, 중단·재개|
|deepagents|0.7.13|create_deep_agent, Skill 연결|
|mcp|2.1.1|MCPServer, 프로토콜 2026-07-28|
|a2a-sdk|1.1.2|Card, Message, Task, HTTP 바인딩|

노트북에서 다음 셀을 실행하면 **현재 커널에 설치된 버전**을 확인할 수 있습니다. 시스템 Python의 버전과 혼동하지 않도록 실행 경로도 함께 봅니다.

```python
import sys
from importlib.metadata import version

print("실행 Python:", sys.executable)
for package in ["langchain", "langchain-openai", "langgraph", "deepagents", "mcp", "a2a-sdk"]:
    print(package, version(package))
```

표와 다르면 현재 커널이 실습 폴더의 `.venv`를 사용하는지 먼저 확인합니다. 실습 중 패키지 하나만 최신으로 올리기보다, [환경 준비](./workshop/start#setup)의 고정된 조합으로 돌아와 같은 입력을 실행합니다.

### 예전 예제를 읽을 때 달라 보이는 부분

|예전 자료에서 볼 수 있는 것|수업에서 사용하는 것|비교할 질문|
|---|---|---|
|create_react_agent 중심 예제|LangChain의 create_agent|모델·도구를 연결하는 함수의 소속과 인자가 같은가?|
|DeepAgents에 계획 도구가 항상 있다는 설명|설정에 따라 달라지는 기본 구성|실제 도구 목록에 무엇이 들어 있는가?|
|MCP initialize 이후 세션을 사용하는 흐름|2026-07-28 요청별 정보 전달|예제가 어떤 프로토콜 버전을 대상으로 하는가?|
|ACP라는 약어만 표시|Agent Communication Protocol과 Agent Client Protocol 구분|Agent 간 위임인가, 편집기와 코딩 Agent의 연결인가?|

LangChain v1의 API 전환은 [공식 변경 안내](https://docs.langchain.com/oss/python/releases/langchain-v1), DeepAgents의 기본 구성 변화는 [v0.7 발표](https://www.langchain.com/blog/deep-agents-v0-7)에서 확인합니다. MCP와 ACP의 구체적인 비교는 [MCP 장](./workshop/mcp#concept)과 [A2A 장](./workshop/a2a#concept)에 연결되어 있습니다.

</section>
<section class="slide" id="reading">

## 해결하려는 질문으로 원문을 고릅니다

한 번에 모두 읽기보다 현재 과제와 가까운 행 하나를 고릅니다. ‘읽을 부분’을 확인한 뒤 마지막 열의 결과를 자신의 실습 기록으로 설명합니다.

|해결하려는 질문|공식 자료와 읽을 부분|읽고 남길 결과|
|---|---|---|
|모델 호출과 도구 실행 사이를 어디서 제어할까?|[LangChain v1](https://docs.langchain.com/oss/python/releases/langchain-v1)의 create_agent·middleware|1B의 메시지 순서에 제어를 넣을 위치 표시|
|한 노드 안에 Agent나 다른 그래프를 넣으려면?|[LangGraph Subgraphs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs)의 공유 상태·변환 예제|부모 입력 → 하위 실행 → 부모 갱신 표|
|긴 실행에서 무엇을 기억하게 할까?|[Anthropic Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)의 조회·요약·외부 메모|다음 실행에 전달할 실패 기록과 추가 조회 위치|
|MCP 서버가 제공하는 기능과 전달 규칙은?|[MCP 2026-07-28 명세](https://modelcontextprotocol.io/specification/2026-07-28)의 아키텍처·서버 기능|4A 목록 조회와 4B 도구 호출을 구분한 요청 흐름|
|다른 Agent의 구현을 모르고 어떻게 위임할까?|[A2A 명세](https://a2a-protocol.org/latest/specification/)의 Agent Card·Message·Task|6D의 발견 결과, 선택한 기능, Task와 산출물 대조|
|도구나 계획 기능을 더 넣어야 할까?|[DeepAgents v0.7](https://www.langchain.com/blog/deep-agents-v0-7)의 기본 구성 변경|기능 추가 전후에 비교할 실패 입력 두 개|

명세는 메시지·기능의 약속을, SDK 문서는 Python에서 그 약속을 사용하는 방법을 설명합니다. 예를 들어 A2A의 Task 필드 의미는 명세에서 확인하고, 수업의 import와 서버 구성은 [A2A 장의 코드](./workshop/a2a#concept) 및 설치된 SDK와 대조합니다.

</section>
<section class="slide" id="compare">

## 새 예제를 가져오기 전에 비교할 것

예제가 실행되는 것과 자신의 과제를 해결하는 것은 다릅니다. 모델·도구·실행 조건 중 무엇을 바꾸었는지 한 번에 하나씩 구분해 확인합니다.

|변경|같은 조건으로 다시 실행할 입력|확인할 결과|
|---|---|---|
|모델 또는 지침|정상 문의·정보 부족·미등록 업무|도구 선택, 근거 사용, 불필요한 초안·위임 여부|
|SDK 또는 프로토콜|MCP 목록·호출, A2A Card·위임|요청·응답 형식과 실제 연결|
|그래프 또는 수정 루프|공백 연락처, 마지막 허용 수정, 같은 초안 반복|방문 경로, 호출 수, 종료 이유|
|역할 분리|같은 후보에 대한 두 검토, 한 결과 지연|누락·다른 버전의 결과를 합격으로 묶지 않는지|

**작은 비교 과제:** 6D에서 후보 순서를 바꾸었더니 담당자 선택이 달라졌습니다. 모델을 바꾸기 전에 어떤 요청·Card·도구 호출 기록을 비교해야 할까요? 자신의 답을 [설계 활동](./workshop/engineering#review)과 대조합니다.

더 읽고 싶다면 먼저 [심화 10문항](./workshop/advanced-quiz)에서 설명하기 어려웠던 문제를 고릅니다. 해당 문제의 원문을 읽고 답을 수정하면, 읽은 자료가 실제 설계 판단으로 이어졌는지 확인할 수 있습니다.

</section>
</div></div>
