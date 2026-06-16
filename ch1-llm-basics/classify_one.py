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


# ── ReAct: 합계를 스스로 검증하는 가장 작은 루프 ──────────────────


def verify_total(rec: RecordV1) -> tuple[bool, float]:
    """Action — 항목 합계가 총액과 맞는지 계산한다(Observation 생성).

    명세서·은행거래는 부호가 섞여 합계 규칙이 다르므로 영수증에만 적용한다.
    """
    item_sum = sum((i.amount or 0) * (i.qty or 1) for i in rec.items if (i.amount or 0) > 0)
    return abs(item_sum - rec.total) < 1.0, item_sum


def extract_react(doc: str, model: str, max_loops: int = 2) -> RecordV1:
    """추출 → 합계 검증 → 어긋나면 다시 추출. ReAct 한 바퀴를 직접 돈다."""
    rec = extract_singleshot(doc, model)
    if rec.doc_type != DocType.receipt.value:
        return rec
    for loop in range(max_loops):
        ok, item_sum = verify_total(rec)
        print(f"  [Observation] 항목합={item_sum:,.0f} / 총액={rec.total:,.0f} → {'일치' if ok else '불일치'}")
        if ok:
            break
        print("  [Thought] 합계가 안 맞는다. 항목을 다시 읽어 보정한다.")
        rec = extract_singleshot(doc, model)  # 실제로는 관찰을 프롬프트에 덧붙여 재요청
    return rec


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
            except Exception as e:  # noqa: BLE001 — 키/네트워크 없으면 건너뜀
                print(f"{m:32} {'skip':>6}  ({type(e).__name__})")
        return

    rec = extract(args.doc, args.model, args.mock, args.react)
    print(json.dumps(rec.model_dump(by_alias=True, mode="json"), ensure_ascii=False, indent=2))

    if not args.mock:
        gold = gold_to_record(load_gold(args.doc))
        print(f"\n정확도(핵심 4필드): {score(rec, gold):.0%}")


if __name__ == "__main__":
    main()
