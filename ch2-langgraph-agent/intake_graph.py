"""Ch2 산출물 — 인박스 적재 파이프라인을 StateGraph로 묶는다.

Ch1의 단발 추출(classify_one)을 상태·재시도·중단점이 있는 흐름으로 끌어올린다.
문서 한 장이 그래프를 이렇게 통과한다.

    classify ─→ verify ─→ (review?) ─→ persist
                  │           │
                  └ 재시도     └ 고액·저신뢰면 interrupt() 로 사람에게 멈춰 묻는다

핵심 학습점
  - StateGraph : 노드·엣지로 흐름을 명시한다(create_agent의 자율 루프와 대비).
  - checkpointer : thread_id 별 상태를 저장해 interrupt 후 같은 자리에서 재개한다.
  - 재시도 : verify 실패(합계 불일치)면 classify로 되돌린다(상한까지).
  - hold : 재시도 상한 뒤에도 검증 실패면 적재하지 않는다(fail-closed).
  - interrupt() HITL : 고액(≥1,000,000)·저신뢰(<0.7) 건은 자동 통과시키지 않는다.

실행:
    uv run python3 ch2-langgraph-agent/intake_graph.py                 # 전체 적재(live 기본, 검토건은 입력)
    uv run python3 ch2-langgraph-agent/intake_graph.py --doc invoice_photo.png
    uv run python3 ch2-langgraph-agent/intake_graph.py --mock          # 진단/오프라인 보조
출력: workspace/classified/<문서>.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

# Ch1 모듈을 그대로 재사용한다 — 계약을 지키면 모듈을 교체할 수 있다.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyst import DocType, RecordV1
from analyst.paths import CLASSIFIED, ensure_workspace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ch1-llm-basics"))
from classify_one import DEFAULT_MODEL, classify_error, extract, gold_to_record, load_gold, score, verify_total

def default_high_value() -> float:
    raw = os.environ.get("ANALYST_HIGH_VALUE", "1000000")
    try:
        return float(raw)
    except ValueError as exc:
        raise RuntimeError("ANALYST_HIGH_VALUE는 숫자여야 합니다.") from exc


HIGH_VALUE = default_high_value()  # 고액 기준(원)
LOW_CONFIDENCE = 0.7    # 저신뢰 기준
MAX_RETRY = 2
QUALITY_MIN_SCORE = 5 / 6


def is_receipt(doc_type) -> bool:
    return doc_type == DocType.receipt or doc_type == DocType.receipt.value


def item_line_totals(rec: RecordV1) -> list[float]:
    """항목 라인 합(단가×수량) 목록. '마스크팩 5매'(6000×1)와 '마스크팩'(1200×5)처럼
    단가/수량 분해가 갈려도 라인 합이 같으면 같은 것으로 본다 — 대사의 불변식은 라인 합이다."""
    return sorted(round(float(item.amount or 0) * float(item.qty or 1), 2) for item in rec.items)


def clear_outputs(docs: list[str]) -> Path | None:
    """전체 실행은 이전 classified 산출물을 백업한 뒤 지워 이번 실행 결과만 보이게 한다."""
    ensure_workspace()
    backup_dir: Path | None = None
    for doc in docs:
        out = CLASSIFIED / (Path(doc).stem + ".json")
        if out.exists():
            if backup_dir is None:
                backup_dir = CLASSIFIED.parent / "classified_backup" / datetime.now().strftime("%Y%m%d-%H%M%S")
                backup_dir.mkdir(parents=True, exist_ok=True)
            out.replace(backup_dir / out.name)
    return backup_dir


class IntakeState(TypedDict, total=False):
    doc: str            # sample_inbox 파일명
    mock: bool
    break_sum: bool     # 교육용: 영수증 총액을 일부러 깨 retry/hold를 관찰
    record: dict        # RecordV1 dump(노드 간 직렬화 가능 형태로 운반)
    retries: int
    flagged: str        # 사람 검토가 필요한 사유("" 면 자동 통과)
    sum_ok: bool        # 영수증 합계 검증 결과(분기용)
    verify_issue: str   # retry/hold를 유발한 검증 사유
    held: str           # 보류 사유

# ── 노드 ─────────────────────────────────────────────────────────


def classify(state: IntakeState) -> dict:
    """문서 한 장을 RecordV1로 추출한다(Ch1 모듈 재사용)."""
    use_react = (not state["mock"]) and state.get("retries", 0) > 0
    if use_react:
        issue = state.get("verify_issue", "검증 실패")
        print(f"  [classify] 이전 {issue} 관측 → ReAct 검산 경로로 재시도")
    rec = extract(state["doc"], model=DEFAULT_MODEL, mock=state["mock"], react=use_react)
    print(f"  [classify] {rec.merchant} · {rec.total:,.0f}원 · 신뢰도 {rec.confidence:.2f}")
    dump = rec.model_dump(by_alias=True, mode="json")  # classified/*.json = 한글 키
    if state.get("break_sum") and is_receipt(rec.doc_type):
        dump["총액"] = (dump.get("총액") or 0) + 1       # 합계를 1원 깨 retry를 발화시킨다
    return {"record": dump}


def verify(state: IntakeState) -> dict:
    """영수증 합계와 샘플 회귀 기준을 검증하고, 검토 플래그를 매긴다."""
    rec = RecordV1.model_validate(state["record"])
    flagged = ""
    if rec.total >= HIGH_VALUE:
        flagged = f"고액({rec.total:,.0f}원)"
    elif rec.confidence < LOW_CONFIDENCE:
        flagged = f"저신뢰({rec.confidence:.2f})"
    ok, item_sum = verify_total(rec)
    if is_receipt(rec.doc_type) and not ok:
        print(f"  [verify] 합계 불일치(항목합 {item_sum:,.0f} ≠ {rec.total:,.0f})")
        return {"flagged": flagged, "sum_ok": False, "verify_issue": "합계 불일치"}
    if not state["mock"] and not state.get("break_sum"):
        gold = gold_to_record(load_gold(state["doc"]))
        quality_issues = []
        quality_score = score(rec, gold)
        if quality_score < QUALITY_MIN_SCORE:
            quality_issues.append(f"score {quality_score:.2f}<{QUALITY_MIN_SCORE:.2f}")
        if rec.merchant.strip() != gold.merchant.strip():
            quality_issues.append(f"판매처 {rec.merchant!r}≠{gold.merchant!r}")
        if rec.doc_type != gold.doc_type:
            quality_issues.append(f"문서유형 {rec.doc_type!r}≠{gold.doc_type!r}")
        if abs(rec.total - gold.total) >= 1.0:
            quality_issues.append(f"금액 {rec.total:,.0f}≠{gold.total:,.0f}")
        if rec.doc_date != gold.doc_date:
            quality_issues.append(f"날짜 {rec.doc_date}≠{gold.doc_date}")
        if len(rec.items) != len(gold.items):
            quality_issues.append(f"항목수 {len(rec.items)}≠{len(gold.items)}")
        elif item_line_totals(rec) != item_line_totals(gold):
            quality_issues.append("항목 라인합 불일치")
        if quality_issues:
            print("  [verify] 샘플 품질 불일치(" + ", ".join(quality_issues) + ")")
            return {"flagged": flagged, "sum_ok": False, "verify_issue": "샘플 품질 불일치"}
    print(f"  [verify] 통과{' · 검토 필요: ' + flagged if flagged else ''}")
    return {"flagged": flagged, "sum_ok": True, "verify_issue": ""}


def review(state: IntakeState) -> dict:
    """고액·저신뢰 건은 interrupt()로 멈춰 사람의 결정을 받는다."""
    rec = state["record"]
    decision = interrupt({
        "사유": state["flagged"],
        "판매처": rec["판매처"],
        "총액": rec["총액"],
        "문서유형": rec["문서유형"],
        "질문": "이 분류를 그대로 적재할까요? (approve / reject)",
    })
    if decision == "approve":
        print("  [review] 승인 — 적재 진행")
        return {"flagged": ""}
    # approve가 아니면(reject·오타·빈 응답) 안전하게 보류한다 — 안전 게이트는 fail-closed
    print(f"  [review] 보류 — 적재 안 함 (결정: {decision!r})")
    return {"flagged": "rejected"}


def persist(state: IntakeState) -> dict:
    """검증된 레코드를 classified/<문서>.json 으로 떨군다."""
    out = CLASSIFIED / (Path(state["doc"]).stem + ".json")
    if state.get("flagged") == "rejected":
        if out.exists():
            out.unlink()
            print(f"  [persist] 기존 파일 제거 → {out.relative_to(out.parents[2])}")
        return {"held": "review rejected"}
    ensure_workspace()
    out.write_text(
        json.dumps(state["record"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  [persist] → {out.relative_to(out.parents[2])}")
    return {}


def hold_failed(state: IntakeState) -> dict:
    """재시도 후에도 검증 실패한 문서는 적재하지 않는다."""
    out = CLASSIFIED / (Path(state["doc"]).stem + ".json")
    if out.exists():
        out.unlink()
        print(f"  [hold] 검증 실패 — 기존 파일 제거 → {out.relative_to(out.parents[2])}")
    else:
        print("  [hold] 검증 실패 — 적재 안 함")
    return {"held": "검증 실패"}


# ── 엣지(분기) ───────────────────────────────────────────────────


def after_verify(state: IntakeState) -> str:
    if state.get("sum_ok", True) is False and state["retries"] < MAX_RETRY:
        return "retry"                          # 합계 불일치 — 상한까지 재분류
    if state.get("sum_ok", True) is False:
        return "hold"                           # 끝내 안 맞으면 fail-closed
    return "review" if state["flagged"] else "persist"


def bump_retry(state: IntakeState) -> dict:
    issue = state.get("verify_issue", "검증 실패")
    print(f"  [retry] 재분류 {state['retries'] + 1}/{MAX_RETRY} — {issue}")
    return {"retries": state["retries"] + 1}


#pragma region build-graph
def build_graph():
    g = StateGraph(IntakeState)
    g.add_node("classify", classify)     # 추출(Ch1 모듈)
    g.add_node("verify", verify)         # 합계·플래그
    g.add_node("retry", bump_retry)      # 재분류 카운터
    g.add_node("review", review)         # interrupt() 멈춤
    g.add_node("persist", persist)       # classified/ 적재
    g.add_node("hold", hold_failed)      # 검증 실패 보류
    g.add_edge(START, "classify")
    g.add_edge("classify", "verify")
    g.add_conditional_edges("verify", after_verify,          # ← 유일한 분기
                            {"retry": "retry", "review": "review", "persist": "persist", "hold": "hold"})
    g.add_edge("retry", "classify")      # 재시도는 classify로 되돌림
    g.add_edge("review", "persist")
    g.add_edge("hold", END)
    g.add_edge("persist", END)
    return g.compile(checkpointer=InMemorySaver())            # ← HITL 재개에 필수
#pragma endregion build-graph


def run_one(graph, doc: str, mock: bool, auto: str = "ask", reject_ok: bool = False,
            break_sum: bool = False) -> None:
    """문서 한 건을 실행한다. 이 수업 데모는 interrupt 뒤 auto 결정으로 재개한다."""
    config = {"configurable": {"thread_id": f"intake-{doc}"}}
    print(f"\n▶ {doc}")
    state = {"doc": doc, "mock": mock, "break_sum": break_sum, "record": {}, "retries": 0, "flagged": ""}
    result = graph.invoke(state, config=config)
    if result.get("__interrupt__"):
        payload = result["__interrupt__"][0].value
        decision = auto
        if auto == "ask":
            if sys.stdin.isatty():
                decision = input(
                    f"  ⏸ interrupt — {payload['사유']} · {payload['판매처']} "
                    f"{payload['총액']:,.0f}원 → approve/reject 입력: "
                ).strip() or "reject"
            else:
                decision = "reject"
                print("  ⏸ interrupt — 비대화형 실행이라 안전하게 'reject'로 처리")
        else:
            print(f"  ⏸ interrupt — {payload['사유']} · {payload['판매처']} {payload['총액']:,.0f}원"
                  f" → 자동 결정 '{decision}'")
        result = graph.invoke(Command(resume=decision), config=config)
    if result.get("held"):
        print(f"  [result] 보류 — {result['held']}")
        if result["held"] == "검증 실패" and not break_sum:
            raise RuntimeError("검증 실패로 보류됨")
        if result["held"] == "review rejected" and not reject_ok:
            raise RuntimeError("검토 반려로 보류됨")


def explain_failure(doc: str, e: Exception) -> str:
    kind = classify_error(e)
    if "검증 실패로 보류" in str(e):
        kind = "quality-gate"
    elif "검토 반려로 보류" in str(e):
        kind = "review-held"
    hints = {
        "auth/key": "OPENROUTER_API_KEY를 확인하세요. 키 없이 구조만 보려면 --mock을 붙입니다.",
        "credit": "OpenRouter 크레딧 또는 결제 한도를 확인하세요.",
        "model-slug": "ANALYST_MODEL/PREFLIGHT_MODEL 슬러그가 계정에서 사용 가능한지 확인하세요.",
        "json/schema": "모델 출력이 RecordV1 JSON 계약을 어겼습니다. 같은 문서를 --mock으로 돌려 그래프를 분리 확인하세요.",
        "quality-gate": "샘플 회귀 검증이 live 오추출을 잡았습니다. 모델/PDF 라우팅을 확인하거나 --mock으로 그래프를 분리 확인하세요.",
        "review-held": "고액·저신뢰 검토가 승인되지 않아 적재하지 않았습니다. 터미널에서 approve를 입력하거나 데모/CI에서는 --approve-flagged를 명시하세요.",
    }
    hint = hints.get(kind, "위 원인 메시지를 확인하고, 키/네트워크 문제면 --mock으로 그래프만 먼저 점검하세요.")
    return f"{doc} 실패 [{kind}] — {type(e).__name__}: {e}\n  ↳ {hint}"


def main() -> None:
    ap = argparse.ArgumentParser(description="인박스 적재 StateGraph")
    ap.add_argument("--doc", help="한 건만 처리(미지정 시 sample_inbox 전체)")
    ap.add_argument("--mock", action="store_true", help="키 없이 gold로 그래프를 점검(진단/오프라인/CI 보조)")
    ap.add_argument("--reject-flagged", action="store_true", help="검토건을 자동 반려(명시적 fail-closed 데모)")
    ap.add_argument("--approve-flagged", action="store_true", help="검토건을 자동 승인(데모/CI용)")
    ap.add_argument("--break-sum", action="store_true", help="영수증 합계를 일부러 깨 retry 분기를 본다")
    ap.add_argument("--high-value", type=float, default=None, help="고액 검토 기준(원). 기본: ANALYST_HIGH_VALUE 또는 1,000,000")
    args = ap.parse_args()

    global HIGH_VALUE
    if args.high_value is not None:
        HIGH_VALUE = args.high_value

    graph = build_graph()
    if args.reject_flagged:
        auto = "reject"
    elif args.approve_flagged or args.mock:
        auto = "approve"
    else:
        auto = "ask"

    if args.doc:
        try:
            run_one(graph, args.doc, args.mock, auto, reject_ok=args.reject_flagged,
                    break_sum=args.break_sum)
        except Exception as e:
            print("  [error] " + explain_failure(args.doc, e))
            raise SystemExit(1) from None
    else:
        import yaml

        from analyst.paths import MANIFEST
        docs = [d["file"] for d in yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["docs"]]
        backup_dir = None
        if not args.break_sum:
            backup_dir = clear_outputs(docs)
            if backup_dir:
                print(f"  [reset] 이전 classified 산출물 백업 → {backup_dir.relative_to(backup_dir.parents[1])}")
            print("  [reset] 이번 실행 결과만 확인")
        failures = []
        for d in docs:
            try:
                run_one(graph, d, args.mock, auto, reject_ok=args.reject_flagged,
                        break_sum=args.break_sum)
            except Exception as e:
                failures.append((d, e))
                print("  [error] " + explain_failure(d, e))
        if failures:
            names = ", ".join(d for d, _ in failures)
            if backup_dir:
                print(f"  [backup] 이전 산출물은 {backup_dir} 에 보관됨")
            print(f"전체 적재 중 {len(failures)}건 실패: {names}")
            raise SystemExit(1) from None
    print(f"\n적재 위치: {CLASSIFIED}")


if __name__ == "__main__":
    main()
