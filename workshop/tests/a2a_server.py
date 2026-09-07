"""실제 A2A 전송을 사용하되 LLM만 테스트 대역으로 주입하는 서버."""
import argparse
import uvicorn
from course.a2a_lab import create_app
from tests.model_stub import ToolCallingStub

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    uvicorn.run(create_app(args.port, model=ToolCallingStub()),
                host="127.0.0.1", port=args.port, log_level="warning")
