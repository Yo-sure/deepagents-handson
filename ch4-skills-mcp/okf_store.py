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

import os
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyst import RecordV1
from analyst.paths import KNOWLEDGE_BASE, ensure_workspace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ch3-deepagents"))
from research_orchestrator import by_type, load_records

OKF_VERSION = "0.1"
SAMPLE_TIMESTAMP = "2026-05-31T00:00:00Z"
SUBSCRIPTION_LIMIT = int(os.getenv("ACDC_SUBSCRIPTION_LIMIT", "30000"))


#pragma region okf-entry
def okf_entry(
    type_: str,
    title: str,
    body_lines: list[str],
    *,
    description: str,
    tags: list[str],
    **meta,
) -> str:
    """OKF concept 하나를 직렬화한다 — YAML frontmatter + Markdown body."""
    # 값에 콜론·# 같은 YAML 메타문자가 와도 안전하게 직렬화한다 — 상호명·품목명은
    # 모델이 뽑은 자유 텍스트라("강남R: 1호점" 등) 손조립하면 파싱이 깨진다.
    front_data = {
        "type": type_,
        "title": title,
        "description": description,
        "tags": tags,
        "timestamp": SAMPLE_TIMESTAMP,
        # name은 기존 실습 코드 호환용 확장 필드다. 표준 표시명은 title을 쓴다.
        "name": title,
        **meta,
    }
    front = yaml.safe_dump(front_data, allow_unicode=True, sort_keys=False).strip()
    body = "\n".join(body_lines)
    return f"---\n{front}\n---\n\n# {title}\n\n{body}\n"
#pragma endregion okf-entry


def okf_index(entries: dict[str, str]) -> str:
    """Bundle root index.md.

    OKF v0.1 keeps ordinary index.md files frontmatter-free, but section 11 permits
    okf_version frontmatter only on the bundle-root index.md.
    """
    grouped: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for filename, text in entries.items():
        meta = yaml.safe_load(text.split("---", 2)[1])
        grouped[meta["type"]].append((
            filename,
            meta.get("title", filename),
            meta.get("description", ""),
        ))
    lines = [
        "---",
        f'okf_version: "{OKF_VERSION}"',
        "---",
        "",
        "# 인박스 지식베이스",
        "",
        "Ch4 실습이 생성한 OKF bundle입니다.",
    ]
    for kind in sorted(grouped):
        lines += ["", f"## {kind}"]
        for filename, title, description in sorted(grouped[kind], key=lambda x: x[1]):
            suffix = f" - {description}" if description else ""
            href = filename if filename.endswith(".md") else f"{filename}.md"
            lines.append(f"* [{title}]({href}){suffix}")
    return "\n".join(lines) + "\n"


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
        sources = sorted({r.source_path for r in recs if r.source_path})
        lines = [
            f"- 2026-05 합계: {total:,.0f}원",
            f"- 문서유형: {', '.join(types)}",
            f"- 건수: {len(recs)}",
        ]
        extra = {"total": int(total)}
        if len(sources) == 1:
            extra["resource"] = sources[0]
        out[f"merchant-{slug(merchant)}"] = okf_entry(
            "merchant",
            merchant,
            lines,
            description=f"{merchant}의 2026년 5월 인박스 누적 거래 요약.",
            tags=["inbox", "merchant", "2026-05"],
            **extra,
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
        if amt < SUBSCRIPTION_LIMIT:
            out[f"subscription-{slug(item.name)}"] = okf_entry(
                "subscription", item.name,
                [f"- 월 {amt:,.0f}원 반복 결제(영수증 없음) — 구독 추정",
                 "- 카드 명세서에만 등장"],
                description=f"{item.name} {amt:,.0f}원 결제의 구독 가능성.",
                tags=["inbox", "subscription", "2026-05"],
                resource=card.source_path,
                amount=int(amt))
        else:
            out[f"gap-{slug(item.name)}"] = okf_entry(
                "gap", item.name,
                [f"- 카드 명세서 {amt:,.0f}원 — 대응 영수증 없음",
                 "- 확인 필요: 영수증 분실 또는 미수령"],
                description=f"{item.name} {amt:,.0f}원 결제의 대응 영수증 누락.",
                tags=["inbox", "gap", "2026-05"],
                resource=card.source_path,
                amount=int(amt))
    return out


def validate_okf_bundle(entries: dict[str, str], index_text: str) -> None:
    """OKF v0.1 teaching minimum: item frontmatter, required type, root-index version exception."""
    if "okf_version:" not in index_text.split("---", 2)[1]:
        raise RuntimeError("OKF 루트 index.md에 okf_version이 없습니다.")
    for name, text in entries.items():
        if not text.startswith("---"):
            raise RuntimeError(f"{name}.md: YAML frontmatter가 없습니다.")
        try:
            meta = yaml.safe_load(text.split("---", 2)[1]) or {}
        except yaml.YAMLError as exc:
            raise RuntimeError(f"{name}.md: YAML frontmatter 파싱 실패: {exc}") from exc
        if not meta.get("type"):
            raise RuntimeError(f"{name}.md: OKF 필수 필드 type이 없습니다.")


def main() -> None:
    records = load_records()
    ensure_workspace()
    entries = {**build_merchant_entries(records), **build_finding_entries(records)}
    index_text = okf_index(entries)
    validate_okf_bundle(entries, index_text)
    for name, text in entries.items():
        (KNOWLEDGE_BASE / f"{name}.md").write_text(text, encoding="utf-8")
    (KNOWLEDGE_BASE / "index.md").write_text(index_text, encoding="utf-8")
    print(f"▶ OKF 항목 {len(entries)}개 적재 → {KNOWLEDGE_BASE}")
    for name in sorted(entries):
        kind = name.split("-")[0]
        print(f"  [{kind:12}] {name}.md")


if __name__ == "__main__":
    main()
