---
layout: page
title: AI Agent 개발 과정 목차
sidebar: false
aside: false
pageClass: lec-page
---
<div class="lec workshop-edition"><div class="deck"><section class="slide">
<div class="eyebrow">2026.09 · 개인 실습</div>

# 개념을 배우고 내 Agent를 완성합니다

[2026.09-rc1 실습 ZIP 받기](./downloads/agent-workshop-2026.09-rc1.zip) · [Git으로 받기](./git-setup)

<p class="lead">Agent 개념을 처음 접하는 개발자도 작은 예제에서 시작합니다. LangChain·LangGraph·Harness·Loop Engineering·MCP·A2A(+ACP)를 배우고, 도구·Agent·업무 분기를 직접 구현하고, 제공 그래프·루프에 연결합니다. 코딩 하네스는 개념과 활용 판단을 익힙니다.</p>

강사 소개와 설문 리뷰 10분으로 시작한 뒤 [환경 준비](./workshop/start#setup)를 함께 진행합니다. 자료 받기부터 편집기·의존성·키 설정·첫 호출까지 확인하고 본 실습으로 이어갑니다.

각 장은 **개념 → 실습 → 풀이** 순서로 읽습니다. 실습 안내는 해당 장 안에 있으며, VS Code에서 같은 `build_lab/student.py`를 이어서 완성합니다. 교재의 Python 실행 칸은 작은 동작을 확인하는 용도입니다. [실습 전체 모아보기](./workshop/build)는 복습할 때 사용합니다.

## 하루 학습 흐름

아래 시각은 예상 진행 기준입니다. 각 세션과 작은 섹션에 예상 시작·종료와 소요 시간을 표시하고, ‘강사용 예상 시간’에 활동 배분과 조절 기준을 제공합니다. 작은 섹션의 시각은 기본 배정을 누적한 기준이며 실제 진행에 따라 이동합니다. ‘생각거리 +3분’은 여유가 있을 때 선택하며 다음 활동 시간을 조절합니다. 설치 시간은 환경에 따라 달라지며, 일찍 마치면 다음 개념 설명으로 이어갑니다.

| 시간 | 학습 주제 | 직접 확인할 결과 |
|---|---|---|
|09:00–09:10|[강사 소개·설문 리뷰](./workshop/start#opening)|경험·관심 업무·질문과 오늘의 학습 연결|
|09:10–09:40|[시작 안내·공동 환경설정](./workshop/start#icebreaker)|자료·편집기·의존성·키 설정, 첫 호출 확인|
|09:40–10:30|[Agent 입문](./workshop/agent#icebreaker)|ReAct의 판단·행동·관찰, 다른 연구 접근과 Harness 구분|
|10:30–10:40|휴식|—|
|10:40–11:50|[LangChain](./workshop/langchain#icebreaker)|모델 설정·도구 등록·Agent 생성과 실행|
|11:50–12:50|점심|—|
|12:50–14:00|[LangGraph](./workshop/graph#icebreaker)|정보가 부족할 때 질문으로 분기|
|14:00–14:10|휴식|—|
|14:10–15:20|[Harness·Loop·Graph Engineering](./workshop/harness#icebreaker)|반복 작업·역할 의존성·검증·중단 판단|
|15:20–15:30|휴식|—|
|15:30–16:35|[MCP](./workshop/mcp#icebreaker)|별도 도구 서버의 조회 결과|
|16:35–16:45|휴식|—|
|16:45–17:30|[A2A·ACP](./workshop/a2a#icebreaker)|작업 상태와 검토 산출물 구분|
|17:30–18:00|[통합·정리](./workshop/wrap#icebreaker)|업무 별칭을 직접 추가하고 기존 동작 유지 확인|

**수업은 18:00에 종료합니다.** 점심은 11:50–12:50입니다. 위 시간표를 당일 진행 기준으로 삼고, 강사가 설문과 현장 반응에 따라 설명·실습의 진행 속도를 조절합니다. 각 장의 활동별 시간은 참고 배정이며 교재 전체를 같은 속도로 읽는 일정은 아닙니다.

각 세션은 최근 사례를 바탕으로 한 **시작 질문 2~3분**으로 문을 엽니다. 이 시간은 위 세션 시간에 포함됩니다. 교재의 개념·실습·심화 자료는 그대로 제공하며 수업 중 다루지 못한 부분은 복습할 수 있습니다.

[Loop·Graph Engineering의 실제 담론과 활용](./workshop/engineering) — Harness 모듈의 개념·개인 활동 자료입니다. 그래프·루프 전체 구현은 선택 심화입니다.

[기술 변화와 추가 읽기](./updates) · [이전 판 교재 (2026.06)](./archive/2026-06)

</section></div></div>
