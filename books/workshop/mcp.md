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

<p class="lead">Python 조회 함수를 MCP 서버로 공개하고, LangChain Agent에서 원격 도구로 사용합니다. 통신 원리는 교재에서 읽고, 실제 호출은 Jupyter에서 실행합니다.</p>

앞 장의 `create_agent`에는 같은 프로그램의 함수를 연결했습니다. 이제 여러 Agent가 동일한 정책 조회를 쓰도록 별도 서버로 제공합니다. **JSON-RPC로 무엇을 요청하는지 → transport로 어떻게 전달하는지 → LangChain에서 어떻게 사용하는지**를 순서대로 배웁니다.

실습은 `notebooks/build-agent.ipynb`의 4번입니다. 조회 데이터와 함수는 앞 장 것을 재사용합니다. 새로 할 일은 도구 등록과 LangChain 연결 두 가지입니다.

</section>
<section class="slide" id="icebreaker">

## 시작 질문 · 같은 조회 도구를 여러 앱에서 쓰려면?

<p class="section-time">예상 3분 · 15:30–15:33</p>

문의 Agent와 코딩 Agent가 같은 사내 규정을 조회해야 합니다. 각 앱에 조회 코드를 복사하면 규정 시스템이 바뀔 때 모두 수정해야 합니다. 서버 하나를 만들면 각 앱은 도구 이름과 입력 형식을 어떻게 알아낼까요?

MCP는 이 발견과 호출 방식을 정합니다. 수업 끝에는 도구가 100개로 늘어났을 때의 문제를 [공식 로드맵](#roadmap)으로 이어갑니다.

</section>
<nav class="lesson-nav" aria-label="수업 흐름"><a href="#concept">01 개념</a><a href="#observe">02 실습</a><a href="#solution">03 풀이</a><a href="#wrap">04 Wrap</a></nav>
<section class="slide" id="concept">

## 개념 1 · 누가 누구에게 요청할까요?

<p class="section-time">예상 5분 · 15:33–15:38</p>

Host는 Agent를 사용하는 앱입니다. 그 안의 MCP client가 MCP server에 요청하고, 서버는 등록된 함수를 실행합니다. 모델은 사용할 도구와 인자를 선택하며 실제 네트워크 통신은 프로그램이 처리합니다.

<CourseVisual kind="mcp" />

| 선택 | 얻는 것 | 추가로 맡을 일 |
|---|---|---|
| 로컬 Python 함수 | 한 앱에서 간단하게 사용 | 여러 앱에 코드 공유·배포 |
| 일반 HTTP API | 기존 서비스 인프라 활용 | Agent가 읽을 도구 설명과 호출 변환 연결 |
| MCP 서버 | 도구 목록·입력 형식·호출 규약 공유 | 서버 운영·접근 제어·통신 오류 처리 |

MCP 서버는 기존 API를 감싸도 됩니다. 한 앱 내부의 작은 함수라면 네트워크로 분리할 필요가 없을 수 있습니다. [공식 아키텍처](https://modelcontextprotocol.io/docs/learn/architecture)

## 개념 2 · JSON-RPC는 요청의 형식, transport는 전달 방법입니다

<p class="section-time">예상 6분 · 15:38–15:44</p>

JSON은 데이터를 표현하는 형식입니다. **JSON-RPC는 JSON으로 메서드 이름과 인자를 보내고 응답을 짝짓는 규칙**입니다. MCP는 그 위에 `tools/list`, `tools/call` 같은 메서드와 결과 형식을 정의합니다.

아래는 메시지 구조를 읽기 위한 축약 예입니다. 2026-07-28의 요청별 버전·기능 metadata는 생략했습니다. 실제 요청은 SDK가 만듭니다.

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "lookup_policy",
    "arguments": {"topic": "계정"}
  }
}
```

`method`는 MCP 작업, `name`은 실행할 업무 도구, `arguments`는 함수에 전달할 값입니다. `id`는 요청과 응답을 짝짓습니다. 모델의 `tool_call_id`와 JSON-RPC 요청 ID는 서로 다른 계층의 식별자입니다.

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [{"type": "text", "text": "계정 담당 팀: IT지원팀, 정책: P-02"}],
    "isError": false
  }
}
```

위 응답의 문장은 형식 설명용입니다. 실습 도구는 text 안에 정책 JSON 문자열을 반환합니다. `tools/list`는 도구의 이름·설명·입력 schema를 반환하고, `tools/call`이 실제 조회를 실행합니다.

