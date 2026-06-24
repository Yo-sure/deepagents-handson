"""Ch1 산출물 — 문서 한 장을 RecordV1으로 읽어 내는 첫 모듈.

애널리스트의 첫 단계는 "문서를 읽고 판단"하는 것이다. 여기서는 영수증 이미지와
PDF 문서를 멀티모달 모델에 보여 주고, Ch0에서 못박은 RecordV1 구조로 뽑아낸다.

두 가지 방식을 비교한다.
  - single-shot : 한 번 호출해 결과를 받는다. 빠르지만 합계가 틀려도 그대로 통과.
  - react       : 추출 → 합계 검증(Action) → 어긋나면 한 번 더 고쳐 쓰기. ReAct
                  루프(Thought→Action→Observation)를 가장 작은 형태로 체험한다.

기본은 실제 모델 호출이다. API 키·네트워크·모델 문제와 코드 경로 문제를 분리해 볼 수
있도록 --mock 을 보조로 둔다(매니페스트의 gold 값을 그대로 RecordV1로 출력).

실행:
    uv run python3 ch1-llm-basics/classify_one.py --doc receipt_starbucks.png
    uv run python3 ch1-llm-basics/classify_one.py --doc receipt_gs25.png --react
    uv run python3 ch1-llm-basics/classify_one.py --doc receipt_starbucks.png --mock
    uv run python3 ch1-llm-basics/classify_one.py --compare        # 모델 비교 표
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

from analyst import DocType, RecordV1
from analyst.paths import MANIFEST, SAMPLE_INBOX

load_dotenv()

# 이 과정 기본 실습 모델. 비교 모델은 수업 당일 계정에서 되는 슬러그를 환경변수로 확장한다.
DEFAULT_MODEL = os.environ.get("ANALYST_MODEL", "google/gemini-3.1-flash-lite")
COMPARE_MODELS = [
    m.strip() for m in os.environ.get("ANALYST_COMPARE_MODELS", DEFAULT_MODEL).split(",")
    if m.strip()
]


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
문서를 보고 아래 JSON 스키마에 맞는 객체 하나만 출력한다. 설명은 쓰지 않는다.

{schema}

규칙:
- 금액은 숫자만(쉼표·원 기호 제거). 최상위 금액을 못 읽었거나 금액이 없는 리포트는 0.
- 은행 입출금 명세서처럼 입금·출금 거래줄만 있고 문서 전체의 청구액/합계액이 따로 없는 문서는 최상위 금액을 0으로 둔다. 거래줄은 항목에 넣고, 출금은 음수로 둔다.
- 판매처/발행처는 문서에 한글 공식명이 보이면 한글명을 우선한다(예: kakaobank가 아니라 카카오뱅크).
- 계약서의 판매처/발행처는 용역대금을 지급하는 발주처·갑·회사명을 우선한다. 개인 수급자·을·서명자는 판매처로 쓰지 않는다.
- 날짜는 문서 발행일/작성일/명세서 작성일을 우선한다. 카드 명세서의 이용기간 종료일·사용기간 종료일·결제예정일·납부기한은 문서 날짜로 쓰지 않는다.
- 계약서의 금액이 "월", "매월" 같은 주기 단가로 적혀 있으면 그 단가를 최상위 금액으로 둔다. 계약기간 개월 수를 곱해 총계약액을 만들지 않는다.
- 항목 금액처럼 null 허용 필드만 못 읽은 값을 null로 둔다.
- 항목 안의 금액은 수량을 곱하기 전 단가다. 라인 총액만 보이면 수량으로 나누어 단가를 적는다.
- 청구서·명세서에 공급가액과 부가세가 따로 보이면 항목을 둘로 분리한다.
- 신뢰도는 네가 읽은 확신도를 0~1로.
- 원본경로는 "{source_path}" 로 그대로 둔다.
"""


def _document_data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def _document_content_part(path: Path) -> dict:
    data_url = _document_data_url(path)
    if path.suffix.lower() == ".pdf":
        return {"type": "file", "file": {"filename": path.name, "file_data": data_url}}
    return {"type": "image_url", "image_url": {"url": data_url}}


