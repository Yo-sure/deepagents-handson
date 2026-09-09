# 원본: notebooks/orientation.ipynb


## 셀 1 · ID 92c780a0

# 시작 안내 · 환경과 첫 모델 호출

환경 확인은 모델 호출이 없습니다. 다음 셀은 실제 모델 API를 호출합니다. 입문에서는 질문과 메시지를 관찰하고, 직접 구현은 build-agent.ipynb에서 진행합니다.

## 셀 2 · ID 2ff5dece

```python
from pathlib import Path
import os, sys

root = Path.cwd()
if root.name == "notebooks":
    root = root.parent
if not (root / "build_lab" / "materials.py").is_file():
    raise RuntimeError("workshop/notebooks에서 이 노트북을 여십시오.")
os.chdir(root)
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
print("실행 위치:", root)

import importlib

print("Python:", sys.version.split()[0])
print("실행 경로:", sys.executable)
for name in ["langchain", "langgraph", "deepagents", "mcp", "a2a"]:
    importlib.import_module(name)
print("라이브러리 준비 완료")
from course.common import get_model
```

## 셀 3 · ID 212d3bc7

## 모델과 도구 호출

질문을 바꾸고 셀을 다시 실행합니다. 정산은 P-01·재무지원팀, 계정은 P-02·IT지원팀입니다. 없는 업무는 추가 확인을 요청해야 합니다. 도구 요청과 결과를 모두 확인합니다.

## 셀 4 · ID 2219f160

```python
from langchain.agents import create_agent
from course.common import lookup_policy

model = get_model()
agent = create_agent(
    model=model,
    tools=[lookup_policy],
    system_prompt="업무 문의는 lookup_policy로 확인하고 담당 팀과 근거 ID를 답하세요. 규정이 없으면 추가 확인을 요청하세요.",
)
question = "정산은 어느 팀에 문의하나요?"
result = agent.invoke({"messages": [{"role": "user", "content": question}]})
for message in result["messages"]:
    message.pretty_print()
```