---
layout: page
title: LangChain으로 모델과 도구 연결하기
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec workshop-edition"><div class="deck">
<section class="slide">
<div class="eyebrow">2026.09 · 예상 10:40–11:50 · 70분</div>

# LangChain으로 모델과 도구 연결하기

<p class="lead">앞 장에서 읽은 실행 기록을 이제 직접 만들어 봅니다. 사내 정책을 찾는 Python 함수와, 그 함수를 도구로 사용하는 Agent를 작성합니다.</p>

마칠 때는 <strong><mark class="key-point">조회 함수를 도구로 등록하고, 모델과 연결해 정산 문의를 처리할 수 있어야 합니다.</mark></strong> 정책이 없는 입력도 실행해 반환값과 답변을 비교합니다.

<div class="cue"><div class="cue-body">짧은 예제는 교재의 Python 실행 창에서, 실습은 <code>workshop/notebooks</code>의 Jupyter 노트북에서 진행합니다. 환경 준비가 필요하면 <a href="./start">시작 안내</a>를 확인합니다.</div></div>


### 이 장의 목표와 완료 확인 {#learning-goals}

|할 수 있어야 하는 일|확인할 결과|
|---|---|
|메시지 역할과 모델 응답을 읽습니다.|role·content·도구 요청·토큰 사용량이 각각 무엇인지 설명합니다.|
|조회 함수를 도구로 만들고 Agent에 연결합니다.|build-agent.ipynb 1A·1B에서 정산·계정·미등록 업무를 실행합니다.|
|입력 검사와 함수 실행 오류를 구분합니다.|교재 실행 창 또는 concepts.ipynb에서 입력 제약을 바꿔 결과를 비교합니다.|



</section>

<section class="slide" id="icebreaker">

## 시작 질문 · Python 함수를 만들면 모델도 사용할 수 있을까요?

<p class="section-time">예상 3분 · 10:40–10:43</p>

정산 담당 팀을 찾아주는 Python 함수가 있습니다. 사람이 `lookup_policy("정산")`을 실행하면 담당 팀이 나옵니다. 이제 사용자 질문을 받은 모델도 이 함수를 사용하게 하려 합니다.

**모델에게 함수의 무엇을 알려줘야 할까요? 함수 이름만으로 용도와 넣을 값을 알 수 있을까요?**

