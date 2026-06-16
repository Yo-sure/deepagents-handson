"""데이터 계약 자체검증.

1) sample_inbox 정답(gold)이 전부 RecordV1을 통과하는가
2) 영수증/세금계산서의 금액 = 항목 합계인가
3) 데이터셋이 상호일관인가 — 카드명세서 거래줄이 개별 영수증과 금액 일치

    uv run python -m analyst.tests.test_contract   (또는 pytest)
"""

from __future__ import annotations

import yaml

from analyst import paths
from analyst.schema import DocType, RecordV1


def _load():
    data = yaml.safe_load(paths.MANIFEST.read_text(encoding="utf-8"))
    return data["docs"]


def test_gold_conforms_to_recordv1():
    for d in _load():
        gold = dict(d["gold"])
        gold.setdefault("신뢰도", 1.0)  # gold = 확실 → 1.0 주입(신뢰도는 본래 모델 산출)
        RecordV1.model_validate(gold)  # alias 입력, 실패 시 예외


def test_amounts_equal_item_sum():
    for d in _load():
        gold = d["gold"]
        if gold["문서유형"] not in (DocType.receipt.value, "세금계산서") and d["file"] != "invoice_photo.png":
            continue
        if not gold["항목"]:
            continue
        s = sum(int(it["금액"]) * int(it.get("수량", 1)) for it in gold["항목"])
        assert s == int(gold["금액"]), f'{d["file"]}: 항목합 {s} != 금액 {gold["금액"]}'


def test_card_statement_matches_receipts():
    docs = {d["file"]: d["gold"] for d in _load()}
    card = docs["statement_card_2026-05.pdf"]
    by_merchant = {it["이름"]: int(it["금액"]) for it in card["항목"]}
    # 카드명세서 거래줄 ↔ 개별 영수증 총액 일치
    pairs = {
        "스타벅스 강남R점": "receipt_starbucks.png",
        "GS25 역삼점": "receipt_gs25.png",
        "광화문 국밥": "receipt_restaurant.png",
        "올리브영 강남본점": "receipt_oliveyoung.png",
        "카카오T 택시": "receipt_taxi.png",
    }
    for merchant, file in pairs.items():
        assert by_merchant[merchant] == int(docs[file]["금액"]), f"{merchant}: 명세서↔영수증 불일치"
    # 명세서엔 있으나 영수증 없는 '쿠팡 89,000' = Ch3 조사 대상 (의도된 갭)
    assert "쿠팡(주)" in by_merchant and by_merchant["쿠팡(주)"] == 89000


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  OK  {name}")
            n += 1
    print(f"\n계약 자체검증 통과: {n}건 · 문서 {len(_load())}건")
