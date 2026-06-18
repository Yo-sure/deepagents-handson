---
layout: page
title: 교재 목차
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec">
<div class="deck">

<section class="slide hero">
<div>
<div class="eyebrow">2026 Edition · 목차</div>

# 인박스 리서치<br>애널리스트

<p class="lead">영수증·명세서·계약서 한 더미를 읽어 분류하고, 나눠 조사하고, 지식으로 쌓고, 외부 검증을 거쳐 브리프 한 장으로 끝냅니다.<br>
매 챕터가 손에 잡히는 부품 하나로 끝나고, Ch6에서 한 줄기로 조립됩니다.</p>

<div class="kicker">
<div class="metric"><span class="num">7</span><strong>챕터</strong><span>Ch0 환경 + Ch1~6</span></div>
<div class="metric"><span class="num">8</span><strong>시간</strong><span>이론 + 핸즈온</span></div>
<div class="metric"><span class="num">6</span><strong>부품</strong><span>키 없이도 동작(--mock)</span></div>
</div>
</div>

<div class="board">
<div class="board-header"><span>데이터 계약 — 부품이 주고받는 한 줄기</span><span class="status-pill">RecordV1</span></div>
<div class="panel-body"><div class="list">
<p><code>sample_inbox/ → classified/ → research_notes/ → knowledge_base/ → brief.md → verified_brief.md</code></p>
<p>모든 챕터가 같은 RecordV1과 디렉터리 규약을 쓰므로, 부품을 갈아끼워도 배선은 그대로입니다.</p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">챕터</div>

## 어디로 들어갈까

</div>
<p class="section-note">각 칸을 누르면 해당 챕터로 들어갑니다. 상단 메뉴의 "교재"로 언제든 이 목차로 돌아옵니다.</p>
</div>

<div class="stack">
<a class="row" href="/deepagents-handson/chapters/chapter-0" style="text-decoration:none;color:inherit">
<div class="code">0</div>
<div class="copy"><strong>환경 셋업 — 인박스 한 통 열어볼 준비</strong><p>WSL·uv·.env·OpenRouter · VSCode 작업공간 · sample_inbox 10건 · RecordV1 미리보기</p></div>
<div class="store">20분</div></a>

<a class="row" href="/deepagents-handson/chapters/chapter-1" style="text-decoration:none;color:inherit">
<div class="code">1</div>
<div class="copy"><strong>에이전트 패러다임 — 영수증을 읽고 판단</strong><p>LLM 4한계 · ReAct · 모델 자리표 · classify_one.py(영수증→RecordV1, 단발 vs ReAct)</p></div>
<div class="store">45분</div></a>

<a class="row" href="/deepagents-handson/chapters/chapter-2" style="text-decoration:none;color:inherit">
<div class="code">2</div>
<div class="copy"><strong>LangGraph 하네스 — 분류·정규화 파이프라인</strong><p>StateGraph · checkpointer 재개 · 고액·저신뢰 interrupt() HITL · intake_graph.py</p></div>
<div class="store">70분</div></a>

<a class="row" href="/deepagents-handson/chapters/chapter-3" style="text-decoration:none;color:inherit">
<div class="code">3</div>
<div class="copy"><strong>DeepAgents 하네스 — fan-out 동시 조사</strong><p>create_deep_agent · write_todos · 파일 퇴피 · 영수증 없는 89,000원 발견 · research_orchestrator.py</p></div>
<div class="store">65분</div></a>

<a class="row" href="/deepagents-handson/chapters/chapter-4" style="text-decoration:none;color:inherit">
<div class="code">4</div>
<div class="copy"><strong>Skills · MCP · 지식 레이어</strong><p>SKILL.md 점진 공개 · plugin 얇게 · MCP 파일[실선]·메일[목] · OKF 지식 적재</p></div>
<div class="store">80분</div></a>

<a class="row" href="/deepagents-handson/chapters/chapter-5" style="text-decoration:none;color:inherit">
<div class="code">5</div>
<div class="copy"><strong>A2A 역할 분리 — 밖에 검증을 맡긴다</strong><p>서명 Agent Card · SendMessage · Task 라이프사이클 · verified_brief.md · a2a-sdk 1.1.0</p></div>
<div class="store">70분</div></a>

<a class="row" href="/deepagents-handson/chapters/chapter-6" style="text-decoration:none;color:inherit">
<div class="code">6</div>
<div class="copy"><strong>통합 캡스톤 + Wrap-up</strong><p>봉투→분류→조사→지식→브리프→검증 엔드투엔드 배선 · 8역량 회고 · analyst_app.py</p></div>
<div class="store">90분</div></a>
</div>

<p class="section-note" style="margin-top:20px">디자인 시스템은 <a href="/deepagents-handson/concept">🎨 디자인 컨셉</a>에서 따로 볼 수 있습니다.</p>
</section>

</div>
</div>
