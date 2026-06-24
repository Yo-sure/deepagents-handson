"""Ch2 실습 — StateGraph를 직접 엮어 본다 (빈칸 채우기).

intake_graph.py의 축소판이다. 노드 로직(classify·verify·review·persist)은 채워져
있다. 네가 손으로 채울 빈칸은 LangGraph 뼈대 네 곳뿐이다:

  ① ExerciseState — 노드 사이로 운반할 상태 필드
  ② build_graph   — 노드·엣지·분기 연결 + checkpointer
  ③ review        — interrupt() 로 멈춰 사람 결정을 받기
  ④ run_one       — Command(resume=...) 로 멈춘 그래프 잇기

읽기만 하면 안 남는다. 직접 쳐서 채운 뒤 자가 점검:

    uv run python3 ch2-langgraph-agent/exercise_graph.py --check   # ✅ 4개면 정답
    uv run python3 ch2-langgraph-agent/exercise_graph.py           # 직접 한 바퀴(고액에서 멈춤→입력)

키·네트워크 불필요(가짜 인박스). 막히면 정답은 intake_graph.py 의 build_graph()/run_one().
"""

from __future__ import annotations

import argparse
import sys
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

HIGH_VALUE = 1_000_000  # 이 금액 이상이면 사람 검토(interrupt)

# 키·네트워크 없이 그래프 뼈대에만 집중하도록 둔 가짜 인박스.
INBOX = {
    "receipt_small": {"판매처": "GS25", "총액": 8_400},
    "invoice_big": {"판매처": "디자인스튜디오 레이", "총액": 1_650_000},
}


def _todo(n: str):
    raise NotImplementedError(f"TODO {n} — 이 부분을 채우세요 (정답: intake_graph.py)")


# ── 빈칸 ① : State ───────────────────────────────────────────────
# 노드들이 읽고 쓰는 키: doc(str) · record(dict) · flagged(str)
class ExerciseState(TypedDict, total=False):
    # TODO ①: 위 세 필드를 타입과 함께 선언하세요. (예: doc: str)
    pass


# ── 노드(완성본 — 고치지 말 것) ──────────────────────────────────
def classify(state: ExerciseState) -> dict:
    rec = dict(INBOX[state["doc"]])
    print(f"  [classify] {rec['판매처']} · {rec['총액']:,}원")
    return {"record": rec}


def verify(state: ExerciseState) -> dict:
    rec = state["record"]
    flagged = f"고액({rec['총액']:,}원)" if rec["총액"] >= HIGH_VALUE else ""
    print(f"  [verify] 통과{' · 검토 필요: ' + flagged if flagged else ''}")
    return {"flagged": flagged}


def review(state: ExerciseState) -> dict:
    rec = state["record"]
    # TODO ③: interrupt()로 그래프를 멈추고 사람의 결정을 받으세요.
    #   interrupt(값)에 넘긴 값이 __interrupt__로 나가고,
    #   Command(resume=X)로 들어온 X가 이 interrupt() 호출의 반환값이 됩니다.
    #   아래 _todo(...)를 지우고 decision = interrupt({...}) 형태로 채우세요.
    decision = _todo("③ review의 interrupt()")
    if decision == "approve":
        print("  [review] 승인 — 적재 진행")
        return {"flagged": ""}
    print(f"  [review] 보류 — 적재 안 함 (결정: {decision!r})")
    return {"flagged": "rejected"}


def persist(state: ExerciseState) -> dict:
    if state.get("flagged") == "rejected":
        print("  [persist] 반려 — 적재 안 함")
        return {}
    print(f"  [persist] 적재 → {state['doc']}.json")
    return {}


def after_verify(state: ExerciseState) -> str:
    """검토 플래그가 있으면 review로, 없으면 바로 persist로."""
    return "review" if state.get("flagged") else "persist"


# ── 빈칸 ② : 그래프 연결 + checkpointer ──────────────────────────
#pragma region exercise-build
def build_graph():
    g = StateGraph(ExerciseState)
    # TODO ②: 아래 다섯 가지를 채우세요.
    #   1) 노드 등록: g.add_node("classify", classify) … verify·review·persist 까지 4개
    #   2) 직선 엣지: START→"classify", "classify"→"verify"
    #   3) 분기: g.add_conditional_edges("verify", after_verify,
    #            {"review": "review", "persist": "persist"})
    #   4) "review"→"persist", "persist"→END
    #   5) return g.compile(checkpointer=InMemorySaver())   ← 없으면 resume이 막힌다
    return _todo("② build_graph 연결 + checkpointer")
