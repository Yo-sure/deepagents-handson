---
layout: page
title: 시작 안내와 하루의 흐름
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec workshop-edition"><div class="deck">
<section class="slide">
<div class="eyebrow">2026.09 · 예상 09:00–09:40 · 40분</div>

# 시작 안내와 하루의 흐름

강사 소개와 설문 리뷰 10분으로 시작합니다. 이어서 실습 자료를 받고 실습 환경을 준비합니다. 이 장에서는 완성된 예제를 한 번 실행하여 모델에 연결되는지 확인합니다. 코드를 직접 작성하는 실습은 LangChain 장에서 시작합니다.

<p class="lead">오늘은 사내 문의에 맞는 규정을 찾아 답변 초안을 만드는 프로그램을 만듭니다. 예제를 실행하고 작동 원리를 배운 뒤 필요한 함수를 직접 작성합니다.</p>

<div class="cue"><div class="cue-body">짧은 예제는 교재의 Python 실행 창에서, 실습은 <code>workshop/notebooks</code>의 Jupyter 노트북에서 진행합니다. 처음이라면 강사 안내에 따라 아래 <a href="#setup">환경 준비</a>를 함께 진행합니다. 이미 준비했다면 마지막 준비 완료 체크부터 확인합니다.</div></div>

### 하루를 마쳤을 때 할 수 있어야 하는 일 {#course-goals}

1. 메시지와 도구 결과를 근거로 Agent의 실행을 설명합니다.
2. 조회 도구·Agent·업무 분기를 구현하고 정상 입력과 반례로 확인합니다.
3. Harness·Skill·수정 루프의 역할을 구별하고 실행·검증·중단 조건을 정합니다.
4. MCP 도구 연결과 A2A 작업 위임을 통합하고, 새 입력을 지원해도 기존 결과가 유지되는지 확인합니다.

이 목표는 각 장의 실행 결과와 마지막 통합 실습으로 확인합니다. <mark class="key-point">퀴즈는 개념 복습이며 구현 성공을 대신하지 않습니다.</mark> 운영 배포·인증·장애 후 영속 복구까지 완성하는 과정은 아닙니다.

### 이 장의 목표와 완료 확인 {#learning-goals}

|할 수 있어야 하는 일|확인할 결과|
|---|---|
|같은 Python 환경에서 노트북을 실행합니다.|orientation.ipynb 환경 셀에서 실행 경로·버전을 확인합니다.|
|모델과 도구가 연결됐는지 구분합니다.|모델 호출 셀에서 도구 요청·P-01 조회 결과·최종 답변을 찾습니다.|



</section>

<nav class="lesson-nav" aria-label="학습 단계"><a href="#opening">01 소개·설문 리뷰</a><a href="#overview">02 오늘의 흐름</a><a href="#setup">03 환경 준비</a><a href="#connection">04 연결 확인</a><a href="#practice">05 다음 장으로</a></nav>

<section class="slide" id="opening">

## 강사 소개와 설문 리뷰

<p class="section-time">예상 10분 · 09:00–09:10</p>

강사의 실무 경험과 오늘 다룰 주제를 소개하고, 사전 설문에 나온 경험 수준·관심 업무·궁금한 점을 함께 살펴봅니다. 설문에 적은 질문을 어느 수업에서 다루는지 확인합니다.

설문 리뷰를 마치면 환경설정을 함께 진행합니다. 설치 여부와 관계없이 같은 실습 폴더를 열고 첫 모델 호출까지 확인합니다. 그다음 개념을 배우고 직접 코드를 작성합니다.

</section>

<section class="slide" id="icebreaker">

## 시작 질문 · 같은 예제가 한 사람의 PC에서만 실패한다면?

<p class="section-time">예상 3분 · 09:10–09:13</p>

같은 예제를 받은 두 사람이 실행했습니다. 한 사람은 답변을 받았고, 다른 사람은 모델에 연결하지 못했다는 오류를 봤습니다.

**코드를 바꾸기 전에 두 사람의 무엇을 비교하면 좋을까요?**

