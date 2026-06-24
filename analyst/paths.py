"""파이프라인 경로 규약 — 챕터가 모듈 산출물을 주고받는 디렉터리 단일 출처.

    sample_inbox/  →  classified/  →  research_notes/  →  brief.md  →  verified_brief.md
       (입력)          (Ch2)            (Ch3)              (Ch4)        (Ch5)

입력(sample_inbox)만 레포에 커밋한다. 학생이 만드는 중간 산출물은 모두
workspace/ 아래에 떨어지며 .gitignore 된다. 경로를 바꾸려면 ANALYST_WORKSPACE
환경변수로 덮어쓸 수 있다(테스트·채점 격리용). 상대경로로 주면 레포 루트 기준으로
풀려 ~/lecture/workspace/... 안(=VSCode 작업트리)에 산출물이 보인다. 절대경로는 그대로.
"""

from __future__ import annotations

import os
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
REPO_ROOT = PKG_DIR.parent

# 입력(커밋됨)
SAMPLE_INBOX = PKG_DIR / "sample_inbox"
MANIFEST = SAMPLE_INBOX / "_manifest.yaml"

# 산출물(학생 생성, gitignore)
_ws = os.environ.get("ANALYST_WORKSPACE")
if not _ws:
    WORKSPACE = REPO_ROOT / "workspace"
elif os.path.isabs(_ws):
    WORKSPACE = Path(_ws)                       # 절대경로는 그대로(예: /tmp/...)
else:
    WORKSPACE = REPO_ROOT / _ws                 # 상대경로는 레포 루트 기준 → VSCode에서 보임
CLASSIFIED = WORKSPACE / "classified"          # Ch2: RecordV1 JSON
RESEARCH_NOTES = WORKSPACE / "research_notes"   # Ch3: fan-out 조사노트
KNOWLEDGE_BASE = WORKSPACE / "knowledge_base"   # Ch4: OKF 지식 항목
BRIEF = WORKSPACE / "brief.md"                  # Ch4: 브리프
VERIFIED_BRIEF = WORKSPACE / "verified_brief.md"  # Ch5: A2A 검증 후


def ensure_workspace() -> None:
    """파이프라인 출력 디렉터리를 만든다(있으면 무시)."""
    for d in (CLASSIFIED, RESEARCH_NOTES, KNOWLEDGE_BASE):
        d.mkdir(parents=True, exist_ok=True)