#pragma endregion exercise-build


def run_one(graph, doc: str, auto: str = "ask") -> dict:
    # 같은 thread_id라야 멈춘 자리에서 잇는다(다른 id면 처음부터 새 실행).
    config = {"configurable": {"thread_id": f"ex-{doc}"}}
    print(f"\n▶ {doc}")
    result = graph.invoke({"doc": doc, "flagged": ""}, config=config)
    if result.get("__interrupt__"):
        payload = result["__interrupt__"][0].value
        if auto == "ask" and sys.stdin.isatty():
            decision = input(
                f"  ⏸ interrupt — {payload['사유']} · {payload['총액']:,}원 → approve/reject: "
            ).strip() or "reject"
        else:
            decision = auto if auto in ("approve", "reject") else "reject"
            print(f"  ⏸ interrupt — {payload['사유']} → 자동 '{decision}'")
        # TODO ④: 멈춘 그래프를 사람 결정으로 재개하세요.
        #   graph.invoke(Command(resume=decision), config=config) 형태.
        result = _todo("④ run_one의 Command(resume)")
    return result


def _check() -> int:
    """채운 뒤 자가 점검 — 네 빈칸이 다 맞으면 ✅ 4개."""
    rows: list[tuple[str, bool, str]] = []

    # ① State 필드
    fields = set(getattr(ExerciseState, "__annotations__", {}))
    need = {"doc", "record", "flagged"}
    rows.append(("① State 필드 선언", need <= fields,
                 f"{sorted(need - fields)} 가 빠졌어요" if not (need <= fields) else ""))

    graph = None
    try:
        graph = build_graph()
        cp_ok = getattr(graph, "checkpointer", None) is not None
        rows.append(("② 그래프 연결", True, ""))
        rows.append(("②+ checkpointer", cp_ok,
                     "compile(checkpointer=InMemorySaver())가 빠졌어요" if not cp_ok else ""))
    except NotImplementedError as e:
        rows.append(("② 그래프 연결", False, str(e)))

    # ③④ 흐름으로 검증
    flow_ok, flow_hint = False, "② 먼저"
    if graph is not None:
        try:
            low = run_one(graph, "receipt_small", auto="approve")   # 저액 → interrupt 없음
            hi_app = run_one(graph, "invoice_big", auto="approve")  # 고액 승인 → 적재
            hi_rej = run_one(graph, "invoice_big", auto="reject")   # 고액 반려 → 보류
            flow_ok = (not low.get("__interrupt__")
                       and hi_app.get("flagged") == ""
                       and hi_rej.get("flagged") == "rejected")
            flow_hint = "" if flow_ok else "흐름 결과가 기대와 달라요(approve→적재 / reject→반려)"
        except NotImplementedError as e:
            flow_hint = str(e)
    rows.append(("③④ interrupt → resume", flow_ok, flow_hint))

    print("\n자가 점검")
    for name, ok, hint in rows:
        print(f"  {'✅' if ok else '❌'}  {name}" + (f"   ← {hint}" if hint else ""))
    passed = sum(ok for _, ok, _ in rows)
    print(f"\n  {passed}/{len(rows)} 통과" + ("  — 정답! 그래프를 직접 엮었습니다." if passed == len(rows) else ""))
    return 0 if passed == len(rows) else 1


def main() -> None:
    ap = argparse.ArgumentParser(description="Ch2 StateGraph 빈칸 채우기 실습")
    ap.add_argument("--check", action="store_true", help="네 빈칸을 채웠는지 자가 점검")
    ap.add_argument("--doc", default="invoice_big", help="한 건 실행(기본: 고액 invoice_big)")
    args = ap.parse_args()
    if args.check:
        raise SystemExit(_check())
    graph = build_graph()
    run_one(graph, args.doc, auto="ask")


if __name__ == "__main__":
    main()