| Transport | 메시지가 지나가는 경로 | 선택할 때 고려할 점 |
|---|---|---|
| stdio | client가 실행한 자식 프로세스의 표준 입력·출력 | 로컬 도구에 간단함. 프로세스 관리가 필요하며 stdout에 일반 로그를 섞으면 통신을 깨뜨릴 수 있음 |
| Streamable HTTP | MCP 주소로 HTTP POST, 응답은 JSON 또는 SSE 스트림 | 원격 서버 공유에 적합. 주소·인증·네트워크 운영 필요 |

SSE는 서버가 응답을 스트림으로 전달하는 방식입니다. HTTP를 사용한다고 매번 스트리밍해야 하는 것은 아닙니다. **이번 실습은 localhost의 Streamable HTTP와 JSON 응답**을 사용합니다. 노트북 안에서 서버를 시작하지만 요청은 실제 HTTP를 통과합니다. [전송 규약](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports)

수업은 MCP 2026-07-28과 SDK 2.1.1을 사용합니다. 이 버전은 요청마다 버전·기능 정보를 보내며 이전 방식의 초기화 handshake와 프로토콜 세션에 의존하지 않습니다. 과거 예제의 `initialize`가 없다고 누락으로 판단하지 않습니다. 무상태 요청이어도 서버의 정책 데이터는 그대로 보관할 수 있습니다.

## 개념 3 · 조회 함수를 도구로 등록합니다

<p class="section-time">예상 3분 · 15:44–15:47</p>

등록은 함수를 실행하는 일이 아닙니다. **함수의 이름·설명·입력 형식과 실행할 함수를 서버에 알려 주는 일**입니다. 새 함수라면 다음처럼 데코레이터로 등록합니다. 이 코드는 문법 비교용이며 실습에서는 이미 작성한 조회 함수를 재사용합니다.

```python
@server.tool()
def lookup_policy(topic: str) -> str:
    """업무명으로 담당 팀과 정책을 조회합니다."""
    return search_policy(topic)
```

이미 만들어 둔 함수를 등록할 때는 같은 데코레이터를 함수에 직접 적용합니다.

```python
server = MCPServer("업무 정책 도구")
register_tool = server.tool()
register_tool(lookup_policy)

# 위 두 줄을 붙여 쓴 표현:
# server.tool()(lookup_policy)
```

첫 괄호는 등록용 데코레이터를 만들고, 두 번째 괄호는 등록할 함수를 넘깁니다. `lookup_policy("계정")`처럼 조회를 실행한 결과를 등록하는 것이 아닙니다. 수업에서는 정책 조회 하나만 공개합니다.

## 개념 4 · 원격 도구도 LangChain 도구로 사용합니다

<p class="section-time">예상 3분 · 15:47–15:50</p>

서버 쪽은 MCP SDK로 도구를 공개합니다. 사용하는 쪽은 LangChain의 `MCPAdapter`로 원격 도구를 LangChain 도구로 변환합니다. 앞 장의 `create_agent(..., tools=...)`에 그대로 연결할 수 있습니다.

```python
# 연결 구조를 읽는 발췌. 실제 실행은 아래 4A·4B 노트북 셀에서 합니다.
async with MCPAdapter(Client(url, mode="2026-07-28")) as adapter:
    tools = await adapter.list_tools()
    agent = create_agent(model=model, tools=tools)
    result = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
```

`await`는 응답을 기다립니다. `async with`는 연결을 사용하는 범위를 정하고 끝나면 정리합니다. 원격 도구 호출이 끝날 때까지 Agent 실행도 이 범위 안에 둡니다. Jupyter는 `await`를 바로 사용할 수 있습니다.

