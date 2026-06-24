"""Ch6 캡스톤 — 모듈을 하나의 파이프라인으로 잇는 엔드투엔드.

지금까지 만든 모듈을 새로 짜지 않고 그대로 연결한다. 샘플 메일 입력을 분류부터
외부 검증까지 순서대로 처리한다. 계약(RecordV1)과 디렉터리 규약이 같아서 가능하다.

    샘플 메일 입력 → 분류·정규화(Ch2) → fan-out 조사(Ch3) + OKF 적재(Ch4)
            → 브리프(Ch4 Skill) → 검증(Ch5, --a2a면 외부 A2A) → verified_brief.md

각 단계는 해당 챕터의 모듈을 import 해 그 함수를 부른다. 기본 live 경로는 Ch4의
Skill 에이전트까지 실제로 실행하고, --mock 경로만 키 없이 끝까지 볼 수 있도록
결정론 브리프 작성으로 대체한다.
"계약을 지키면 모듈을 교체할 수 있다".

실행:
    uv run python3 ch6-integration/analyst_app.py --a2a            # live 분류·live 조사·실제 A2A
    uv run python3 ch6-integration/analyst_app.py --mock           # 전 구간 오프라인
    uv run python3 ch6-integration/analyst_app.py --mock --a2a     # 분류·조사는 mock, 검증은 실제 A2A
출력: workspace/{classified,research_notes,knowledge_base}/ · brief.md · verified_brief.md
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# ch1~5 실습 모듈을 레포 내부 경로 기준으로 가져온다. uv는 레포 루트에서 실행해야
# pyproject.toml의 의존성/가상환경까지 함께 잡는다.
for sub in ("", "ch1-llm-basics", "ch2-langgraph-agent", "ch3-deepagents",
            "ch4-skills-mcp", "ch5-a2a"):
    sys.path.insert(0, str(ROOT / sub))

from analyst.paths import BRIEF, CLASSIFIED, KNOWLEDGE_BASE, MANIFEST, WORKSPACE, ensure_workspace


def step(n: int, title: str) -> None:
    print(f"\n[{n}/6] {title}")


def run_intake(mock: bool) -> None:
    """Ch2 — 샘플 입력의 문서를 분류·정규화해 classified/ 에 적재."""
    import yaml
    from intake_graph import build_graph, run_one

    graph = build_graph()
    docs = [d["file"] for d in yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["docs"]]
    for d in docs:
        run_one(graph, d, mock, auto="approve")


def run_research(mock: bool) -> dict:
    """Ch3 — fan-out 교차 조사 → research_notes/ + brief_draft.md."""
    from research_orchestrator import fan_out_live, fan_out_mock, load_records, synthesize

    records = load_records()
    if mock:
        notes = fan_out_mock(records)
        synthesize(notes, records)
    else:
        notes = fan_out_live(records)
    return {"records": records, "notes": notes}


def run_okf() -> int:
    """Ch4 — classified 레코드를 OKF 지식 항목으로 적재."""
    from okf_store import build_finding_entries, build_merchant_entries, okf_index, validate_okf_bundle
    from analyst.paths import KNOWLEDGE_BASE
    from research_orchestrator import load_records

    records = load_records()
    ensure_workspace()
    entries = {**build_merchant_entries(records), **build_finding_entries(records)}
    index_text = okf_index(entries)
    validate_okf_bundle(entries, index_text)
    for name, text in entries.items():
        (KNOWLEDGE_BASE / f"{name}.md").write_text(text, encoding="utf-8")
    (KNOWLEDGE_BASE / "index.md").write_text(index_text, encoding="utf-8")
    return len(entries)


def write_brief_deterministic() -> None:
    """Ch4 결정론 보조 경로 — 레코드와 OKF 지식을 모아 한 장짜리 brief.md."""
    import yaml

    from analyst.paths import KNOWLEDGE_BASE
    from research_orchestrator import by_type, load_records

    records = load_records()
    receipts = by_type(records, "영수증")
    spend = sum(r.total for r in receipts)
    flags = []
    for p in sorted(KNOWLEDGE_BASE.glob("*.md")):
        t = p.read_text(encoding="utf-8")
        if "type: gap" in t or "type: subscription" in t:
            meta = yaml.safe_load(t.split("---", 2)[1]) if t.startswith("---") else {}
            name = meta.get("title") or meta.get("name") or t.split("# ", 1)[1].splitlines()[0]
            kind = meta.get("type") or ("gap" if "type: gap" in t else "subscription")
            amount = meta.get("amount")
            suffix = " — 확인 필요" if kind == "gap" else " — 구독 추정"
            amount_text = f" {float(amount):,.0f}원" if amount is not None else ""
            flags.append(f"- ({kind}) {name}{amount_text}{suffix}")
    lines = [
        "# 인박스 브리프 — 2026년 5월", "",
        "## 한 줄 요약",
        f"문서 {len(records)}건 · 영수증 지출 {spend:,.0f}원 · 짚을 점 {len(flags)}건.", "",
        "## 짚을 점", *(flags or ["- 특이사항 없음"]), "",
        "## 할 일",
        "- [ ] 영수증 없는 카드 결제 확인", "- [ ] 구독 목록 점검",
    ]
    ensure_workspace()
    BRIEF.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_brief(use_skill: bool) -> None:
    """Ch4 — live는 Skill 에이전트, mock은 결정론 보조 경로."""
    if use_skill:
        from skill_agent import run_agent

        run_agent()
    else:
        write_brief_deterministic()


def run_verify(use_a2a: bool) -> None:
    """Ch5 — 브리프를 외부 검증 에이전트에 보내 verified_brief.md."""
    from a2a_verify import verify_via_a2a, wait_for_server, write_verified, VERIFIER_URL
    import subprocess

    brief = BRIEF.read_text(encoding="utf-8") if BRIEF.exists() else ""
    if use_a2a:
        import asyncio
        proc = None
        if not wait_for_server(VERIFIER_URL, timeout=1.0):
            proc = subprocess.Popen(
                [sys.executable, str(ROOT / "ch5-a2a" / "verifier_agent.py")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        try:
            if not wait_for_server(VERIFIER_URL):
                raise RuntimeError("검증 에이전트 기동 실패")
            block = asyncio.run(verify_via_a2a(brief))
        finally:
            if proc:
                proc.terminate()
    else:
        from verifier_agent import verify_brief
        ok, notes = verify_brief(brief)
        block = (f"## 외부 검증 결과 — {'PASS' if ok else 'NEEDS_REVISION'}\n"
                 "검증 주체: 세무·정합성 검증 에이전트 (직접 호출)\n\n"
                 + "\n".join(f"- {n}" for n in notes))
    write_verified(brief, block)


def main() -> None:
    ap = argparse.ArgumentParser(description="인박스 리서치 애널리스트 — 엔드투엔드")
    ap.add_argument("--mock", action="store_true", help="분류·조사·브리프 작성을 결정론 보조 경로로(키 없이)")
    ap.add_argument("--a2a", action="store_true", help="검증 단계를 실제 A2A로")
    args = ap.parse_args()

    print("=== 인박스 리서치 애널리스트 — 엔드투엔드 ===")
    print("샘플 메일 입력을 분류부터 검증까지 순서대로 처리합니다.")

#pragma region wiring
    step(1, "분류·정규화 (Ch2 intake_graph)")
    run_intake(args.mock)
    step(2, "fan-out 교차 조사 (Ch3 research_orchestrator)")
    ctx = run_research(args.mock)
    step(3, "OKF 지식 적재 (Ch4 okf_store)")
    if os.getenv("ACDC_SKIP_OKF") == "1":
        n = 0
        ensure_workspace()
        for p in KNOWLEDGE_BASE.glob("*.md"):
            p.unlink()
        print("  ACDC_SKIP_OKF=1 — 실패 실험을 위해 OKF 적재를 건너뜀")
    else:
        n = run_okf()
        print(f"  지식 항목 {n}개")
    step(4, "브리프 작성 (Ch4 inbox-brief Skill)")
    write_brief(use_skill=not args.mock)
    print(f"  → {BRIEF.relative_to(WORKSPACE.parent)}")
    step(5, "외부 검증 (Ch5 A2A)" if args.a2a else "직접 검증 (Ch5 verifier)")
    run_verify(args.a2a)
    step(6, "완료")
    print(f"\n분류 {len(list(CLASSIFIED.glob('*.json')))}건 · 조사 {len(ctx['notes'])}갈래")
    print(f"최종 산출물: {WORKSPACE / 'verified_brief.md'}")
#pragma endregion wiring


if __name__ == "__main__":
    main()
