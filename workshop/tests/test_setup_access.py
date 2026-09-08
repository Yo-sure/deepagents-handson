from pathlib import Path
import importlib.util
import pytest
from dotenv import dotenv_values

spec = importlib.util.spec_from_file_location(
    "access", Path(__file__).parents[1] / "configure_access.py"
)
access = importlib.util.module_from_spec(spec)
spec.loader.exec_module(access)
KEY = "sk-" + "example" * 3


def test_shared_file_and_preserve_other_settings(tmp_path):
    shared = tmp_path / "access.txt"
    shared.write_text(
        f"OPENROUTER_API_KEY={KEY}\nWORKSHOP_MODEL=google/gemini-3.8-flash\n",
        encoding="utf-8-sig",
    )
    key, model = access.read_access(shared)
    target = tmp_path / ".env"
    target.write_text("OTHER=preserved\n", encoding="utf-8")
    access.save_access(target, key, model)
    assert dotenv_values(target) == {
        "OTHER": "preserved",
        "OPENROUTER_API_KEY": KEY,
        "WORKSHOP_MODEL": model,
    }


def test_raw_key_and_invalid_input(tmp_path):
    shared = tmp_path / "access.txt"
    shared.write_text(KEY, encoding="utf-8")
    assert access.read_access(shared) == (KEY, access.DEFAULT_MODEL)
    with pytest.raises(ValueError):
        access.save_access(tmp_path / ".env", "invalid", access.DEFAULT_MODEL)
    assert not (tmp_path / ".env").exists()
