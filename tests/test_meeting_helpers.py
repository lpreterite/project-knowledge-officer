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

    def test_init_project_creates_knowledge_log_with_parseable_initial_entry(self) -> None:
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

            log = project_root / "knowledge" / "log.md"
            self.assertTrue(log.exists())
            log_text = log.read_text(encoding="utf-8")
            self.assertIn("# 项目知识操作日志", log_text)
            self.assertRegex(log_text, r"## \[\d{4}-\d{2}-\d{2}\] init-project \| project")
            self.assertIn("- Created: project knowledge repository scaffold", log_text)

    def test_validate_project_reports_missing_or_malformed_knowledge_log(self) -> None:
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

            log = project_root / "knowledge" / "log.md"
            log.unlink()
            missing = self.run_helper(
                "--project-root",
                str(project_root),
                "validate-project",
                check=False,
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("knowledge/log.md", missing.stdout)

            log.write_text("# 项目知识操作日志\n\n## init-project project\n", encoding="utf-8")
            malformed = self.run_helper(
                "--project-root",
                str(project_root),
                "validate-project",
                check=False,
            )
            self.assertNotEqual(malformed.returncode, 0)
            self.assertIn("knowledge/log.md: malformed log heading", malformed.stdout)

    def test_new_meeting_appends_metadata_only_log_entry(self) -> None:
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

            self.run_helper(
                "--project-root",
                str(project_root),
                "new-meeting",
                "--date",
                "2026-06-17",
                "--location",
                "remote",
                "--topic",
                "planning",
            )

            log_text = (project_root / "knowledge" / "log.md").read_text(encoding="utf-8")
            self.assertRegex(log_text, r"## \[\d{4}-\d{2}-\d{2}\] new-meeting \| 2026-06-17_remote_planning")
            self.assertIn("- Created: meetings/2026/2026-06-17_remote_planning", log_text)
            self.assertNotIn("## Content", log_text)

    def test_health_lint_reports_duplicate_open_todos_without_mutating_files(self) -> None:
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
            todos = project_root / "knowledge" / "current-todos.md"
            todos.write_text(
                "# 当前 Todo\n\n"
                "| ID | Todo | Domain | Status | Owner | Due | Updated | Source |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                "| todo-1 | Follow up with client | 协作/责任 | open | unknown | unknown | 2026-06-17 | [m1](../meetings/2026/m1/analysis.md) |\n"
                "| todo-2 | Follow up with client | 协作/责任 | open | unknown | unknown | 2026-06-17 | [m1](../meetings/2026/m1/analysis.md) |\n",
                encoding="utf-8",
            )
            before = todos.read_text(encoding="utf-8")

            result = self.run_helper(
                "--project-root",
                str(project_root),
                "health-lint",
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("WARN:", result.stdout)
            self.assertIn("duplicate open todo", result.stdout)
            self.assertEqual(before, todos.read_text(encoding="utf-8"))

    def test_health_lint_reports_active_decision_that_supersedes_another_decision(self) -> None:
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
            decisions = project_root / "knowledge" / "current-decisions.md"
            decisions.write_text(
                "# 当前决定\n\n"
                "| ID | Decision | Domain | Status | Updated | Supersedes | Source |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| decision-1 | Use local project repos | 方案/决策 | active | 2026-06-17 | decision-0 | [m1](../meetings/2026/m1/analysis.md) |\n",
                encoding="utf-8",
            )

            result = self.run_helper(
                "--project-root",
                str(project_root),
                "health-lint",
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("WARN:", result.stdout)
            self.assertIn("active decision has Supersedes", result.stdout)

    def test_health_lint_reports_ok_for_clean_project(self) -> None:
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

            result = self.run_helper(
                "--project-root",
                str(project_root),
                "health-lint",
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertEqual("OK\n", result.stdout)

    def test_health_lint_reports_missing_source_links_and_unreferenced_open_questions(self) -> None:
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
            questions = project_root / "knowledge" / "current-open-questions.md"
            questions.write_text(
                "# 当前未决事项\n\n"
                "| ID | Question | Domain | Status | Owner | Updated | Source |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| question-1 | Confirm launch owner | 协作/责任 | open | unknown | 2026-06-17 | m1 |\n",
                encoding="utf-8",
            )

            result = self.run_helper(
                "--project-root",
                str(project_root),
                "health-lint",
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("missing markdown source link", result.stdout)
            self.assertIn("open question not referenced in timeline", result.stdout)

    def test_health_lint_reports_repeated_terms_missing_from_advanced_context(self) -> None:
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
                "--profile",
                "advanced",
                "--no-git",
            )
            for meeting_id in ["m1", "m2"]:
                meeting_dir = project_root / "meetings" / "2026" / meeting_id
                meeting_dir.mkdir(parents=True)
                (meeting_dir / "analysis.md").write_text(
                    "# 会议分析\n\n- 术语：Agent Memory\n",
                    encoding="utf-8",
                )

            result = self.run_helper(
                "--project-root",
                str(project_root),
                "health-lint",
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("repeated term missing from domain/context", result.stdout)
            self.assertIn("Agent Memory", result.stdout)


if __name__ == "__main__":
    unittest.main()
