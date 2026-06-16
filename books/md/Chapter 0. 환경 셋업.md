---
layout: page
title: Ch0 · 환경 셋업
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec">
<div class="deck">

<section class="slide hero">
<div>
<div class="eyebrow">Chapter 0 · 환경 셋업</div>

# 인박스 한 통,<br>열어볼 준비

<p class="lead">앞으로 8시간 동안 만들 인박스 리서치 애널리스트는 메일과 스캔 폴더로 들어온 영수증·명세서·계약서를 스스로 읽고 정리합니다.<br>
Ch0에서는 그 바탕을 깝니다. 도구를 설치하고, 모델을 한 번 불러 보고, 분석에 쓸 문서를 받아 둡니다.</p>

<div class="kicker">
<div class="metric"><span class="num">20</span><strong>분</strong><span>설치 · 작업공간 · 첫 호출</span></div>
<div class="metric"><span class="num">10</span><strong>건의 문서</strong><span>영수증·명세서·계약·리포트</span></div>
<div class="metric"><span class="num">1</span><strong>데이터 계약</strong><span>전 챕터가 공유하는 RecordV1</span></div>
</div>
</div>

<div class="board">
<div class="board-header"><span>이 챕터가 끝나면</span><span class="status-pill">체크리스트</span></div>
<div class="stack">
<div class="row"><div class="code">1</div><div class="copy"><strong>.venv + .env</strong><p>uv로 의존성 설치, API 키 한 곳에</p></div><div class="store">동작</div></div>
<div class="row"><div class="code">2</div><div class="copy"><strong>첫 LLM 호출</strong><p>Gemini 3.5 Flash 라우팅 확인</p></div><div class="store">응답</div></div>
<div class="row"><div class="code">3</div><div class="copy"><strong>sample_inbox/</strong><p>분석할 문서 10건 확보</p></div><div class="store">10건</div></div>
</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">Step 1 · 한 줄 설치</div>

## 도구는 한 번에 깐다

</div>
<p class="section-note">런타임은 WSL2 · Python 3.12 · uv · Node로 맞춥니다. 하나씩 직접 설치하지 않아도 됩니다.<br>
setup.sh가 가상환경 생성과 의존성 설치, .env 템플릿까지 한 번에 처리합니다. 실행한 다음 키만 채우면 준비가 끝납니다.</p>
</div>

```bash
bash scripts/setup.sh        # .venv 생성 · uv sync · .env 템플릿
```

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>uv sync</strong><span>의존성 설치</span></div><div class="panel-body"><div class="list">
<p>deepagents · langchain · langgraph</p>
<p>mcp · a2a-sdk · pydantic</p>
<p>레포-로컬 <code>.venv</code> (전역 오염 없음)</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>.env</strong><span>API 키 한 곳에</span></div><div class="panel-body"><div class="list">
<p><code>OPENROUTER_API_KEY</code> 하나로 시작합니다</p>
<p>레포-로컬 파일이라 <code>~/.bashrc</code>는 건드리지 않습니다</p>
<p>git에는 올라가지 않습니다(<code>.gitignore</code>)</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>검증</strong><span>준비됐을까</span></div><div class="panel-body"><div class="list">
<p>Python 3.12 · uv 버전 확인</p>
<p><code>uv run python -c "import deepagents"</code></p>
<p>키가 잘 읽히는지 확인</p>
</div></div></div>
</div>

<p class="section-note" style="margin-top:18px">설치가 끝나면 마지막에 프리플라이트 점검표가 뜹니다. API 키 한 줄 빼고 모두 ✅면 준비가 된 겁니다.<br>
키는 다음 단계에서 채웁니다.</p>

```text
▶ Preflight 점검
  ✅ Python 3.12+        ✅ langchain import
  ✅ uv 설치됨           ✅ langgraph import
  ❌ OPENROUTER_API_KEY  ✅ deepagents import
  ── 결과: ✅ 6 / ❌ 1 ──
```
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">Step 2 · 작업 공간</div>

