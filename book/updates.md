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

## LangChain: 연결과 실행 제어를 함께 봅니다

LangChain v1은 `create_agent`를 중심으로 Agent 구성을 정리하고, 모델·도구 호출 전후의 동작을 middleware로 제어합니다. `create_agent`는 LangGraph 위에서 실행됩니다. 수업에서는 API 이름만 외우기보다 도구 요청과 실제 실행, 상태 저장과 재개의 역할을 구분합니다. [공식 v1 변경 안내](https://docs.langchain.com/oss/python/releases/langchain-v1)

## Harness: 기본 구성이 많을수록 좋은가

DeepAgents v0.7에서는 `TodoListMiddleware`가 기본 구성에서 빠지고 선택 사항이 됐습니다. 공식 설명은 평가 결과를 보고 구성을 줄였다고 밝힙니다. 이것이 모든 업무에서 계획이 불필요하다는 뜻은 아닙니다. 수업에서도 도구·계획·subagent를 추가한 개수보다 실패 사례가 어떻게 달라졌는지 확인합니다. [공식 v0.7 발표](https://www.langchain.com/blog/deep-agents-v0-7)

## MCP: 배포된 변경과 로드맵을 구분합니다

2026-07-28에는 프로토콜 세션과 초기화 handshake가 제거됐고 `server/discover`로 지원 정보를 확인할 수 있게 됐습니다. Tasks는 공식 확장으로 옮겨졌습니다. 이 교재의 기본 실습은 도구 조회·호출이며 Tasks를 구현한 것은 아닙니다.

새 로드맵에는 Agent 메시징, HTTP 전송, Agent 신원과 보안, 기본 기능, SDK 개발 경험이 포함됩니다. 로드맵에 있다는 사실만으로 현재 SDK가 모두 지원한다고 판단하지 않습니다. [공식 로드맵](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/)

주제를 찾는 읽기 자료로는 [GeekNews의 새 MCP 로드맵 소개](https://news.hada.io/topic?id=32777)가 있습니다. 구현 여부와 API 계약을 판단할 때는 해당 글이 연결하는 공식 원문·명세·SDK를 확인합니다.

## ACP: 약어만으로 판단하지 않습니다

Agent Communication Protocol 공식 사이트는 A2A에 합류했음을 안내합니다. Agent Client Protocol은 편집기/IDE와 코딩 Agent의 통신을 다루는 별도 프로젝트입니다. 이름이 같아도 연결 대상이 다르므로 교재에서 풀네임을 함께 확인합니다. [Agent Communication Protocol 안내](https://agentcommunicationprotocol.dev/introduction/welcome), [Agent Client Protocol 소개](https://agentclientprotocol.com/get-started/introduction)

## 새 글을 읽을 때의 확인 순서

흥미로운 사례를 찾으면 발행일·대상 버전·원문을 확인합니다. 그다음 최소 예제를 실행하고, 현재 과제의 입력과 실패 조건에도 적용되는지 시험합니다. 예제 한 번의 성공, 제공 모델의 고정 응답, 실제 모델 판단, 운영 환경의 신뢰성은 서로 다른 검증 범위입니다.
