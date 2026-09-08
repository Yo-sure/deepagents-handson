"""학생이 등록한 MCP 도구를 실제 HTTP 서버로 실행합니다."""

import argparse
import importlib

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument(
        "--implementation",
        choices=[
            "build_lab.student",
            "build_lab.reference",
            "build_lab.transfer_solution",
        ],
        default="build_lab.student",
    )
    args = parser.parse_args()
    impl = importlib.import_module(args.implementation)
    impl.build_mcp_server(impl.lookup_policy).run(
        transport="streamable-http",
        host="127.0.0.1",
        port=args.port,
        stateless_http=True,
        json_response=True,
    )
