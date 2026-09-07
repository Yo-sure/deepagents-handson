---
title: 2026.09 기술 변화와 추가 읽기
---

# 2026.09 기술 변화와 추가 읽기

확인일은 2026-09-06입니다. 수업은 검증한 `uv.lock`으로 진행하고, 새 버전의 변경 사항은 공식 릴리스 노트와 실행 결과를 함께 확인합니다. 아래는 수업 중 관련 개념을 배울 때 참고하거나 수업 후 읽는 자료입니다.

| 변화 | 교재에서 달라진 부분 | 확인할 질문 |
|---|---|---|
|LangChain v1의 `create_agent`와 middleware|모델·도구 연결부터 배우고 실행 제어를 분리|구성을 만든 시점과 도구가 실행되는 시점은 언제인가?|
|DeepAgents v0.7의 기본 구성 축소|계획 도구가 항상 있다고 가정하지 않음|추가 구성이 실제 문제를 해결하는가?|
|MCP 2026-07-28의 세션·초기화 변경|새 요청 버전을 지정한 실제 HTTP 실습|연결 상태와 업무 저장소의 차이는 무엇인가?|
|ACP 명칭과 연결 대상|A2A와 두 ACP를 구분|Agent 간 작업 위임인가, 편집기와 Agent의 연결인가?|

## 검증한 최신 안정 버전

PyPI의 최신 배포 정보와 설치 lock을 2026-09-06에 대조했습니다. 핵심 패키지는 아래 버전이며, 이 목록이 수업 이후에도 최신이라는 뜻은 아닙니다.