현재 LangChain은 도구의 설명과 입력 형식을 모델에 전달하고, 모델이 요청한 함수를 실행해 결과를 돌려주는 연결을 제공합니다. [공식 문서 · Agents](https://docs.langchain.com/oss/python/langchain/agents)

먼저 평범한 Python 함수를 읽고, 도구 등록과 `create_agent` 구성을 차례로 붙입니다. 어떤 부분을 우리가 작성하고 어떤 연결을 LangChain이 맡는지 살펴봅니다.

<details class="instructor-note"><summary>강사용 진행 노트 · 시작 질문</summary>

함수의 용도·입력값이라는 답을 받은 뒤 아래 코드의 이름, 설명, `topic`을 짚습니다. 앞 장의 “조회했는지 확인하기”를 다시 토론하기보다, 그 실행을 만드는 코드로 넘어갑니다.

이 도입은 프레임워크가 맡는 연결을 이해하기 위한 질문입니다. 실행 결과를 검증하고 다음 작업을 시작하는 Loop Engineering은 Harness 장에서 다룹니다. 최신 소식을 별도로 덧붙이기보다 현재 공식 API가 해결하는 문제와 연결합니다.

</details>

</section>

<nav class="lesson-nav" aria-label="수업 흐름"><a href="#concept">01 개념</a><a href="#observe">02 실습</a><a href="#solution">03 풀이</a><a href="#wrap">04 Wrap</a></nav>

<section class="slide" id="concept">

## 개념 1 · LangChain으로 모델을 호출합니다

<p class="section-time">예상 14분 · 10:43–10:57</p>

LangChain은 모델 호출, 메시지, 도구 연결에 쓰는 인터페이스를 제공합니다. 이 장에서는 **모델 설정 → 도구 등록 → Agent 생성 → 질문 전달 → 응답 읽기** 순서로 기본 사용법을 익힙니다.

### 모델 호출 코드를 읽습니다

이 절은 교재의 코드와 예시 결과를 읽는 개념 설명입니다. 웹페이지를 읽는 동안 모델이 호출되지는 않습니다. 직접 실행할 때는 아래의 [선택 실습 · 응답과 토큰 비교](#response-lab)를 따라갑니다.

```python
from course.common import get_model

model = get_model()
response = model.invoke("안녕하세요. 한 문장으로 답해주세요.")
print(response.content)
```

`model`은 모델 접속 설정을 담은 객체입니다. `invoke()`가 실제 요청을 보내고, 응답 객체의 `content`에서 답변을 읽습니다. 이 호출에는 도구가 없으므로 모델의 응답만 받습니다.

### OpenAI 호환 API인데 Gemini를 부르는 이유

`get_model()`은 `.env`의 값을 읽고 `ChatOpenAI` 객체를 만드는 제공 함수입니다. 접속 주소는 OpenRouter이며, 모델 이름은 `google/gemini-3.8-flash`입니다.

**OpenAI 호환은 요청과 응답의 형식을 맞췄다는 뜻입니다.** OpenRouter가 Chat Completions 형식을 제공하므로 `ChatOpenAI`로도 Gemini에 요청할 수 있습니다. `base_url`은 접속할 서버, `model`은 그 서버에서 선택할 모델, `api_key`는 해당 서버의 인증 키입니다. 모델 제공사와 접속 서버, Python 클래스 이름을 구별해 읽습니다.

```text
LangChain의 ChatOpenAI
  → OpenRouter /api/v1/chat/completions
  → 선택한 Gemini 모델
  ← 응답 JSON을 LangChain의 AIMessage로 변환
```

이 연결에서는 공통 호출 형식을 사용합니다. 제공사 전용 기능이나 모든 옵션까지 같다는 뜻은 아니므로 도구 호출·구조화 출력 등의 지원 여부는 별도로 확인합니다. [OpenRouter API 형식](https://openrouter.ai/docs/api_reference/overview)

### 문자열을 펼치면 역할이 있는 메시지입니다

위의 문자열 입력은 사용자 메시지 한 개를 보내는 간단한 표기입니다. 대화에 지시문과 이전 답변을 넣으려면 **누가 한 말인지 나타내는 `role`과 내용인 `content`**를 함께 전달합니다.

**① 요청: 어떤 모델에 무엇을 보낼까요?** 아래는 `ChatOpenAI`가 OpenRouter에 보내는 요청의 형태를 설명한 예시입니다. 터미널에서 실행할 명령이 아닙니다. 실제 호출은 아래 Jupyter 셀에서 진행합니다.

```http
POST https://openrouter.ai/api/v1/chat/completions
Authorization: Bearer [설정한 OpenRouter 키]
Content-Type: application/json
```

`Authorization`은 접속 인증, `Content-Type`은 본문이 JSON임을 알리는 헤더입니다. 다음 본문의 `model`은 선택할 모델이고, `messages`는 모델에 전달할 대화입니다. 키는 본문에 넣지 않습니다.

```json
{
  "model": "google/gemini-3.8-flash",
  "messages": [
    {"role": "system", "content": "한국어로 한 문장만 답합니다."},
    {"role": "user", "content": "LangChain은 무엇인가요?"}
  ]
}
```

같은 요청을 LangChain 메시지 객체로 표현한 코드입니다. `invoke`에서 모델을 호출하고, 그 아래 네 줄은 응답의 어떤 값을 출력하는지 보여 줍니다. 여기서는 코드를 읽고 다음 예시 결과와 연결합니다.

```python
from course.common import get_model
from langchain.messages import SystemMessage, HumanMessage

model = get_model()
messages = [
    SystemMessage(content="한국어로 한 문장만 답합니다."),
    HumanMessage(content="LangChain은 무엇인가요?"),
]
response = model.invoke(messages)

print("응답 종류:", type(response).__name__)
print("답변:", response.content)
print("토큰 사용량:", response.usage_metadata)
print("종료 이유:", response.response_metadata.get("finish_reason"))
```

|API의 `role`|LangChain 객체|담기는 내용|
|---|---|---|
|`system`|`SystemMessage`|답변 방식 등 전체 지시|
|`user`|`HumanMessage`|사용자의 질문이나 요청|
|`assistant`|`AIMessage`|모델의 답변 또는 도구 호출 요청|
|`tool`|`ToolMessage`|프로그램이 실행한 도구의 결과|

LangChain은 `[{"role": "user", "content": "..."}]` 같은 Python dict 목록도 받습니다. 객체와 dict는 메시지를 작성하는 두 가지 표현입니다. 도구 결과를 보낼 때는 `tool_call_id`로 앞의 도구 요청과 짝을 맞춥니다. 다음 절의 Agent가 이 연결을 처리합니다. [LangChain 메시지 문서](https://docs.langchain.com/oss/python/langchain/messages)

### 답변 문자열 밖에 무엇이 남을까요?

`response`는 답변만 든 문자열이 아니라 `AIMessage` 객체입니다. `usage_metadata`에는 입력·출력·전체 토큰 수가 각각 `input_tokens`, `output_tokens`, `total_tokens`로 담깁니다. 아래 예시에서 그 위치를 확인합니다. 토큰은 모델이 입력과 출력을 처리하는 단위이며 글자 수나 단어 수와 같지 않습니다. 입력에는 사용자 질문 외에 함께 보낸 지시문과 대화 기록도 포함됩니다.

**② 응답: 답변과 종료 이유, 사용량이 함께 옵니다.** 위 질문에 대한 비스트리밍 응답은 다음 형태입니다. 필드를 읽기 위한 축약 예시이며, 답변·ID·토큰 수는 실측값이 아닙니다.

```json
{
  "id": "gen-example",
  "object": "chat.completion",
  "model": "google/gemini-3.8-flash",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "LangChain은 모델과 도구를 연결해 AI 애플리케이션을 구성하는 프레임워크입니다."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 30,
    "completion_tokens": 25,
    "total_tokens": 55
  }
}
```

`choices`는 생성 결과 목록이고 `[0]`은 첫 결과입니다. 그 안의 `message`에서 답변을, `finish_reason`에서 이번 생성이 끝난 이유를 읽습니다. 바깥의 `id`는 이 응답의 식별자이며, 도구 요청의 `tool_call_id`와는 다릅니다.

**③ LangChain 객체: JSON의 값을 다음 위치에서 읽습니다.** `ChatOpenAI`는 HTTP 응답을 `AIMessage`로 변환하므로, 노트북에서는 원시 JSON의 경로 대신 오른쪽 표현을 사용합니다.

|HTTP 응답 JSON에서 읽는 위치|LangChain에서 읽는 위치|
|---|---|
|`choices[0].message.content`|`response.content`|
|`usage.prompt_tokens`|`response.usage_metadata["input_tokens"]`|
|`usage.completion_tokens`|`response.usage_metadata["output_tokens"]`|
|`usage.total_tokens`|`response.usage_metadata["total_tokens"]`|
|`choices[0].finish_reason`|`response.response_metadata.get("finish_reason")`|

위 설명용 JSON을 LangChain으로 읽었을 때의 출력도 함께 봅니다. **실제 실행 로그가 아니라 같은 예시 값을 옮긴 것입니다.**

```text
응답 종류: AIMessage
답변: LangChain은 모델과 도구를 연결해 AI 애플리케이션을 구성하는 프레임워크입니다.
토큰 사용량: {'input_tokens': 30, 'output_tokens': 25, 'total_tokens': 55}
종료 이유: stop
```

이 예시에서는 입력 30 + 출력 25 = 전체 55입니다. 실제 호출의 토큰 수와 문장은 달라질 수 있습니다.

사용량이 없는 응답에서는 `usage_metadata`가 `None`일 수 있습니다. 이때 사용량이 0이라고 해석하지 않습니다. 모델에 따라 추론 토큰 등 세부 항목이 추가되기도 하며, 토큰 수만으로 내부 추론 내용을 볼 수 있는 것은 아닙니다.

### `finish_reason`은 왜 확인하나요?

<mark class="key-point">`finish_reason`은 이번 모델 생성이 끝난 이유이며, 답변의 정확성이나 업무 성공을 판정하는 값은 아닙니다.</mark> 이 Chat Completions 응답의 필드명은 `finish_reason`입니다. 다른 API나 SDK에서 본 `finishReason`을 그대로 이 JSON의 키로 사용하지 않습니다.

|값|무슨 일이 끝났나요?|다음에 확인할 것|
|---|---|---|
|`stop`|자연스럽게 생성을 마쳤거나 지정한 종료 문자열에 도달했습니다.|답변이 질문과 근거에 맞는지 확인합니다. 정답이라는 표시는 아닙니다.|
|`length`|생성 토큰 한도에 도달했습니다.|문장·JSON·도구 인자가 잘렸는지 확인합니다. 입력이나 출력 한도를 조정한 뒤 다시 실행할지 판단합니다.|
|`tool_calls`|모델이 도구 호출 요청을 반환했습니다.|`message.tool_calls`의 이름·인자를 읽습니다. 프로그램이 도구를 실행하고 결과를 돌려줘야 합니다.|
|`content_filter`|콘텐츠 필터에 의해 출력이 제한됐습니다.|누락된 내용을 완성된 답변으로 쓰지 않고, 제한 사유를 확인합니다.|
|`error`|OpenRouter가 생성 오류로 표시했습니다.|오류 내용을 확인합니다. HTTP 오류나 SDK 예외로 전달되는 실패도 있으므로 이 값만 검사하지 않습니다.|

`tool_calls`일 때 `message.content`는 비어 있을 수 있습니다. **답변이 없다는 이유만으로 실패라고 판단하지 않고 도구 요청이 있는지 확인합니다.** 직접 `model.invoke()`한 응답은 요청을 읽는 단계까지이며, 뒤에서 만들 `create_agent`가 도구 실행과 다음 모델 호출을 연결합니다.

OpenRouter는 여러 제공사의 종료 이유를 위 값으로 맞추며, 원래 값은 `native_finish_reason`에 별도로 담을 수 있습니다. 제공사 원본 필드가 LangChain 객체에 모두 그대로 남는다고 가정하지 않습니다. [OpenRouter 요청·응답 형식과 종료 이유](https://openrouter.ai/docs/api_reference/overview#finish-reason) · [OpenAI Chat Completions 공식 API](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)

**먼저 확인:** 위 JSON에서 `finish_reason`만 `length`로 바뀌었다면 같은 답변을 그대로 써도 될까요? `stop`이어도 내용이 틀릴 수 있는 이유는 무엇인가요?

### 선택 실습 · 응답과 토큰 비교 {#response-lab}

직접 결과를 확인하려면 **JupyterLab에서 `notebooks/concepts.ipynb`를 열고, 맨 아래 ‘모델 응답과 토큰 비교’ 절**로 이동합니다. 이 활동은 실제 모델을 두 번 호출합니다. 시작 안내에서 키 설정을 마친 환경이 필요합니다.

1. 노트북 맨 위의 **환경 확인 코드 셀**을 Shift+Enter로 실행합니다.
2. ‘모델 응답과 토큰 비교’의 **첫 코드 셀**을 실행합니다. 한 문장 지시문의 답변·사용량·종료 이유가 셀 아래에 나옵니다.
3. 바로 다음 **두 번째 코드 셀**을 실행합니다. 질문은 그대로 두고 지시문을 다섯 문장으로 바꾼 결과가 나옵니다. 첫 결과도 변수에 남아 있어 함께 비교할 수 있습니다.

|확인할 것|완료 기준|
|---|---|
|응답 내용|두 출력에서 답변을 찾고 실제 문장 수를 비교합니다. 모델이 지시를 따랐는지도 봅니다.|
|토큰 사용량|입력·출력·전체 토큰을 각각 짚습니다. 출력이 길어질 때 사용량이 어떻게 달라졌는지 자신의 결과로 설명합니다.|
|종료 이유|각 결과의 `finish_reason`을 읽고, 잘린 출력인지 등을 위 표로 판단합니다.|

<mark class="key-point">예시의 숫자와 같아야 성공하는 실습이 아닙니다. 지시문을 바꾼 두 응답에서 내용·사용량·종료 이유를 찾아 설명하면 됩니다.</mark> 사용량이 제공되지 않으면 ‘미제공’으로 기록하며 0으로 바꾸지 않습니다. 오류가 나면 다음 비교 셀로 넘어가지 않고 접속 설정을 확인합니다.


### `ainvoke()`는 언제 쓰나요?

`invoke()`는 응답이 돌아올 때까지 현재 실행 흐름을 기다리게 합니다. 한 파일에서 한 요청씩 확인할 때는 이 방식으로 충분합니다. **비동기 서버처럼 기다리는 동안 다른 요청도 처리해야 하는 환경에서는 `await model.ainvoke(...)`를 사용합니다.** `a`는 async를 뜻합니다.

```python
# 위 파일의 model과 messages를 사용합니다.
# 동기 호출을 아래 방식으로 바꾸어 실행하는 예입니다.
import asyncio

async def main():
    response = await model.ainvoke(messages)
    print(response.content)

asyncio.run(main())  # 일반 Python 파일에서 실행
```

`await`는 이 함수의 다음 줄을 응답이 올 때까지 기다리게 하되, 이벤트 루프가 다른 비동기 작업을 처리할 수 있게 합니다. `ainvoke()` 하나로 여러 요청이 자동 병렬화되거나 모델이 더 빨리 생성하는 것은 아닙니다. Jupyter처럼 이벤트 루프가 이미 있는 곳에서는 `asyncio.run()` 대신 셀에서 `await main()`을 실행합니다. 답변을 조금씩 표시하는 스트리밍은 별도 기능인 `stream()`·`astream()`입니다. [ChatOpenAI 동기·비동기 API](https://reference.langchain.com/python/langchain-openai/langchain_openai/chat_models/base/ChatOpenAI)

<details class="instructor-note"><summary>강사 진행 노트 · 기초 호출 14분</summary>

연결 구조 2분 → 역할과 메시지 4분 → 실제 응답·토큰 비교 5분 → 비동기 사용 상황 3분을 예상합니다. 비동기는 서버에서 기다림을 처리하는 목적까지만 설명하고 이벤트 루프 구현으로 확장하지 않습니다. 주 실습의 함수 작성 시간은 유지하고, 마지막 운영 사례는 필요에 따라 복습으로 이어갑니다.

</details>

</section>
<section class="slide">

## 개념 2 · Python 함수를 도구로 등록합니다

<figure class="trace-example">

![모델 작업대에서 조회 요청을 보내고, 도구 작업대에서 자료를 찾아 결과를 돌려주는 두 작업대.](/images/workshop/model-tool-exchange.png)

<figcaption>모델은 조회를 요청하고, 프로그램은 도구를 실행해 결과를 돌려줍니다. AI로 제작한 역할 비유이며, 그림의 체크 표시는 도구의 반환 결과를 뜻합니다. 결과의 정확성까지 자동 보장하지는 않습니다.</figcaption>
</figure>


<p class="section-time">예상 6분 · 10:57–11:03</p>

먼저 함수는 입력을 받아 결과를 돌려주는 일반 Python 코드입니다. 아래 실행 칸에서 `topic`을 `정산`, `계정`, `없는업무`로 바꿔 실행해 봅니다.

<PythonPlayground kind="lookup" />

여기서는 모델을 호출하지 않습니다. 다음 노트북 실습에서는 이 조회 원리를 사용해 JSON 문자열을 반환하는 함수를 작성합니다.

### 도구의 이름·설명·입력 형식

```python
from langchain.tools import tool

@tool
def lookup_team(topic: str) -> str:
    """업무명으로 담당 팀을 찾습니다. 정산 또는 계정을 입력합니다."""
    teams = {"정산": "재무지원팀", "계정": "IT지원팀"}
    return teams.get(topic.strip(), "등록된 업무가 없습니다")

print(lookup_team.name)
print(lookup_team.description)
print(lookup_team.invoke({"topic": "정산"}))
```

### `@tool`을 붙이면 무엇이 달라질까요?

Python의 데코레이터는 함수를 다른 함수에 전달하고, 그 반환값을 원래 이름에 붙이는 문법입니다. `@tool`은 조회를 실행하는 것이 아니라 **<mark class="key-point">함수를 도구 객체로 변환</mark>**합니다. 이 예제에서는 `StructuredTool`이 만들어집니다.

```python
# @tool을 쓰지 않고 같은 변환을 풀어 쓴 모습입니다.
def lookup_team(topic: str) -> str:
    """업무명으로 담당 팀을 찾습니다."""
    return {"정산": "재무지원팀", "계정": "IT지원팀"}.get(topic, "등록된 업무가 없습니다")

lookup_team = tool(lookup_team)
print(type(lookup_team).__name__)  # StructuredTool
print(lookup_team.args)           # 모델에게 알릴 입력 필드
print(lookup_team.invoke({"topic": "정산"}))
```

변환 전에는 `lookup_team("정산")`으로 함수를 호출합니다. 변환 후에는 도구 인터페이스인 `.invoke({"topic": "정산"})`을 사용합니다. 도구 객체에는 실행할 함수뿐 아니라 <mark class="key-point">이름·설명·입력 schema(입력 형식)</mark>가 담깁니다. 모델은 이 설명과 형식을 받아 어떤 도구에 어떤 값을 요청할지 고릅니다. Python 함수 본문을 모델이 직접 실행하는 것은 아닙니다.

### 모델도 도구도 왜 `invoke()`로 실행할까요? {#runnable}

LangChain의 **Runnable은 입력을 받아 실행하고 결과를 돌려주는 공통 인터페이스**입니다. 모델이나 도구처럼 서로 다른 객체를 같은 메서드 이름으로 실행할 수 있도록 약속한 것입니다. `@tool`로 만든 도구도 이 인터페이스를 따릅니다. 일반 Python 함수의 호출 문법이 바뀐 것이 아니라, 함수를 감싼 **도구 객체의 메서드**를 사용하는 것입니다.

아래는 앞에서 본 모델·도구와 뒤에서 만들 Agent를 비교한 표입니다. 실행 지시가 아니라 각 호출의 역할을 읽는 예시입니다.

|호출|받는 입력|실행하는 일과 반환값|
|---|---|---|
|`model.invoke(messages)`|대화 메시지|모델을 호출하고 `AIMessage`를 반환합니다.|
|`lookup_team.invoke({"topic": "정산"})`|도구의 입력 형식에 맞는 값|일반 입력 dict로 직접 호출하므로 문자열 `"재무지원팀"`을 반환합니다. 모델 호출은 없습니다.|
|`agent.invoke({"messages": messages})`|Agent의 초기 상태|구성된 그래프를 실행하고 메시지 등을 담은 상태를 반환합니다. 내부에서 모델·도구를 여러 번 호출할 수 있습니다.|

**Agent 안에서 보는 결과는 왜 `ToolMessage`일까요?** 위 표는 함수 인자만 담은 dict로 직접 호출한 경우입니다. 호출 ID가 포함된 **ToolCall**을 전달하면, 같은 도구도 결과를 `ToolMessage`로 감싸서 반환합니다. ID는 어느 요청의 결과인지 연결하는 데 쓰입니다.

```python
# 위에서 만든 lookup_team 도구를 두 방식으로 호출한 비교입니다.
plain = lookup_team.invoke({"topic": "정산"})
message = lookup_team.invoke({
    "type": "tool_call",
    "name": "lookup_team",
    "args": {"topic": "정산"},
    "id": "call_1",
})
print(type(plain).__name__, repr(plain))
print(type(message).__name__, repr(message.content), message.tool_call_id)
```

설치된 실습 환경에서 모델 호출 없이 확인한 출력입니다.

```text
str '재무지원팀'
ToolMessage '재무지원팀' call_1
```

<mark class="key-point">일반 입력 dict로 직접 호출한 반환값과, Agent의 도구 요청에 대응하는 `ToolMessage`를 구분합니다.</mark> 이 예제에서 함수가 만든 내용은 같지만, 후자는 `content`와 `tool_call_id`를 가진 메시지입니다. Agent 실행에서는 이 메시지를 다음 모델 입력에 연결합니다.

<mark class="key-point">`invoke()`는 입력 하나로 실행한다는 공통 사용법입니다. 무엇을 실행하고 어떤 값을 반환하는지는 대상 객체에 따라 다릅니다.</mark> 따라서 `invoke()` 한 번이 항상 모델 호출 한 번을 뜻하지는 않습니다.

앞에서 본 `ainvoke()`는 비동기 실행 방법입니다. Runnable에는 여러 입력을 처리하는 `batch()`, 결과를 순차적으로 받는 `stream()`도 있습니다. 실제 병렬 처리나 스트리밍 방식은 구현에 따라 달라집니다. 이 절에서는 <strong>일반 함수는 `함수(인자)`, LangChain 도구 객체는 `.invoke(입력)`</strong>으로 실행한다는 차이를 먼저 익힙니다. [Runnable 공식 API](https://reference.langchain.com/python/langchain-core/runnables/base/Runnable) · [BaseTool의 실행 인터페이스](https://reference.langchain.com/python/langchain-core/tools/base/BaseTool)

### 이름·설명·입력 조건을 직접 정합니다

기본값은 함수 이름 → 도구 이름, docstring → 도구 설명, 타입 힌트 → 입력 schema입니다. 함수 이름을 바꾸지 않고 공개 이름을 정하거나, 허용할 입력을 더 분명히 제한할 수도 있습니다.

`notebooks/concepts.ipynb`의 ‘도구 입력 조건’ 셀을 실행합니다. 모델 호출이나 API 키는 필요하지 않습니다.



<<< ../../workshop/labs/tool_basics.py{python}

`Literal`은 허용하는 값 두 개를 나타냅니다. `Field(description=...)`은 그 필드의 뜻을 설명합니다. `args_schema`가 함수 실행 전에 입력을 검사하므로 `휴가`는 함수 본문에 들어가기 전에 거절됩니다. schema의 `topic`과 함수 인자 `topic`은 이름을 맞춥니다.

이 예제는 **지원 목록 밖의 입력을 거절하는 도구**입니다. 뒤의 주 실습은 임의의 업무명을 받아 `found=false`를 반환하는 조회 도구입니다. 입력 정책이 다르므로 주 실습에 이 `Literal` 제한을 그대로 옮기지 않습니다.

|설정|하는 일|사용할 때 확인할 것|
|---|---|---|
|`@tool("lookup_team")`|모델에 공개할 이름 지정|다른 도구와 구별되게 정하고 공백 없이 `snake_case` 사용|
|`description="..."`|도구 전체 설명 지정|명시한 설명이 docstring보다 우선. 용도와 지원 범위를 짧게 작성|
|`args_schema=TeamInput`|입력 필드·설명·제약 지정|함수 인자와 이름·기본값을 맞춤|
|`infer_schema=True`|함수 시그니처에서 입력 형식 추론. 기본값|명시 schema가 필요 없을 때도 타입 힌트 작성|
|`parse_docstring=True`|Google 스타일 docstring의 `Args:`를 필드 설명으로 해석|기본은 `False`. 형식이 잘못되면 기본 설정에서 도구 생성 오류|
|`error_on_invalid_docstring=False`|docstring 파싱 오류로 생성을 중단하지 않도록 설정|파싱을 켰을 때 관련됨. 잘못된 설명을 고치는 것이 우선|

<details><summary>추가 옵션 · 결과 전달과 종료</summary>

조회한 원본 데이터가 길면 모델에는 짧은 설명만 보내고, 프로그램은 원본을 따로 사용할 수 있습니다. `content_and_artifact`를 지정한 도구는 **설명과 원본을 한 쌍으로 반환**합니다.

<<< ../../workshop/labs/tool_artifact.py{python}

|출력 필드|예제의 값|사용처|
|---|---|---|
|`content`|정산 담당은 재무지원팀입니다.|모델이 다음 답변을 작성할 때 읽음|
|`artifact`|정책 ID와 담당 팀을 담은 dict|프로그램이 화면 표시·후속 처리에 사용|

`type="tool_call"`과 `id`를 함께 전달하면 `ToolMessage`를 받아 두 필드를 확인할 수 있습니다. 단순 입력 dict로 호출하면 이 메시지 포장을 받지 못합니다. artifact는 모델 입력에 자동으로 포함되지 않습니다.

`concepts.ipynb`의 ‘도구의 content와 artifact’ 셀에서 두 출력을 확인합니다.


`return_direct=True`는 이 도구 실행 뒤 추가 모델 응답 단계를 거치지 않고 Agent 실행을 끝내도록 하는 설정입니다. 실제 종료 처리는 도구를 사용하는 Agent 실행기에 달려 있습니다. 단순히 “도구를 빠르게 실행하는 옵션”은 아니며, 결과를 모델이 설명해야 하는 이번 실습에는 기본값 `False`를 사용합니다.

</details>

### 잘못된 입력과 실행 실패를 구별합니다

앞 예제의 `휴가`는 입력 조건 위반입니다. 반면 지원하는 `정산`을 조회하다 DB 연결이 끊기는 것은 실행 실패입니다. schema 검사를 통과해도 외부 서비스가 정상이라는 보장은 없습니다. 직접 `.invoke()`하면 예외를 호출한 코드에서 처리해야 하며, Agent 안에서의 오류 처리는 실행기의 설정을 확인합니다.

설명에 “읽기 전용”이라고 쓰는 것만으로 쓰기가 차단되지는 않습니다. 인증 키·사용자 권한은 모델이 채울 인자로 받지 않고 프로그램에서 관리하며, 조회 함수 안에서 필요한 권한을 검사합니다. 타입 힌트는 입력 형식의 재료이고, 반환 타입 `-> str`만으로 업무 결과가 정확한지 검사해 주지는 않습니다.

### 직접 구현 · 휴가 문의도 처리하도록 확장합니다 {#tool-input-lab}

지금 조회 기능은 정산·계정 문의만 처리합니다. **“휴가 문의는 인사지원팀으로 안내해 주세요”**라는 새 요구가 들어왔습니다. 아래 코드의 입력 조건과 조회 함수를 수정해 휴가를 지원해 봅니다.

<mark class="key-point">휴가는 인사지원팀으로 안내하고, 기존 정산·계정 조회도 그대로 동작해야 완료입니다.</mark> 이 활동에서는 새 입력을 허용하는 일과 그 입력을 처리할 데이터를 준비하는 일이 어떻게 다른지 확인합니다.

아래 실행 칸을 직접 수정합니다. 앞에서 배운 `TeamInput`과 `Literal`로 입력을 검사한 뒤 `find_team`이 담당 팀을 찾습니다. 처음 실행하면 브라우저가 Python과 Pydantic을 준비합니다. 모델 호출이나 API 키는 필요하지 않습니다.

<PythonPlayground kind="validation" />

**먼저 현재 코드를 실행해 휴가 문의가 어디에서 거절되는지 확인합니다.** 그다음 휴가를 처리하도록 수정합니다. 수정할 위치를 먼저 찾아보고, 막히면 아래 힌트를 펼칩니다.

<details><summary>수정 힌트 · 입력은 통과했는데 조회가 실패한다면?</summary>

|순서|바꿀 곳|실행해서 확인할 것|
|---|---|---|
|1|처음 코드 실행|`TeamInput(topic="휴가")`에서 입력을 거절합니다. 아직 조회 함수는 실행되지 않았습니다.|
|2|`TeamInput`의 `Literal`에 `"휴가"` 추가|입력 검사는 통과합니다. 하지만 `teams`에 휴가 담당 팀이 없어 조회할 때 `KeyError`가 납니다.|
|3|함수 안 `teams`에 `"휴가": "인사지원팀"` 추가|휴가 문의에 `인사지원팀`을 반환합니다.|

`KeyError`는 새 요구가 아직 절반만 반영됐다는 단서입니다. 입력 허용 범위를 바꿔도 담당 팀 데이터가 자동으로 추가되지는 않습니다.

</details>

**완료 확인:** 수정한 코드의 `TeamInput(topic="휴가")`에서 `topic` 값을 아래 순서로 바꾸고, 매번 **Python 실행**을 누릅니다. 나머지 코드는 유지합니다.

|입력|확인할 결과|
|---|---|
|`"휴가"`|`인사지원팀` 출력|
|`"정산"`|기존과 같이 `재무지원팀` 출력|
|`"계정"`|기존과 같이 `IT지원팀` 출력|
|`"없는업무"`|입력 검증 오류 안내. 임의의 담당 팀을 반환하지 않음|

**설명해 보기:** 휴가를 `Literal`에만 추가했을 때는 왜 실패했나요? 입력 검사와 담당 팀 조회가 각각 책임지는 일을 한 문장씩 설명합니다.

이 실행 칸에서는 검증 단계를 보이기 위해 `TeamInput(...)`을 직접 호출합니다. 앞의 `@tool(args_schema=TeamInput)` 예제에서는 도구 객체가 같은 스키마로 입력을 검사한 뒤 함수를 호출합니다. 실제 LangChain 도구까지 함께 실행하려면 `notebooks/concepts.ipynb`의 ‘도구 입력 조건’ 셀을 사용합니다.

### 일반 함수도 결국 도구 객체로 변환됩니다

`create_agent(tools=[lookup_team], ...)`처럼 일반 함수를 넘겨도 내부에서 `tool(lookup_team)` 변환을 거칩니다. 소스 코드에 `@tool` 문자를 붙이는 것이 아니라, 같은 변환 함수를 호출하는 방식입니다.

```python
# 직접 변환한 도구를 전달
policy_tool = tool(lookup_team)
agent = create_agent(model=model, tools=[policy_tool])

# 일반 함수를 전달하면 내부에서 변환
agent = create_agent(model=model, tools=[lookup_team])
```

`@tool`은 함수 정의 시 변환하고, 일반 함수 전달은 Agent 구성 과정에서 변환합니다. 공개 이름이나 입력 제약을 직접 정하려면 `@tool(...)` 또는 `tool(...)(함수)`를 사용합니다. 이번 실습은 MCP에서도 같은 조회 함수를 쓰므로 원래 함수는 유지하고 `build_agent` 안에서 변환합니다.

참고: [공식 도구 사용법](https://docs.langchain.com/oss/python/langchain/tools), [tool 옵션 API](https://reference.langchain.com/python/langchain-core/tools/convert/tool)

<details class="instructor-note"><summary>강사 진행 노트 · 도구 기본과 확장</summary>

기본 설명은 기존 6분을 기준으로 데코레이터 변환과 이름·설명·입력 형식을 짚습니다. 명시 schema 예제 실행과 반례 수정까지 함께 진행하면 추가 8~10분을 예상합니다. 전체 세션 종료는 11:50이며, 이 경우 뒤의 개인 과제에서 같은 입력 검사를 다시 다루는 시간을 통합하고 운영 상세는 복습으로 이어갑니다. 모든 옵션을 외우게 하기보다 “모델에 무엇을 알리고 프로그램이 무엇을 검사하는가”를 코드에서 찾습니다.

</details>

</section>
<section class="slide">

## 개념 3 · Agent를 만들고 실행합니다

<p class="section-time">예상 5분 · 11:03–11:08</p>

```python
from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=[lookup_team],
    system_prompt="업무 문의는 도구로 조회하고 담당 팀을 알려주세요.",
)
result = agent.invoke({
    "messages": [{"role": "user", "content": "정산은 어느 팀에 문의하나요?"}]
})
print(result["messages"][-1].content)
```

앞에서 준비한 `model`과 도구를 연결한 예제입니다. `tools`에는 `lookup_team(...)`의 실행 결과가 아니라 **도구 자체**를 넣습니다. `system_prompt`에는 Agent의 역할과 응답 지침을 적습니다.

`create_agent()`는 실행 구성을 만들고, `agent.invoke()`는 질문을 전달해 실행합니다. `messages`는 대화 목록이며 `role`과 `content`로 발화자와 내용을 표현합니다. 마지막 메시지는 `result["messages"][-1]`로 읽습니다.

<CourseVisual kind="langchain" />

`system_prompt`는 이 구성에서 `SystemMessage`로 만들어져 **각 모델 호출 시 현재 messages 앞에 붙습니다.** 따라서 반환된 `result["messages"]`에 시스템 지침이 없다고 해서 모델이 지침을 못 받은 것은 아닙니다.

OpenAI API에는 애플리케이션 지침을 담는 `developer` 역할도 있습니다. 모든 제공자의 `system`이 일괄적으로 이름을 바꾼 것은 아닙니다. 이 그림은 LangChain의 `SystemMessage`를 기준으로 하며, 실제 API 역할은 모델·연결 어댑터에 따라 확인합니다. [OpenAI 메시지 역할 설명](https://developers.openai.com/api/docs/guides/text)


<mark class="key-point">LangChain은 모델의 도구 요청을 받아 함수를 실행하고, 결과를 메시지에 추가해 모델에 돌려줍니다.</mark> `messages`는 Agent State의 필드이며 `add_messages`라는 병합 규칙이 적용됩니다. 새 ID는 추가하고 같은 ID는 갱신합니다. 다음 장의 [Reducer 설명](./graph#reducers)에서 직접 비교합니다. 우리는 조회 로직과 지침을 작성하고, 이 반복 연결은 프레임워크를 사용합니다. 직접 연결할 수도 있지만 도구 요청 처리와 메시지 누적도 직접 구현해야 합니다.

이제 아래 실습에서 `lookup_policy`와 `build_agent`를 완성합니다. 첫 함수는 데이터를 찾고, 두 번째 함수는 모델과 그 도구를 연결합니다.

</section>
<section class="slide">

## 실습 · 조회 함수와 Agent 만들기 {#observe}

<p class="section-time">예상 15분 · 11:08–11:23</p>

JupyterLab의 `notebooks/build-agent.ipynb`에서 해당 번호의 구현 셀을 작성합니다. 실행 결과는 셀 바로 아래에서 확인합니다.

<!-- lesson-exercise:first-code -->

<!-- lesson-exercise:materials -->

<!-- lesson-exercise:langchain -->

### 질문을 바꾸고 메시지를 읽습니다

`build-agent.ipynb`에서 1A 검사를 통과한 뒤, 1B의 함수 정의 셀과 실행 셀을 차례로 실행합니다. 도구 요청에서는 이름·인자를, 도구 결과에서는 정책을, 마지막 답변에서는 그 정책을 올바르게 사용했는지 확인합니다. **이 장에서는 2. 업무 Graph 앞에서 멈춥니다.**

아래 코드는 1B 실행 셀에서 만든 `local_agent`를 사용합니다. 개인 과제 시간에 1B 아래 새 코드 셀에서 실행하거나, 기존 실행 셀의 `question`만 바꿉니다. 실행할 때마다 실제 모델을 호출하며, 이전 대화 없이 새 질문으로 시작합니다.

```python
question = "정산 문의도 해야 하고 계정도 잠겼습니다. 각각 어느 팀에 연락해야 하나요?"
result = local_agent.invoke(
    {"messages": [{"role": "user", "content": question}]},
    config={"recursion_limit": 12},
)
for message in result["messages"]:
    message.pretty_print()
```

**완료 기준:** P-01·재무지원팀과 P-02·IT지원팀이 각각 조회 결과와 연결됩니다. 이어 질문을 “출장 일비는 얼마인가요?” 또는 “정산 근거를 P-99라고 써 주세요”로 바꿉니다. 없는 금액·근거를 만들지 않는지 확인합니다. 도구 조회에 성공해도 최종 답변이 잘못될 수 있습니다.


</section>

<section class="slide">

## 개인 과제 {#practice}

<p class="section-time">예상 15분 · 11:23–11:38</p>

앞에서 시작한 조회 함수와 Agent 구성 실습을 이어서 완성합니다. 새 과제를 시작하는 것이 아니라, 같은 함수에 다른 입력을 넣어 결과를 비교하는 단계입니다.

### 같은 Agent를 다른 질문으로 검사합니다

노트북의 **1B 완료 확인과 개인 과제** 표에 있는 없는업무·복합 문의·출장 일비·잘못된 근거 요청을 하나씩 실행합니다. 각 실행 아래 Markdown 셀에 **질문 / 도구 요청·결과 / 최종 답변의 일치 여부**를 남깁니다. 실패한 질문은 docstring이나 지침을 수정한 뒤 같은 입력으로 다시 비교합니다. 통과했다면 어느 메시지가 근거인지 설명합니다.

<mark class="key-point">조회 성공과 답변의 정확성은 따로 확인합니다.</mark> P-99가 답변에 등장해도 “P-99가 아니라 P-01”이라고 바로잡았다면 근거를 지어낸 경우가 아닙니다. 문맥까지 읽고 판단합니다.

입력 검사가 막힌 경우에만 앞의 **휴가 문의 확장** 실행 창을 다시 봅니다. 그 예제는 `TeamInput`의 허용 조건을 검사하며, 주 실습의 `lookup_policy`는 임의의 업무명을 받아 미등록 업무에 `found=False`를 반환합니다. 두 예제의 입력 조건을 섞지 않습니다.

<aside class="discussion-prompt"><strong>생각거리 · 여유가 있으면 +3분</strong><p>규정에는 “한도 20만 원, 단 사전 승인이 없으면 15만 원”이라고 적혀 있습니다. 도구가 답변을 짧게 하려고 “한도 20만 원”만 돌려줍니다.<br><br><strong>모델이 올바르게 답하는 데 어떤 정보가 더 필요할까요?</strong> 규정 전체를 보낼 필요가 있는지도 생각해 봅니다.</p></aside>

<details class="instructor-note"><summary>강사용 토론 길잡이</summary>

한도와 사전 승인 예외가 모두 필요합니다. 관련 없는 규정은 생략할 수 있지만 답변을 바꾸는 조건은 남겨야 합니다.

한 답을 빨리 받기보다, 반대 선택이 더 나아지는 조건을 하나 더 묻습니다. 별도 기록이나 제출은 요구하지 않습니다. 기본 배정에 추가하는 선택 활동이므로 다음 섹션의 시간을 조절합니다.

</details>

</section>

<section class="slide">

## 풀이와 다음 모듈 {#solution}

<p class="section-time">예상 10분 · 11:38–11:48</p>

주 실습 풀이는 `notebooks/build-agent-solution.ipynb`의 `lookup_policy`와 `build_agent`를 자신의 구현과 비교합니다. 코드가 비슷한지보다 아래 입력에서 무엇이 실행되고 어떤 근거가 남는지 설명합니다.

|주 실습에서 확인할 입력·변경|확인할 근거|틀렸을 때 먼저 볼 곳|
|---|---|---|
|`" 정산 "`을 조회|앞뒤 공백을 정리한 topic, P-01, 재무지원팀|제공 search_policy에 전달한 입력과 반환값|
|없는 업무를 조회|`found=false`, `policy=null`|없는 결과를 정상 정책으로 채우지 않았는지|
|정산 대신 계정을 질문|실제 도구 인자와 P-02·IT지원팀|정산 답을 코드나 프롬프트에 고정했는지|
|도구를 등록한 Agent 실행|호출 요청 뒤 실제 도구 결과가 존재|`tools`에 전달한 함수와 도구 설명|
|1B에서 P-99를 쓰라는 질문 실행|도구 결과와 최종 응답의 일치 여부|조회 실패인지, 조회 후 근거를 무시한 것인지|

마지막 행은 1B의 질문을 바꿔 자신의 Agent에서 직접 확인합니다. 한 번 올바르게 답했다고 입력 공격을 막았다고 판단하지 않습니다. 조회 결과와 최종 응답을 대조합니다.

</section>
<section class="slide"><details><summary>복습 자료 · 운영으로 옮길 때 확인할 것</summary>



풀이에서는 주 실습의 입력·근거 표와 자신의 실패 한 건을 비교합니다. 아래 운영 사례는 실습 후 읽으며 자신의 업무에 적용할 항목을 고릅니다.

### JSON 세 곳을 구별합니다

도구 입력의 `topic`, 도구가 반환한 `found/policy`, 최종 답변의 필드는 각각 다른 계약입니다. 조회 함수가 JSON을 반환한다고 Agent의 최종 응답도 JSON이 되는 것은 아닙니다.

최종 답변을 다른 프로그램이 읽어야 한다면 `create_agent`의 `response_format`으로 출력 구조를 지정할 수 있습니다. `ProviderStrategy`는 제공자의 구조화 출력 기능을, `ToolStrategy`는 도구 호출 방식으로 표현한 출력 구조를 사용합니다. 결과는 `structured_response`에서 읽습니다. 현재 주 실습은 이 옵션을 설정하지 않고 최종 메시지를 읽습니다. [공식 구조화 출력 설명](https://docs.langchain.com/oss/python/langchain/structured-output)

예를 들어 최종 결과에 `policy_id`, `team`, `needs_confirmation`이 필요하다고 가정합니다. 문자열·불리언 타입을 검사해도 `policy_id="P-99"`라는 잘못된 근거까지 잡히지는 않습니다. **출력 구조 검사 → 실제 조회 결과와 대조 → 다음 동작 허용 여부 결정**이 필요합니다. 제공 모델이 도구 호출과 구조화 출력을 함께 지원하는지도 확인해야 합니다. 현재 연결에서 이 확장을 실행 검증했다고 가정하지 않습니다.

### 오류가 났을 때 어디까지 실행됐는가

|관찰한 상황|첫 확인|재실행 전에 판단할 것|
|---|---|---|
|인증·접속 단계에서 실패|키 설정, HTTP 오류 종류, 모델 이름|설정을 고쳐 실제 연결을 복구해야 함|
|도구 요청은 있으나 결과를 못 받음|함수 이름·인자와 Python 오류|입력 오류인지, 외부 서비스 문제인지|
|정상 도구 결과 뒤 잘못된 답변|조회 데이터와 답변의 주장|같은 질문 재전송만으로 해결할 문제인지|
|실행 상한에 걸림|반복된 도구 요청과 마지막 결과|상한을 늘리기 전에 종료하지 못한 이유|

`course/common.py`의 현재 설정은 `timeout=45`, `max_retries=1`, `max_tokens=1500`입니다. 이는 모델 요청 설정입니다. 전체 Agent 작업이 45초 안에 끝난다는 뜻도, 전체 비용이 1,500토큰으로 제한된다는 뜻도 아닙니다. 여러 번의 모델 호출과 재시도에는 각각 시간과 비용이 듭니다. `recursion_limit=12` 역시 그래프 실행 단계의 제한이며 업무 합격 기준이나 모델 호출 횟수와 동일하지 않습니다.

지금 도구는 읽기 전용 조회입니다. 실제 발송·결제 도구로 바꾼다면 응답 유실 뒤 재실행해도 되는지 먼저 정해야 합니다. 해당 업무가 이미 처리됐는지 확인할 식별자와 중복 방지 장치는 이후 [MCP 운영 사례](./mcp#operations)에서 다룹니다.

현재 `trace_messages`는 역할·내용·도구 요청을 요약합니다. 지연 시간·사용 토큰·도구 호출 ID 전체를 보존하는 운영 추적기는 아닙니다. 운영 기록에는 요청을 연결할 ID와 실패 단계가 필요하며, 원문 문의나 비밀값을 무조건 기록하지 않습니다.



### 기본 사용법을 정리합니다

1. `create_agent()`와 `agent.invoke()` 중 실제 질문을 보내는 것은 무엇인가요?
2. `tools=[lookup_policy]`에 함수 호출 결과를 넣으면 왜 안 될까요?
3. 새 업무를 지원하려면 정책 데이터·도구 설명·Agent 지침 중 무엇을 바꿔야 할까요?

직접 만든 조회 도구를 모델에 연결하고 실행하는 것이 이 장의 목표였습니다. 지금 만든 Agent도 LangGraph의 실행 가능한 그래프입니다. 다음 장에서는 이 구조를 펼쳐 보고, Agent 앞뒤에 업무 조건을 붙입니다.

참고: [LangChain Agents](https://docs.langchain.com/oss/python/langchain/agents).


<details class="instructor-note"><summary>강사용 진행 노트 · 풀이 비교</summary>

학생 구현의 조회 조건을 먼저 보고 계정·없는업무 입력을 비교합니다. 이후 완성 예제의 P-99 사례로 도구 오류와 답변 오류를 구분합니다. 질문은 노트북 1B 셀에서 바꿉니다.

</details>


</details></section>


<section class="slide" id="wrap">

## Wrap · 모델·도구·메시지를 다시 연결해 봅니다

<p class="section-time">예상 3분 · 기존 마무리 시간에 포함</p>

|다시 짚을 개념|오늘 확인한 내용|
|---|---|
|모델 호출|invoke는 요청을 보내고 AIMessage를 받습니다. ainvoke는 비동기 호출입니다.|
|도구 연결|조회 기능을 tool로 감싸 이름·설명·입력 형식을 모델에 알립니다.|
|Agent 실행|HumanMessage → 도구 요청 AIMessage → ToolMessage → 최종 AIMessage가 쌓입니다.|

**짧게 설명해 보기:** 도구 결과는 맞는데 최종 답변이 이상하다면 messages에서 어느 두 항목을 비교할까요?

<details><summary>설명 비교</summary>

ToolMessage의 조회 결과와 마지막 AIMessage의 답변을 비교합니다.

</details>


**목표 확인:** [이 장 첫머리의 완료 기준](#learning-goals)을 자신의 출력이나 설명과 대조합니다. 확인하지 못한 항목은 해당 셀 또는 개념 예제로 돌아갑니다. 풀이를 읽은 것과 직접 실행해 확인한 것을 구분합니다.

</section>
<nav class="chapnav"><a href="../toc">전체 목차</a></nav>
</div></div>