#pragma region singleshot
def extract_singleshot(doc: str, model: str) -> RecordV1:
    """모델에 문서 한 장을 보여 주고 RecordV1 JSON을 한 번에 받는다."""
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
                    _document_content_part(path),
                ],
            }
        ]
    )
    raw = msg.content if isinstance(msg.content, str) else str(msg.content)
    return RecordV1.model_validate_json(_strip_fences(raw))
#pragma endregion singleshot


def _strip_fences(text: str) -> str:
    """```json … ``` 울타리와 앞뒤 설명을 걷어내 JSON 객체 본문만 남긴다."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```")[1]
        if t.startswith("json"):
            t = t[4:]
    t = t.strip()
    if t.startswith("{") and t.endswith("}"):
        return t
    start, end = t.find("{"), t.rfind("}")
    if start != -1 and end != -1 and start < end:
        return t[start:end + 1]
    return t


# ── 합계 검산 (Ch2 파이프라인이 그대로 재사용하는 순수 함수) ──────


def verify_total(rec: RecordV1, tol: float = 1.0) -> tuple[bool, float]:
    """항목 합계(수량 반영)가 총액과 맞는지 계산한다. 명세서·은행은 부호가 섞여 영수증에만 쓴다.

    tol = 허용 오차(원). 부동소수 반올림을 흡수한다. tol=0.0이면 1원만 어긋나도 실패.
    """
    item_sum = sum((i.amount or 0) * (i.qty or 1) for i in rec.items if (i.amount or 0) > 0)
    return abs(item_sum - rec.total) < tol, item_sum


class ReceiptToolItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, description="품목명")
    amount: float = Field(description="항목 1개 단가(원). 라인 총액이 아님")
    qty: float = Field(default=1.0, description="수량")


class CheckReceiptSumInput(BaseModel):
    """check_receipt_sum 도구 입력."""

    items: list[ReceiptToolItem] = Field(description="영수증 품목 목록")
    total: float = Field(description="영수증에 적힌 총액(원)")


CheckReceiptSumInput.model_rebuild(_types_namespace={"ReceiptToolItem": ReceiptToolItem})


def _coerce_tool_items(items: list[ReceiptToolItem | dict]) -> list[ReceiptToolItem]:
    parsed = []
    for item in items:
        parsed.append(item if isinstance(item, ReceiptToolItem)
                      else ReceiptToolItem.model_validate(item))
    return parsed


# ── ReAct 에이전트: 모델이 도구 호출 여부를 정하고 관측해 보정한다 ──
#
# ReAct는 우리가 검증 함수를 직접 부르는 게 아니라, 모델이 추론 끝에 도구 호출을
# 결정하고(Action) 그 결과를 보고(Observation) 다음 행동을 정한다. 아래는 그 루프다.


def _receipt_sum_observation(
    items: list[ReceiptToolItem | dict],
    total: float,
    tol: float = 1.0,
) -> tuple[bool, str]:
    parsed = _coerce_tool_items(items)
    s = sum(item.amount * item.qty for item in parsed if item.amount > 0)
    ok = abs(s - total) < tol
    # 관측(Observation)은 사실만 보고한다. '그럼 어떻게 하라'(일치→출력 / 불일치→재검산)는
    # 시스템 프롬프트의 정책이고, 다음 행동은 모델이 이 사실을 보고 스스로 정한다.
    obs = (f"항목합={s:,.0f}원, 총액={total:,.0f}원 → "
           + ("일치" if ok else f"불일치(차이 {abs(s - total):,.0f}원)"))
    return ok, obs


def is_receipt_doc(doc: str, rec: RecordV1 | None = None) -> bool:
    if rec and rec.doc_type == DocType.receipt:
        return True
    # 샘플 인박스는 파일명으로 문서군을 드러낸다. gold 정답은 mock 적재와 채점에만 쓴다.
    return Path(doc).stem.startswith("receipt_")


def _check_sum_tool():
    from langchain_core.tools import tool

#pragma region react-tool
    @tool(args_schema=CheckReceiptSumInput)
    def check_receipt_sum(items: list[ReceiptToolItem], total: float) -> str:
        """영수증 항목 합계가 총액과 맞는지 검산한다. 영수증으로 판단될 때 호출한다.

        Args:
            items: [{"name": 품목, "amount": 단가(원), "qty": 수량}] 목록.
            total: 영수증에 적힌 총액(원)
        """
        return _receipt_sum_observation(items, total)[1]
#pragma endregion react-tool

    return check_receipt_sum


REACT_SYSTEM = """너는 문서를 읽어 RecordV1 JSON으로 정리하는 회계 보조다.
절차: ① 문서에서 항목과 총액을 추출한다. ② 문서가 영수증이면(항목 합계가 총액과 같아야 하는 문서)
반드시 check_receipt_sum 도구를 호출해 검산한다. 명세서·계약서·리포트처럼 항목합이 총액과 일치하지
않는 게 정상인 문서는 검산이 의미 없으니 도구를 부르지 말고 바로 출력한다. ③ 검산에서 '불일치'가 나오면
문서를 다시 보고 고친 뒤 다시 검산한다. ④ 검산이 '일치'거나 애초에 검산이 불필요하면 그때
RecordV1 JSON만 출력한다(설명·도구호출 없이)."""


def extract_react(doc: str, model: str, max_steps: int = 5) -> RecordV1:
    """ReAct 루프 — 모델이 check_receipt_sum 호출(Action)을 결정하고
    관측(Observation) 결과를 반영해 최종 JSON을 낸다."""
    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

    from analyst.schema import schema_json

    key = os.environ.get("OPENROUTER_API_KEY")
    if not key or key == "sk-or-...":
        raise RuntimeError("OPENROUTER_API_KEY 미설정 — .env에 키를 넣거나 --mock 으로 실행")

    from langchain_openai import ChatOpenAI

#pragma region react-loop
    tool_fn = _check_sum_tool()
    llm = ChatOpenAI(model=model, base_url="https://openrouter.ai/api/v1",
                     api_key=key, temperature=0).bind_tools([tool_fn])

    prompt = EXTRACT_PROMPT.format(schema=schema_json(), source_path=f"sample_inbox/{doc}")
    messages = [
        SystemMessage(content=REACT_SYSTEM),
        HumanMessage(content=[
            {"type": "text", "text": prompt},
            _document_content_part(SAMPLE_INBOX / doc),
        ]),
    ]

    verified: bool | None = None                            # None=검산 없음, True/False=마지막 검산 결과
    for _ in range(max_steps):
        ai = llm.invoke(messages)
        messages.append(ai)
        if ai.content and isinstance(ai.content, str) and ai.content.strip() and ai.tool_calls:
            print(f"  [Thought] {ai.content.strip()[:80]}")
        if ai.tool_calls:                                   # Action — 모델이 도구 호출을 결정
            for tc in ai.tool_calls:
                print(f"  [Action] {tc['name']} 호출")
                if tc["name"] == "check_receipt_sum":
                    verified, obs = _receipt_sum_observation(**tc["args"])
                else:
                    obs = tool_fn.invoke(tc["args"])        # 런타임이 실제 실행
                print(f"  [Observation] {obs}")
                messages.append(ToolMessage(content=obs, tool_call_id=tc["id"]))
            continue                                        # 관측을 들고 다시 모델에게
        rec = RecordV1.model_validate_json(_strip_fences(_as_text(ai.content)))
        must_verify = is_receipt_doc(doc, rec)
        if must_verify and verified is None:
            raise RuntimeError("영수증인데 check_receipt_sum 검산 없이 최종 JSON을 냈습니다")
        final_ok, final_sum = verify_total(rec)
        if must_verify and (verified is False or not final_ok):
            raise RuntimeError("검산 불일치 — 모델이 재검산 없이 최종 JSON을 냈습니다")
        # tool_calls 없음 = 종료. 검산 대상 여부와 마지막 검산 상태를 분리해 보여 준다.
        if verified is True:
            final_status = "검산 통과"
        elif verified is False:
            final_status = "마지막 검산 불일치였으나 최종 유형은 검산 대상 아님"
        else:
            final_status = "검산 불필요(영수증 아님)"
        print(f"  [Final] {final_status} — 최종 JSON 출력")
        return rec
    raise RuntimeError("ReAct 루프가 max_steps 안에 끝나지 않았다")
#pragma endregion react-loop


def _as_text(content) -> str:
    return content if isinstance(content, str) else str(content)


# ── 채점(모델 비교용) ────────────────────────────────────────────


def score(pred: RecordV1, gold: RecordV1) -> float:
    """핵심 필드와 항목 구조 일치율 0~1."""
    def item_key(item) -> tuple[str, float, float]:
        return (item.name.strip(), round(float(item.amount or 0), 2), round(float(item.qty or 1), 2))

    pred_items = {item_key(i) for i in pred.items}
    gold_items = {item_key(i) for i in gold.items}
    checks = [
        pred.merchant.strip() == gold.merchant.strip(),
        abs(pred.total - gold.total) < 1.0,
        pred.doc_date == gold.doc_date,
        pred.doc_type == gold.doc_type,
        len(pred.items) == len(gold.items),
        pred_items == gold_items,
    ]
    return sum(checks) / len(checks)


def classify_error(e: Exception) -> str:
    """모델 비교표에서 학생이 바로 원인을 좁힐 수 있게 오류를 분류한다."""
    text = str(e).lower()
    if "openrouter_api_key" in text or "401" in text or "unauthorized" in text:
        return "auth/key"
    if "402" in text or "credit" in text or "payment" in text:
        return "credit"
    if "404" in text or "model" in text and "not found" in text:
        return "model-slug"
    if "json" in text or "validation" in text:
        return "json/schema"
    return type(e).__name__


def _print_mock_react_trace(rec: RecordV1) -> None:
    """키 없이도 ReAct 루프의 모양을 그대로 보여 준다 — gold로 검산 한 번을 재현.

    실제 루프(extract_react)와 똑같은 Action/Observation/Final 문자열을 찍는다. 차이는
    '모델이 도구를 부를지 정하는' 부분이 없다는 것뿐 — mock은 영수증이면 무조건 한 번 검산한다.
    """
    ok, item_sum = verify_total(rec)
    is_receipt = rec.doc_type == DocType.receipt          # 영수증만 합계 검산 대상
    if is_receipt:
        print("  [Action] check_receipt_sum 호출")
        verdict = "일치" if ok else f"불일치(차이 {abs(item_sum - rec.total):,.0f}원)"
        print(f"  [Observation] 항목합={item_sum:,.0f}원, 총액={rec.total:,.0f}원 → {verdict}")
    if is_receipt and not ok:
        raise RuntimeError("검산 불일치 — mock gold 레코드의 항목합과 총액이 맞지 않습니다")
    else:
        print(f"  [Final] {'검산 통과' if is_receipt else '검산 불필요(영수증 아님)'} — 최종 JSON 출력")


def extract(doc: str, model: str, mock: bool, react: bool) -> RecordV1:
    if mock:
        rec = gold_to_record(load_gold(doc))
        if react:                                       # 키 없이도 루프 모양을 재현
            _print_mock_react_trace(rec)
        return rec
    return extract_react(doc, model) if react else extract_singleshot(doc, model)


def main() -> None:
    ap = argparse.ArgumentParser(description="문서 한 장 → RecordV1")
    ap.add_argument("--doc", default="receipt_starbucks.png", help="sample_inbox 안 파일명")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--mock", action="store_true", help="키 없이 gold RecordV1 출력(진단/오프라인 확인)")
    ap.add_argument("--react", action="store_true", help="합계 검증 루프 사용")
    ap.add_argument("--compare", action="store_true", help="모델 정확도 비교표(ANALYST_COMPARE_MODELS로 확장)")
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
                print(f"{m:32} {'skip':>6}  ({classify_error(e)})")
        return

    rec = extract(args.doc, args.model, args.mock, args.react)
    print(json.dumps(rec.model_dump(by_alias=True, mode="json"), ensure_ascii=False, indent=2))

    if not args.mock:
        gold = gold_to_record(load_gold(args.doc))
        print(f"\n정확도(핵심 필드+항목): {score(rec, gold):.0%}")


if __name__ == "__main__":
    main()