|패키지|수업 버전|배포일|
|---|---|---|
|[LangChain](https://pypi.org/project/langchain/)|1.4.0|2026-09-03|
|[langchain-openai](https://pypi.org/project/langchain-openai/)|1.6.0|2026-08-19|
|[LangGraph](https://pypi.org/project/langgraph/)|1.2.11|2026-08-11|
|[DeepAgents](https://pypi.org/project/deepagents/)|0.7.13|2026-09-02|
|[MCP Python SDK](https://pypi.org/project/mcp/)|2.1.1|2026-08-25|
|[A2A SDK](https://pypi.org/project/a2a-sdk/)|1.1.2|2026-07-22|

## LangChain: 연결과 실행 제어를 함께 봅니다

LangChain v1은 `create_agent`를 중심으로 Agent 구성을 정리하고, 모델·도구 호출 전후의 동작을 middleware로 제어합니다. `create_agent`는 LangGraph 위에서 실행됩니다. 수업에서는 API 이름만 외우기보다 도구 요청과 실제 실행, 상태 저장과 재개의 역할을 구분합니다. [공식 v1 변경 안내](https://docs.langchain.com/oss/python/releases/langchain-v1)

2026-09-03에는 MCP 연동이 `langchain.mcp`에 들어왔습니다. 수업에도 `MCPAdapter`로 원격 조회 도구를 연결하는 예제를 추가했습니다. 라이브러리 정식 버전 안에서도 이 API 자체는 beta이므로 구분해서 봅니다. 목록 캐시·elicitation 지원 소식도 있지만, 이번 기본 실습의 범위는 도구 목록과 호출입니다. [공식 변경 글](https://www.langchain.com/blog/mcp-in-langchain-stateless-protocol-elicitation-and-more)

## Harness: 기본 구성이 많을수록 좋은가

DeepAgents v0.7에서는 `TodoListMiddleware`가 기본 구성에서 빠지고 선택 사항이 됐습니다. 공식 설명은 평가 결과를 보고 구성을 줄였다고 밝힙니다. 이것이 모든 업무에서 계획이 불필요하다는 뜻은 아닙니다. 수업에서도 도구·계획·subagent를 추가한 개수보다 실패 사례가 어떻게 달라졌는지 확인합니다. [공식 v0.7 발표](https://www.langchain.com/blog/deep-agents-v0-7)

## MCP: 배포된 변경과 로드맵을 구분합니다

2026-07-28에는 프로토콜 세션과 초기화 handshake가 제거됐고 `server/discover`로 지원 정보를 확인할 수 있게 됐습니다. Tasks는 공식 확장으로 옮겨졌습니다. 이 교재의 기본 실습은 도구 조회·호출이며 Tasks를 구현한 것은 아닙니다.

새 로드맵에는 Agent 메시징, HTTP 전송, Agent 신원과 보안, 기본 기능, SDK 개발 경험이 포함됩니다. 로드맵에 있다는 사실만으로 현재 SDK가 모두 지원한다고 판단하지 않습니다. [공식 로드맵](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/)

주제를 찾는 읽기 자료로는 [GeekNews의 새 MCP 로드맵 소개](https://news.hada.io/topic?id=32777)가 있습니다. 구현 여부와 API 계약을 판단할 때는 해당 글이 연결하는 공식 원문·명세·SDK를 확인합니다.

## ACP: 약어만으로 판단하지 않습니다

Agent Communication Protocol 공식 사이트는 A2A에 합류했음을 안내합니다. Agent Client Protocol은 편집기/IDE와 코딩 Agent의 통신을 다루는 별도 프로젝트입니다. 이름이 같아도 연결 대상이 다르므로 교재에서 풀네임을 함께 확인합니다. [Agent Communication Protocol 안내](https://agentcommunicationprotocol.dev/introduction/welcome), [Agent Client Protocol 소개](https://agentclientprotocol.com/get-started/introduction)

## 새 글을 읽을 때의 확인 순서

흥미로운 사례를 찾으면 발행일·대상 버전·원문을 확인합니다. 그다음 최소 예제를 실행하고, 현재 과제의 입력과 실패 조건에도 적용되는지 시험합니다. 코드 계약 검사, 실제 모델 판단, 운영 환경의 신뢰성은 서로 다른 검증 범위입니다.

## 최근 아티클을 수업에 적용한 기준

### 입력·환경·성공 조건을 먼저 적습니다

LangChain의 2026-08-25 글은 과제를 바로 코드로 생성하기 전에 입력·실행 환경·채점 기준을 문서로 정하고, 실제 실행을 보며 보완하는 과정을 설명합니다. 수업의 종합 문제에도 이 순서를 적용했습니다. 학생은 자신이 고른 실패 사례의 성공 조건부터 작성한 뒤 수정 위치를 고릅니다. 자동 생성된 과제가 실제 업무와 맞는지는 사람이 확인해야 합니다. [원문](https://www.langchain.com/blog/building-agent-environments-and-tasks)

### 코드 검사와 모델 평가를 나눕니다

LangChain의 2026-03-26 평가 글은 SDK 연결·설정 검사를 모델 능력 평가와 구분합니다. Anthropic의 2026-01-09 글도 코드·모델·사람의 평가가 서로 다른 장단점을 가진다고 설명합니다. 최신 기사만으로 채우지 않고, 지금의 실습 결과를 잘못 해석하지 않게 해주는 자료도 함께 읽습니다. [LangChain 평가 설계](https://www.langchain.com/blog/how-we-build-evals-for-deep-agents), [Anthropic 평가 설명](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

수업의 자동 검사가 통과해도 여러 표현의 문의를 제대로 해석하는지는 따로 확인해야 합니다. 모델을 바꿀 때도 정상 입력뿐 아니라 정보 부족·잘못된 정책·검토 실패 입력을 다시 실행합니다. 코드 검사는 팀명과 ID를 확인하고, 정책과 답변의 의미가 맞는지는 사람이나 별도로 검증한 평가 방법으로 살펴봅니다.

### 긴 실행에서는 평가 기준과 인계할 상태가 필요합니다

Anthropic의 2026-03-24 사례는 생성과 평가를 나누고 구체적인 평가 기준을 만드는 접근을 설명합니다. 긴 작업을 작은 단위로 나누고 다음 실행에 필요한 상태를 전달하는 설계도 다룹니다. 이를 모든 업무의 필수 다중 Agent 구조로 일반화하지 않습니다. 이 수업은 먼저 작은 수정 루프와 메모리 재개의 한계를 관찰합니다. [원문](https://www.anthropic.com/engineering/harness-design-long-running-apps)


## 2026-09-07 · 코딩 에이전트로 실행 구조 개선하기

Codex의 작업 범위·검증 지침, Claude Code의 실행 가능한 확인 기준, LangChain의 trace 기반 하네스 개선 사례를 대조했습니다. 제품 내부 구현이 같은 그래프라고 단정하지 않고, 현재 과제의 분기·수정 종료 조건을 변경하고 확인하는 활동으로 적용했습니다.

[설계 확장 실습](./workshop/engineering)에서 공백 입력, 동일 초안 정체, 마지막 허용 수정의 성공, 개선 없는 예산 소진을 다룹니다. 학생이 고친 두 함수를 실제 통합 요청에 연결하여 검사 파일만 통과한 상태와 실제 실행을 구분합니다.

출처: [Codex 모범 사례](https://learn.chatgpt.com/guides/best-practices), [Claude Code 모범 사례](https://code.claude.com/docs/en/best-practices), [LangChain 하네스 개선](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering).
