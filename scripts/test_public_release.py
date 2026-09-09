"""The publication boundary excludes records, not useful learning guidance."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("boundary", Path(__file__).with_name("check-public-release.py"))
boundary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boundary)


class PublicBoundaryTests(unittest.TestCase):
    def test_learning_guidance_is_allowed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "lesson.html").write_text("토론 길잡이: 승인한 버전과 현재 버전을 비교합니다.", encoding="utf-8")
            self.assertEqual(boundary.check_site(root), [])

    def test_private_files_and_bundled_reports_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "VALIDATION.md").write_text("internal", encoding="utf-8")
            (root / "page.js").write_text("다관점 감사 — 검토 이력", encoding="utf-8")
            self.assertEqual(len(boundary.check_site(root)), 2)


if __name__ == "__main__":
    unittest.main()
