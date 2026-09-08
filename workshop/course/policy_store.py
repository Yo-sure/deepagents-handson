"""제공 데이터 접근 함수. CSV 읽기와 결과 직렬화를 담당합니다."""

import csv
import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "policies.csv"


def load_policies():
    with DATA_FILE.open(encoding="utf-8", newline="") as source:
        return {
            row["topic"]: {key: row[key] for key in ("id", "team", "rule")}
            for row in csv.DictReader(source)
        }


def search_policy(topic: str) -> str:
    """업무명으로 CSV를 조회하고 공통 결과 JSON 문자열을 반환합니다."""
    topic = topic.strip()
    policy = load_policies().get(topic)
    return json.dumps(
        {"found": policy is not None, "topic": topic, "policy": policy},
        ensure_ascii=False,
    )