## 에디터를 WSL에 붙인다

</div>
<p class="section-note">남은 8시간 동안 코드는 전부 WSL 안에서 돕니다. VSCode를 WSL에 연결해 두면 리눅스 쪽 파일과 방금 만든 <code>.venv</code>를 그대로 열어 실행할 수 있습니다.<br>
윈도우와 리눅스 경로가 엉키는 문제도 이때 사라집니다. 한 번만 맞춰 두면 됩니다.</p>
</div>

```bash
# WSL 터미널에서 레포 폴더로 간 다음
code .          # VSCode가 'WSL: Ubuntu' 모드로 열린다
```

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>① 연결</strong><span>WSL 원격 모드</span></div><div class="panel-body"><div class="list">
<p>왼쪽 아래 모서리에 <code>WSL: Ubuntu</code>가 보이면 연결된 상태입니다</p>
<p>안 보이면 확장 <code>WSL</code>(ms-vscode-remote)을 설치합니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>② 확장</strong><span>두 개면 충분</span></div><div class="panel-body"><div class="list">
<p><code>Python</code> — 실행·디버그·인텔리센스</p>
<p><code>Jupyter</code> — 노트북 셀 실행</p>
<p>확장은 WSL 쪽에 설치합니다(창 안내를 따르면 됩니다)</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>③ 인터프리터</strong><span>.venv 지정</span></div><div class="panel-body"><div class="list">
<p><code>Ctrl+Shift+P</code> → <code>Python: Select Interpreter</code></p>
<p>레포 안 <code>.venv/bin/python</code>을 고릅니다</p>
<p>이걸 골라야 설치한 라이브러리가 잡힙니다</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>실행은 두 갈래</span><span class="status-pill">.py 와 .ipynb</span></div>
<div class="stack">
<div class="row"><div class="code">py</div><div class="copy"><strong>스크립트 — 터미널에서</strong><p>완성된 부품은 .py로 둡니다. <code>uv run python3 ch1-llm-basics/classify_one.py</code>처럼 실행하면 <code>.venv</code>를 거쳐 도므로 키와 의존성이 그대로 잡힙니다.</p></div><div class="store">부품</div></div>
<div class="row"><div class="code">nb</div><div class="copy"><strong>노트북 — 셀 단위로</strong><p>실험과 비교는 <code>.ipynb</code>에서 합니다. 노트북을 열고 오른쪽 위 커널을 <code>.venv</code>로 맞춘 뒤 셀을 하나씩 돌려 결과를 눈으로 확인합니다.</p></div><div class="store">실험</div></div>
</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">Step 3 · 첫 호출</div>

## 모델이 살아있나

</div>
<p class="section-note">기본 실습 모델은 비용이 낮은 Gemini 3.5 Flash입니다. OpenRouter 게이트웨이로 한 번 불러 보면 키와 경로, 모델 라우팅이 제대로 잡혔는지 30초 안에 확인됩니다.<br>
더 비싼 모델은 비교가 필요할 때만 꺼내 씁니다.</p>
</div>

```python
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    model="google/gemini-3.5-flash",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
print(llm.invoke("한 문장으로 자기소개 해줘").content)
```

<div class="board">
<div class="board-header"><span>응답이 오면 라우팅 정상</span><span class="status-pill">기대 출력</span></div>
<div class="panel-body"><div class="list">
<p>응답 텍스트가 한 줄 출력되면 키 로드와 OpenRouter 연결, 모델 슬러그가 모두 맞다는 뜻입니다.</p>
<p><span class="badge red">오류</span> 401이면 키를, 404면 모델 슬러그를, 빈 응답이면 네트워크를 살펴봅니다.</p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">Step 4 · 데이터 표면</div>

## 분석할 문서 더미를 받는다

