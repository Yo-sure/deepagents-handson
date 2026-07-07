"""Ch4 실습 B — Skill을 직접 배선한다 (빈칸 채우기).

Skill = SKILL.md(앞머리 name·description + 본문 절차) + 그걸 발견하는 SkillsMiddleware.
'점진 공개 1단계'는 미들웨어가 시작 시(before_agent) 각 SKILL.md의 앞머리만 읽어
목록에 싣는 것이다. 채울 칸은 둘:

  ① SKILL.md 앞머리 — name·description  (name은 반드시 디렉터리 이름과 같아야 발견된다)
  ② SkillsMiddleware로 그 스킬을 발견 — before_agent hook 호출

키·네트워크 불필요. 스킬이 발견되면 완성이다:

    uv run python3 ch4-skills-mcp/exercise_skill.py --check

막히면 정답: skill_agent.py 의 show_progressive_disclosure() + ch4-skills-mcp/inbox-brief/SKILL.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from analyst.paths import ensure_workspace

SKILL_NAME = "inbox-alert"
SKILL_SRC_REL = "workspace/_exercise_skill"          # REPO 기준 상대 경로(스킬들의 부모)
SKILL_DIR = REPO / SKILL_SRC_REL / SKILL_NAME        # 디렉터리 이름 = 스킬 이름


def _todo(n: str):
    raise NotImplementedError(f"TODO {n} — 채우세요 (정답: skill_agent.py / inbox-brief/SKILL.md)")


# ── 빈칸 ① : SKILL.md 앞머리를 채우세요. ───────────────────────────
# TODO ①: 아래 ___ 두 곳을 채우세요.
#   name        은 반드시 "inbox-alert"(= 디렉터리 이름)이어야 발견됩니다.
#   description 은 이 스킬이 언제 쓰이는지 한 줄(발견의 핵심 필드).
SKILL_MD = """---
name: ___
description: ___
---

# 인박스 경보
영수증 없는 카드 결제가 있으면 브리프의 '짚을 점'에 한 줄로 올린다.
"""


def build_skill() -> None:
    """SKILL.md를 스킬 디렉터리에 쓴다(이미 채워져 있음 — 너는 위 SKILL_MD만 채우면 된다)."""
    SKILL_DIR.mkdir(parents=True, exist_ok=True)
    (SKILL_DIR / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")


def discover_skill() -> list:
    """SkillsMiddleware로 위 스킬을 발견해 metadata 목록을 돌려준다(before_agent hook)."""
    from deepagents.backends import FilesystemBackend
    from deepagents.middleware.skills import SkillsMiddleware

    backend = FilesystemBackend(root_dir=str(REPO), virtual_mode=True)
    # ── 빈칸 ② : SkillsMiddleware를 만들고 before_agent로 발견하세요. ──
    # TODO ②: sources에 스킬들의 부모(SKILL_SRC_REL)를 주고, before_agent를 불러
    #         skills_metadata를 돌려받으세요.
    #   힌트:
    #   mw = SkillsMiddleware(backend=backend, sources=[SKILL_SRC_REL])
    #   return (mw.before_agent({}, None, {}) or {}).get("skills_metadata", [])
    _todo("②")


def check() -> None:
    ensure_workspace()
    build_skill()
    if "___" in SKILL_MD:
        print("  ⬜ ① SKILL.md 앞머리에 ___ 가 남아 있습니다 — name·description을 채우세요.")
        print("\n결과: 0/2 — 빈칸 ①부터")
        return
    print("  ✅ ① SKILL.md 앞머리 채움")
    try:
        skills = discover_skill()
    except NotImplementedError as e:
        print(f"  ⬜ ② {e}")
        print("\n결과: 1/2 — 다음은 빈칸 ②")
        return
    names = {s["name"] for s in skills}
    ok = SKILL_NAME in names
    print(f"  {'✅' if ok else '⬜'} ② SkillsMiddleware가 '{SKILL_NAME}' 발견: {'예' if ok else '아니오'}")
    if ok:
        s = next(x for x in skills if x["name"] == SKILL_NAME)
        print(f"     → description: {s['description']}")
        print("     (본문은 아직 안 읽음 — description이 작업과 맞을 때 read_file = 점진 공개)")
    print("\n결과: " + ("2/2  🎉 Skill 완성!" if ok
                        else "미완성 — name이 디렉터리 이름(inbox-alert)과 같아야 발견됩니다"))


if __name__ == "__main__":
    check()
