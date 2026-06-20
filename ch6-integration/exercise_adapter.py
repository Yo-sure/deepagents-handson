"""Ch6 핸즈온 — 경계 어댑터를 직접 채운다 (스캐폴드).

캡스톤의 핵심 명제는 "계약(RecordV1)이 부품 교체의 자유를 준다"이다. 그 자유의 대가는
**경계 어댑터** — 바깥세상의 제멋대로인 표기를 계약의 타입으로 바꾸는 얇은 코드다.

외부에서 들어온 금액은 "11,500원" · "₩1,650,000" 같은 문자열일 수 있다. 하지만 파이프라인
계약은 total: float을 요구한다. 이 경계를 잇는 coerce_amount를 네가 채워야 파이프가 [PASS]로
살아난다. 지금은 NotImplementedError로 끊겨 있다 — 아래 TODO를 5~10줄로 채워라.

    uv run python3 ch6-integration/exercise_adapter.py    # 채우기 전: ✗ / 채운 뒤: [PASS]
"""

from __future__ import annotations


#pragma region coerce
def coerce_amount(raw: object) -> float:
    """바깥 금액 표기 → 계약의 float.

    들어올 수 있는 것: "11,500원" · "₩1,650,000" · "89,000 원" · 8400(이미 숫자) · "1,234.5"
    돌려줄 것: 8400.0 같은 float.

    TODO: 너의 5~10줄.
      힌트 ① 이미 int/float이면 그대로 float()로.
      힌트 ② 문자열이면 숫자·소수점만 남기고(₩·원·콤마·공백 제거) float()로.
             정규식 re.sub(r"[^0-9.]", "", s) 가 한 줄로 해결한다.
    """
    raise NotImplementedError("coerce_amount를 채우세요 — 위 docstring의 힌트를 보라")
#pragma endregion coerce


# ── 검증 케이스(고치지 마세요) — 경계에서 실제로 마주치는 표기들 ──
CASES = [
    ("11,500원", 11500.0),
    ("₩1,650,000", 1650000.0),
    ("89,000 원", 89000.0),
    (8400, 8400.0),
    ("1,234.5", 1234.5),
]


def main() -> None:
    print("▶ 경계 어댑터 검증 — coerce_amount\n")
    all_ok = True
    for raw, want in CASES:
        try:
            got = coerce_amount(raw)
        except NotImplementedError as e:
            print(f"  ✗ {e}")
            print("\n[FAIL] 아직 채우지 않았습니다 — coerce_amount의 TODO를 채우고 다시 실행하세요.")
            raise SystemExit(1)
        ok = isinstance(got, float) and abs(got - want) < 1e-6
        all_ok = all_ok and ok
        print(f"  {'✅' if ok else '❌'} coerce_amount({raw!r}) = {got!r}   (기대 {want})")
    if all_ok:
        print("\n[PASS] 경계 어댑터 완성 — 이제 어떤 표기로 들어와도 계약(float)으로 흐른다.")
        print("       부품(목·실선)을 바꿔도 이 한 겹만 맞으면 파이프 전체가 그대로 돈다.")
    else:
        print("\n[FAIL] 일부 케이스가 어긋납니다 — 콤마·₩·원·공백을 모두 제거했는지 확인하세요.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