</div>
<p class="section-note">실습 내내 같은 입력을 씁니다. 5월 한 사람의 인박스 열 건입니다.<br>
이미지와 PDF가 섞여 있습니다. 이것이 우리가 다룰 멀티모달 입력입니다. 그래서 웹 검색을 따로 붙이지 않아도 됩니다.</p>
</div>

<div class="grid-4">
<div class="panel"><div class="panel-head"><strong>영수증 ×5</strong><span>이미지(png)</span></div><div class="panel-body"><div class="list">
<p>카페·편의점·택시·식당·드럭스토어</p>
<p><span class="badge">멀티모달</span> 한 장에서 판매처·금액·항목을 읽어 냅니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>명세서 ×3</strong><span>카드·은행·세금계산서</span></div><div class="panel-body"><div class="list">
<p>카드와 은행 명세서는 PDF, 세금계산서는 사진입니다</p>
<p>거래가 여러 줄이라 항목도 여러 개입니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>계약서 ×1</strong><span>PDF</span></div><div class="panel-body"><div class="list">
<p>용역 계약. 발행처·계약금·날짜가 적혀 있습니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>리포트 ×1</strong><span>PDF</span></div><div class="panel-body"><div class="list">
<p>시장 리포트. 금액이 없는 문서도 다룹니다</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>문서가 서로 연결된다</span><span class="status-pill">교차 참조</span></div>
<div class="panel-body"><div class="list">
<p>카드 명세서의 거래줄은 개별 영수증과 금액이 일치합니다. 은행 명세서는 계약서, 세금계산서와 이어집니다.</p>
<p>그래서 Ch3에서 여러 에이전트가 문서를 나눠 조사할 때 명세서에는 있지만 영수증이 없는 89,000원처럼 실제로 따져 볼 거리가 드러납니다.</p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">Step 5 · 데이터 계약</div>

## 한 곳에서 정의한다 — RecordV1

</div>
<p class="section-note">문서가 영수증이든 계약서든 읽고 나면 모두 이 RecordV1 구조로 정규화됩니다. 그다음부터 모든 챕터는 파일 포맷이 아니라 이 계약 하나에만 기댑니다.<br>
코드가 정본입니다. 교재는 그 파일을 그대로 가져와 보여 줍니다. 복사해 붙인 것이 아닙니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>analyst/schema.py</strong><span>repo 루트의 공유 패키지 · 단일 소스</span></div>
<div class="panel-body">

<<< ../../analyst/schema.py{python}

</div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>파이프라인 경로</span><span class="status-pill">디렉터리 규약</span></div>
<div class="panel-body"><div class="list">
<p><code>sample_inbox/</code> → <code>classified/</code> → <code>research_notes/</code> → <code>brief.md</code> → <code>verified_brief.md</code></p>
<p>입력만 저장소에 들어 있습니다. 만들어 내는 산출물은 모두 <code>workspace/</code> 아래에 쌓입니다. 각 챕터가 이 경로를 한 단계씩 채웁니다.</p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">마무리</div>

## 다음 — 영수증을 읽게 만든다

</div>
<p class="section-note">환경과 문서, 계약이 모두 준비됐습니다. Ch1에서는 영수증 이미지 한 장을 모델에게 보여 주고 방금 본 RecordV1 구조로 뽑아냅니다.<br>
애널리스트의 첫 번째 부품입니다.</p>
</div>

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>지금 손에 든 것</strong></div><div class="panel-body"><div class="list">
<p>동작하는 <code>.venv</code> · <code>.env</code></p>
<p>문서 10건 + RecordV1 계약</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>Ch1에서 할 것</strong></div><div class="panel-body"><div class="list">
<p>영수증 1장 → RecordV1 추출</p>
<p>모델 티어 3종 비용·정확도 비교</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>최종 목적지</strong></div><div class="panel-body"><div class="list">
<p>인박스 한 통 → 검증된 브리프</p>
<p>Ch6 통합 캡스톤</p>
</div></div></div>
</div>
</section>

</div>
</div>
