from typing import Literal
from pydantic import BaseModel, Field, ValidationError
from langchain.tools import tool

class TeamInput(BaseModel):
    topic: Literal["정산", "계정"] = Field(description="담당 팀을 찾을 업무명")

@tool(
    "lookup_team",
    description="정산 또는 계정 업무의 담당 팀을 찾습니다. 다른 업무는 지원하지 않습니다.",
    args_schema=TeamInput,
)
def find_team(topic: str) -> str:
    return {"정산": "재무지원팀", "계정": "IT지원팀"}[topic]

print(find_team.name)         # lookup_team
print(find_team.description)
print(find_team.args)
print(find_team.invoke({"topic": "정산"}))  # 재무지원팀

try:
    print(find_team.invoke({"topic": "휴가"}))
except ValidationError:
    print("입력 오류: 정산 또는 계정만 조회할 수 있습니다.")
