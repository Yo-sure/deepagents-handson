"""Ch4 산출물 — Skill이 "어떻게 읽히는지"를 코드로 보여 준다.

deepagents의 **SkillsMiddleware**가 핵심이다. 에이전트가 시작할 때(before_agent)
스킬 디렉터리를 훑어 SKILL.md 앞머리(frontmatter)의 name·description만 시스템
프롬프트에 싣는다(1단계). 본문은 모델이 "이 작업에 맞다"고 판단할 때 read_file로
가져오고(2단계), references/*.md는 본문이 가리킬 때만 펼친다(3단계). 이게 컨텍스트를
아끼는 progressive disclosure다 — Skill이 100개여도 1단계는 각 수십 토큰뿐이다.

    uv run python3 ch4-skills-mcp/skill_agent.py --show   # 미들웨어가 무엇을 싣는지 (키 불필요)
    uv run python3 ch4-skills-mcp/skill_agent.py --offline # SKILL.md 절차로 brief.md 생성(키 불필요)
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
LIVE_MODEL = "openai:anthropic/claude-haiku-4.5"


def prepare_runtime_view() -> Path:
    """Expose only workspace outputs and the skill package to the file backend."""
    from analyst.paths import WORKSPACE, ensure_workspace

    ensure_workspace()
    root = WORKSPACE / "_skill_runtime"
    if root.exists():
        shutil.rmtree(root)
    (root / "ch4-skills-mcp").mkdir(parents=True)
    shutil.copytree(REPO / "ch4-skills-mcp" / "inbox-brief", root / "ch4-skills-mcp" / "inbox-brief")
    shutil.copytree(REPO / "ch4-skills-mcp" / "reconcile-rules", root / "ch4-skills-mcp" / "reconcile-rules")
    if WORKSPACE.exists():
        shutil.copytree(WORKSPACE, root / "workspace", ignore=shutil.ignore_patterns("_skill_runtime"))
    return root


def sync_runtime_brief(runtime_root: Path) -> None:
    from analyst.paths import BRIEF

    generated = runtime_root / "workspace" / "brief.md"
    if generated.exists():
        BRIEF.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(generated, BRIEF)


def brief_has_bad_card_gap(text: str) -> bool:
    markers = ("대응 문서 없음", "영수증 없음", "미확인", "누락", "분실", "미수령")
    for line in text.splitlines():
        if "신한카드 결제" in line and any(marker in line for marker in markers):
            return True
    return False


def show_progressive_disclosure() -> None:
    """SkillsMiddleware의 공개 before_agent hook으로 1단계 metadata를 보여 준다."""
    from deepagents.backends import FilesystemBackend
    from deepagents.middleware.skills import SkillsMiddleware

    backend = FilesystemBackend(root_dir=str(REPO), virtual_mode=True)
    skills_mw = SkillsMiddleware(backend=backend, sources=[SKILLS_SOURCE])

    # ── 훅 ①: before_agent (세션당 1회) ─────────────────────────────
    # 미들웨어는 backend.ls(source)로 스킬 디렉터리를 훑어 각 SKILL.md 앞머리만 파싱해
    # state["skills_metadata"]에 싣는다.
    state_update = skills_mw.before_agent({}, None, {}) or {}
    skills = state_update.get("skills_metadata", [])
    print("[before_agent · 세션당 1회] backend.ls(source)로 스킬을 훑어 SKILL.md 앞머리만 읽어")
    print("  state['skills_metadata']에 싣는다. (PrivateStateAttr — 서브에이전트엔 전파 안 됨)\n")
    for s in skills:
        body_lines = len((REPO / s["path"].lstrip("/")).read_text(encoding="utf-8").splitlines())
        print(f"  • {s['name']}  →  {s['path']}")
        print(f"    description: {s['description']}")
        print(f"    allowed_tools: {', '.join(s.get('allowed_tools') or []) or '(없음)'}")
        print(f"    (본문 {body_lines}줄은 아직 안 읽음 — description이 작업과 맞을 때 read_file)\n")

    # ── 훅 ②: wrap_model_call (매 모델 호출) ────────────────────────
    # 위 메타데이터를 Skills System 섹션으로 만들어 시스템 메시지에 덧붙인다. 실제 문자열
    # 포맷은 deepagents 버전에 따라 바뀔 수 있으므로, 실습은 공개 hook의 metadata만 점검한다.
    print("[wrap_model_call · 매 모델 호출] 위 metadata가 Skills System 섹션으로 시스템 프롬프트에 주입된다")
    print("  — 이름·설명·경로만 올라간다(=1단계). 본문은 안 들어간다.")
    print("\n[2단계] 모델이 'description이 내 작업과 맞다' → read_file(path, limit=1000)로 본문을 읽는다")
    print("        (미들웨어가 아니라 모델의 도구 호출 — 그래서 --run 추적에 [read_file]이 찍힌다).")
    print("[3단계] 본문이 references/*.md를 가리키면 그때만 그 파일을 read_file 한다.")


def run_agent() -> None:
    """실제 deep agent에 스킬을 붙여 돌린다 — read_file(SKILL.md)가 점진 공개의 증거다."""
    import os
    import time

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
    generated = runtime_root / "workspace" / "brief.md"
    if generated.exists():
        generated.unlink()
    start = time.time()
    workspace_root = runtime_root / "workspace"
    classified_files = sorted(f"/workspace/classified/{p.name}"
                              for p in (workspace_root / "classified").glob("*.json"))
    kb_files = sorted(
        f"/workspace/knowledge_base/{p.name}"
        for p in (workspace_root / "knowledge_base").glob("*.md")
        if p.name.startswith(("gap-", "subscription-"))
    )
    note_files = sorted(f"/workspace/research_notes/{p.name}"
                        for p in (workspace_root / "research_notes").glob("*.md"))
    requires_reconcile = bool(
        any("statement_card" in path or "statement_bank" in path for path in classified_files)
        and any("reconcile" in path for path in note_files)
    )
    backend = FilesystemBackend(root_dir=runtime_root, virtual_mode=True)
    skills_mw = SkillsMiddleware(
        backend=backend,
        sources=[SKILLS_SOURCE],
    )
    agent = create_deep_agent(
        model=init_chat_model(LIVE_MODEL, temperature=0, timeout=90, max_retries=1),
        middleware=[skills_mw],
        backend=backend,
    )
    task = (
        "분류 레코드, OKF 지식, 조사 노트를 모아 /workspace/brief.md를 작성하라.\n"
        "사용 가능한 Skill 목록에서 이 작업에 맞는 브리프 작성 Skill을 찾아 본문을 읽고 따르라.\n"
        "조사 노트의 대응 문서 없음이나 영수증 없음 판정은 레코드와 충돌할 수 있으므로, "
        "사용 가능한 대사 검증 Skill도 읽어 규칙을 적용하라.\n"
        "입력은 /workspace/classified, /workspace/knowledge_base, "
        "/workspace/research_notes 아래에만 있다. ls로 파일명을 확인한 뒤 필요한 파일만 "
        "read_file로 읽어라. glob/grep으로 전체를 뒤지지 말라.\n"
        "런타임이 확인한 실제 입력 파일 목록은 다음과 같다.\n"
        f"- classified: {', '.join(classified_files)}\n"
        f"- knowledge_base 짚을 점: {', '.join(kb_files)}\n"
        f"- research_notes: {', '.join(note_files)}\n"
        "ls 결과 해석이 애매해도 위 경로는 존재하므로 그대로 read_file하라.\n"
        "knowledge_base에서는 type: gap 또는 type: subscription 항목을 짚을 점으로 쓰고, "
        "각 항목의 title(또는 name)과 amount를 반드시 함께 적어라.\n"
        "위 파일들을 읽은 뒤에는 다른 디렉터리를 탐색하지 말고 바로 brief를 작성하라. "
        "특히 /, /root, 상위 디렉터리로 이동하지 말라.\n"
        "마지막 작업은 write_file로 /workspace/brief.md를 쓰는 것이다. "
        "brief.md를 쓴 뒤에는 짧게 완료만 보고하라."
    )
    print(f"task: {task}\n--- 도구 호출 추적 (read_file이 곧 점진 공개) ---")
    saw_write = False
    read_targets: list[str] = []
    final_text = ""
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": task}]},
        {"recursion_limit": 60},
        stream_mode="updates",
    ):
        for upd in (chunk or {}).values():
            for m in (upd or {}).get("messages", []):
                msg_type = getattr(m, "type", "")
                if msg_type == "tool":
                    content = getattr(m, "content", "")
                    text = content if isinstance(content, str) else str(content)
                    if "error" in text.lower() or "not found" in text.lower() or "denied" in text.lower():
                        print(f"    → {text[:300]}")
                content = getattr(m, "content", "")
                if isinstance(content, str) and content.strip():
                    final_text = content.strip()
                for call in getattr(m, "tool_calls", None) or []:
                    args = call.get("args", {})
                    target = args.get("file_path") or args.get("path") or ""
                    print(f"  [{call['name']}] {target}".rstrip())
                    if call["name"] == "read_file" and target:
                        read_targets.append(str(target))
                    if call["name"] == "write_file" and "brief.md" in str(args):
                        saw_write = True
    if final_text:
        print(f"final: {final_text[:500]}")
    if not saw_write or not generated.exists() or generated.stat().st_mtime < start:
        raise RuntimeError("Skill 실행이 workspace/brief.md를 새로 쓰지 않았습니다.")
    brief_text = generated.read_text(encoding="utf-8")
    if not any("inbox-brief/SKILL.md" in target for target in read_targets):
        raise RuntimeError("Skill 실행이 inbox-brief 본문을 read_file로 읽지 않았습니다.")
    if requires_reconcile and not any("reconcile-rules/SKILL.md" in target for target in read_targets):
        raise RuntimeError("대사 검증이 필요한 입력인데 reconcile-rules Skill을 읽지 않았습니다.")
    if brief_has_bad_card_gap(brief_text):
        raise RuntimeError("정상 매칭된 신한카드 결제를 짚을 점으로 잘못 올렸습니다.")
    sync_runtime_brief(runtime_root)


def run_offline_rehearsal() -> None:
    """키 없이 SKILL.md 절차를 따라 brief.md를 만든다.

    기본 학습 경로는 --run의 LLM 호출이다. 이 함수는 모델이 없는 환경에서 같은 입력 계약과
    Skill 문서의 절차를 끝까지 확인하기 위한 결정론 보조 경로다.
    """
    sys.path.insert(0, str(REPO / "ch3-deepagents"))
    sys.path.insert(0, str(REPO / "ch4-skills-mcp"))
    from analyst.paths import BRIEF, KNOWLEDGE_BASE, ensure_workspace
    from research_orchestrator import by_type, load_records
    from okf_store import build_finding_entries, build_merchant_entries, okf_index, validate_okf_bundle

    skill = REPO / "ch4-skills-mcp" / "inbox-brief" / "SKILL.md"
    reconcile_skill = REPO / "ch4-skills-mcp" / "reconcile-rules" / "SKILL.md"
    ref = REPO / "ch4-skills-mcp" / "inbox-brief" / "references" / "brief_format.md"
    print("--- 오프라인 리허설: LLM·SkillsMiddleware 도구 호출 로그가 아님 ---")
    print(f"  [offline-read] {skill.relative_to(REPO)}")
    print(f"  [offline-read] {reconcile_skill.relative_to(REPO)}")
    print(f"  [offline-read] {ref.relative_to(REPO)}")

    records = load_records(allow_gold=True)
    ensure_workspace()
    existing_findings = [
        p for p in KNOWLEDGE_BASE.glob("*.md")
        if p.name != "index.md" and ("gap-" in p.name or "subscription-" in p.name)
    ]
    if not existing_findings:
        entries = {**build_merchant_entries(records), **build_finding_entries(records)}
        index_text = okf_index(entries)
        validate_okf_bundle(entries, index_text)
        for name, text in entries.items():
            (KNOWLEDGE_BASE / f"{name}.md").write_text(text, encoding="utf-8")
        (KNOWLEDGE_BASE / "index.md").write_text(index_text, encoding="utf-8")
        try:
            index_target = (KNOWLEDGE_BASE / "index.md").relative_to(REPO)
        except ValueError:
            index_target = KNOWLEDGE_BASE / "index.md"
        print(f"  [offline-write] {index_target}")
    receipts = by_type(records, "영수증")
    spend = sum(r.total for r in receipts)
    categories = {
        "식비": sum(r.total for r in receipts if any(k in r.merchant for k in ("스타벅스", "국밥", "GS25"))),
        "교통": sum(r.total for r in receipts if "택시" in r.merchant),
        "생활": sum(r.total for r in receipts if "올리브영" in r.merchant),
    }

    flags = []
    for p in sorted(KNOWLEDGE_BASE.glob("*.md")):
        if p.name == "index.md":
            continue
        text = p.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        meta = yaml.safe_load(text.split("---", 2)[1]) or {}
        kind = meta.get("type")
        if kind not in {"gap", "subscription"}:
            continue
        title = meta.get("title") or meta.get("name") or p.stem
        amount = meta.get("amount")
        amount_text = f" {float(amount):,.0f}원" if amount is not None else ""
        suffix = " — 영수증 없음, 확인 필요" if kind == "gap" else " — 구독 추정"
        flags.append(f"- ({kind}) {title}{amount_text}{suffix}")

    lines = [
        "# 인박스 브리프 — 2026년 5월",
        "",
        "## 한 줄 요약",
        f"문서 {len(records)}건 · 영수증 지출 합계 {spend:,.0f}원 · 짚을 점 {len(flags)}건.",
        "",
        "## 지출",
        *(f"- {name}: {amount:,.0f}원" for name, amount in categories.items() if amount),
        "",
        "## 짚을 점",
        *(flags or ["- 특이사항 없음"]),
        "",
        "## 할 일",
        "- [ ] 영수증 없는 카드 결제 확인",
        "- [ ] 구독 목록 점검",
    ]
    BRIEF.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        target = BRIEF.relative_to(REPO)
    except ValueError:
        target = BRIEF
    print(f"  [offline-write] {target}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Skill 점진 공개를 코드로 본다")
    ap.add_argument("--run", action="store_true", help="에이전트로 실제 실행(키 필요)")
    ap.add_argument("--offline", action="store_true", help="SKILL.md 절차로 brief.md 작성(키 불필요·LLM 아님)")
    ap.add_argument("--show", action="store_true", help="미들웨어가 싣는 메타데이터만(키 불필요·기본)")
    args = ap.parse_args()
    if args.run:
        run_agent()
    elif args.offline:
        run_offline_rehearsal()
    else:
        show_progressive_disclosure()


if __name__ == "__main__":
    main()
