"""LangChain 1.4 MCPAdapter로 원격 도구를 Agent에 연결합니다."""
import argparse
import asyncio
import json
import tempfile
from pathlib import Path
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from fastmcp import Client
from .common import ROOT, get_model, trace_messages
from .mcp_lab import PROTOCOL
from .processes import server


#pragma region adapter
async def connect_agent(url, topic="정산", mode="fixed"):
    client = Client(url, mode=PROTOCOL)
    async with MCPAdapter(client) as adapter:
        catalog = await adapter.list_tools()
        # 조회 실습에는 티켓 생성 도구를 전달하지 않습니다.
        tools = [tool for tool in catalog if tool.name == "lookup_policy"]
        if len(tools) != 1:
            raise ValueError("정책 조회 도구를 찾지 못했습니다.")
        agent = create_agent(get_model(mode), tools=tools,
            system_prompt="정책을 도구로 조회하고 담당 팀과 근거 ID를 답하십시오. 없으면 추가 확인을 요청하십시오.")
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": json.dumps({"topic": topic}, ensure_ascii=False)}]},
            config={"recursion_limit": 12})
        return {"mode": mode, "tools": [tool.name for tool in tools],
                "trace": trace_messages(result["messages"])}
#pragma endregion adapter


def run(topic="정산", mode="fixed"):
    with tempfile.TemporaryDirectory() as temp:
        with server("course.mcp_lab", "--db", Path(temp) / "tickets.sqlite") as url:
            return asyncio.run(connect_agent(url + "/mcp", topic, mode))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="정산")
    parser.add_argument("--mode", choices=["fixed", "live"], default="fixed")
    args = parser.parse_args()
    result = json.dumps(run(args.topic, args.mode), ensure_ascii=False, indent=2)
    (ROOT / "runs").mkdir(exist_ok=True)
    (ROOT / "runs" / f"mcp-agent-{args.mode}.json").write_text(result, encoding="utf-8")
    print(result)
