---
layout: page
title: MCP로 도구 서버를 연결한다
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec workshop-edition"><div class="deck">
<section class="slide">
<div class="eyebrow">2026.09 · 예상 15:30–16:35 · 65분</div>

# MCP로 도구 서버를 연결한다

<p class="lead">정책 조회를 별도 서버에서 호출합니다. 연결의 상태와 업무 데이터가 저장되는 위치를 구분합니다.</p>

Harness에서 이 프로그램을 개선하는 방법을 살펴봤습니다. 이제 실행 대상인 문의 Agent로 돌아옵니다. 정책을 조회하는 프로그램이 여러 개가 되어 조회 기능을 별도 서버로 제공한다고 가정합니다. 학생이 만든 조회 함수의 입력과 업무 결과는 유지하고, 그것을 호출하는 경계가 바뀝니다. 한 프로그램 안에서만 사용할 때도 반드시 서버로 분리해야 한다는 뜻은 아닙니다.

<div class="cue"><div class="cue-body">모든 명령은 <code>workshop</code> 폴더에서 실행합니다. 처음이라면 <a href="./start">시작 안내</a>를 먼저 확인합니다. 앞 단계가 미완료라면 <a href="./build#recovery">복귀 절차</a>로 필요한 함수만 보완한 뒤 이어갑니다.</div></div>
<details class="instructor-note"><summary>강사용 예상 시간 · 15:30–16:35 / 65분</summary>

**예상 배분:** 각 소제목 아래의 소요 시간과 예상 시각을 참고합니다. 시작 질문도 세션 시간에 포함됩니다. 현장 실측이 아닌 진행 기준이며 학습자의 반응에 따라 조절합니다.

도구 공개와 실제 HTTP 연결을 우선합니다. 운영 사례의 세부 설명은 복습으로 돌릴 수 있습니다.

</details>

</section>

<section class="slide" id="icebreaker">

## 시작 질문 · 검색 도구가 100개라면 무엇을 먼저 보여줄까요?

<p class="section-time">예상 3분 · 15:30–15:33</p>

Agent에 사내 검색 도구 100개를 연결했습니다. 사용자는 오늘 식당 메뉴만 물었는데, 계약서·정산·인사 검색 도구 설명까지 모두 전달됩니다.

**도구 설명을 전부 읽게 할까요, 필요한 도구부터 찾게 할까요?**

