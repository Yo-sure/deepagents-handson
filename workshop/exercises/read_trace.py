"""저장된 LangChain 기록과 학생 함수의 출력을 나란히 읽습니다."""

import argparse
import json
from pathlib import Path
from .student import answer_from_policy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path", nargs="?", type=Path, default=Path("runs/langchain.json")
    )
    args = parser.parse_args()
    data = json.loads(args.path.read_text(encoding="utf-8"))
    trace = data["langchain"]["trace"]
    for message in trace:
        print(f"\n[{message['role']}]")
        if message.get("tool_calls"):
            print(json.dumps(message["tool_calls"], ensure_ascii=False, indent=2))
        content = message["content"]
        if message["role"] == "tool":
            policy = json.loads(content)
            print(json.dumps(policy, ensure_ascii=False, indent=2))
            print("[학생 함수 출력]", answer_from_policy(policy))
        elif content:
            print(content)


if __name__ == "__main__":
    main()
