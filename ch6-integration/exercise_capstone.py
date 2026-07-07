"""Ch6 랩업 실습 — 다섯 챕터를 하나의 파이프라인으로 엮는다 (빈칸 채우기).

전체를 새로 짜지 않는다. 각 챕터에서 만든 부품은 이미 있다(그냥 import). 네가 채울 건
그 부품을 '순서대로 잇는' 파이프라인 다섯 칸뿐이다. 전부 mock/결정론이라 키·네트워크 불필요.
교재 Ch6를 옆에 두고 30~40분에 완성하는 게 목표다.

  ① intake   — Ch2 그래프로 sample_inbox 문서 → classified/
  ② research — Ch3 fan-out(mock) → research_notes/
  ③ knowledge— Ch4 OKF 적재 → knowledge_base/
  ④ brief    — 레코드 + OKF 지식 → brief.md
  ⑤ verify   — Ch5 검증(결정론) → verified_brief.md

읽기만 하면 안 남는다. 직접 쳐서 채운 뒤:

    uv run python3 ch6-integration/exercise_capstone.py --check   # ✅ 5/5 산출물이면 완성
    uv run python3 ch6-integration/exercise_capstone.py           # 파이프라인 한 바퀴 직접

막히면 정답: ch6-integration/analyst_app.py 의
    run_intake · run_research · run_okf · write_brief_deterministic · run_verify
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for sub in ("", "ch1-llm-basics", "ch2-langgraph-agent", "ch3-deepagents",
            "ch4-skills-mcp", "ch5-a2a"):
    sys.path.insert(0, str(ROOT / sub))

from analyst.paths import BRIEF, CLASSIFIED, KNOWLEDGE_BASE, MANIFEST, RESEARCH_NOTES, ensure_workspace


def _todo(n: str):
    raise NotImplementedError(f"TODO {n} — 이 칸을 채우세요 (정답: analyst_app.py)")


# ── 빈칸 ① : 분류·정규화 (Ch2) ───────────────────────────────────
def stage_intake() -> None:
    """sample_inbox 문서를 Ch2 그래프로 분류해 classified/ 에 적재한다(mock)."""
    import yaml

    from intake_graph import build_graph, run_one

    graph = build_graph()
    docs = [d["file"] for d in yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["docs"]]
    # TODO ①: docs의 각 문서 d를 그래프로 한 바퀴 돌리세요. 고액은 자동 승인.
    #   힌트: for d in docs: run_one(graph, d, mock=True, auto="approve")
    _todo("①")


# ── 빈칸 ② : fan-out 교차 조사 (Ch3) ─────────────────────────────
def stage_research() -> None:
    """Ch3 fan-out(mock)으로 research_notes/ 와 brief_draft.md 를 만든다."""
    from research_orchestrator import fan_out_mock, load_records, synthesize

    records = load_records()
    # TODO ②: fan_out_mock으로 세 갈래 노트를 만들고, synthesize로 종합하세요.
    #   힌트: notes = fan_out_mock(records) → synthesize(notes, records)
    _todo("②")


# ── 빈칸 ③ : OKF 지식 적재 (Ch4) ─────────────────────────────────
def stage_knowledge() -> None:
    """classified 레코드를 OKF 항목으로 knowledge_base/ 에 적재한다."""
    from okf_store import build_finding_entries, build_merchant_entries, okf_index
    from research_orchestrator import load_records

    records = load_records()
    ensure_workspace()
    entries = {**build_merchant_entries(records), **build_finding_entries(records)}
    # TODO ③: entries의 각 (name, text)를 KNOWLEDGE_BASE/{name}.md 로 쓰고,
    #         okf_index(entries)를 KNOWLEDGE_BASE/index.md 로 쓰세요.
    _todo("③")


# ── 빈칸 ④ : 브리프 한 장 (Ch4 결정론 보조) ──────────────────────
def _render_brief(n_records: int, spend: float, flags: list[str]) -> str:
    """브리프 마크다운을 짠다(형식은 제공 — 너는 위에서 값만 모으면 된다)."""
    lines = [
        "# 인박스 브리프 — 2026년 5월", "",
        "## 한 줄 요약",
        f"문서 {n_records}건 · 영수증 지출 {spend:,.0f}원 · 짚을 점 {len(flags)}건.", "",
        "## 짚을 점", *(flags or ["- 특이사항 없음"]), "",
        "## 할 일", "- [ ] 영수증 없는 카드 결제 확인", "- [ ] 구독 목록 점검",
    ]
    return "\n".join(lines) + "\n"


def stage_brief() -> None:
    """레코드와 OKF 지식(gap·subscription)을 모아 brief.md 를 쓴다."""
    import yaml

    from research_orchestrator import by_type, load_records

    records = load_records()
    spend = sum(r.total for r in by_type(records, "영수증"))
    flags: list[str] = []
    for p in sorted(KNOWLEDGE_BASE.glob("*.md")):
        t = p.read_text(encoding="utf-8")
        if "type: gap" in t or "type: subscription" in t:
            meta = yaml.safe_load(t.split("---", 2)[1]) if t.startswith("---") else {}
            kind = meta.get("type", "")
            amt = meta.get("amount")
            amount_text = f" {float(amt):,.0f}원" if amt is not None else ""
            suffix = " — 확인 필요" if kind == "gap" else " — 구독 추정"
            flags.append(f"- ({kind}) {meta.get('title', '?')}{amount_text}{suffix}")
    # TODO ④: _render_brief(레코드 수, spend, flags)로 브리프를 만들어 BRIEF에 쓰세요.
    #   힌트: ensure_workspace() 후 BRIEF.write_text(_render_brief(len(records), spend, flags), encoding="utf-8")
    _todo("④")


# ── 빈칸 ⑤ : 외부 검증 (Ch5 결정론) ──────────────────────────────
def stage_verify() -> None:
    """브리프를 검증자에게(여기선 결정론 직접 호출) 보내 verified_brief.md 를 쓴다."""
    from a2a_verify import write_verified
    from verifier_agent import verify_brief

    brief = BRIEF.read_text(encoding="utf-8") if BRIEF.exists() else ""
    # TODO ⑤: verify_brief(brief)로 판정을 받고(3-튜플: ok, notes, _),
    #         결과 블록을 만들어 write_verified(brief, block)으로 저장하세요.
    #   힌트: ok, notes, _ = verify_brief(brief)
    #         block = f"## 외부 검증 결과 — {'PASS' if ok else 'NEEDS_REVISION'}\\n\\n" + "\\n".join(f"- {n}" for n in notes)
    _todo("⑤")


STAGES = [
    ("① 분류·정규화 (Ch2)", stage_intake, lambda: any(CLASSIFIED.glob("*.json"))),
    ("② fan-out 조사 (Ch3)", stage_research, lambda: any(RESEARCH_NOTES.glob("*.md"))),
    ("③ OKF 지식 (Ch4)", stage_knowledge, lambda: (KNOWLEDGE_BASE / "index.md").exists()),
    ("④ 브리프 (Ch4)", stage_brief, lambda: BRIEF.exists()),
    ("⑤ 검증 (Ch5)", stage_verify, lambda: (BRIEF.parent / "verified_brief.md").exists()),
]


def run_pipeline() -> None:
    ensure_workspace()
    for i, (title, fn, _check) in enumerate(STAGES, 1):
        print(f"\n[{i}/5] {title}")
        fn()


def check() -> None:
    """파이프라인 순서대로 돌며 첫 미완성 칸에서 멈춘다(다음 단계는 앞 산출물에 의존하므로)."""
    ensure_workspace()
    for i, (title, fn, produced) in enumerate(STAGES, 1):
        try:
            fn()
        except NotImplementedError:
            print(f"  ⬜ [{i}/5] {title} — 아직 빈칸입니다. 여기부터 채우세요.")
            print(f"\n결과: {i - 1}/5 완성 — 다음 칸은 {title} (정답: analyst_app.py)")
            return
        except Exception as e:  # noqa: BLE001 - 학습용, 어느 단계가 깨졌는지 그대로 보여 준다
            print(f"  ❌ [{i}/5] {title} — {type(e).__name__}: {e}")
            print(f"\n결과: {i - 1}/5 완성 — {title}에서 막혔습니다")
            return
        if not produced():
            print(f"  ❌ [{i}/5] {title} — 실행은 됐지만 산출물이 없습니다")
            print(f"\n결과: {i - 1}/5 완성 — {title} 산출물을 확인하세요")
            return
        print(f"  ✅ [{i}/5] {title}")
    print("\n결과: 5/5  🎉 랩업 완성!")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        run_pipeline()
