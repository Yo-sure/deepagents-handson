"""도구·Agent·분기·MCP 등록·A2A 수용을 구현합니다. 그래프·수정 루프 구조는 제공됩니다. 재료와 계약은 교재 '직접 완성하기'에 있습니다."""
import json
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from mcp.server.mcpserver import MCPServer
from .materials import POLICIES, Inquiry, inspect_draft

#pragma region lookup
def lookup_policy(topic: str) -> str:
    """Look up the current internal policy by topic, such as 정산 or 계정."""
    # 공백을 제거한 topic으로 POLICIES를 조회합니다. JSON 문자열을 반환합니다.
    raise NotImplementedError("1A: found, topic, policy를 반환하는 조회 도구를 구현하십시오.")
#pragma endregion lookup

#pragma region agent
def build_agent(model, policy_tool):
    # model·tools·system_prompt를 지정합니다. 실제 호출은 호출자가 수행합니다.
    raise NotImplementedError("1B: create_agent로 도구를 가진 Agent를 구성하십시오.")
#pragma endregion agent

#pragma region graph
def route_inquiry(state):
    """정책과 회신 대상을 읽고 draft 또는 ask로 분기합니다."""
    # 정책이 있어도 회신 대상이 없으면 생성하면 안 됩니다.
    raise NotImplementedError("2: 정책 유무와 공백 연락처를 검사하는 분기를 구현하십시오.")


def build_workflow(lookup, generate, refine, limit=2):
    """제공 그래프에 학생 분기를 연결합니다. guided.py의 노드·간선을 읽습니다."""
    from .guided import build_workflow as assemble
    return assemble(lookup, generate, refine, limit, router=route_inquiry)
#pragma endregion graph

#pragma region loop
def refine_answer(draft, data, revise, limit=2):
    """제공 루프를 사용합니다. 전체 알고리즘 작성은 선택 심화입니다."""
    from .guided import refine_answer as refine
    return refine(draft, data, revise, limit)
#pragma endregion loop

#pragma region mcp
def build_mcp_server(policy_tool):
    raise NotImplementedError("4: MCPServer를 만들고 policy_tool을 도구로 등록하십시오.")
#pragma endregion mcp

#pragma region a2a
def accept_review(state, artifact, request_id, version):
    raise NotImplementedError("5: 작업 상태·요청 ID·버전·passed를 확인해 수용 여부를 반환하십시오.")
#pragma endregion a2a
