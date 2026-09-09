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
            (root / "lesson.html").write_text("토론 길잡이: 승인한 버전과 현재 버전을 비교합니다. 학생용 검증 과제: 학습 목표·실행·복습 결과를 점검합니다.", encoding="utf-8")
            self.assertEqual(boundary.check_site(root), [])

    def test_private_files_and_bundled_reports_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "VALIDATION.md").write_text("internal", encoding="utf-8")
            (root / "page.js").write_text("다관점 감사 — 검토 이력", encoding="utf-8")
            self.assertEqual(len(boundary.check_site(root)), 2)


    def test_named_quality_report_is_rejected_case_insensitively(self):
        for name in ("WORKSHOP_QUALITY_REVIEW.md", "workshop_quality_review.md"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                (root / name).write_text("internal report", encoding="utf-8")
                self.assertEqual(boundary.check_site(root), [f"Private path: {name}"])

    def test_quality_report_title_is_rejected_after_renaming_or_bundling(self):
        for name in ("lesson.html", "chunk.js"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                (root / name).write_text("워크숍 목표·실행·복습 정합성 점검", encoding="utf-8")
                self.assertEqual(boundary.check_site(root), [f"Private teaching record: {name}"])


if __name__ == "__main__":
    unittest.main()