LangChain 1.4의 `langchain.mcp`는 FastMCP client 위에서 작동합니다. 이전 별도 패키지의 `MultiServerMCPClient`와 달리 이번 고정 버전은 `MCPAdapter`를 사용합니다. 현재 beta API이므로 수업의 lockfile을 사용합니다. [공식 변경 안내](https://www.langchain.com/blog/mcp-in-langchain-stateless-protocol-elicitation-and-more)

</section>
<section class="slide" id="observe">

## 실습 · 등록 → 직접 호출 → Agent 연결

<p class="section-time">예상 15분 · 15:50–16:05</p>

<!-- lesson-exercise:protocols -->

**제공되는 것:** 정책 데이터·조회 함수, HTTP 서버 시작과 종료 코드, 결과 출력 코드입니다. 직접 작성하는 것은 `build_mcp_server`의 등록 코드와 4B의 도구 목록 연결 한 줄입니다.

4A의 `await policy_tool.ainvoke({"topic": topic})`는 모델 없이 도구를 직접 실행합니다. 4B의 `await agent.ainvoke(...)`는 모델이 도구 요청을 만들게 합니다. 같은 `ainvoke`라도 호출 대상이 다릅니다.

</section>
<section class="slide" id="practice">

## 실습 · 입력을 바꿔 완료 기준을 확인합니다

<p class="section-time">예상 15분 · 16:05–16:20</p>

먼저 4A의 세 입력을 확인한 뒤, 4B의 질문을 아래처럼 바꾸어 실행합니다. 새 파일을 만들지 않습니다.

| 입력 | 4A 도구 결과 | 4B에서 확인할 것 |
|---|---|---|
| 정산 | P-01·재무지원팀 | 조회 요청과 결과를 거쳐 팀·정책 ID를 답함 |
| 계정 | P-02·IT지원팀 | 계정으로 조회하며 정산 결과를 재사용하지 않음 |
| 없는업무 | found=false, policy=null | 임의의 담당 팀 대신 추가 확인 안내 |

**직접 설명하기:** `tools=[]`인 채로 실행해도 문장이 나올 수 있습니다. 그 실행에는 왜 원격 조회가 없었을까요? 도구 목록을 연결한 실행의 `messages`와 비교합니다.

셀에서 오류가 나면 마지막 정상 출력부터 찾습니다. 서버 주소가 만들어지기 전인지, 목록 조회 중인지, 원격 함수 실행 중인지, 모델 요청 중인지에 따라 고칠 곳이 다릅니다. API 인증 오류가 나면 모델 없이 실행하는 4A까지 완료하고 모델 연결을 복구한 뒤 4B를 재실행합니다.

</section>
<section class="slide" id="solution">

## 풀이 · 바뀐 것은 조회 함수가 아니라 연결입니다

<p class="section-time">예상 7분 · 16:20–16:27</p>

`notebooks/build-agent-solution.ipynb`의 4번과 비교합니다. 도구 등록은 다음 세 줄입니다.

```python
def build_mcp_server(policy_tool):
    server = MCPServer("업무 정책 도구")
    server.tool()(policy_tool)
    return server
```

4B에서는 `tools = await adapter.list_tools()`로 받은 도구를 Agent에 전달합니다. 데이터 조회 로직을 다시 작성할 필요가 없습니다. 서버가 등록한 함수, adapter가 반환한 도구, 모델이 요청한 도구 이름이 `lookup_policy`로 이어지는지 확인합니다.

| 보이는 결과 | 뜻 | 확인 위치 |
|---|---|---|
| 서버 접속 실패 | 통신이 성립하지 않음 | 서버 시작 셀과 URL |
| JSON-RPC error | 요청 처리 단계의 프로토콜 오류 | 메서드·요청 형식과 오류 내용 |
| 도구 실행 오류 | 호출된 도구의 실행이 실패 | 도구 인자·실행 로그 |
| found=false | 조회는 끝났지만 해당 규정이 없음 | 사용자에게 확인할 업무명 |

프로토콜 응답의 `isError`는 도구 실행 오류 표시이며 `found`는 우리가 정한 업무 결과입니다. Adapter는 도구 실행 오류를 LangChain 도구 호출 예외로 전달할 수 있습니다. 필드명을 암기하는 대신 **어느 계층에서 어떤 일이 끝났는지**를 출력으로 읽습니다.

</section>
<section class="slide" id="operations">

<p class="section-time">예상 5분 · 16:27–16:32 · 표와 사례 하나 / 나머지는 복습</p>

### 로드맵 읽기 · 도구 서버가 커지면 무엇이 달라질까요? {#roadmap}

지금 만든 서버는 도구 수가 적고 조회 결과를 바로 돌려줍니다. 이 서버를 여러 팀이 사용하고, 오래 걸리는 작업도 맡기게 된다면 어떤 문제가 생길까요?

2026년 8월 로드맵은 이런 확장을 다룹니다. **이미 출시한 변화와 앞으로 추진할 방향을 나누어 읽어야 합니다.** [8월 22일 발표](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/) · [공식 로드맵 · 확인 2026-09-09](https://modelcontextprotocol.io/development/roadmap)

#### 이미 달라진 기반: 요청마다 필요한 정보를 전달합니다

7월 28일 명세에서는 초기화 handshake와 프로토콜 세션을 없앴습니다. 서버가 이전 연결을 기억하지 않아도 요청을 처리할 수 있도록 바뀐 것입니다. `server/discover`는 지원 버전과 기능을 알아보는 선택적 호출이며, 예전 초기화 절차를 다른 이름으로 반드시 수행한다는 뜻은 아닙니다. 목록 결과의 캐시 지원도 이 릴리스에 포함됩니다. [7월 명세 발표](https://blog.modelcontextprotocol.io/posts/2026-07-28/)

예를 들어 첫 요청은 서버 A가 받고 다음 요청은 서버 B가 받을 수 있습니다. 각 요청이 필요한 정보를 담으면 프로토콜 세션 때문에 같은 서버에 묶일 필요가 줄어듭니다. 다만 두 서버가 같은 티켓을 읽어야 한다면 **업무 저장소를 공유하는 설계**는 여전히 필요합니다. 이 경우 저장소 공유는 별도의 서비스 설계 문제입니다.

#### 다음 다섯 방향은 어떤 문제를 풀려는 걸까요?

|운영에서 생기는 상황|로드맵의 방향|읽을 때 주의할 점|
|---|---|---|
|보고서 생성이 오래 걸리고 도중에 취소 요청도 옴|장시간 작업·이벤트·진행 통신의 조합 정리|관련 기능을 같은 수명주기와 오류 처리로 연결하는 작업|
|로컬 연결과 원격 연결을 각각 구현·관리함|HTTP 중심 전송 통합과 강화|원격의 무상태 전환은 출시됐지만 HTTP over stdio는 추진 방향|
|사용자가 자리를 비운 동안 Agent가 다른 Agent에 일을 맡김|Agent 신원과 권한 위임|누구를 대신해 어떤 권한으로 호출하는지 다루는 문제|
|도구가 많고 클라이언트마다 반환값을 다르게 다룸|점진적 발견과 도구 결과 형식 개선|구체 API가 모두 확정·배포된 것으로 읽지 않음|
|명세·SDK·빠른 시작 예제가 서로 어긋남|SDK 개발 경험과 명세 적합성 개선|명세에서 SDK·예제를 생성하고 검증하는 실험도 포함|

로드맵은 향후 6~12개월의 방향을 설명하며 고정된 출시 약속은 아닙니다. 구현 여부는 사용하는 명세와 SDK에서 확인합니다. [공식 우선순위와 범위](https://modelcontextprotocol.io/development/roadmap#priority-areas)

#### 사례 1 · 도구 100개를 처음부터 모두 알려줘야 할까요?

식당 메뉴 문의에는 식당 관련 도구만 필요합니다. 작은 진입점에서 시작해 대화가 구체화될수록 도구를 더 발견하는 방식이 Progressive Discovery의 방향입니다. 처음 전달할 설명을 줄일 수 있지만, 필요한 도구를 찾는 단계가 추가됩니다. 어떤 도구를 숨기고 언제 더 보여줄지도 설계해야 합니다.

**생각해 보기:** 사용자가 “출장비 정산”을 물었는데 처음에는 일반 정산 도구만 보입니다. 출장 전용 도구를 찾을 경로가 없다면 무슨 일이 생길까요?

현재 실습의 목록 조회는 이 점진적 발견 시스템 전체가 아닙니다. `server/discover`로 서버의 버전·기능을 확인하는 것과도 구분합니다. 로드맵은 `tools/call`의 텍스트·구조화 결과를 클라이언트가 일관되게 다루는 문제도 함께 다룹니다. [도구 발견·결과 형식의 개선 방향](https://modelcontextprotocol.io/development/roadmap#4-improved-primitives)

<details><summary>사례 2 · 10분 걸리는 보고서는 어떻게 기다릴까요?</summary>

“완료됐나요?”를 계속 묻는 polling과 서버가 완료 소식을 보내는 방식은 비용과 연결 조건이 다릅니다. 그동안 진행률을 표시하거나 사용자가 취소할 수도 있습니다. 각각의 기능이 있어도, 취소 직후 완료 통지가 도착했을 때 어떻게 처리할지는 함께 정해야 합니다.

로드맵은 Tasks·이벤트·진행 통신이 서로 맞물리도록 정리하는 방향을 제시합니다. **Tasks는 7월 개편에서 공식 확장으로 이동했으며, 핵심 프로토콜에 다시 포함하는 것은 향후 목표**입니다. [Tasks 확장 제안](https://modelcontextprotocol.io/seps/2663-tasks-extension)

**질문:** 사용자가 취소한 직후 결과가 도착했습니다. 화면에 보여주는 것과 실제 발송·저장하는 것을 같은 방식으로 처리해도 될까요?

MCP에도 장시간 작업이 있다는 이유로 A2A와 같아지는 것은 아닙니다. 다음 장에서는 도구 호출의 결과를 기다리는 일과 독립 Agent에 작업을 맡기는 일을 비교합니다.

</details>

<details><summary>사례 3 · 정산 조회 권한을 받은 Agent가 다른 Agent를 부른다면?</summary>

사용자가 정산 자료의 조회만 허용했습니다. 첫 Agent가 보조 Agent에 일부 조사를 맡길 때, 같은 자격 증명을 통째로 넘기면 허용 범위를 좁히기 어렵습니다.

로드맵의 Agent Identity는 사람이 없는 실행에서도 호출 주체와 위임된 권한을 다루려는 방향입니다. DPoP, 워크로드 신원, 토큰 교환처럼 기존 보안 표준을 활용하는 작업을 포함합니다. [신원과 위임의 추진 범위](https://modelcontextprotocol.io/development/roadmap#3-agent-identity-and-enterprise-ready-security)

**질문:** 보조 Agent에게도 전체 정산 자료가 필요할까요? 특정 출장 건만 읽도록 맡길 수 있다면 서버는 무엇을 확인해야 할까요?

권한을 식별하는 토큰이 있어도 실제 자료의 접근 허용 여부는 서버에서 검사해야 합니다. 현재 localhost 실습 서버에는 이런 인증·위임 체계가 구현되어 있지 않습니다.

</details>

<details class="instructor-note"><summary>강사용 진행 노트 · 로드맵 해설과 토론</summary>

다섯 방향을 모두 설명하면 약 8~10분, 전체 표를 짚고 사례 하나만 논의하면 약 3~5분을 예상합니다. 고정된 65분 안에서 운영 시연과 풀이의 배분을 조절합니다. 새 필수 구현 과제를 추가하지 않습니다.

처음 질문의 “도구 100개”를 회수한 뒤, 실제 참가자의 업무에 가까운 장시간 작업 또는 권한 위임 사례 하나를 고릅니다. 약어 암기보다 “지금 만든 서버에 어떤 요구가 추가되는가”를 말하게 합니다.

마지막에는 무상태 기반은 출시된 변화, 점진적 발견·전송 통합 등의 구체 작업은 로드맵, 구현 지원은 SDK별 확인이라는 세 구분을 짚습니다. 위 업무 상황과 장단점은 원문 방향을 구체화한 예시이며 해당 기능의 성능을 측정한 결과가 아닙니다.

</details>



</section>
<section class="slide" id="wrap">

## Wrap · 무엇을 요청하고, 어떻게 전달하고, 누가 실행했나요?

<p class="section-time">예상 3분 · 16:32–16:35</p>

| 개념 | 이번 실습에서 확인한 것 |
|---|---|
| JSON-RPC | tools/list와 tools/call, 요청·응답 ID |
| Transport | localhost의 Streamable HTTP로 메시지 전달 |
| MCP server | 기존 조회 함수를 도구로 등록 |
| LangChain adapter | 원격 도구를 create_agent의 tools에 연결 |
| Skill과 MCP | Skill은 작업 절차, MCP는 사용할 도구의 발견·호출 규약 |

**설명해 보기:** “정책을 조회한 뒤 담당 팀과 근거를 답하라”는 Skill이 있습니다. MCP 도구를 연결하지 않았다면 Skill 문서만으로 사내 규정을 조회할 수 있을까요?

<details><summary>설명 비교</summary>

절차 문서만으로 실제 조회 기능이 생기지는 않습니다. Harness가 Skill을 읽게 하고, 조회 도구도 연결해야 합니다. 같은 MCP 도구도 어떤 Skill과 지침을 함께 주는지에 따라 작업 절차가 달라질 수 있습니다.

</details>

다음 장에서는 조회 도구를 호출하는 데서 더 나아가 완성한 초안을 독립 검토 Agent에 맡깁니다.

</section>
<nav class="chapnav"><a href="../toc">전체 목차</a></nav>
</div></div>
