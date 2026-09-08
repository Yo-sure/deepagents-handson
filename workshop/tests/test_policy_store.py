"""제공 데이터 함수의 파일 경로·조회 계약을 확인합니다."""

import json
from course import policy_store


def test_csv_changes_are_visible_and_missing_topic_is_preserved(tmp_path, monkeypatch):
    data = tmp_path / "policies.csv"
    data.write_text(
        "topic,id,team,rule\n휴가,P-03,인사지원팀,휴가 문의를 받습니다.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(policy_store, "DATA_FILE", data)
    monkeypatch.chdir(tmp_path)
    result = json.loads(policy_store.search_policy(" 휴가 "))
    assert result["policy"]["team"] == "인사지원팀"
    assert result["topic"] == "휴가"
    assert json.loads(policy_store.search_policy(" 없는업무 ")) == {
        "found": False,
        "topic": "없는업무",
        "policy": None,
    }
    data.write_text(
        "topic,id,team,rule\n휴가,P-03,휴가지원팀,담당 팀 변경\n", encoding="utf-8"
    )
    assert (
        json.loads(policy_store.search_policy("휴가"))["policy"]["team"] == "휴가지원팀"
    )
