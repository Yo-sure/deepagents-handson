"""Ch6 핸즈온 — 경계 어댑터를 확인하고 변형한다.

캡스톤의 핵심 명제는 "RecordV1과 디렉터리 규약을 만족하는 모듈만 교체할 수 있다"이다.
경계 어댑터는 외부 입력 표기를 계약의 타입으로 바꾸는 얇은 코드다.

외부에서 들어온 금액은 "11,500원" · "₩1,650,000" 같은 문자열일 수 있다. 하지만 파이프라인
계약은 total: float을 요구한다. coerce_amount는 그 경계 변환의 레퍼런스 구현이다.
학생은 검증 케이스를 추가하거나 규칙을 바꿔 보며 "입력원과 RecordV1 사이"의 어댑터 위치를 익힌다.

    uv run python3 ch6-integration/exercise_adapter.py    # [PASS]
"""

from __future__ import annotations

import re  # 힌트 ②의 re.sub 용 — 미리 import 해 둔다


#pragma region coerce
def coerce_amount(raw: object) -> float:
    """외부 금액 표기 → 계약의 float.

    들어올 수 있는 것: "11,500원" · "₩1,650,000" · "결제금액: 205,900원" · 8400(이미 숫자) · "1,234.5"
    돌려줄 것: 8400.0 같은 float.

    구현 원칙:
      ① 이미 int/float이면 그대로 float()로.
      ② 문자열이면 숫자·소수점만 남기고(₩·원·콤마·공백 제거) float()로.
    """
    if isinstance(raw, (int, float)):
        return float(raw)
    cleaned = re.sub(r"[^0-9.]", "", str(raw))
    if not cleaned:
        raise ValueError(f"금액을 읽을 수 없습니다: {raw!r}")
    return float(cleaned)
#pragma endregion coerce


# ── 검증 케이스(고치지 마세요) — 경계에서 실제로 마주치는 표기들 ──
CASES = [
    ("11,500원", 11500.0),
    ("₩1,650,000", 1650000.0),
    ("결제금액: 205,900원", 205900.0),
    (8400, 8400.0),
    ("1,234.5", 1234.5),
]


def main() -> None:
    print("▶ 경계 어댑터 검증 — coerce_amount\n")
    all_ok = True
    for raw, want in CASES:
        try:
            got = coerce_amount(raw)
        except ValueError as e:
            print(f"  ❌ {e}")
            all_ok = False
            continue
        ok = isinstance(got, float) and abs(got - want) < 1e-6
        all_ok = all_ok and ok
        print(f"  {'✅' if ok else '❌'} coerce_amount({raw!r}) = {got!r}   (기대 {want})")
    if all_ok:
        print("\n[PASS] 경계 어댑터 검증 통과")
        print("       위 5개 입력 표기를 모두 계약의 float 값으로 변환했습니다.")
    else:
        print("\n[FAIL] 일부 케이스가 어긋납니다 — 콤마·₩·원·공백을 모두 제거했는지 확인하세요.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
