"""Ch1 산출물 — 영수증 한 장을 RecordV1으로 읽어 내는 첫 부품.

애널리스트의 첫 단계는 "문서를 읽고 판단"하는 것이다. 여기서는 영수증 이미지
한 장을 멀티모달 모델에 보여 주고, Ch0에서 못박은 RecordV1 구조로 뽑아낸다.

두 가지 방식을 비교한다.
  - single-shot : 한 번 호출해 결과를 받는다. 빠르지만 합계가 틀려도 그대로 통과.
  - react       : 추출 → 합계 검증(Action) → 어긋나면 한 번 더 고쳐 쓰기. ReAct
                  루프(Thought→Action→Observation)를 가장 작은 형태로 체험한다.

API 키가 없어도 파이프라인을 끝까지 돌려 볼 수 있도록 --mock 을 둔다(매니페스트의
gold 값을 그대로 RecordV1로 적재). 실제 모델 호출은 키가 있을 때 --model 로 한다.

실행:
    uv run python3 ch1-llm-basics/classify_one.py --doc receipt_starbucks.png --mock
    uv run python3 ch1-llm-basics/classify_one.py --doc receipt_gs25.png --react
    uv run python3 ch1-llm-basics/classify_one.py --compare        # 모델 3종 정확도 표
"""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path

import yaml

from analyst import DocType, RecordV1
from analyst.paths import MANIFEST, SAMPLE_INBOX

# 이 과정 기본 실습 모델 + 비교축 (OpenRouter 슬러그)
DEFAULT_MODEL = "google/gemini-3.5-flash"
COMPARE_MODELS = ["google/gemini-3.5-flash", "openai/gpt-5.5", "anthropic/claude-opus-4-8"]


def load_gold(doc: str) -> dict:
    """매니페스트에서 한 문서의 gold(정답) 레코드를 찾는다."""
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    for entry in manifest["docs"]:
        if entry["file"] == doc:
            return entry["gold"]
    raise SystemExit(f"매니페스트에 없는 문서: {doc}")


def gold_to_record(gold: dict) -> RecordV1:
    """gold(한글 키 dict) → RecordV1. 신뢰도는 모델 산출이므로 1.0으로 주입."""
    return RecordV1.model_validate({**gold, "신뢰도": 1.0})


# ── 멀티모달 추출 ────────────────────────────────────────────────

EXTRACT_PROMPT = """너는 영수증·명세서를 읽어 구조화하는 회계 보조다.
이미지를 보고 아래 JSON 스키마에 맞는 객체 하나만 출력한다. 설명은 쓰지 않는다.

{schema}

규칙:
- 금액은 숫자만(쉼표·원 기호 제거). 못 읽은 값은 null.
- 신뢰도는 네가 읽은 확신도를 0~1로.
- 원본경로는 "{source_path}" 로 그대로 둔다.
"""


def _image_data_url(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/png;base64,{b64}"


def extract_singleshot(doc: str, model: str) -> RecordV1:
    """모델에 이미지 한 장을 보여 주고 RecordV1 JSON을 한 번에 받는다."""
    from langchain_openai import ChatOpenAI

    from analyst.schema import schema_json

    key = os.environ.get("OPENROUTER_API_KEY")
    if not key or key == "sk-or-...":
        raise RuntimeError("OPENROUTER_API_KEY 미설정 — .env에 키를 넣거나 --mock 으로 실행")
    path = SAMPLE_INBOX / doc
    llm = ChatOpenAI(
        model=model,
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
        temperature=0,
    )
    prompt = EXTRACT_PROMPT.format(schema=schema_json(), source_path=f"sample_inbox/{doc}")
    msg = llm.invoke(
        [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": _image_data_url(path)}},
                ],
            }
        ]
    )
    raw = msg.content if isinstance(msg.content, str) else str(msg.content)
    return RecordV1.model_validate_json(_strip_fences(raw))


