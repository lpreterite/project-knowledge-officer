from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER = REPO_ROOT / "scripts" / "meeting_helpers.py"


class MeetingHelpersTest(unittest.TestCase):
    def run_helper(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(HELPER), *args],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if check and result.returncode != 0:
            self.fail(
                "helper command failed\n"
                f"args: {args}\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )
        return result

    def test_init_project_creates_knowledge_index_for_minimal_and_advanced_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            for profile in ["minimal", "advanced"]:
                project_root = Path(tmpdir) / f"{profile}-project"

                self.run_helper(
                    "--project-root",
                    str(project_root),
                    "init-project",
                    "--project-id",
                    f"{profile}-project",
                    "--name",
                    f"{profile.title()} Project",
                    "--profile",
                    profile,
                    "--no-git",
                )

                index = project_root / "knowledge" / "index.md"
                self.assertTrue(index.exists())
                index_text = index.read_text(encoding="utf-8")
                self.assertIn("# 项目知识索引", index_text)
                self.assertIn("## 当前状态入口", index_text)
                self.assertIn("## 会议", index_text)
                self.assertIn("## 当前决定", index_text)
                self.assertIn("## 当前 Todo", index_text)
                self.assertIn("## 当前未决事项", index_text)
                self.assertIn("## 重要材料", index_text)
                self.assertIn("## 最近知识更新", index_text)

    def test_validate_project_reports_missing_or_malformed_knowledge_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "project"
            self.run_helper(
                "--project-root",
                str(project_root),
                "init-project",
                "--project-id",
                "project",
                "--name",
                "Project",
                "--no-git",
            )

            index = project_root / "knowledge" / "index.md"
            index.unlink()
            missing = self.run_helper(
                "--project-root",
                str(project_root),
                "validate-project",
                check=False,
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("knowledge/index.md", missing.stdout)

            index.write_text("# 项目知识索引\n\n## 当前状态入口\n", encoding="utf-8")
            malformed = self.run_helper(
                "--project-root",
                str(project_root),
                "validate-project",
                check=False,
            )
            self.assertNotEqual(malformed.returncode, 0)
            self.assertIn("knowledge/index.md: missing section ## 会议", malformed.stdout)


if __name__ == "__main__":
    unittest.main()
