"""모델에 보낼 내용과 프로그램이 사용할 원본을 나눕니다."""

from langchain.tools import tool


@tool(response_format="content_and_artifact")
def lookup_record() -> tuple[str, dict]:
    """정산 담당 팀과 정책 원본을 조회합니다."""
    return "정산 담당은 재무지원팀입니다.", {"id": "P-01", "team": "재무지원팀"}


message = lookup_record.invoke(
    {"name": "lookup_record", "args": {}, "id": "call_1", "type": "tool_call"}
)
print(message.content)
print(message.artifact)
