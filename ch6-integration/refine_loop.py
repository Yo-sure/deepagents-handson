"""Ch6 — 루프를 닫는다: generate → verify → refine → 반복 (루프 엔지니어링).

하네스(Ch2~5)는 '한 번 잘 도는 시스템'을 만든다. 루프 엔지니어링은 그 위에
'스스로 고치는 순환'을 얹는다: 검증자가 미달을 잡으면 그 지적을 반영해 다시 만들고,
다시 검증한다 — 통과하거나 반복 상한에 닿을 때까지. 순환의 품질은 검증자가 정한다.

프롬프트 → 컨텍스트 → 하네스 → **루프**. 이 파일은 그 마지막 칸을 결정론으로 보여 준다
(키 불필요). 실무의 refine 단계는 LLM이 검증 피드백을 받아 다시 쓰는 자리(Reflexion)이고,
여기서는 재현성을 위해 규칙으로 재생성한다 — 루프 '구조'가 학습 목표다.

실행:
    uv run python3 ch6-integration/refine_loop.py     # 미달 브리프 → 루프가 PASS로 끌어올린다
전제: workspace/classified/ 에 레코드가 있어야 검증자가 기대값을 계산한다(먼저 Ch2 intake).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ch5-a2a"))
from analyst.paths import CLASSIFIED, WORKSPACE, ensure_workspace
from verifier_agent import verify_brief   # Ch5 검증자 = 루프의 엔진

MAX_ITERS = 3

# 일부러 gap 항목(쿠팡)을 빠뜨린 첫 초안 — 루프가 이걸 스스로 채워 PASS로 만든다.
DRAFT = """# 이번 달 인박스 브리프

### 짚을 점
- 넷플릭스 17,000원 — 구독 추정
"""


#pragma region refine-loop
def refine(brief: str, missing: list[tuple[str, float]]) -> str:
    """검증자가 짚은 누락 항목을 브리프의 '### 짚을 점'에 채워 넣는다(다음 생성).

    실무에선 이 자리에 LLM이 검증 피드백을 받아 다시 쓴다(Reflexion). 여기선 결정론.
    """
    add = "\n".join(f"- {name} {amount:,.0f}원 — 대응 영수증 없음(확인 필요)"
                    for name, amount in missing)
    if "### 짚을 점" in brief:
        return brief.replace("### 짚을 점", "### 짚을 점\n" + add, 1)
    return brief.rstrip() + "\n\n### 짚을 점\n" + add + "\n"


def refine_loop(brief: str, max_iters: int = MAX_ITERS) -> tuple[str, bool]:
    """generate → verify → refine 순환. 통과하거나 상한까지 반복한다."""
    for i in range(1, max_iters + 1):
        ok, _notes, missing = verify_brief(brief)          # ← 검증자가 루프의 게이트
        print(f"  [반복 {i}] 검증: {'PASS' if ok else 'NEEDS_REVISION'}"
              + (f" — 누락 {len(missing)}건" if missing else ""))
        if ok:
            return brief, True                             # 통과 → 순환 종료
        brief = refine(brief, missing)                     # ← 지적을 반영해 다시 만든다
        print(f"           교정 반영 → {', '.join(n for n, _ in missing)}")
    return brief, verify_brief(brief)[0]
#pragma endregion refine-loop


def main() -> None:
    if not CLASSIFIED.exists() or not any(CLASSIFIED.glob("*.json")):
        print("workspace/classified/ 가 비어 있습니다. 먼저 Ch2 intake를 실행하세요.")
        raise SystemExit(1)
    print("▶ 루프: generate → verify → refine (검증 통과까지)")
    refined, ok = refine_loop(DRAFT)
    print(f"\n최종: {'PASS — 루프가 미달 초안을 통과로 끌어올렸다' if ok else 'FAIL — 상한 도달'}")
    ensure_workspace()
    out = WORKSPACE / "refined_brief.md"
    out.write_text(refined, encoding="utf-8")
    print(f"  → {out.relative_to(WORKSPACE.parent)}")


if __name__ == "__main__":
    main()
