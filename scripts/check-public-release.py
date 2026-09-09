"""Fail a site release if private teaching records enter the generated output."""
from pathlib import Path
import sys

PRIVATE_NAMES = {"_workspace", ".claude", "validation.md", "agents.md", "claude.md", "workshop_quality_review.md"}
PRIVATE_TEXT = ("통합 검증 전 초안", "다관점 감사 —", "자가 피드백 큐", "크로스 전파 로그", "워크숍 목표·실행·복습 정합성 점검")


def check_site(root: Path) -> list[str]:
    errors = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part.lower() in PRIVATE_NAMES for part in relative.parts):
            errors.append(f"Private path: {relative}")
        if path.suffix in {".html", ".js", ".json", ".md", ".txt"}:
            content = path.read_text(encoding="utf-8")
            if any(marker in content for marker in PRIVATE_TEXT):
                errors.append(f"Private teaching record: {relative}")
    return errors


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "book/.vitepress/dist")
    if not root.is_dir():
        raise SystemExit(f"Build output missing: {root}")
    errors = check_site(root)
    if errors:
        raise SystemExit("\n".join(errors))
    print("Public site boundary check passed")