Anthropic은 Agent 평가에서 실행 환경을 분리하고 이전 작업의 영향이 남지 않게 하는 문제를 다룹니다. 같은 코드만으로 같은 실행 조건이 만들어지지는 않습니다. [2026-01-09 · 기술 해설](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

이제 실행 폴더와 라이브러리, 키와 접속 조건을 함께 확인하고 첫 답변을 받아 봅니다.

<details class="instructor-note"><summary>강사용 진행 노트 · 시작 질문</summary>

진행 예: 상황 30초 → 의견 한두 개 1분 → 최근 사례와 본문 연결 1분 30초. 별도 기록이나 제출은 요구하지 않습니다.

설문에서 나온 환경설정 경험 한 건과 연결합니다. 폴더·라이브러리·접속 조건 중 한두 답을 들으면 충분합니다. 원문은 평가 환경에 관한 글이며 PC 설치 문제를 직접 실험한 연구는 아닙니다.

</details>

</section>

<section class="slide" id="overview">




## 오늘 만드는 것

<p class="section-time">예상 2분 · 09:13–09:15</p>

<CourseVisual kind="start" />


업무 문의를 읽고 규정을 조회하여 근거가 있는 답변 초안을 만듭니다. 정보가 부족하면 질문하고, 검토에 실패하면 제한된 횟수만 수정합니다. 마지막에는 도구 서버와 검토 Agent를 연결합니다.


LangChain으로 모델·도구를 연결하고 LangGraph로 분기를 표현합니다. Harness에서는 이 Agent가 일하는 환경과, 개발자가 코딩 에이전트로 이 프로그램을 개선하는 방식을 함께 살펴봅니다. 두 관점의 전환은 해당 모듈에서 구분합니다.

MCP는 도구 연결, A2A는 독립 Agent에 작업을 위임할 때 사용합니다. 각 이름의 의미는 해당 모듈에서 예제로 설명합니다.

<aside class="discussion-prompt"><strong>생각거리 · 여유가 있으면 +3분</strong><p>오늘은 만든 답변을 화면에서 확인합니다. 내일부터는 그 답변을 고객에게 자동으로 메일로 보낸다고 가정해 봅니다.<br><br><strong>바로 보내게 할까요, 사람이 먼저 읽게 할까요?</strong> 이 질문은 마지막 수업에서 다시 생각해 봅니다.</p></aside>

<details class="instructor-note"><summary>강사용 토론 길잡이</summary>

지금 정답을 확정하지 않습니다. 마지막 통합 시간에 선택이 바뀌었는지 다시 묻습니다. 구체적인 개인 업무 데이터를 공개할 필요는 없습니다.

한 답을 빨리 받기보다, 반대 선택이 더 나아지는 조건을 하나 더 묻습니다. 별도 기록이나 제출은 요구하지 않습니다. 기본 배정에 추가하는 선택 활동이므로 다음 섹션의 시간을 조절합니다.

</details>

</section>

<section class="slide">

## 환경 준비: 자료를 받은 뒤 첫 호출까지 {#setup}

<p class="section-time">예상 22분 · 09:15–09:37</p>

**자료 받기 → Ubuntu에서 설치 스크립트 실행 → 키 파일 지정 → 노트북에서 첫 호출** 순서로 준비합니다. 이미 준비한 항목은 확인 후 넘어갑니다. 환경설정은 강사와 함께 진행합니다. 이미 설치한 사람도 편집기 위치·의존성·키 설정·첫 호출을 차례로 확인합니다.

<details><summary>Python 코드 읽기가 어색하다면: 사전 준비 5분</summary>

함수에 값을 넣고 반환값을 받는 흐름을 먼저 확인합니다. Python 전체 문법을 다시 배우는 시간이 아니라, 뒤 실습에서 반복해서 읽을 표기입니다.

```python
import json

def read_team(topic):
    teams = {"정산": "재무지원팀", "계정": "IT지원팀"}
    team = teams.get(topic.strip())
    return json.dumps({"team": team}, ensure_ascii=False)

result = read_team(" 계정 ")
print(result)
print(json.loads(result)["team"])
```

`topic`은 함수에 넣은 값, `return`은 호출자에게 돌려줄 값입니다. `strip()`은 앞뒤 공백을 정리하고 `get()`은 이름에 대응하는 값을 찾습니다. `dumps()`는 dict를 JSON 문자열로, `loads()`는 JSON 문자열을 Python 값으로 바꿉니다.

첫 출력은 `{"team": "IT지원팀"}`, 두 번째는 `IT지원팀`입니다. 입력을 `출장`으로 바꾸면 첫 출력의 team은 `null`, 두 번째는 `None`입니다. 이 차이를 설명하기 어렵다면 설치 후 새 Python 파일에 위 예제를 실행하고 한 줄씩 비교합니다. LangChain·LangGraph 경험이나 Git 숙련은 이 확인의 조건이 아닙니다.

</details>

### 1. 이번 수업 자료를 받습니다

**2026.09-rc1 실습 자료**를 [ZIP으로 받습니다](../downloads/agent-workshop-2026.09-rc1.zip). 압축을 풀면 workshop 폴더가 나옵니다. 교재 웹페이지를 여는 것만으로 실습 코드가 설치되지는 않습니다. 다른 버전의 파일을 섞지 않습니다. Git을 사용하는 경우 [Git으로 받기](../git-setup)의 별도 안내를 따릅니다.

```text
workshop/                   ← 압축을 푼 자료와 명령 실행 위치
├── pyproject.toml          ← 라이브러리 목록
├── uv.lock                 ← 검증한 의존성 버전
├── setup.sh                ← uv·Python·Jupyter 설치와 키 설정
├── configure_access.py     ← 공유 파일의 키·모델 저장
├── .env.example            ← 설정 형식 참고
├── RELEASE.md              ← 자료 버전과 시작 안내
├── MANIFEST.json           ← 파일별 무결성 정보
├── notebooks/              ← 환경 확인·주 실습·개념 예제·풀이
├── build_lab/              ← 노트북이 사용하는 제공 구조·참고 구현
├── labs/                   ← 교재에 임베드하는 개념 코드
├── course/                 ← 비교 시연용 완성 예제
├── exercises/              ← 개발용 회귀 검사에 사용한 기존 예제
├── tests/                  ← 단계별 검사
└── skills/                 ← Agent가 읽는 업무 지침
```

압축을 푼 뒤 `workshop/notebooks/build-agent.ipynb`가 있는지 확인합니다. `setup.sh`도 함께 있어야 합니다. 파일이 없다면 위 ZIP을 다시 받아 다른 폴더에 압축을 풉니다.

### 2. Windows에서는 Ubuntu 터미널을 엽니다

아래 두 명령은 **Windows PowerShell**에서 실행합니다. 첫 명령으로 설치된 배포판을 확인한 뒤, 목록에 `Ubuntu-24.04`가 있으면 두 번째 명령으로 들어갑니다.

```powershell
wsl --list --verbose
wsl -d Ubuntu-24.04
```

Ubuntu에 들어온 뒤에는 아래 절의 `bash` 명령을 그 터미널에서 실행합니다. PowerShell 창과 Ubuntu 창에 같은 명령을 번갈아 입력하지 않습니다. 이 교재의 실행 검증 환경은 WSL2의 Ubuntu 24.04입니다.

<details><summary>Ubuntu가 아직 없다면: 설치 방법</summary>

관리자 PowerShell에서 다음 명령을 실행합니다. 재시작 안내가 나오면 Windows를 재시작하고 Ubuntu의 사용자 이름과 비밀번호를 만듭니다.

```powershell
wsl --install -d Ubuntu-24.04
```

회사 PC에서 설치가 제한되면 담당자가 승인한 실습 환경을 준비합니다. 설치 권한이나 재부팅 문제로 진행이 막히면 강사에게 알려 사용할 수 있는 실습 환경을 함께 확인합니다. 자세한 절차는 [Microsoft WSL 설치 안내](https://learn.microsoft.com/en-us/windows/wsl/install)를 참고합니다.

</details>

macOS·Linux는 WSL 진입 단계가 없습니다. 자신의 터미널에서 이어갈 수 있으나, 설치·실행 안내의 기준 환경은 위 WSL 구성입니다.

### 3. 같은 폴더를 편집기와 터미널에서 엽니다

Windows에서 받은 자료는 파일 탐색기의 주소 표시줄에 `\\wsl.localhost\Ubuntu-24.04\home`을 입력하고 자신의 Ubuntu 사용자 폴더 안으로 복사할 수 있습니다. 그 안에 `lecture` 폴더를 새로 만들고, 압축을 풀어 얻은 **workshop 폴더 전체**를 넣습니다. 결과는 `자신의 사용자 폴더/lecture/workshop/pyproject.toml` 형태입니다. 이미 사용 중인 동명 폴더를 덮어쓰지 않습니다.

**Ubuntu 터미널**에서 다음 명령을 실행합니다. `cd`는 폴더 이동, `pwd`는 현재 위치 확인, `ls`는 파일 목록 확인입니다.

```bash
cd ~/lecture/workshop
pwd
ls pyproject.toml uv.lock course exercises skills
code .
```

`code .`은 현재 폴더를 VS Code로 엽니다. 왼쪽 아래에 `WSL: Ubuntu-24.04`와 같은 표시가 있는지 확인합니다. VS Code의 **터미널 → 새 터미널**을 열고 `pwd`를 실행했을 때도 끝이 `/lecture/workshop`이어야 합니다.

`code`를 찾지 못하면 Windows에 VS Code와 WSL 확장을 설치한 뒤 Ubuntu 터미널을 다시 엽니다. 편집기를 통해 WSL 폴더를 여는 절차는 [VS Code WSL 안내](https://code.visualstudio.com/docs/remote/wsl)를 참고합니다.

### 4. 설치 스크립트를 실행합니다

Ubuntu 터미널에서 `workshop` 폴더로 이동한 뒤 실행합니다.

```bash
bash setup.sh
```

스크립트는 uv가 없으면 설치하고 Python 3.12와 수업에 필요한 Jupyter·라이브러리를 준비합니다. 교재는 웹에서 읽으므로 Node.js는 설치하지 않습니다. 다운로드에 실패하면 오류가 표시된 단계에서 멈춥니다. 문제를 해결한 뒤 같은 명령을 다시 실행합니다.

`curl`이 없다는 안내가 나오면 Ubuntu에서 아래 명령을 실행한 뒤 `bash setup.sh`를 다시 실행합니다.

```bash
sudo apt-get update
sudo apt-get install -y curl ca-certificates
```

### 5. 강사가 공유한 키 파일을 지정합니다

강사가 수업 시작 전에 안내한 <strong>공유폴더의 <code>workshop-access.txt</code></strong>를 내려받습니다. 설치 중 ‘키 파일 경로’를 물으면 내려받은 파일의 Ubuntu 경로를 입력합니다. 예를 들어 Windows 다운로드 폴더는 `/mnt/c/Users/자신의사용자명/Downloads/workshop-access.txt`로 접근합니다.

설정 프로그램이 키와 모델을 `.env`에 저장하므로 `.env.example`을 복사하거나 노트북에 키를 붙여 넣지 않습니다. 개인 키를 쓴다면 파일 경로에서 Enter를 누른 뒤 키를 입력합니다. 키는 화면에 표시되지 않습니다. 기존 설정이 있으면 유지 여부와 현재 모델을 확인합니다. 예전 모델이 남아 있다면 `n`을 입력하고 새 공유 파일을 지정합니다.

수업 기본 모델은 **google/gemini-3.8-flash**입니다. 공유 파일에 모델 ID가 있으면 그 값을 사용합니다. 설치 완료 메시지에서 모델을 확인하고, 다음 <mark class="key-point">노트북 셀에서 실제 연결을 확인합니다.</mark>

<details><summary>강사 준비 · 키 파일 배포</summary>

수강생만 접근할 수 있는 공유폴더를 만들고, 수업 전에 링크와 파일명을 전달합니다. 다음 두 항목을 담은 `workshop-access.txt`를 올립니다. 아래 빈 키 항목에는 발급한 실제 키를 넣습니다.

```dotenv
OPENROUTER_API_KEY=
WORKSHOP_MODEL=google/gemini-3.8-flash
```

배포 전에 이 파일로 설치와 첫 호출을 확인합니다. 키의 사용 한도·모델 접근·유효 기간이 수업을 감당하는지도 확인합니다. 키 파일은 공개 교재·Git·실습 ZIP에 넣지 않습니다. 실제 공유폴더 주소와 키 발급은 강사가 준비합니다.

</details>

### 6. JupyterLab을 열고 환경을 확인합니다

workshop 폴더에서 한 번 실행합니다. 이 명령은 노트북 화면을 여는 준비 단계입니다. 이후 실습은 셀에서 실행합니다.

```bash
.venv/bin/jupyter lab notebooks/orientation.ipynb
```

터미널에 표시된 로컬 주소를 열고 Python 3 커널을 선택합니다. 터미널은 열어 둡니다. **환경 확인** 셀을 Shift+Enter로 실행하여 Python 경로와 라이브러리를 확인합니다.

### 7. 노트북에서 모델과 도구를 호출합니다

`orientation.ipynb`의 **모델과 도구 호출** 셀을 실행합니다. 이 셀은 .env의 키로 실제 모델을 호출합니다. 메시지에서 lookup_policy 요청, P-01·재무지원팀이 담긴 도구 결과, 마지막 답변을 확인합니다. 문장이 예시와 같을 필요는 없습니다. API 오류가 나면 아래 복구 안내를 확인하고 다시 실행합니다.

이 노트북은 입문에서 완성 예제를 관찰하는 용도입니다. LangChain 장부터는 왼쪽 파일 탐색기에서 `build-agent.ipynb`를 열어 직접 함수를 작성합니다. 개념 예제를 따로 실행할 때는 `concepts.ipynb`를 사용합니다. 함수 정의를 고쳤다면 정의 셀과 연결·실행 셀을 다시 실행합니다. 커널을 재시작했다면 해당 단계까지 순서대로 실행합니다.

### 준비 완료 체크

<div class="setup-checklist" role="group" aria-label="준비 완료 체크">
<label><input type="checkbox"><span><code>workshop</code> 폴더가 있고, 편집기에서 <code>notebooks/build-agent.ipynb</code>를 열고 첫 셀을 실행할 수 있습니다.</span></label>
<label><input type="checkbox"><span>편집기 터미널의 현재 위치가 <code>workshop</code>이며 Python과 라이브러리 확인이 성공합니다.</span></label>
<label><input type="checkbox"><span><code>.env</code>를 저장했고 실제 모델 호출이 성공합니다.</span></label>
<label><input type="checkbox"><span><code>orientation.ipynb</code> 셀 아래에서 도구 요청·결과와 정산 문의 답변을 확인했습니다.</span></label>
</div>

수업 당일에는 이 상태를 확인하고 오늘의 흐름을 안내합니다. 환경이 준비되지 않았다면 어느 단계에서 막혔는지와 오류 메시지를 전달합니다. 키 값은 공유하지 않습니다.


</section>

<section class="slide" id="connection">

## 실제 모델로 실습합니다

<p class="section-time">예상 2분 · 09:37–09:39</p>

노트북의 모델 호출 셀은 실제 LLM에 연결합니다. 실제 모델이므로 답변 표현이나 도구 호출 횟수는 실행마다 달라질 수 있습니다.

앞의 준비 단계에서 설정한 키를 사용합니다. `WORKSHOP_MODEL`로 모델을 바꿀 수 있으며, 제공 키의 사용 가능 여부는 수업 전에 확인합니다.

<details><summary>모델 호출이 실패할 때: 원인 확인과 복구</summary>

LLM 호출 성공까지가 실습 준비입니다. 오류 코드와 메시지를 확인하고 원인을 해결한 뒤 같은 노트북 셀을 다시 실행합니다. 키 값은 공유하지 않습니다.

| 증상 | 확인할 것 | 복구 방법 |
|---|---|---|
|키 누락·인증 오류|현재 작업 폴더의 `.env`, 키의 유효 상태|유효한 실습용 키를 설정하고 다시 실행|
|잔액·호출 한도 오류|계정 잔액과 사용 한도, 응답의 재시도 안내|담당자에게 한도 조정을 요청하거나 사용 가능한 실습 계정으로 변경|
|모델 사용 불가|`WORKSHOP_MODEL`의 모델 ID와 계정의 접근 가능 여부|담당자가 확인한 도구 호출 지원 모델로 변경하고 재실행|
|연결 실패·시간 초과|사내 프록시·방화벽·네트워크 상태|허용된 네트워크 또는 준비된 실행 환경에서 연결 확인|

복구 확인에는 실제 모델의 도구 요청, 도구 반환값, 최종 답변이 포함됩니다. 개인 과제의 코드 검사는 별도로 실행할 수 있지만 실제 모델 실행은 복구 후 완료합니다.

</details>

</section>

<section class="slide" id="practice">

## 환경 준비가 끝났습니다

<p class="section-time">예상 1분 · 09:39–09:40</p>

다음 장에서는 방금 실행한 예제를 보며 Agent가 모델과 도구를 어떻게 사용하는지 알아봅니다. `orientation.ipynb`의 셀 출력을 그때 다시 읽습니다. 지금은 프로그램을 수정하거나 미완성 함수를 검사하지 않아도 됩니다.

[다음: Agent는 어떻게 실행되는가](./agent)

</section>

<nav class="chapnav"><a href="../toc">전체 목차</a></nav>
</div></div>