def _strip_fences(text: str) -> str:
    """```json … ``` 울타리를 벗긴다."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```")[1]
        if t.startswith("json"):
            t = t[4:]
    return t.strip()


# ── 합계 검산 (Ch2 파이프라인이 그대로 재사용하는 순수 함수) ──────


def verify_total(rec: RecordV1) -> tuple[bool, float]:
    """항목 합계(수량 반영)가 총액과 맞는지 계산한다. 명세서·은행은 부호가 섞여 영수증에만 쓴다."""
    item_sum = sum((i.amount or 0) * (i.qty or 1) for i in rec.items if (i.amount or 0) > 0)
    return abs(item_sum - rec.total) < 1.0, item_sum


# ── ReAct 에이전트: 모델이 스스로 도구를 호출하고 관측해 보정한다 ──
#
# 진짜 ReAct는 우리가 검증 함수를 부르는 게 아니라, 모델이 추론 끝에 도구 호출을
# 결정하고(Action) 그 결과를 보고(Observation) 다음 행동을 정한다. 아래는 그 루프다.


def _check_sum_tool():
    from langchain_core.tools import tool

    @tool
    def check_receipt_sum(items: list[dict], total: float) -> str:
        """영수증 항목 합계가 총액과 맞는지 검산한다. 추출한 직후 반드시 호출해 확인하라.

        Args:
            items: [{"name": 품목, "amount": 단가(원), "qty": 수량}] 목록
            total: 영수증에 적힌 총액(원)
        """
        s = sum((it.get("amount") or 0) * (it.get("qty") or 1)
                for it in items if (it.get("amount") or 0) > 0)
        ok = abs(s - total) < 1.0
        return (f"항목합={s:,.0f}원, 총액={total:,.0f}원 → "
                + ("일치. 이 추출을 그대로 최종 JSON으로 출력하라."
                   if ok else "불일치. 이미지를 다시 보고 항목이나 수량을 고쳐 재검산하라."))

    return check_receipt_sum


REACT_SYSTEM = """너는 문서를 읽어 RecordV1 JSON으로 정리하는 회계 보조다.
절차: ① 이미지에서 항목과 총액을 추출한다. ② 문서가 영수증이면(항목 합계가 총액과 같아야 하는 문서)
반드시 check_receipt_sum 도구를 호출해 검산한다. 명세서·계약서·리포트처럼 항목합이 총액과 일치하지
않는 게 정상인 문서는 검산이 의미 없으니 도구를 부르지 말고 바로 출력한다. ③ 검산에서 '불일치'가 나오면
이미지를 다시 보고 고친 뒤 다시 검산한다. ④ 검산이 '일치'거나 애초에 검산이 불필요하면 그때
RecordV1 JSON만 출력한다(설명·도구호출 없이)."""


def extract_react(doc: str, model: str, max_steps: int = 5) -> RecordV1:
    """진짜 ReAct 루프 — 모델이 check_receipt_sum을 직접 호출(Action)하고
    관측(Observation)해 스스로 보정한 뒤 최종 JSON을 낸다."""
    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

    from analyst.schema import schema_json

    key = os.environ.get("OPENROUTER_API_KEY")
    if not key or key == "sk-or-...":
        raise RuntimeError("OPENROUTER_API_KEY 미설정 — .env에 키를 넣거나 --mock 으로 실행")

    from langchain_openai import ChatOpenAI

    tool_fn = _check_sum_tool()
    llm = ChatOpenAI(model=model, base_url="https://openrouter.ai/api/v1",
                     api_key=key, temperature=0).bind_tools([tool_fn])

    prompt = EXTRACT_PROMPT.format(schema=schema_json(), source_path=f"sample_inbox/{doc}")
    messages = [
        SystemMessage(content=REACT_SYSTEM),
        HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": _image_data_url(SAMPLE_INBOX / doc)}},
        ]),
    ]

    for _ in range(max_steps):
        ai = llm.invoke(messages)
        messages.append(ai)
        if ai.content and isinstance(ai.content, str) and ai.content.strip() and ai.tool_calls:
            print(f"  [Thought] {ai.content.strip()[:80]}")
        if ai.tool_calls:                                   # Action — 모델이 도구 호출을 결정
            for tc in ai.tool_calls:
                print(f"  [Action] {tc['name']} 호출")
                obs = tool_fn.invoke(tc["args"])            # 런타임이 실제 실행
                print(f"  [Observation] {obs}")
                messages.append(ToolMessage(content=obs, tool_call_id=tc["id"]))
            continue                                        # 관측을 들고 다시 모델에게
        print("  [Final] 검산 통과 — 최종 JSON 출력")        # tool_calls 없음 = 종료
        return RecordV1.model_validate_json(_strip_fences(_as_text(ai.content)))
    raise RuntimeError("ReAct 루프가 max_steps 안에 끝나지 않았다")


def _as_text(content) -> str:
    return content if isinstance(content, str) else str(content)


# ── 채점(모델 비교용) ────────────────────────────────────────────


def score(pred: RecordV1, gold: RecordV1) -> float:
    """핵심 4필드(판매처·총액·날짜·문서유형) 일치율 0~1."""
    checks = [
        pred.merchant.strip() == gold.merchant.strip(),
        abs(pred.total - gold.total) < 1.0,
        pred.doc_date == gold.doc_date,
        pred.doc_type == gold.doc_type,
    ]
    return sum(checks) / len(checks)


def extract(doc: str, model: str, mock: bool, react: bool) -> RecordV1:
    if mock:
        return gold_to_record(load_gold(doc))
    return extract_react(doc, model) if react else extract_singleshot(doc, model)


def main() -> None:
    ap = argparse.ArgumentParser(description="영수증 한 장 → RecordV1")
    ap.add_argument("--doc", default="receipt_starbucks.png", help="sample_inbox 안 파일명")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--mock", action="store_true", help="키 없이 gold로 적재(파이프라인 확인)")
    ap.add_argument("--react", action="store_true", help="합계 검증 루프 사용")
    ap.add_argument("--compare", action="store_true", help="모델 3종 정확도 비교표")
    args = ap.parse_args()

    if args.compare:
        gold = gold_to_record(load_gold(args.doc))
        print(f"문서: {args.doc}  (gold: {gold.merchant}, {gold.total:,.0f}원)\n")
        print(f"{'모델':32} {'정확도':>6}")
        for m in COMPARE_MODELS:
            try:
                acc = score(extract_singleshot(args.doc, m), gold)
                print(f"{m:32} {acc:>6.0%}")
            except Exception as e:  # 키/네트워크 없으면 건너뜀
                print(f"{m:32} {'skip':>6}  ({type(e).__name__})")
        return

    rec = extract(args.doc, args.model, args.mock, args.react)
    print(json.dumps(rec.model_dump(by_alias=True, mode="json"), ensure_ascii=False, indent=2))

    if not args.mock:
        gold = gold_to_record(load_gold(args.doc))
        print(f"\n정확도(핵심 4필드): {score(rec, gold):.0%}")


if __name__ == "__main__":
    main()
