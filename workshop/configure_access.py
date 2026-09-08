"""Configure workshop credentials locally without displaying them."""

from getpass import getpass
from pathlib import Path
import re
from io import StringIO

from dotenv import dotenv_values, set_key

DEFAULT_MODEL = "google/gemini-3.8-flash"


def read_access(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8-sig").strip()
    if text.startswith("sk-") and "\n" not in text:
        key, model = text, DEFAULT_MODEL
    else:
        values = dotenv_values(stream=StringIO(text))
        key = values.get("OPENROUTER_API_KEY") or ""
        model = values.get("WORKSHOP_MODEL") or DEFAULT_MODEL
    validate(key, model)
    return key, model


def validate(key: str, model: str) -> None:
    if not key.startswith("sk-") or any(c.isspace() for c in key) or len(key) < 16:
        raise ValueError("키 형식을 확인하세요. 키 내용은 출력하지 않습니다.")
    if not re.fullmatch(r"[\w./:-]+", model):
        raise ValueError("모델 ID 형식을 확인하세요.")


def save_access(target: Path, key: str, model: str) -> None:
    validate(key, model)
    target.touch(mode=0o600, exist_ok=True)
    target.chmod(0o600)
    set_key(target, "OPENROUTER_API_KEY", key)
    set_key(target, "WORKSHOP_MODEL", model)


def main() -> None:
    target = Path(__file__).resolve().parent / ".env"
    current = dotenv_values(target) if target.exists() else {}
    if current.get("OPENROUTER_API_KEY"):
        print(
            "기존 키 설정이 있습니다. 현재 모델:",
            current.get("WORKSHOP_MODEL") or DEFAULT_MODEL,
        )
        if input("기존 설정을 유지할까요? [Y/n] ").strip().lower() != "n":
            return
    print(
        "강사가 공유한 workshop-access.txt를 내려받으세요. 파일이 없으면 Enter 후 키를 직접 입력합니다."
    )
    location = input("키 파일 경로: ").strip().strip('"').strip("'")
    try:
        if location:
            key, model = read_access(Path(location).expanduser())
        else:
            key = getpass("OpenRouter API 키 (화면에 표시되지 않음): ").strip()
            model = (
                input(f"모델 ID [기본값 {DEFAULT_MODEL}]: ").strip() or DEFAULT_MODEL
            )
        save_access(target, key, model)
    except (OSError, ValueError):
        raise SystemExit(
            "설정을 저장하지 못했습니다. 파일 경로·키·모델 형식을 확인한 뒤 다시 실행하세요."
        ) from None
    print("키를 .env에 저장했습니다. 모델:", model)


if __name__ == "__main__":
    main()