MCP의 새 로드맵은 필요한 도구를 점차 발견하는 방향을 다룹니다. 같은 글에서 무상태 통신을 포함한 이미 출시된 변화도 별도로 설명합니다. [2026-08-22 · 공식 로드맵](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/) · [GeekNews 소개](https://news.hada.io/topic?id=32777)

먼저 도구의 존재와 입력 형식을 알아내는 단계, 실제로 도구를 실행하는 단계를 나누어 봅니다.

<details class="instructor-note"><summary>강사용 진행 노트 · 시작 질문</summary>

진행 예: 상황 30초 → 의견 한두 개 1분 → 최근 사례와 본문 연결 1분 30초. 별도 기록이나 제출은 요구하지 않습니다.

도구 개수가 많다는 사실만으로 정확도가 반드시 떨어진다고 단정하지 않습니다. 설명 길이와 선택 부담을 생각하게 합니다. Progressive Discovery는 로드맵의 방향이고, 현재 교재의 목록 조회·호출 실습이 그 기능 전체를 구현한 것은 아닙니다.

</details>

</section>

<nav class="lesson-nav" aria-label="학습 단계"><a href="#concept">01 개념</a><a href="#observe">02 함께 실행</a><a href="#practice">03 개인 과제</a><a href="#solution">04 풀이</a></nav>

<section class="slide" id="concept">

<aside class="teacher-aside"><strong>강사의 한마디</strong><p>연결에 성공해도 조회 결과가 맞다는 보장은 없습니다. 서버에 도달했는지와 업무 결과가 맞는지를 나눠 보겠습니다.</p></aside>


## 함수 호출에서 서버 연결로

<p class="section-time">예상 5분 · 15:33–15:38</p>

<CourseVisual kind="mcp" />


지금까지 조회 함수는 같은 프로그램 안에 있었습니다. 여러 애플리케이션이 같은 도구를 사용할 때 서버가 도구의 목록·입력 형식·결과를 일관되게 제공하면 연결 코드를 줄일 수 있습니다.

MCP host는 Agent를 사용하는 애플리케이션, client는 서버와 통신하는 구성, server는 도구·데이터를 제공하는 구성입니다. 모델 자체가 HTTP 요청을 직접 보내는 것은 아닙니다.


### 함수 호출로 둘까요, 서버로 공개할까요?

|선택|장점|감수할 점|적합한 상황|
|---|---|---|---|
|같은 프로그램의 함수|네트워크 없이 연결이 단순|여러 앱에서 쓰려면 코드 배포·공유 방법을 정해야 함|한 앱 내부의 작은 기능|
|일반 HTTP API|독립 서비스로 제공하고 기존 API 인프라 활용|호출 형식과 도구 설명 연결을 클라이언트별로 구성|이미 운영하는 API와 연동|
|MCP 서버|도구 발견·입력 형식·호출 규약을 MCP 클라이언트와 공유|서버 운영, 접근 권한, 네트워크 오류와 호환성 관리|여러 Agent 앱에서 같은 도구를 사용|

MCP는 필요하다면 기존 API를 감싸 제공할 수도 있습니다. 도구 하나를 같은 앱에서만 쓴다면 서버 분리가 불필요할 수 있습니다. [MCP 아키텍처](https://modelcontextprotocol.io/docs/learn/architecture)

아래의 ‘목록’과 ‘실행’은 대안이 아니라 서로 다른 단계입니다. 각각의 장단점을 비교하는 대상은 아닙니다.

</section>

<section class="slide">

## 도구 발견·호출·결과

<p class="section-time">예상 5분 · 15:38–15:43</p>

<figure class="trace-example">
<a href="https://mintcdn.com/mcp/gk28X8wi_tbRYzej/images/inspector/web-monitor-sidebar.png" target="_blank" rel="noopener noreferrer"><img src="https://mintcdn.com/mcp/gk28X8wi_tbRYzej/images/inspector/web-monitor-sidebar.png" alt="MCP 공식 Inspector. 왼쪽 도구 목록에서 get_weather가 선택되고 중앙에 날씨 결과, 오른쪽에 통신 기록이 표시됩니다." loading="lazy" referrerpolicy="no-referrer"></a>
<figcaption>공식 제품 화면 · <a href="https://modelcontextprotocol.io/docs/tools/inspector">MCP Inspector 문서</a> · 확인 2026-09-08 · 클릭하면 원본 확대</figcaption>
</figure>

**화면 읽기:** 왼쪽은 사용 가능한 도구, 가운데는 선택한 `get_weather`의 결과, 오른쪽은 통신 기록입니다. 도구를 찾는 단계와 실제 결과를 받는 단계를 나누어 볼 수 있습니다. 이 화면은 공식 예시이며 우리 정책 조회 결과가 아닙니다. 수업에서는 Inspector 설치 없이 아래 코드로 목록과 반환값을 확인합니다.


<<< ../../workshop/course/mcp_lab.py#server{python}

`server.tool()`은 함수를 도구로 등록합니다. 도구 목록의 입력 schema(입력 형식)는 어떤 인자를 받을지 설명합니다. 도구 목록에 이름이 보인다는 것과 실제 호출 성공은 다릅니다.

<<< ../../workshop/course/mcp_lab.py#client{python}

실제 호출 후 `is_error`와 결과를 확인합니다. Python SDK 필드명과 JSON wire 필드명은 다를 수 있습니다. 이 교재는 mcp 2.1.1을 lockfile로 고정합니다.

<aside class="discussion-prompt"><strong>생각거리 · 여유가 있으면 +3분</strong><p>도구 목록에 “메일 보내기”가 보입니다. 하지만 눌러 보면 권한이 없다는 오류가 납니다.<br><br><strong>도구 목록에 보이는 것과 실제 사용할 수 있는 것은 왜 다를까요?</strong> 발송 전에 무엇을 확인하면 좋을까요?</p></aside>

<details class="instructor-note"><summary>강사용 토론 길잡이</summary>

도구 발견과 실행 권한은 별개입니다. 실제 요청에 적용되는 권한을 서버에서 확인해야 합니다. 목록을 숨기는 것만으로 접근 통제가 끝나는 것은 아닙니다.

한 답을 빨리 받기보다, 반대 선택이 더 나아지는 조건을 하나 더 묻습니다. 별도 기록이나 제출은 요구하지 않습니다. 기본 배정에 추가하는 선택 활동이므로 다음 섹션의 시간을 조절합니다.

</details>

</section>

<section class="slide">

## 첫 호출을 관찰하고 상태를 구분합니다

<p class="section-time">예상 7분 · 15:43–15:50</p>

코드에서 낯선 문법은 다음처럼 읽습니다. 이 모듈에서 비동기 프로그램을 처음부터 작성할 필요는 없습니다.

|표현|이 예제에서 하는 일|
|---|---|
|`@mcp.tool()`|아래 함수를 호출 가능한 도구로 등록합니다.|
|`async def`|네트워크 응답을 기다릴 수 있는 함수를 정의합니다.|
|`await client.call_tool(...)`|도구를 호출하고 결과가 올 때까지 기다립니다.|
|`async with Client(...)`|client 사용 범위를 정하고, 끝나면 연결 자원을 정리합니다.|
|`asyncio.run(...)`|일반 Python 실행에서 비동기 함수를 시작합니다.|

먼저 `uv run python -m course.cli mcp --topic 정산`을 실행합니다. `tools`에서 lookup_policy를 찾고 `result.content`에서 P-01을 읽습니다. 도구 발견→입력 전달→결과 확인의 순서를 손으로 짚습니다.

이 과정의 프로토콜은 2026-07-28입니다. 새 요청은 연결 세션에 의존하지 않고 버전·기능 정보를 요청 단위로 전달합니다. `Client(..., mode="2026-07-28")`로 요청 버전을 명시합니다.

| 위치 | 무엇을 보관하는가 | 연결을 끊으면? |
|---|---|---|
|프로토콜 요청|호출 인자와 요청별 metadata|다음 요청은 필요한 정보를 다시 전달|
|업무 저장소|티켓·정책 등 업무 데이터|저장소에 남음|

Stateless는 업무 데이터를 삭제한다는 뜻이 아닙니다. client를 바꾸거나 서버를 다시 시작해도 저장소가 같으면 업무 기록을 다시 조회할 수 있습니다. 구 SDK의 HTTP 설정과 새 프로토콜을 같은 것으로 외우지 않습니다. 다음은 모두 함께 관찰하는 재시작 시연입니다. 구현은 뒤의 확장 과제에서 다룹니다.

```bash
uv run python -c "import json; from exercises.extension_solutions import ticket_restart; print(json.dumps(ticket_restart(), ensure_ascii=False, indent=2))"
```

명령은 첫 서버에서 티켓을 저장한 뒤 서버를 종료하고, 새 서버에 같은 SQLite 파일을 연결합니다. `first.data.created`는 true, `again.data.created`는 false이며 두 ticket_id가 같은지 비교합니다. `conflict.error`는 true입니다. 내용 충돌을 만드는 마지막 호출에서는 서버 로그에 `UnexpectedToolError`가 표시될 수 있습니다. 최종 결과의 `conflict.error=true`와 함께 나타나면 의도한 충돌이며, 연결 실패와 구분합니다. 이는 제공된 예제의 시연이며 학생 과제 통과 결과가 아닙니다. 연결 상태가 사라져도 업무 기록은 저장소에 남는다는 점을 설명합니다.

</section>

<section class="slide" id="observe">

## 함께 실습

<p class="section-time">예상 15분 · 15:50–16:05</p>

[실습: MCP 도구 공개](./build#protocols)를 엽니다. `build_lab/student.py`의 `build_mcp_server`를 작성합니다. 해당 단계의 입력·반환값과 검사 방법을 따라 진행한 뒤 이 장으로 돌아옵니다. 아래 완성 예제는 비교가 필요할 때 펼칩니다.

<details><summary>비교하며 읽는 완성 예제와 시연</summary>

<div class="command-purpose">완성 예제 실행</div>

```bash
uv run python -m course.cli mcp --topic 정산
uv run python -m course.cli mcp --topic 계정
```

명령은 로컬 서버 프로세스를 시작하고 client로 실제 HTTP 호출한 뒤 자신이 시작한 서버를 종료합니다. 출력에서 protocol, tools, result.content를 읽습니다. `result.content`는 블록 목록이며 첫 블록의 `text` 안에 정책 JSON 문자열이 들어 있습니다. 그 안의 `found`와 `policy`는 LangChain 모듈에서 읽은 업무 데이터와 같습니다.

이제 LangChain에서 같은 원격 조회 도구를 사용합니다. 목록과 결과를 확인한 뒤 아래 연결을 실행합니다.

```bash
uv run python -m course.mcp_agent_lab
```

<<< ../../workshop/course/mcp_agent_lab.py#adapter{python}

LangChain 1.4의 `langchain.mcp.MCPAdapter`가 MCP 도구를 LangChain 도구로 바꿉니다. 서버에 등록된 도구 중 조회 도구만 Agent에 전달했습니다.

모델은 도구 사용을 요청하고, adapter가 원격 호출을 수행합니다. `runs/mcp-agent.json`에서 요청→tool 결과→최종 답변을 확인합니다. 앞의 직접 호출은 모델을 거치지 않았고, 이번에는 실제 모델이 도구 요청을 만드는 차이가 있습니다.

이 API는 현재 beta 경고를 표시합니다. 수업은 검증한 버전을 고정하며, 기본 MCP 직접 호출 예제도 함께 제공합니다.

[2026-09-03 공식 변경 안내](https://www.langchain.com/blog/mcp-in-langchain-stateless-protocol-elicitation-and-more)

선택 관찰: 서버를 직접 열려면 `uv run python -m course.mcp_lab --port 9710 --db runs/tickets.sqlite`를 실행합니다. 종료는 Ctrl+C입니다. 포트가 사용 중이면 다른 프로그램을 종료하지 말고 기본 CLI의 자동 포트 선택을 사용합니다.


</details>

</section>

<section class="slide" id="practice">

## 개인 과제

<p class="section-time">예상 15분 · 16:05–16:20</p>

앞에서 시작한 [MCP 도구 공개 실습](./build#protocols)을 이어서 완성합니다. 새 과제를 시작하는 것이 아니라, 같은 함수에 다른 입력을 넣어 결과를 비교하는 단계입니다.

아래 준비 문제는 주 실습에서 막힌 개념을 작은 함수로 확인할 때 사용합니다.

<details><summary>개념을 확인하는 준비 문제와 추가 반례</summary>

**기본:** `team_for_topic`이 입력과 관계없이 첫 번째 팀만 반환합니다. 주제로 정책을 찾아 `found`와 `team`을 반환하도록 고칩니다.

없는 주제는 Python에서 `{"found": False, "team": None}`을 반환합니다. JSON 출력에서는 `false`, `null`로 표시됩니다.

<<< ../../workshop/exercises/student.py#mcp{python}

<div class="command-purpose">준비 문제 검사</div>

```bash
uv run python -m exercises.check mcp
```

이 검사는 학생 함수를 실제 MCP 도구로 등록해 호출합니다. 과제 검사는 같은 프로세스의 SDK 경로이고, 앞의 CLI는 별도 HTTP 서버 경로라는 차이가 있습니다.

### 연결 성공과 조회 성공을 따로 판정합니다

정산만 조회하면 초기 구현이 맞는 것처럼 보일 수 있습니다. 계정과 없는업무의 결과도 먼저 예상합니다.

| 입력 | found 예상 | team 예상 | 서버 오류여야 하는가 |
|---|---|---|---|
|정산|작성|작성|작성|
|계정|작성|작성|작성|
|없는업무|작성|작성|작성|

수정한 학생 함수의 검사 후, 제공 HTTP 예제에서도 없는 정책을 조회합니다.

<div class="command-purpose">완성 예제 실행</div>

```bash
uv run python -m course.cli mcp --topic 없는업무
```

응답의 오류 표시와 본문의 `found`를 비교합니다. 정상적인 조회 결과가 “없음”일 수 있습니다. 연결 실패, 잘못된 인자, 조회 결과 없음은 같은 문제가 아닙니다. 이번 입력은 서버를 고장 내는 실험이 아니므로 다른 프로세스를 종료할 필요가 없습니다.

추가 반례로 빈 정책 표를 전달합니다. 서버 통신을 추가하지 않고 학생 함수의 데이터 처리를 직접 확인합니다.

```bash
uv run python -c "from exercises.student import team_for_topic; print(team_for_topic('정산', {}))"
```

**확장:** MCP 도구 `submit_ticket`에 같은 키·같은 내용, 같은 키·다른 내용을 보내 예상 결과를 검증합니다. 서버 내부의 저장 함수는 `create_ticket`입니다. 서버 재시작 후 같은 DB를 사용해 기록이 유지되는지도 확인합니다. 인증과 actor별 권한은 이 로컬 예제에 구현되어 있지 않습니다.

확장 시작 파일은 `exercises/extensions.py`의 `ticket_restart()`입니다. 기본 함수의 인자는 바꾸지 않습니다.

```bash
uv run python -m exercises.extension_check mcp
```

학생 검사 결과를 먼저 확인합니다. 다음 명령은 풀이 시간에 기준 구현을 확인할 때만 실행합니다.

```bash
uv run python -m exercises.extension_check mcp --solution
```

`submit_ticket` 결과를 읽을 때 `structured_content`가 반드시 있다고 가정하지 않습니다. 현재 예제의 성공 응답은 다음처럼 텍스트 블록의 JSON을 읽습니다. 조회 도구의 반환 포장과 구분합니다.

```python
import json

# result는 await client.call_tool(...)의 반환값입니다.
data = None if result.is_error else json.loads(result.content[0].text)
```

이 확장 검사는 반환값의 계약을 확인합니다. 미리 작성한 dict만 반환해도 통과할 수 있으므로 통과 표시만으로 실제 재시작을 증명할 수 없습니다. 두 `server(...)` 실행에 같은 DB 경로를 전달했는지 코드와 실제 출력에서 확인합니다.

반환 dict의 first.data.created는 True, again.data.created는 False이고 ticket_id는 같아야 합니다. conflict.error는 True입니다.

### 응답을 못 받았을 때 다시 보내도 되는가

서버에는 티켓이 저장됐지만 응답을 받기 전에 연결이 끊겼다고 가정합니다. 사용자는 저장 여부를 모릅니다. 단순히 다시 호출하면 티켓이 두 개 생길 수 있습니다.

재시작 실험을 실행하기 전에 다음 두 설계 중 어떤 것이 이 요구를 만족하는지 고릅니다.

|설계|재전송할 때 보내는 키|예상 결과|
|---|---|---|
|HTTP 요청마다 새 키 생성|항상 새 값|작성|
|같은 업무 요청에는 같은 키 사용|최초 생성한 업무 키|작성|

`business_key`는 이 예제의 업무 데이터 계약입니다. MCP의 요청 ID와 같은 역할이라고 가정하지 않습니다. 서버 세션을 유지하지 않아도 SQLite의 고유 키와 저장된 내용을 기준으로 같은 업무인지 판단할 수 있습니다.

실험 후 최초 생성·재시작 후 재사용·내용 충돌의 세 결과를 설명합니다. “Stateless라 상태가 없다”는 설명 대신 **무슨 상태가 어디에 남는지** 말할 수 있어야 합니다.

**더 어려운 변경 요청:** 동일한 내용으로 새 티켓을 의도적으로 생성할 때는 어떻게 구분할까요? 내용의 해시만 키로 쓰는 설계의 한계를 적고, 업무 요청 ID를 누가 언제 만들고 보관할지 제안합니다. 이 로컬 예제의 키는 사용자나 조직별로 구분하지 않습니다. 여러 사용자가 함께 쓰는 서비스로 옮긴다면 키의 범위도 설계해야 합니다.

참고 풀이처럼 임시 폴더의 같은 DB를 두 서버 실행에 넘깁니다. 업무 키와 내용이 같을 때만 기존 결과를 재사용합니다.

시작 코드는 FAIL이 정상입니다. 첫 명령으로 자신의 구현을 검사하고, 풀이 시간에 `exercises/extension_solutions.py`의 같은 함수를 열어 비교합니다. 정상·실패 사례는 `exercises/extension_check.py`에서 확인합니다.

<details><summary>힌트</summary>

첫 정책을 가져오는 대신 `policies.get(topic)`으로 조회합니다. 없는 경우에는 `team`을 읽지 않습니다.

</details>


</details>

<aside class="discussion-prompt"><strong>생각거리 · 여유가 있으면 +3분</strong><p>“티켓 만들기”를 눌렀는데 응답이 없어 다시 눌렀습니다. 나중에 보니 티켓이 두 개 생겼습니다.<br><br><strong>서버가 두 요청을 같은 작업으로 알아보려면 무엇이 필요할까요?</strong> 이번에 배운 business_key를 떠올려 봅니다.</p></aside>

<details class="instructor-note"><summary>강사용 토론 길잡이</summary>

재시도에서는 같은 업무 키를 사용해 기존 결과를 확인할 수 있습니다. 정말 새 티켓을 만들려는 요청에는 새 키가 필요하므로 내용이 같다는 이유만으로 모두 합치지는 않습니다.

한 답을 빨리 받기보다, 반대 선택이 더 나아지는 조건을 하나 더 묻습니다. 별도 기록이나 제출은 요구하지 않습니다. 기본 배정에 추가하는 선택 활동이므로 다음 섹션의 시간을 조절합니다.

</details>

</section>

<section class="slide" id="operations">

## 운영 관점: 어디에서 실패했는가

<p class="section-time">예상 5분 · 16:20–16:25</p>

주 실습을 마친 뒤 자신의 기록을 아래 표와 대조합니다. 풀이 시간에는 한 사례를 골라 첫 확인 위치와 재시도 여부를 설명합니다. 모든 장애를 직접 일으키는 활동은 아닙니다.

|관찰|아직 알 수 없는 것|첫 확인과 다음 행동|
|---|---|---|
|서버 접속 실패|도구 코드가 맞는지|주소·서버 시작 로그부터 확인. 프롬프트를 바꾸어 해결할 문제가 아님|
|JSON-RPC 오류|업무 조회가 실행됐는지|메서드·도구 이름·요청 구조 확인|
|정상 응답 안에 isError=true|호출 실패의 원인과 수정 가능성|도구 오류 내용을 읽고 입력 수정 또는 의존 서비스 복구 여부 판단|
|isError=false, found=false|정책을 새로 만들거나 임의로 답해도 되는지|조회 결과 없음으로 처리하고 추가 확인. 같은 조회의 무한 재시도는 근거를 만들지 못함|
|티켓 저장 요청 후 timeout|서버가 저장했는지|업무 키로 결과 확인. 응답이 없다고 저장 실패로 단정하지 않음|

MCP 명세는 프로토콜 오류와 도구 실행 오류를 구분합니다. `found=false`는 이 교재가 정한 업무 결과입니다. 이 세 가지를 하나의 실패 코드로 합치면 어떤 입력을 고쳐야 하는지 잃습니다. [공식 오류 구분](https://modelcontextprotocol.io/specification/2026-07-28/server/tools#error-handling)

현재 `query()`는 `result.is_error`를 발견하면 RuntimeError로 종료합니다. 이는 실습 실행을 멈추는 최소 처리이며, 오류별 자동 재시도·알림·복구를 구현한 것은 아닙니다. 성공 결과에서는 SDK의 `is_error`와 JSON의 `isError` 표기가 다를 수 있으므로 실제 출력 구조를 읽습니다.

### 재시도 전에 읽기와 쓰기를 구분합니다

정책 조회는 같은 요청을 다시 읽는 작업입니다. 티켓 저장은 결과가 쌓이는 작업입니다. 잠깐의 접속 실패를 같은 방식으로 재시도하더라도 업무 영향은 다릅니다.

수업용 사고 사례: 사용자가 티켓 생성 버튼을 눌렀고 서버가 저장했지만 응답만 사라졌습니다. 클라이언트가 새 business_key로 재전송하면 예제 DB는 새 업무로 취급합니다. 기존 키와 같은 내용으로 보내면 기존 ticket_id를 돌려줍니다. 같은 키에 다른 내용을 보내면 충돌로 멈춥니다. 이 동작은 MCP 세션이 아니라 `create_ticket()`의 저장 계약이 만듭니다.

<<< ../../workshop/course/mcp_lab.py#ticket{python}

`business_key TEXT UNIQUE`는 같은 키의 중복 저장을 막고, `BEGIN IMMEDIATE`는 조회 후 저장하는 쓰기 작업의 경쟁을 제어합니다. 이 예제는 한 SQLite 저장소의 동작입니다. 여러 조직의 키 구분·보존 기간·다른 서비스까지 포함한 정확히 한 번 실행을 해결했다고 보지는 않습니다.

**재시도 질문:** 티켓 생성 응답을 받지 못해 다시 요청합니다. 새 통신 요청에는 새 JSON-RPC ID를 붙였습니다. 같은 티켓을 만들려던 요청이라면 business_key도 바꿔야 할까요? 둘 다 새로 만들면 서버가 같은 작업임을 알아볼 수 있을지 생각해 봅니다.

### 도구 설명은 권한 검사가 아닙니다

“읽기 전용 도구”라는 설명을 모델에 주는 것과 서버가 쓰기 동작을 거부하는 것은 다릅니다. 실제 서비스에서는 호출자의 권한을 서버에서 확인하고, Agent에 필요한 도구만 노출해야 합니다. MCP 명세도 신뢰하지 않는 서버의 도구 annotation을 보장으로 취급하지 않도록 합니다. [도구 metadata의 신뢰 경계](https://modelcontextprotocol.io/specification/2026-07-28/server/tools#tool)

이 교재 서버는 localhost의 학습용 데이터만 사용하며 사용자 인증을 구현하지 않았습니다. “MCP로 연결했다”는 이유로 사내 전체 정책이나 쓰기 기능을 같은 방식으로 공개할 준비가 된 것은 아닙니다. 운영으로 옮길 때는 호출자·도구·대상 데이터의 조합으로 허용 여부를 정하고, 기록에는 비밀키와 정책 본문 전체 대신 추적에 필요한 식별자·결과·소요 시간을 우선 남깁니다.

</section>

<section class="slide" id="solution">

## 풀이

<p class="section-time">예상 10분 · 16:25–16:35</p>

<details class="instructor-note"><summary>강사용 진행 노트 · 오류 비교</summary>

정산과 계정 조회를 비교한 뒤 접속 실패·도구 오류·조회 결과 없음을 구분합니다. 운영 사례 표는 한 사례만 골라 첫 확인 위치를 묻습니다. 모든 장애를 재현할 필요는 없습니다.

</details>

주 실습 풀이는 `build_lab/reference.py`의 해당 함수를 자신의 구현과 비교합니다. [완성 기준](./build#finish)에 따라 코드·실행 경로·반례를 설명합니다. 아래 표와 명령은 준비 문제의 풀이입니다.

<div class="command-purpose">준비 문제 풀이 확인</div>

```bash
uv run python -m exercises.check mcp --solution
```

| 관찰 | 의미 | 다음에 확인할 위치 |
|---|---|---|
|도구 목록에 lookup_policy가 있음|도구 발견 성공|실제 호출 결과|
|조회가 정상 반환, found=false|업무 데이터 없음|사용자에게 추가 확인 요청|
|계정 조회에 재무지원팀 반환|도구 로직 오류|topic으로 정책을 고르는 함수|

원격 연결 코드를 바꾸지 않아도 조회 함수를 고쳐 업무 결과를 바로잡을 수 있습니다. 반대로 도구 로직이 맞아도 접속 오류는 별도로 해결해야 합니다. 자신의 실패가 어느 행에 해당하는지 찾아봅니다.

정산 입력만 시험하면 항상 첫 팀을 반환하는 버그를 놓칩니다. 다른 유효 주제와 없는 주제를 포함해야 합니다. schema에 맞는 dict를 반환해도 업무 결과는 틀릴 수 있습니다.

여기까지는 다른 서버의 **조회 도구를 사용**했습니다. 다음에는 완성한 초안을 **독립 검토 시스템에 맡기는** 상황을 다룹니다. 함수 결과만 받는 것으로 충분한지, 접수·진행·완료와 산출물을 구분해야 하는지에 따라 연결 방식을 판단합니다.

참고: [MCP 2026-07-28 변경](https://modelcontextprotocol.io/specification/2026-07-28/changelog), [Python SDK migration](https://py.sdk.modelcontextprotocol.io/migration/).

</section>

<nav class="chapnav"><a href="../toc">전체 목차</a></nav>
</div></div>
