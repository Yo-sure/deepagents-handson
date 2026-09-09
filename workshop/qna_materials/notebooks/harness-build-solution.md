# 원본: notebooks/harness-build-solution.ipynb


## 셀 1 · ID h-intro

# DeepAgents Harness를 직접 구성하고 실행합니다

4장 주 실습입니다. 이 파일의 H1 → H2 → H3 순서로 진행합니다. API 키는 setup.sh가 준비한 workshop/.env에서 읽습니다. 모델을 실제 호출하며 별도의 앞 장 커널은 필요하지 않습니다.

**만들 결과:** 자신이 작성한 Skill을 읽고 정책 도구로 조회하는 DeepAgents Agent. 학습자가 backend·skills·tools·system_prompt와 요청을 직접 연결합니다. 모델과 도구를 새로 개발하는 작업이 아니라, DeepAgents가 제공하는 Harness를 구성하는 작업입니다.

막히면 같은 폴더의 `harness-build-solution.ipynb`에서 같은 H 번호를 찾습니다. 풀이 코드 아래의 결과 해석까지 비교합니다. 함수를 수정하면 정의 셀과 실행 셀을 다시 실행합니다.

## 셀 2 · ID h-env

```python
from pathlib import Path
import os, sys

root = Path.cwd()
if root.name == "notebooks":
    root = root.parent
if not (root / "course" / "common.py").is_file():
    raise RuntimeError("workshop/notebooks에서 이 노트북을 여십시오.")
os.chdir(root)
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from course.common import get_model, lookup_policy
print("실습 위치:", root)
```

## 셀 3 · ID h1-guide

## H1. Skill 작성 · 7분

아래 `skill_body`의 빈 문자열에 작업 절차를 작성합니다. 정책 조회 도구의 이름은 `lookup_policy`입니다. ① 언제 정책을 조회할지 ② 팀과 근거를 어떻게 답할지 ③ 정책이 없을 때 무엇을 물을지 ④ 완료 전에 무엇을 대조할지를 포함합니다.

파일 저장 코드는 제공됩니다. 기존 수업 Skill과 겹치지 않게 `workspace/harness-practice/skills/my-policy/SKILL.md`에 저장합니다. description은 기본으로 읽히는 사용 조건이고, 본문은 Agent가 필요할 때 읽을 절차입니다. 자신의 질문이 description의 사용 조건에 맞는지도 확인합니다.

## 셀 4 · ID h1-skill

```python
skill_body = '1. 문의의 업무명을 확인하고 lookup_policy로 정책을 조회한다.\n2. found가 참이면 실제 policy의 team과 id를 근거로 답한다.\n3. found가 거짓이면 담당 팀을 만들지 않는다. 어떤 업무인지 구체적으로 다시 질문한다.\n4. 답변 전에 정책 ID와 담당 팀이 조회 결과와 일치하는지 대조한다.\n'

workspace = root / "workspace" / "harness-practice"
skill_path = workspace / "skills" / "my-policy" / "SKILL.md"
if not skill_body.strip():
    raise NotImplementedError("H1: 정책 조회·응답·예외·완료 기준을 Skill 본문으로 작성하십시오.")
skill_path.parent.mkdir(parents=True, exist_ok=True)
skill_path.write_text(
    "---\nname: my-policy\ndescription: 사내 업무의 담당 팀과 정책 근거를 확인하는 문의에 사용합니다.\n---\n\n"
    + skill_body, encoding="utf-8",
)
print("저장한 Skill:", skill_path.relative_to(root))
print(skill_path.read_text(encoding="utf-8"))
```

## 셀 5 · ID h2-guide

## H2. Harness 생성과 호출 작성 · 10분

`build_harness`와 `run_harness`를 직접 작성합니다.

|인자/구성|연결할 값과 이유|
|---|---|
|backend|`FilesystemBackend(root_dir=str(workspace), virtual_mode=True)` — 이 실습 파일 경로의 기준|
|skills|`["/skills/"]` — backend 기준의 가상 경로. Windows 경로가 아님|
|tools|인자로 받은 정책 도구를 목록으로 전달|
|model|인자로 받은 실제 모델|
|system_prompt|관련 Skill을 읽어 작업하고 정책 도구를 사용하도록 작성. 파일 수정은 요청하지 않음|
|invoke 입력|`{"messages": [{"role": "user", "content": question}]}`|

`create_deep_agent`로 만든 Agent를 반환합니다. 실행 함수는 `invoke`의 전체 결과를 반환합니다. 실행 한도는 `config={"recursion_limit": 20}`으로 둡니다. 이 한도는 API 호출 횟수·금액 예산과 같지 않습니다. virtual_mode도 OS 프로세스 격리나 모든 도구의 권한 제어를 대신하지 않습니다.

