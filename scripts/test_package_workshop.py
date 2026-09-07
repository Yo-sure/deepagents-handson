"""Packaging checks; run with python -m unittest discover -s scripts -p test_package_workshop.py."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("package_workshop", Path(__file__).with_name("package-workshop.py"))
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class PackagingTests(unittest.TestCase):
    def test_reproducible_and_manifest_verified_after_extraction(self):
        payload = {"workshop/course/z.py": b"z = 1\n", "workshop/README.md": b"Read me\n"}
        first = package.archive_bytes(payload)
        second = package.archive_bytes(dict(reversed(list(payload.items()))))
        self.assertEqual(first, second)
        self.assertEqual(package.verify_archive(first), 2)

    def test_private_inputs_are_never_read(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in package.TOP_FILES:
                (root / name).write_text("", encoding="utf-8")
            for name in package.DIRECTORIES:
                (root / name).mkdir()
            for name in package.EXTRA_FILES:
                (root / name).write_text("", encoding="utf-8")
            # A directory where .env would be makes accidental reading fail.
            (root / ".env").mkdir()
            (root / "runs").mkdir()
            (root / "runs" / "private.py").write_text("private", encoding="utf-8")
            (root / "course" / ".private").mkdir()
            (root / "course" / ".private" / "private.py").write_text("private", encoding="utf-8")
            (root / "course" / "main.py").write_bytes(b"print('ok')\r\n")
            payload = package.collect(root)
            self.assertEqual(len(payload), len(package.TOP_FILES) + len(package.EXTRA_FILES) + 1)
            self.assertFalse(any("private" in name for name in payload))
            self.assertEqual(payload["workshop/course/main.py"], b"print('ok')\n")
            (root / "course" / "main.py").write_bytes(b"print('ok')\n")
            self.assertEqual(package.archive_bytes(payload), package.archive_bytes(package.collect(root)))

    def test_secret_pattern_rejected_without_value_in_error(self):
        fake = b"sk-or-v1-" + b"x" * 32
        with self.assertRaises(ValueError) as error:
            package.validate_content("workshop/course/a.py", fake)
        self.assertNotIn(fake.decode(), str(error.exception))

    def test_notebook_outputs_and_counts_rejected(self):
        for cell in ({"outputs": [{"text": "private"}]}, {"execution_count": 1}):
            with self.assertRaises(ValueError):
                package.validate_content("x.ipynb", json.dumps({"cells": [cell]}).encode())

    def test_empty_env_example_does_not_consume_next_line(self):
        package.validate_content("workshop/.env.example", b"OPENROUTER_API_KEY=\nWORKSHOP_MODEL=example\n")

    def test_traversal_and_non_allowlisted_entries_rejected(self):
        for name in ("../escape.py", "workshop/../escape.py", "workshop/.env", "workshop/runs/result.py"):
            with self.assertRaises(ValueError):
                package.verify_archive(package.archive_bytes({name: b"fake"}))

    def test_corrupted_file_does_not_pass_manifest(self):
        data = package.archive_bytes({"workshop/README.md": b"original"})
        import io
        import zipfile
        out = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(data)) as source, zipfile.ZipFile(out, "w") as changed:
            for info in source.infolist():
                changed.writestr(info, b"changed" if info.filename.endswith("README.md") else source.read(info.filename))
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            package.verify_archive(out.getvalue())


if __name__ == "__main__":
    unittest.main()
