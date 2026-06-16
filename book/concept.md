---
layout: page
title: 디자인 컨셉
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec">
<div class="deck">

<section class="slide hero">
<div>
<div class="eyebrow">SDS Agent Course · 2026 Edition</div>
<h1>AI Agent를<br>업무에 들이는 법</h1>
<p class="lead">메일·캘린더·문서를 스스로 처리하는 <strong>퍼스널 워크플로 어시스턴트</strong>를
8시간 만에 직접 만든다. LLM의 한계에서 출발해 Agent → Harness → 협업까지, 한 시나리오로 쌓아 올린다.</p>
<div class="kicker">
<div class="metric"><span class="num">8</span><strong>시간 핸즈온</strong><span>이론 최소화, 실습 중심</span></div>
<div class="metric"><span class="num">6</span><strong>챕터 + Ch0 환경</strong><span>setup.sh 한 방 온보딩</span></div>
<div class="metric"><span class="num">1</span><strong>통합 캡스톤</strong><span>내 하루를 관리하는 Agent</span></div>
</div>
</div>
<div class="board">
<div class="board-header"><span>Framework → Runtime → Harness</span><span class="status-pill">3계층 멘탈모델</span></div>
<div class="stack">
<div class="row"><div class="code">F</div><div class="copy"><strong>Framework · LangChain</strong><p>LLM과 Tool을 연결하는 기본 인프라. <code>@tool</code>·<code>bind_tools</code>로 모델이 도구를 인식·호출.</p></div><div class="store">create_agent</div></div>
<div class="row"><div class="code">R</div><div class="copy"><strong>Runtime · LangGraph</strong><p>상태·분기·재시도·중단(HITL)을 관리하는 실행 엔진. <code>StateGraph</code> + checkpointer.</p></div><div class="store">interrupt()</div></div>
<div class="row"><div class="code">H</div><div class="copy"><strong>Harness · DeepAgents</strong><p>파일시스템·플래닝·서브에이전트를 감싸는 운영 인프라. <code>create_deep_agent()</code> 한 줄.</p></div><div class="store">0.6.10</div></div>
</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div><div class="eyebrow">Chapter 1 · 모델 지형도</div><h2>이제 모델 단독 성능보다<br>Harness 설계가 순위를 가른다</h2></div>
<p class="section-note">SWE-bench Verified 상위권이 88~95%대에 밀집(2026-06). 고정 수치 암기 대신 <strong>티어로 이해</strong>하고, 비용·역량을 엔지니어링한다.</p>
</div>
<div class="grid-4">
<div class="metric"><span class="num">~95</span><strong>Fable 5</strong><span>프런티어 천장 · $10/$50</span></div>
<div class="metric"><span class="num">88.6</span><strong>Opus 4.8</strong><span>워크호스 · $5/$25</span></div>
<div class="metric"><span class="num">~88.7</span><strong>GPT-5.5</strong><span>OpenAI 비교축 · Codex</span></div>
<div class="metric"><span class="num">~81</span><strong>Gemini 3.5 Flash</strong><span>기본 실습 모델 · $1.5/$9</span></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div><div class="eyebrow">Chapter 2 · 핵심 패턴</div><h2>Agent는 ReAct 루프로<br>LLM의 한계를 넘는다</h2></div>
<p class="section-note">생각 → 행동 → 관찰을 반복하다 더 호출할 Tool이 없으면 최종 답변으로 빠져나온다. 이 수동 루프를 다음 Step에서 <strong>LangGraph로 구조화</strong>한다.</p>
</div>
<div class="flow">
<div class="flow-step"><small>Thought</small><strong>🤔 무엇을 할지 판단</strong><p>"메일을 확인하려면 check_inbox를 불러야겠다"</p></div>
<div class="flow-step"><small>Action</small><strong>🔧 Tool 호출</strong><p>tool_calls가 비어있지 않은 경우 도구를 실행</p></div>
<div class="flow-step"><small>Observation</small><strong>👀 결과 관찰</strong><p>ToolMessage로 결과를 대화 기록에 추가</p></div>
<div class="flow-step"><small>Loop / End</small><strong>🔁 반복 또는 종료</strong><p>또 있으면 반복, 없으면 content를 최종 답변으로</p></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div><div class="eyebrow">Capstone · 한 장의 그림</div><h2>퍼스널 어시스턴트는<br>하나의 허브로 수렴한다</h2></div>
<p class="section-note"><strong>ConceptGraph</strong> 컴포넌트 — 노드/엣지 데이터만 주면 우리 디자인 톤으로 그려지는 교재 삽화. mermaid보다 "표지급" 개념도에 쓴다.</p>
</div>

<ConceptGraph
  title="내 하루를 관리하는 Agent — 능력 축"
  :nodes="[
    { id:'agent', type:'hub', label:'Agent', sub:'DeepAgents Harness', x:500, y:300 },
    { id:'skills', type:'skill', label:'Skills', sub:'SKILL.md · 절차(How)', x:210, y:130 },
    { id:'mcp', type:'tool', label:'MCP Tools', sub:'mail·calendar·docs', x:790, y:130 },
    { id:'okf', type:'knowledge', label:'OKF 지식', sub:'llm-wiki · What-knows', x:880, y:330 },
    { id:'mem', type:'memory', label:'Memory', sub:'Mem0 / LangMem', x:700, y:495 },
    { id:'user', type:'user', label:'User', sub:'HITL 승인', x:300, y:495 },
    { id:'llm', type:'llm', label:'LLM', sub:'Gemini 3.5 Flash', x:120, y:330 },
  ]"
  :edges="[
    { from:'skills', to:'agent', label:'절차 주입' },
    { from:'mcp', to:'agent', label:'도구 호출' },
    { from:'okf', to:'agent', label:'지식 참조' },
    { from:'mem', to:'agent', label:'선호 기억' },
    { from:'user', to:'agent', label:'HITL 승인' },
    { from:'llm', to:'agent', label:'추론' },
  ]"
/>
</section>

<section class="slide">
<div class="eyebrow">Wrap-up</div>
<h2>스킬은 갈아끼우고, 도구는 재사용한다</h2>
<p class="lead">mail·calendar·docs를 MCP로, 도메인 지식을 OKF로, 절차를 SKILL.md로, 선호를 메모리로,
위험 액션을 HITL로, 품질을 평가로 — <strong>연속 진화형 어시스턴트</strong>가 이 과정의 목적지다.</p>
<p style="margin-top:20px"><span class="badge">Personal Workflow Assistant</span> <span class="badge blue">8h Hands-on</span> <span class="badge amber">2026 Edition</span> <span class="badge red">WSL · uv · OpenRouter</span></p>
</section>

</div>
</div>
