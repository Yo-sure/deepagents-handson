"""Ch3 산출물 — 여러 문서를 나눠 동시에 조사하는 fan-out 오케스트레이터.

Ch2까지 인박스가 classified/*.json 으로 정규화됐다. 이제 그 레코드들을 서로
맞대 본다. 카드 명세서의 거래줄마다 영수증이 있나? 은행 입출금은 계약·세금계산서와
이어지나? 한 사람이 순서대로 보면 느리다. 조사 주제를 나눠 동시에 돌린다.

DeepAgents 하네스가 하는 일
  - write_todos : 무엇을 조사할지 계획을 먼저 세운다.
  - task(서브에이전트) : 주제별로 하위 에이전트에 위임해 fan-out.
  - write_note : 긴 중간 결과를 workspace/research_notes/ 디스크 파일로 저장.
  - 종합 : 노트를 모아 brief_draft.md 로 묶는다.

이 파일은 두 길로 돈다.
  - 기본 : 메인이 task로 세 서브에이전트(card·bank·spend)에 위임해 live fan-out.
  - --mock : 키 없이 결정론적 대사 로직으로 같은 노트·브리프를 만든다(진단/오프라인 보조).

실행:
    uv run python3 ch3-deepagents/research_orchestrator.py
    uv run python3 ch3-deepagents/research_orchestrator.py --mock
출력: workspace/research_notes/*.md, workspace/brief_draft.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyst import RecordV1
from analyst.paths import (
    CLASSIFIED,
    MANIFEST,
    RESEARCH_NOTES,
    WORKSPACE,
    ensure_workspace,
)

MATCH_TOL = 1.0
BRIEF_DRAFT = WORKSPACE / "brief_draft.md"
SAFE_NOTE = re.compile(r"^[a-z0-9_-]{1,64}$")
LIVE_MODEL = "openai:anthropic/claude-haiku-4.5"


# ── 입력: classified 레코드 ───────────────────────────────────────


def load_records(allow_gold: bool = False) -> list[RecordV1]:
    """Ch2가 떨군 classified/*.json 을 읽는다.

    live 기본 경로는 Ch2 산출물을 요구한다. gold 보충은 --mock 진단 경로에서만 허용해
    Ch2→Ch3 계약 실패가 조용히 가려지지 않게 한다.
    """
    files = sorted(CLASSIFIED.glob("*.json")) if CLASSIFIED.exists() else []
    if files:
        validate_sample_classified_complete(files)
        return [RecordV1.model_validate_json(f.read_text(encoding="utf-8")) for f in files]
    if not allow_gold:
        raise RuntimeError(
            "workspace/classified/*.json 이 비어 있습니다. "
            "먼저 `uv run python3 ch2-langgraph-agent/intake_graph.py`를 실행하세요. "
            "키/네트워크 없이 Ch3 구조만 확인하려면 `--mock`을 붙이면 gold 샘플로 보충합니다."
        )
    import yaml

    print("  (classified 비어 있음 — --mock 진단용으로 gold에서 보충)")
    docs = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["docs"]
    return [RecordV1.model_validate({**d["gold"], "신뢰도": 1.0}) for d in docs]


def manifest_docs() -> list[dict]:
    import yaml

    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["docs"]


def sample_classified_stems() -> set[str]:
    return {Path(doc["file"]).stem for doc in manifest_docs()}


def validate_sample_classified_complete(files: list[Path]) -> None:
    """샘플 classified가 일부만 있으면 Ch3 live가 조용히 성공하지 못하게 막는다."""
    expected = sample_classified_stems()
    present = {path.stem for path in files}
    sample_present = present & expected
    if not sample_present:
        return
    missing = expected - present
    if missing:
        raise RuntimeError(
            "workspace/classified/ 에 샘플 JSON이 일부만 있습니다: "
            + ", ".join(sorted(missing))
            + ". 먼저 `uv run python3 ch2-langgraph-agent/intake_graph.py --mock` "
            "또는 live Ch2 전체 실행으로 JSON 10개를 다시 만들세요."
        )


def by_type(records: list[RecordV1], t: str) -> list[RecordV1]:
    return [r for r in records if r.doc_type == t]


# ── 조사 주제(서브에이전트가 하나씩 맡는다) ──────────────────────


#pragma region reconcile-card
def reconcile_card(records: list[RecordV1]) -> str:
    """카드 명세서 거래줄 ↔ 개별 영수증 대사. 영수증 없는 줄을 찾는다."""
    receipts = by_type(records, "영수증")
    card = next((r for r in by_type(records, "명세서") if "카드" in r.merchant), None)
    if not card:
        return "# 카드 대사\n\n카드 명세서를 찾지 못했습니다.\n"
    lines = []
    unmatched = []
    for item in card.items:
        amt = item.amount or 0
        hit = next((r for r in receipts if abs(r.total - amt) < MATCH_TOL), None)
        if hit:
            lines.append(f"- ✅ {item.name} {amt:,.0f}원 ↔ 영수증 「{hit.merchant}」")
        else:
            lines.append(f"- ⚠️ {item.name} {amt:,.0f}원 — 매칭 영수증 없음")
            unmatched.append((item.name, amt))
    note = [f"# 카드 명세서 대사 — {card.merchant} ({card.total:,.0f}원)", ""]
    note += lines
    note.append("")
    note.append("## 확인 필요")
    if unmatched:
        for name, amt in unmatched:
            kind = "구독 추정" if amt < 30000 else "영수증 분실 또는 미수령"
            note.append(f"- {name} {amt:,.0f}원 → {kind}")
    else:
        note.append("- 모든 거래줄에 대응 영수증 있음")
    return "\n".join(note) + "\n"
#pragma endregion reconcile-card


def reconcile_bank(records: list[RecordV1]) -> str:
    """은행 입출금 ↔ 계약·세금계산서·카드 대사."""
    bank = next((r for r in by_type(records, "명세서") if "뱅크" in r.merchant or "은행" in r.merchant), None)
    others = [r for r in records if r is not bank]
    if not bank:
        return "# 은행 대사\n\n은행 명세서를 찾지 못했습니다.\n"
    note = [f"# 은행 입출금 대사 — {bank.merchant}", ""]
    for item in bank.items:
        amt = abs(item.amount or 0)
        hit = next((r for r in others if abs(r.total - amt) < MATCH_TOL), None)
        sign = "입금" if (item.amount or 0) > 0 else "출금"
        if hit:
            note.append(f"- ✅ {item.name} {item.amount:,.0f}원({sign}) ↔ 「{hit.merchant}」 {hit.doc_type}")
        else:
            note.append(f"- ⚠️ {item.name} {item.amount:,.0f}원({sign}) — 대응 문서 없음")
    return "\n".join(note) + "\n"


def summarize_spend(records: list[RecordV1]) -> str:
    """영수증 지출을 카테고리로 모은다."""
    cat = {"식비": ["국밥", "스타벅스", "GS25"], "교통": ["택시", "카카오T"], "생활": ["올리브영"]}
    receipts = by_type(records, "영수증")
    note = ["# 지출 요약 — 영수증 기준", ""]
    total = sum(r.total for r in receipts)
    for c, keys in cat.items():
        s = sum(r.total for r in receipts if any(k in r.merchant for k in keys))
        if s:
            note.append(f"- {c}: {s:,.0f}원")
    note.append("")
    note.append(f"영수증 합계 {total:,.0f}원 · {len(receipts)}건")
    return "\n".join(note) + "\n"


THREADS = {
    "card_reconcile": reconcile_card,
    "bank_reconcile": reconcile_bank,
    "spend_summary": summarize_spend,
}
EXPECTED_NOTES = tuple(THREADS)
SAMPLE_CHECK_ALIASES = {
    "쿠팡": ("쿠팡",),
    "넷플릭스": ("넷플릭스",),
    "월세": ("월세", "임대료", "임대차"),
}
NEGATIVE_MARKERS = (
    "⚠️", "❌", "없음", "없는", "분실", "미수령", "미확인", "미보유", "미대응",
    "미매칭", "누락", "불일치", "부재", "전무",
)
MIN_NOTE_CHARS = 80


# ── fan-out (mock: 동시 실행) + 종합 ─────────────────────────────


def fan_out_mock(records: list[RecordV1]) -> dict[str, str]:
    """조사 주제를 스레드로 동시에 돌려 노트를 만든다(fan-out 체감)."""
    ensure_workspace()
    print("  [plan] write_todos →", " / ".join(THREADS))

    def run(name_fn):
        name, fn = name_fn
        text = fn(records)
        (RESEARCH_NOTES / f"{name}.md").write_text(text, encoding="utf-8")
        print(f"  [task] {name} → research_notes/{name}.md")
        return name, text

    with ThreadPoolExecutor(max_workers=len(THREADS)) as ex:
        return dict(ex.map(run, THREADS.items()))


def synthesize(notes: dict[str, str], records: list[RecordV1]) -> None:
    """노트를 모아 brief_draft.md 로 종합한다."""
    flags: list[str] = []
    seen: set[str] = set()
    combined_notes = "\n".join(notes.values())
    alias_groups = record_alias_groups(records)
    for stripped in collect_evidence_lines(combined_notes, alias_groups):
        body = evidence_body(stripped)
        # 같은 거래의 상세 설명 줄(→ 영수증 분실...)은 먼저 나온 경고 줄과 합친다.
        key = evidence_key(body, alias_groups)
        if key in seen:
            continue
        seen.add(key)
        flags.append(stripped)
    parts = ["# 인박스 브리프 (초안)", "", f"문서 {len(records)}건을 교차 조사했습니다.", ""]
    parts.append("## 짚어야 할 것")
    parts += (flags or ["- 특이사항 없음"])
    parts += ["", "## 조사 노트", ""]
    for name in notes:
        parts.append(f"- research_notes/{name}.md")
    brief = "\n".join(parts) + "\n"
    if is_sample_record_set(records):
        validate_sample_findings(brief, combined_notes)
    BRIEF_DRAFT.write_text(brief, encoding="utf-8")
    print(f"  [synthesize] → {BRIEF_DRAFT.relative_to(WORKSPACE.parent)}")


def is_sample_record_set(records: list[RecordV1]) -> bool:
    stems = {Path(record.source_path).stem for record in records}
    return stems == sample_classified_stems()


def record_alias_groups(records: list[RecordV1]) -> dict[str, tuple[str, ...]]:
    groups: dict[str, tuple[str, ...]] = {}
    for rec in records:
        for item in rec.items:
            add_alias_group(groups, item.name)
    return groups


def add_alias_group(groups: dict[str, tuple[str, ...]], value: str | None) -> None:
    if not value:
        return
    base = value.strip()
    if len(base) < 2:
        return
    variants = {base, re.sub(r"\(주\)|주식회사|\s+", "", base).strip()}
    variants = {v for v in variants if len(v) >= 2}
    groups.setdefault(base, tuple(sorted(variants, key=len, reverse=True)))


def collect_evidence_lines(text: str, alias_groups: dict[str, tuple[str, ...]]):
    seen_keys: set[str] = set()
    for line in iter_evidence_lines(text, alias_groups):
        key = evidence_key(evidence_body(line), alias_groups)
        seen_keys.add(key)
        yield line
    for key, aliases in alias_groups.items():
        if key in seen_keys:
            continue
        section = evidence_section_line(text, aliases)
        if section:
            yield section


def iter_evidence_lines(text: str, alias_groups: dict[str, tuple[str, ...]]):
    aliases = tuple(alias for group in alias_groups.values() for alias in group)
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if not any(marker in stripped for marker in NEGATIVE_MARKERS):
            continue
        if not any(alias in stripped for alias in aliases):
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith(("- ", "* ")):
            yield stripped
        elif stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            cells = [c for c in cells if c and not re.fullmatch(r"[-:\s]+", c)]
            if cells:
                yield normalize_table_evidence(cells, aliases)
        else:
            yield "- " + stripped


def evidence_body(line: str) -> str:
    body = re.sub(r"^[-*]\s*", "", line)
    body = body.replace("\ufe0f", "")
    body = re.sub(r"^[✅⚠❌]\s*", "", body).strip()
    return body


def normalize_table_evidence(cells: list[str], aliases: tuple[str, ...]) -> str:
    subject = next((cell for cell in cells if any(alias in cell for alias in aliases)), cells[0])
    amount = next((cell for cell in cells if re.search(r"-?\d[\d,]*원", cell)), "")
    status = next((cell for cell in cells if any(marker in cell for marker in NEGATIVE_MARKERS)), "")
    head = " ".join(part for part in (subject, amount) if part)
    return "- " + " — ".join(part for part in (head, status) if part)


def evidence_key(body: str, alias_groups: dict[str, tuple[str, ...]] | None = None) -> str:
    alias_groups = alias_groups or SAMPLE_CHECK_ALIASES
    for label, aliases in alias_groups.items():
        if any(alias in body for alias in aliases):
            return label
    return re.split(r"\s+[—→]\s+", body, maxsplit=1)[0].strip()


def first_evidence_line(text: str, aliases: tuple[str, ...]) -> str | None:
    alias_groups = {"target": aliases}
    for line in iter_evidence_lines(text, alias_groups):
        if any(alias in line for alias in aliases):
            return line
    section = evidence_section_line(text, aliases)
    if section:
        return section
    return None


def evidence_section_line(text: str, aliases: tuple[str, ...]) -> str | None:
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if not any(alias in line for alias in aliases):
            continue
        if not is_section_anchor(line):
            continue
        header = clean_evidence_text(line)
        for nearby in lines[idx + 1: idx + 8]:
            if any(marker in nearby for marker in NEGATIVE_MARKERS):
                detail = clean_evidence_text(nearby)
                if header and detail:
                    return f"- {header} — {detail}"
    return None


def is_section_anchor(line: str) -> bool:
    stripped = line.strip()
    plain = stripped.strip("*_ ")
    return (
        stripped.startswith("#")
        or re.match(r"^\d+[\).]", plain) is not None
        or "항목" in plain
    )


def clean_evidence_text(line: str) -> str:
    text = line.strip().strip("|")
    text = re.sub(r"^#+\s*", "", text)
    text = re.sub(r"^[-*]\s*", "", text)
    text = re.sub(r"^\d+\.\s*", "", text)
    text = text.replace("**", "").replace("__", "")
    return text.strip()


def finding_evidenced(text: str, aliases: tuple[str, ...]) -> bool:
    for alias in aliases:
        start = text.find(alias)
        while start != -1:
            window = text[max(0, start - 160): start + 360]
            if any(marker in window for marker in NEGATIVE_MARKERS):
                return True
            start = text.find(alias, start + len(alias))
    return False


def validate_sample_findings(brief: str, notes: str) -> None:
    missing_from_notes = []
    missing_from_brief = []
    for label, aliases in SAMPLE_CHECK_ALIASES.items():
        if not finding_evidenced(notes, aliases):
            missing_from_notes.append(label)
        elif not finding_evidenced(brief, aliases):
            missing_from_brief.append(label)
    if missing_from_notes:
        raise RuntimeError("브리프 합성에서 기대 확인 항목이 노트에도 없습니다: " + ", ".join(missing_from_notes))
    if missing_from_brief:
        raise RuntimeError("브리프 합성에서 노트의 확인 항목을 브리프로 옮기지 못했습니다: " + ", ".join(missing_from_brief))


def read_expected_notes() -> tuple[dict[str, str], list[str]]:
    notes: dict[str, str] = {}
    missing = []
    for name in EXPECTED_NOTES:
        path = RESEARCH_NOTES / f"{name}.md"
        if not path.exists() or path.stat().st_size == 0:
            missing.append(name)
            continue
        text = path.read_text(encoding="utf-8")
        if len(text.strip()) < MIN_NOTE_CHARS:
            missing.append(f"{name}(내용 검증 실패)")
            continue
        notes[name] = text
    return notes, missing


def clear_expected_notes() -> None:
    ensure_workspace()
    if BRIEF_DRAFT.exists():
        BRIEF_DRAFT.unlink()
    for name in EXPECTED_NOTES:
        path = RESEARCH_NOTES / f"{name}.md"
        if path.exists():
            path.unlink()
    leftovers = [p.name for p in RESEARCH_NOTES.glob("*.md")]
    if leftovers:
        print("  [warn] 이전 추가 노트는 보존됨:", ", ".join(sorted(leftovers)))


def message_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [block.get("text", "") for block in content
                 if isinstance(block, dict) and block.get("type") == "text"]
        return "\n".join(p for p in parts if p).strip()
    return str(content)


def _tool_call_parts(call) -> tuple[str | None, str | None, dict]:
    if isinstance(call, dict):
        name = call.get("name") or call.get("function", {}).get("name")
        args = call.get("args") or {}
        if not args and call.get("function", {}).get("arguments"):
            try:
                args = json.loads(call["function"]["arguments"])
            except json.JSONDecodeError:
                args = {}
        return call.get("id"), name, args
    return getattr(call, "id", None), getattr(call, "name", None), getattr(call, "args", {}) or {}


def task_call_batches(messages) -> list[set[str]]:
    batches = []
    seen = set()
    for msg in messages:
        targets = set()
        calls = list(getattr(msg, "tool_calls", []) or [])
        calls += list(getattr(msg, "additional_kwargs", {}).get("tool_calls", []) or [])
        for call in calls:
            call_id, name, args = _tool_call_parts(call)
            marker = call_id or repr(call)
            if marker in seen:
                continue
            seen.add(marker)
            if name == "task" and args.get("subagent_type"):
                targets.add(args["subagent_type"])
        if targets:
            batches.append(targets)
    return batches


def tool_call_names(messages) -> set[str]:
    names = set()
    seen = set()
    for msg in messages:
        calls = list(getattr(msg, "tool_calls", []) or [])
        calls += list(getattr(msg, "additional_kwargs", {}).get("tool_calls", []) or [])
        for call in calls:
            call_id, name, _args = _tool_call_parts(call)
            marker = call_id or repr(call)
            if marker in seen:
                continue
            seen.add(marker)
            if name:
                names.add(name)
    return names


# 서브에이전트 명세 — create_deep_agent에 그대로 배선되는 하네스 구성(--trace로 열어 본다).
SUBAGENT_SPECS = [
    {
        "name": "card_reconcile",
        "description": "카드 명세서 거래줄 ↔ 개별 영수증 대사. 영수증 없는 줄을 찾는다.",
        "system_prompt": (
        "너는 카드 대사 담당이다. list_records로 레코드를 받아 카드 명세서의 "
        "거래줄마다 같은 금액의 영수증이 있는지 맞춰 본다. 영수증 없는 줄은 금액이 "
        "3만원 미만이면 '구독 추정', 이상이면 '영수증 분실/미수령'으로 표시하고 "
        "합계나 비율을 쓰기 전에는 거래줄 금액을 다시 더해 검산한다. "
        "검산이 확실하지 않으면 총액 산식은 쓰지 않는다. "
        "미확인 항목은 반드시 '- ⚠️ 상호명 금액원 — 사유' 한 줄로 남긴다. "
        "write_note('card_reconcile', ...)로 저장한다."
    ),
    },
    {
        "name": "bank_reconcile",
        "description": "은행 입출금 ↔ 계약·세금계산서 대사. 대응 문서 없는 거래를 찾는다.",
        "system_prompt": (
        "너는 은행 대사 담당이다. list_records로 레코드를 받아 은행 명세서의 "
        "입출금 줄마다 같은 금액의 계약·세금계산서·카드가 있는지 맞춰 보고, "
        "특히 은행의 신한카드 결제와 같은 금액의 카드 명세서가 있으면 대응 문서가 있는 것으로 처리한다. "
        "대응 문서 없는 거래는 반드시 '- ⚠️ 거래명 금액원 — 대응 문서 없음' 한 줄로 남긴다. "
        "대응 문서 없는 줄을 표시해 write_note('bank_reconcile', ...)로 저장한다."
    ),
    },
    {
        "name": "spend_summary",
        "description": "영수증 지출을 카테고리(식비·교통·생활)로 집계한다.",
        "system_prompt": (
            "너는 지출 집계 담당이다. list_records로 영수증을 받아 식비·교통·생활로 "
            "묶어 합계를 내고 write_note('spend_summary', ...)로 저장한다."
        ),
    },
]
ORCHESTRATOR_PROMPT = (
    "너는 인박스 리서치 애널리스트의 오케스트레이터다. 직접 조사하지 말고, "
    "write_todos로 세 조사를 계획한 뒤 task로 card_reconcile·bank_reconcile·"
    "spend_summary 서브에이전트에 한 번에 위임해 fan-out 한다. 세 노트가 모이면 "
    "각 노트의 '- ⚠️ ... — ...' 증거 줄을 모아 '짚어야 할 것'으로 brief 초안을 정리한다."
)


def trace_harness() -> None:
    """create_deep_agent에 무엇이 배선되는지 연다 — 키 불필요(구성만 출력, 호출 안 함)."""
    print("create_deep_agent에 배선되는 하네스 구성 (키 없이 보는 내부):\n")
    print("  [기본 장비] write_todos(계획) · task(서브에이전트 위임)")
    print("             · 파일시스템(ls·read_file·write_file·edit_file·glob·grep)\n")
    print("  [런타임 참고] DeepAgents 버전에 따라 general-purpose 기본 후보가 함께 보일 수 있다.")
    print("               이 실습 하니스가 요구·검증하는 전용 위임 대상은 아래 3개다.\n")
    print("  [오케스트레이터 system_prompt]")
    print(f"    {ORCHESTRATOR_PROMPT}\n")
    print(f"  [서브에이전트 {len(SUBAGENT_SPECS)}개 — task로 fan-out 위임, 각자 격리 컨텍스트]")
    for s in SUBAGENT_SPECS:
        print(f"    • {s['name']}: {s['description']}")
    print("\n  핵심: 메인은 직접 조사하지 않는다 — task로 세 워커에 위임하고 요약만 돌려받아 종합한다.")
    print("  task 위임에는 워커별 name·description·system_prompt·tools 정의가 필요하다.")


def build_agent(records: list[RecordV1]):
    """키가 있을 때 — DeepAgents live fan-out.

    메인 에이전트는 조사하지 않는다. write_todos로 계획하고 task로 세 서브에이전트
    (card·bank·spend)에 한 번에 위임한다. 각 서브에이전트는 격리된 컨텍스트에서 돌고
    write_note로 결과만 남긴다 — 메인은 요약만 돌려받아 종합한다(인지 부하의 외주).
    """
    from deepagents import create_deep_agent
    from langchain_core.tools import tool

    @tool
    def list_records() -> str:
        """분류된 모든 레코드와 항목 상세를 JSON으로 돌려준다."""
        payload = []
        for r in records:
            payload.append(
                {
                    "문서유형": r.doc_type,
                    "판매처": r.merchant,
                    "금액": r.total,
                    "통화": r.currency,
                    "날짜": r.doc_date.isoformat() if r.doc_date else None,
                    "원본경로": r.source_path,
                    "항목": [
                        {"이름": item.name, "금액": item.amount, "수량": item.qty}
                        for item in r.items
                    ],
                }
            )
        return json.dumps(payload, ensure_ascii=False, indent=2)

    @tool
    def write_note(name: str, body: str) -> str:
        """조사 노트를 research_notes/<name>.md 로 저장한다."""
        if not SAFE_NOTE.fullmatch(name):
            return f"invalid note name: {name}"
        ensure_workspace()
        path = (RESEARCH_NOTES / f"{name}.md").resolve()
        try:
            path.relative_to(RESEARCH_NOTES.resolve())
        except ValueError:
            return f"invalid note name: {name}"
        path.write_text(body, encoding="utf-8")
        return f"saved {name}.md"

    worker_tools = [list_records, write_note]
    # 위 SUBAGENT_SPECS(정적 구성)에 이 실행 도구를 붙여 배선한다.
    subagents = [{**spec, "tools": worker_tools} for spec in SUBAGENT_SPECS]

    return create_deep_agent(
        model=LIVE_MODEL,
        tools=[list_records],
        subagents=subagents,
        system_prompt=ORCHESTRATOR_PROMPT,
    )


def fan_out_live(records: list[RecordV1]) -> dict[str, str]:
    """DeepAgents live fan-out을 실행하고 노트·브리프 계약을 검증한다."""
    clear_expected_notes()
    try:
        agent = build_agent(records)
        print("  [live] create_deep_agent → task 서브에이전트 3개 위임 요청")
        out = agent.invoke({"messages": [{"role": "user",
              "content": (
                  "인박스를 교차 조사해라. 반드시 write_todos로 계획한 뒤 task로 "
                  "card_reconcile, bank_reconcile, spend_summary 세 서브에이전트에 "
                  "위임하고, 각 워커는 write_note로 같은 이름의 노트를 저장해야 한다. "
                  "마지막에는 저장한 파일명과 핵심 요약만 답해라."
              )}]})
    except Exception as e:
        raise RuntimeError(
            f"DeepAgents live 호출 실패: {type(e).__name__}: {e}. "
            "Ch0 preflight는 기본 Gemini 호출을 확인하고, Ch3 live는 DeepAgents/OpenAI 호환 경로의 "
            f"{LIVE_MODEL} 호출을 별도로 사용합니다. 키/크레딧/모델 라우팅을 확인하고, "
            "하네스 구조만 보려면 --mock 또는 --trace를 실행하세요."
        ) from e
    final = message_text(out["messages"][-1].content)
    print(final)
    names = tool_call_names(out["messages"])
    if "write_todos" not in names:
        raise RuntimeError(
            "live 실행에서 write_todos 계획 호출이 빠졌습니다. "
            "조사 전에 TodoListMiddleware 계획을 남긴 뒤 task fan-out으로 위임해야 합니다."
        )
    print("  [verify] write_todos 계획 호출 확인")
    batches = task_call_batches(out["messages"])
    expected = set(EXPECTED_NOTES)
    all_targets = set().union(*batches) if batches else set()
    if not expected.issubset(all_targets):
        missing_targets = sorted(expected - all_targets)
        raise RuntimeError(
            "live fan-out에서 기대 서브에이전트 task 호출이 빠졌습니다: "
            + ", ".join(missing_targets)
            + " — 메인이 직접 처리하지 말고 세 워커에 위임해야 합니다."
        )
    if not any(expected.issubset(batch) for batch in batches):
        raise RuntimeError(
            "live fan-out에서 세 서브에이전트가 같은 턴에 함께 호출되지 않았습니다. "
            "순차 호출이 아니라 한 번에 위임해야 fan-out입니다."
        )
    print(f"  [verify] task 호출 대상 확인: {', '.join(sorted(expected))}")
    notes, missing = read_expected_notes()
    if missing:
        raise RuntimeError(
            "live fan-out 후 기대 노트가 없습니다: "
            + ", ".join(f"research_notes/{name}.md" for name in missing)
            + " — 모델이 task/write_note 지시를 따르지 않았습니다. --trace로 배선을 확인하거나 --mock으로 하네스만 점검하세요."
        )
    synthesize(notes, records)
    return notes


def main() -> None:
    ap = argparse.ArgumentParser(description="fan-out 리서치 오케스트레이터")
    ap.add_argument("--mock", action="store_true", help="키 없이 결정론적 대사")
    ap.add_argument("--trace", action="store_true", help="하네스 구성을 열어 본다(키 불필요, 호출 안 함)")
    args = ap.parse_args()

    if args.trace:
        trace_harness()
        return

    records = load_records(allow_gold=args.mock)
    print(f"▶ 조사 대상 {len(records)}건")

    if args.mock:
        notes = fan_out_mock(records)
        synthesize(notes, records)
        print(f"\n노트: {RESEARCH_NOTES}\n브리프 초안: {BRIEF_DRAFT}")
    else:
        fan_out_live(records)
        print(f"\n노트: {RESEARCH_NOTES}\n브리프 초안: {BRIEF_DRAFT}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        raise SystemExit(f"❌ {e}") from None
