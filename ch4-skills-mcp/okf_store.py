"""Ch4 산출물 — 조사 결과를 OKF 지식 항목으로 적재한다.

Ch3의 노트는 이번 인박스에만 쓰는 메모다. 다음 달에도 다시 쓰려면 표준 형식으로
쌓아 둬야 한다. OKF(Open Knowledge Format v0.1)는 마크다운 본문 + YAML 프런트매터
구조이고 `type` 필드가 필수다. 사람도 읽고 에이전트도 파싱한다.

여기서는 분류 레코드에서 세 종류의 지식을 뽑아 knowledge_base/ 에 적재한다.
  - merchant     : 거래처별 누적(이번 달 합계·문서유형)
  - subscription : 영수증 없이 반복되는 소액 결제(구독 추정)
  - gap          : 명세서엔 있으나 영수증이 없는 건(확인 필요)

실행:
    uv run python3 ch4-skills-mcp/okf_store.py
출력: workspace/knowledge_base/*.md  (OKF 항목)
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyst import RecordV1
from analyst.paths import KNOWLEDGE_BASE, ensure_workspace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ch3-deepagents"))
from research_orchestrator import by_type, load_records

OKF_VERSION = "okf/0.1"


# #region okf-entry
def okf_entry(type_: str, name: str, body_lines: list[str], **meta) -> str:
    """OKF 항목 한 개를 직렬화한다 — YAML 프런트매터(type 필수) + 마크다운 본문."""
    # 값에 콜론·# 같은 YAML 메타문자가 와도 안전하게 직렬화한다 — 상호명·품목명은
    # 모델이 뽑은 자유 텍스트라("강남R: 1호점" 등) 손조립하면 파싱이 깨진다.
    front_data = {"type": type_, "name": name, "schema_version": OKF_VERSION, **meta}
    front = yaml.safe_dump(front_data, allow_unicode=True, sort_keys=False).strip()
    body = "\n".join(body_lines)
    return f"---\n{front}\n---\n\n# {name}\n\n{body}\n"
# #endregion okf-entry


def slug(name: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in name).strip("-").lower()


def build_merchant_entries(records: list[RecordV1]) -> dict[str, str]:
    """거래처별 누적 지식."""
    agg: dict[str, list[RecordV1]] = defaultdict(list)
    for r in records:
        agg[r.merchant].append(r)
    out = {}
    for merchant, recs in agg.items():
        total = sum(r.total for r in recs)
        types = sorted({r.doc_type for r in recs})
        lines = [
            f"- 2026-05 합계: {total:,.0f}원",
            f"- 문서유형: {', '.join(types)}",
            f"- 건수: {len(recs)}",
        ]
        out[f"merchant-{slug(merchant)}"] = okf_entry(
            "merchant", merchant, lines, total=int(total)
        )
    return out


def build_finding_entries(records: list[RecordV1]) -> dict[str, str]:
    """카드 명세서 ↔ 영수증 대사에서 나오는 구독·확인필요 지식."""
    receipts = by_type(records, "영수증")
    card = next((r for r in by_type(records, "명세서") if "카드" in r.merchant), None)
    out: dict[str, str] = {}
    if not card:
        return out
    for item in card.items:
        amt = item.amount or 0
        if any(abs(r.total - amt) < 1.0 for r in receipts):
            continue  # 영수증 있음 — 지식거리 아님
        if amt < 30000:
            out[f"subscription-{slug(item.name)}"] = okf_entry(
                "subscription", item.name,
                [f"- 월 {amt:,.0f}원 반복 결제(영수증 없음) — 구독 추정",
                 "- 카드 명세서에만 등장"],
                amount=int(amt))
        else:
            out[f"gap-{slug(item.name)}"] = okf_entry(
                "gap", item.name,
                [f"- 카드 명세서 {amt:,.0f}원 — 대응 영수증 없음",
                 "- 확인 필요: 영수증 분실 또는 미수령"],
                amount=int(amt))
    return out


def main() -> None:
    records = load_records()
    ensure_workspace()
    entries = {**build_merchant_entries(records), **build_finding_entries(records)}
    for name, text in entries.items():
        (KNOWLEDGE_BASE / f"{name}.md").write_text(text, encoding="utf-8")
    print(f"▶ OKF 항목 {len(entries)}개 적재 → {KNOWLEDGE_BASE}")
    for name in sorted(entries):
        kind = name.split("-")[0]
        print(f"  [{kind:12}] {name}.md")


if __name__ == "__main__":
    main()