## 셀 6 · ID h2-build

```python
def build_harness(model, policy_tool, workspace):
    backend = FilesystemBackend(root_dir=str(workspace), virtual_mode=True)
    return create_deep_agent(
        model=model,
        tools=[policy_tool],
        backend=backend,
        skills=["/skills/"],
        system_prompt=(
            "사내 문의를 처리합니다. 관련 Skill 문서를 먼저 읽고 그 절차에 따라 "
            "lookup_policy로 조회하십시오. 파일은 수정하지 마십시오."
        ),
    )

def run_harness(agent, question):
    return agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"recursion_limit": 20},
    )
```

## 셀 7 · ID h2-run

```python
harness = build_harness(get_model(), lookup_policy, workspace)
question = "계정이 잠겼습니다. 담당 팀과 정책 근거를 알려 주세요."
harness_result = run_harness(harness, question)
for message in harness_result["messages"]:
    message.pretty_print()

# 요청·결과의 실제 기록입니다. read_file 요청만 있고 실행이 실패했을 수도 있습니다.
read_calls = [call for m in harness_result["messages"]
              for call in getattr(m, "tool_calls", []) if call["name"] == "read_file"]
print("Skill 읽기 요청:", read_calls)
print("마지막 답변:", harness_result["messages"][-1].content)
```

## 셀 8 · ID h3-guide

## H3. 자신의 지침과 출력 비교 · 13분

정상 입력을 확인한 뒤 `question`을 “없는업무 담당 팀과 근거를 알려 주세요”로 바꿉니다. 실행 셀은 매번 새 Harness와 새 대화로 시작합니다. 모델의 요청 순서, read_file에 대응하는 ToolMessage, 정책 조회 결과와 최종 답변을 기록합니다.

이어서 H1의 본문에서 정책이 없을 때 묻는 방식을 **“업무명과 발생한 상황을 각각 질문한다”**로 구체화합니다. H1 저장 셀 → H2 실행 셀 순서로 다시 실행하고 동일 질문의 결과를 비교합니다. 코드의 문자열을 수정하지 않고 파일 편집기만 썼다면 H1 셀을 재실행하지 않습니다. 문자열이 파일을 다시 덮어쓰기 때문입니다.

**완료 기준:** 직접 작성한 두 함수로 DeepAgents가 실행되고, 자신이 저장한 Skill의 read_file 요청·성공 결과가 있으며, 정책 결과에 근거한 답변 또는 추가 질문이 나옵니다. 좋은 답변만으로 Skill을 읽었다고 판단하지 않습니다. 실패하면 경로·도구 설명·Skill 내용 중 첫 번째 어긋난 부분을 고쳐 재실행합니다.

**고급 확장:** Skill의 사용 조건과 본문 지시를 각각 바꿔 어느 변경이 읽기 선택과 최종 답변에 영향을 주는지 비교합니다. 파일을 안 읽었는데도 정상 답변이 나왔다면, 그 실행에서 Skill 효과를 주장할 수 있는지 설명합니다. 파일 내용과 문서 읽기 기록을 함께 남깁니다.

## 셀 9 · ID h-reading

## H1~H3 풀이 · 실행에서 무엇을 확인했나요?

|출력|의미|아직 증명하지 못한 것|
|---|---|---|
|저장한 Skill 경로와 본문|학습자가 쓴 문서가 디스크에 있음|Agent가 읽었다는 증거는 아님|
|read_file 요청의 file_path가 /skills/my-policy/SKILL.md|모델이 그 문서를 선택함|읽기 성공은 다음 ToolMessage에서 확인|
|같은 tool_call_id의 ToolMessage에 자신의 본문|이번 실행에서 실제 문서 내용을 받음|모든 지시를 지켰다는 뜻은 아님|
|lookup_policy 결과의 P-02·IT지원팀과 최종 답변|조회와 응답이 일치함|실제 이메일 발송이나 코드 테스트를 수행한 것은 아님|
|없는업무 조회 뒤 추가 질문|없는 정책을 추측하지 않음|다른 입력에서도 항상 같은 행동을 한다는 보장은 아님|

Skill을 바꿨는데 예전 문장이 보이면 저장 위치와 실행 순서를 확인합니다. read_file 오류이면 가상 경로와 backend root를 대조합니다. 문서는 바뀌었지만 답변이 같을 수도 있습니다. 수정 전후 trace에서 모델이 받은 내용부터 비교합니다.

이 실습은 DeepAgents Harness의 파일·Skill·도구 구성을 직접 실행했습니다. 세션을 넘는 장기 작업 복구나 코딩 Agent의 테스트 강제 실행까지 구현한 것은 아닙니다. 교재의 수정 Loop 및 Harness 설계 메모는 별도의 확장 과제입니다.