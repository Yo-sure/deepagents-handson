"""Ch4 산출물 — Skill이 "어떻게 읽히는지"를 코드로 보여 준다.

deepagents의 **SkillsMiddleware**가 핵심이다. 에이전트가 시작할 때(before_agent)
스킬 디렉터리를 훑어 SKILL.md 앞머리(frontmatter)의 name·description만 시스템
프롬프트에 싣는다(1단계). 본문은 모델이 "이 작업에 맞다"고 판단할 때 read_file로
가져오고(2단계), references/*.md는 본문이 가리킬 때만 펼친다(3단계). 이게 컨텍스트를
아끼는 progressive disclosure다 — Skill이 100개여도 1단계는 각 수십 토큰뿐이다.

    uv run python3 ch4-skills-mcp/skill_agent.py --show   # 미들웨어가 무엇을 싣는지 (키 불필요)
    uv run python3 ch4-skills-mcp/skill_agent.py --run    # 에이전트가 실제로 읽어 쓰는지 (키 필요)
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
# 스킬 소스 = 스킬들이 모인 디렉터리. 그 하위 디렉터리 하나가 스킬 하나(SKILL.md 보유)다.
# 스펙 규칙: 스킬 이름(name)은 디렉터리 이름과 같아야 한다 — 그래서 inbox-brief/ 안에 name: inbox-brief.
SKILLS_SOURCE = "ch4-skills-mcp"


def prepare_runtime_view() -> Path:
    """Expose only workspace outputs and the skill package to the file backend."""
    from analyst.paths import WORKSPACE, ensure_workspace

    ensure_workspace()
    root = WORKSPACE / "_skill_runtime"
    if root.exists():
        shutil.rmtree(root)
    (root / "ch4-skills-mcp").mkdir(parents=True)
    shutil.copytree(REPO / "ch4-skills-mcp" / "inbox-brief", root / "ch4-skills-mcp" / "inbox-brief")
    if WORKSPACE.exists():
        shutil.copytree(WORKSPACE, root / "workspace", ignore=shutil.ignore_patterns("_skill_runtime"))
    return root


def sync_runtime_brief(runtime_root: Path) -> None:
    from analyst.paths import BRIEF

    generated = runtime_root / "workspace" / "brief.md"
    if generated.exists():
        BRIEF.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(generated, BRIEF)


def show_progressive_disclosure() -> None:
    """SkillsMiddleware가 시작 시 하는 일을 그대로 재현한다 — 앞머리만 읽어 싣는다."""
    from deepagents.backends import FilesystemBackend
    from deepagents.middleware.skills import SkillsMiddleware

    # 실제 에이전트 실행은 아래 run_agent처럼 virtual_mode=True와 좁은 runtime view를 쓴다.
    backend = FilesystemBackend(root_dir=str(REPO), virtual_mode=True)
    skills_mw = SkillsMiddleware(backend=backend, sources=[SKILLS_SOURCE])

    print("[1단계] 시작 시 시스템 프롬프트에 오르는 것 — 메타데이터만\n")
    for skill_dir in sorted((REPO / SKILLS_SOURCE).iterdir()):
        md = skill_dir / "SKILL.md"
        if not md.exists():
            continue
        text = md.read_text(encoding="utf-8")
        fm = yaml.safe_load(text.split("---")[1])  # 미들웨어가 읽는 것도 이 앞머리다
        print(f"  • {fm['name']}  (dir: {skill_dir.name})")
        print(f"    description: {fm['description']}")
        # 표준 스키마의 나머지 필드 — 있으면 그대로 보여 준다(없으면 건너뜀).
        if fm.get("license"):
            print(f"    license: {fm['license']}")
        if fm.get("allowed-tools"):
            print(f"    allowed-tools: {fm['allowed-tools']}  (실험적 — 제한이 아니라 사전승인)")
        if fm.get("metadata"):
            print(f"    metadata: {fm['metadata']}  (version·author는 표준상 여기 들어간다)")
        print(f"    path: {md.relative_to(REPO)}")
        print(f"    (본문 {len(text.splitlines())}줄은 아직 안 읽음 — description이 작업과 맞을 때 read_file)\n")

    print("[2단계] 모델이 'description이 내 작업과 맞다' → read_file(path, limit=1000)로 본문을 가져온다.")
    print("[3단계] 본문이 references/*.md를 가리키면 그때만 그 파일을 read_file 한다.\n")
    print(f"미들웨어({type(skills_mw).__name__})가 시스템 프롬프트에 'Skills System' 섹션으로 위 목록을 싣고,")
    print("'필요할 때 read_file로 본문을 읽으라'는 사용법까지 함께 주입한다.")


def run_agent() -> None:
    """실제 deep agent에 스킬을 붙여 돌린다 — read_file(SKILL.md)가 점진 공개의 증거다."""
    import os

    sys.path.insert(0, str(REPO))
    from analyst import RecordV1  # .env 로드 + 계약 확인  # noqa: F401

    key = os.environ.get("OPENROUTER_API_KEY")
    if not key or key == "sk-or-...":
        raise SystemExit("OPENROUTER_API_KEY 미설정 — 먼저 --show 로 메커니즘만 확인하세요.")

    from deepagents import create_deep_agent
    from deepagents.backends import FilesystemBackend
    from deepagents.middleware.skills import SkillsMiddleware
    from langchain.chat_models import init_chat_model

    runtime_root = prepare_runtime_view()
    skills_mw = SkillsMiddleware(
        backend=FilesystemBackend(root_dir=runtime_root, virtual_mode=True),
        sources=[SKILLS_SOURCE],
    )
    agent = create_deep_agent(
        model=init_chat_model("openai:google/gemini-3.5-flash", temperature=0),
        middleware=[skills_mw],
    )
    task = "inbox-brief 스킬을 사용해 workspace의 분류 레코드·OKF 지식·조사 노트를 모아 brief.md를 작성하라. 스킬 지침을 먼저 읽고 따르라."
    print(f"task: {task}\n--- 도구 호출 추적 (read_file이 곧 점진 공개) ---")
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": task}]},
        {"recursion_limit": 40},
        stream_mode="updates",
    ):
        for upd in (chunk or {}).values():
            for m in (upd or {}).get("messages", []):
                for call in getattr(m, "tool_calls", None) or []:
                    args = call.get("args", {})
                    target = args.get("file_path") or args.get("path") or ""
                    print(f"  [{call['name']}] {target}".rstrip())
    sync_runtime_brief(runtime_root)


def main() -> None:
    ap = argparse.ArgumentParser(description="Skill 점진 공개를 코드로 본다")
    ap.add_argument("--run", action="store_true", help="에이전트로 실제 실행(키 필요)")
    ap.add_argument("--show", action="store_true", help="미들웨어가 싣는 메타데이터만(키 불필요·기본)")
    args = ap.parse_args()
    if args.run:
        run_agent()
    else:
        show_progressive_disclosure()


if __name__ == "__main__":
    main()
