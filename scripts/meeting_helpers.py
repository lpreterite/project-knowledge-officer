#!/usr/bin/env python3
"""Small scaffolding helper for file-based meeting knowledge repositories."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Iterable


DOMAINS = [
    "业务目标",
    "范围/需求",
    "方案/决策",
    "数据/证据",
    "交付/执行",
    "风险/依赖",
    "协作/责任",
]


HELPER_ROOT = Path(__file__).resolve().parents[1]
DOMAIN_TEMPLATE_ROOT = HELPER_ROOT / "domain"
PROJECT_KNOWLEDGE_TEMPLATE_ROOT = HELPER_ROOT / "templates" / "project-knowledge"
ARTIFACT_MANIFEST_TEMPLATE = HELPER_ROOT / "templates" / "artifact-manifest.yaml"
KNOWLEDGE_INDEX_TEMPLATE = HELPER_ROOT / "templates" / "knowledge-index.md"
KNOWLEDGE_LOG_TEMPLATE = HELPER_ROOT / "templates" / "knowledge-log.md"
BRIEF_TEMPLATE = HELPER_ROOT / "templates" / "brief-template.md"
PROFILES = {"minimal", "advanced"}
MAX_DEFAULT_ARTIFACT_SIZE_BYTES = 25 * 1024 * 1024
RAW_ARTIFACT_SUFFIXES = {
    ".3gp",
    ".7z",
    ".aac",
    ".aiff",
    ".avi",
    ".flac",
    ".gz",
    ".m4a",
    ".mkv",
    ".mov",
    ".mp3",
    ".mp4",
    ".ogg",
    ".opus",
    ".rar",
    ".tar",
    ".wav",
    ".webm",
    ".zip",
}
RAW_ARTIFACT_DIRS = {"artifacts", "inbox"}
ARTIFACT_MANIFEST_REQUIRED_FIELDS = {
    "filename",
    "storage",
    "path",
    "size_bytes",
    "sha256",
    "received_datetime",
    "source_note",
    "access_note",
    "git_policy",
}
ARTIFACT_GIT_POLICIES = {"committed", "ignored_external", "external_only", "local_only"}
LOCAL_ARTIFACT_POLICIES = {"committed", "ignored_external", "local_only"}
KNOWLEDGE_INDEX_REQUIRED_SECTIONS = [
    "## 当前状态入口",
    "## 会议",
    "## 当前决定",
    "## 当前 Todo",
    "## 当前未决事项",
    "## 重要材料",
    "## 最近知识更新",
]
KNOWLEDGE_LOG_HEADING_RE = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] [a-z][a-z0-9-]* \| .+")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


PROJECT_GITIGNORE = """# OS/editor noise
.DS_Store
Thumbs.db
*.tmp
*.temp

# Python/cache noise
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
venv/

# Raw or large meeting materials are not committed by default.
# Keep controlled source links, hashes, or explicit small evidence files in Markdown/YAML.
*.3gp
*.7z
*.aac
*.aiff
*.avi
*.flac
*.gz
*.m4a
*.mkv
*.mov
*.mp3
*.mp4
*.ogg
*.opus
*.rar
*.tar
*.wav
*.webm
*.zip
"""


def warn(message: str) -> None:
    print(f"WARN: {message}", file=sys.stderr)


def run_git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as error:
        raise RuntimeError("git executable was not found") from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or error.stdout.strip() or str(error)
        raise RuntimeError(detail) from error


def is_git_repo(path: Path) -> bool:
    try:
        result = run_git(["rev-parse", "--is-inside-work-tree"], path, check=False)
    except RuntimeError:
        return False
    return result.returncode == 0 and result.stdout.strip() == "true"


def git_top_level(path: Path) -> Path | None:
    try:
        result = run_git(["rev-parse", "--show-toplevel"], path, check=False)
    except RuntimeError:
        return None
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def init_git_repo(path: Path) -> bool:
    path.mkdir(parents=True, exist_ok=True)
    if is_git_repo(path):
        return True
    try:
        result = run_git(["init", "-b", "main"], path, check=False)
        if result.returncode != 0:
            run_git(["init"], path)
            run_git(["branch", "-M", "main"], path)
    except RuntimeError as error:
        warn(f"Could not initialize local Git repository at {path}: {error}")
        return False
    return True


def git_has_changes(path: Path) -> bool:
    try:
        result = run_git(["status", "--short"], path)
    except RuntimeError as error:
        warn(f"Could not inspect Git status at {path}: {error}")
        return False
    return bool(result.stdout.strip())


def git_changed_paths(path: Path) -> list[Path]:
    try:
        result = run_git(["status", "--short", "--untracked-files=all"], path)
    except RuntimeError as error:
        warn(f"Could not inspect Git status at {path}: {error}")
        return []
    changed: list[Path] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        changed_path = line[3:].strip()
        if " -> " in changed_path:
            changed_path = changed_path.split(" -> ", 1)[1].strip()
        changed.append(Path(changed_path))
    return changed


def git_ignored_untracked_paths(path: Path) -> list[Path]:
    try:
        result = run_git(
            ["ls-files", "--others", "--ignored", "--exclude-standard", "-z"],
            path,
        )
    except RuntimeError as error:
        warn(f"Could not inspect ignored Git paths at {path}: {error}")
        return []
    return [Path(item) for item in result.stdout.split("\0") if item]


def is_portfolio_metadata_path(path: Path) -> bool:
    allowed_global = {
        Path("global/project-index.md"),
        Path("global/access-boundaries.md"),
        Path("global/sync-status.md"),
    }
    return (
        path == Path("vault.yaml")
        or path.parts[:1] in [( "domain", ), ( "archive", )]
        or path in allowed_global
    )


def is_artifact_or_inbox_path(path: Path) -> bool:
    return bool(RAW_ARTIFACT_DIRS.intersection(path.parts))


def is_project_knowledge_path(path: Path) -> bool:
    if path in {Path(".gitignore"), Path("project.md"), Path("project-config.yaml")}:
        return True
    if len(path.parts) == 2 and path.parts[0] in {"knowledge", "domain"} and path.suffix in {".md", ".yaml", ".yml"}:
        return True
    if len(path.parts) == 3 and path.parts[:2] == ("knowledge", "briefs") and path.suffix == ".md":
        return True
    if len(path.parts) >= 3 and path.parts[0] == "meetings":
        filename = path.name
        if filename in {"metadata.yaml", "transcript.md", "analysis.md"}:
            return True
        if len(path.parts) >= 5 and path.parts[-2] == "artifacts" and filename == "manifest.yaml":
            return True
    return False


def risky_artifact_paths(root: Path, paths: Iterable[Path]) -> list[Path]:
    risky: list[Path] = []
    for path in paths:
        if not is_artifact_or_inbox_path(path):
            continue
        full_path = root / path
        suffix = path.suffix.lower()
        too_large = full_path.exists() and full_path.is_file() and full_path.stat().st_size > MAX_DEFAULT_ARTIFACT_SIZE_BYTES
        if suffix in RAW_ARTIFACT_SUFFIXES or too_large:
            risky.append(path)
    return risky


def repository_files(path: Path) -> set[Path]:
    if not path.exists():
        return set()
    return {
        item.relative_to(path)
        for item in path.rglob("*")
        if item.is_file() and ".git" not in item.relative_to(path).parts
    }


def commit_git_repo(
    path: Path,
    message: str,
    paths: Iterable[Path] | None = None,
    force_paths: Iterable[Path] | None = None,
) -> bool:
    if not is_git_repo(path):
        if not init_git_repo(path):
            return False
    force_path_set = set(force_paths or [])
    if not git_has_changes(path) and not force_path_set:
        return False
    selected_path_set = set(paths or [])
    selected_paths = [str(item) for item in selected_path_set - force_path_set] if paths is not None else []
    selected_force_paths = [str(item) for item in force_path_set]
    try:
        if paths is not None:
            if not selected_paths and not selected_force_paths:
                return False
            if selected_paths:
                run_git(["add", "--", *selected_paths], path)
            if selected_force_paths:
                run_git(["add", "-f", "--", *selected_force_paths], path)
        else:
            run_git(["add", "."], path)
        diff_result = run_git(["diff", "--cached", "--quiet"], path, check=False)
        if diff_result.returncode == 0:
            return False
        run_git(["commit", "-m", message], path)
    except RuntimeError as error:
        warn(f"Could not create local Git commit at {path}: {error}")
        return False
    return True


def write_if_missing(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def copy_template_if_missing(template: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        shutil.copyfile(template, destination)


def copy_templates(source_root: Path, destination_root: Path) -> None:
    if not source_root.exists():
        return
    for template in source_root.glob("*"):
        if template.is_file():
            copy_template_if_missing(template, destination_root / template.name)


def make_project_log_entry(operation: str, summary: str, details: list[str] | None = None) -> str:
    lines = [f"## [{date.today().isoformat()}] {operation} | {summary}"]
    for detail in details or []:
        lines.append(f"- {detail}")
    return "\n".join(lines) + "\n"


def write_project_log_if_missing(path: Path, operation: str, summary: str, details: list[str] | None = None) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    template = read_text(KNOWLEDGE_LOG_TEMPLATE)
    content = template.rstrip() + "\n\n" + make_project_log_entry(operation, summary, details)
    path.write_text(content, encoding="utf-8")


def append_project_log(path: Path, operation: str, summary: str, details: list[str] | None = None) -> None:
    if not path.exists():
        write_project_log_if_missing(path, operation, summary, details)
        return
    existing = read_text(path).rstrip()
    path.write_text(existing + "\n\n" + make_project_log_entry(operation, summary, details), encoding="utf-8")


def make_yaml_list(values: Iterable[str], indent: int = 2) -> str:
    prefix = " " * indent
    return "\n".join(f'{prefix}- "{value}"' for value in values)


def make_vault_config(profile: str) -> str:
    advanced = "true" if profile == "advanced" else "false"
    return f"""version: 1
repository_role: "portfolio_index"
profile: "{profile}"
language: "zh-CN"
source_policy: "meeting_or_artifact_required"
time_policy: "meeting_datetime_only"
domains:
{make_yaml_list(DOMAINS)}
enabled_layers:
  domain_knowledge: {advanced}
  portfolio_index: true
  global_fact_registers: false
"""


def make_project_config(profile: str, domains: list[str] | None = None) -> str:
    selected_domains = domains or DOMAINS
    advanced = "true" if profile == "advanced" else "false"
    advanced_required = ""
    if profile == "advanced":
        advanced_required = '  - "by-domain.md"\n  - "domain-context.md"\n  - "entity-aliases.md"\n  - "project-taxonomy.md"\n  - "source-map.md"\n'
    return f"""version: 1
repository_role: "project_knowledge"
profile: "{profile}"
language: "zh-CN"
# 项目级 taxonomy 是执行时的权威来源。portfolio/index vault 的 vault.yaml 只作为批量创建项目时的默认值。
collaboration_scope: "project_participants_only"
remote_policy: "explicit_when_collaboration_requires"
cross_project_references: "explicit_source_and_confirmation_required"
artifact_git_policy:
  markdown_yaml_default: "commit"
  raw_media_default: "external_or_explicit"
  large_binary_default: "external_or_explicit"
  max_default_artifact_size_mb: 25
domains:
{make_yaml_list(selected_domains)}
required_current_files:
  - "index.md"
  - "log.md"
  - "current-summary.md"
  - "current-decisions.md"
  - "current-open-questions.md"
  - "current-todos.md"
  - "timeline.md"
{advanced_required}advanced_layers:
  by_domain: {advanced}
  domain_context: {advanced}
  source_map: {advanced}
"""


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def parse_scalar_config(path: Path, key: str, default: str) -> str:
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{key}:"):
            value = stripped.split(":", 1)[1].strip().strip('"').strip("'")
            return value or default
    return default


def parse_domains(path: Path) -> list[str]:
    text = read_text(path)
    domains: list[str] = []
    in_domains = False
    for line in text.splitlines():
        if line.startswith("domains:"):
            in_domains = True
            continue
        if in_domains:
            if line and not line.startswith(" "):
                break
            stripped = line.strip()
            if stripped.startswith("- "):
                domains.append(stripped[2:].strip().strip('"').strip("'"))
    return domains or DOMAINS


def write_project_config(project_root: Path, profile: str, domains: list[str]) -> None:
    (project_root / "project-config.yaml").write_text(
        make_project_config(profile, domains),
        encoding="utf-8",
    )


def vault_profile(vault_root: Path) -> str:
    return parse_scalar_config(vault_root / "vault.yaml", "profile", "minimal")


def project_profile(project_root: Path, fallback: str) -> str:
    return parse_scalar_config(project_root / "project-config.yaml", "profile", fallback)


def nearest_existing_parent(path: Path) -> Path:
    current = path
    while not current.exists() and current.parent != current:
        current = current.parent
    return current


def has_mechanism_package_marker(path: Path) -> bool:
    return (path / "AGENTS.md").exists() and (path / "scripts/meeting_helpers.py").exists()


def is_inside_legacy_projects_dir(path: Path, ancestor: Path) -> bool:
    try:
        relative = path.relative_to(ancestor)
    except ValueError:
        return False
    return len(relative.parts) >= 2 and relative.parts[0] == "projects"


def has_project_knowledge_marker(path: Path) -> bool:
    return (path / "project.md").exists() and (path / "project-config.yaml").exists()


def is_existing_project_git_root(project_root: Path) -> bool:
    top_level = git_top_level(project_root)
    return top_level == project_root.resolve() and has_project_knowledge_marker(project_root)


def ensure_project_root_boundary(project_root: Path, adopt_existing: bool = False) -> None:
    if adopt_existing:
        return
    existing_parent = nearest_existing_parent(project_root)
    if existing_parent == project_root and is_existing_project_git_root(project_root):
        return
    if is_git_repo(existing_parent):
        top_level = git_top_level(existing_parent) or existing_parent
        raise SystemExit(
            f"Refusing to initialize project knowledge repo inside existing Git worktree: {top_level}. "
            "Use an independent directory, or pass --adopt-existing only after confirming the boundary."
        )
    for ancestor in [project_root, *project_root.parents]:
        if has_mechanism_package_marker(ancestor):
            raise SystemExit(f"Refusing to initialize real project knowledge inside mechanism package: {ancestor}")
        if (ancestor / "vault.yaml").exists() and is_inside_legacy_projects_dir(project_root, ancestor):
            raise SystemExit(
                f"Refusing to initialize project knowledge inside legacy/portfolio vault projects/: {ancestor}. "
                "Use migrate-project --dry-run or the explicit legacy flow."
            )
        if ancestor != project_root and has_project_knowledge_marker(ancestor):
            raise SystemExit(f"Refusing to initialize nested project knowledge repo inside existing project root: {ancestor}")


def project_id_from_root(project_root: Path) -> str:
    project_md = read_text(project_root / "project.md")
    for line in project_md.splitlines():
        stripped = line.strip()
        if stripped.startswith("- Project ID:"):
            value = stripped.split(":", 1)[1].strip()
            if value and value != "unknown":
                return value
    return project_root.name


def init_vault(vault_root: Path, profile: str, initialize_git: bool = True, initial_commit: bool = True) -> None:
    ensure_profile(profile)
    existing_files = repository_files(vault_root)
    for rel in [
        "inbox",
        "projects",
        "archive/superseded",
    ]:
        (vault_root / rel).mkdir(parents=True, exist_ok=True)

    write_if_missing(vault_root / "vault.yaml", make_vault_config(profile))

    if profile == "advanced":
        (vault_root / "domain").mkdir(parents=True, exist_ok=True)
        (vault_root / "global").mkdir(parents=True, exist_ok=True)
        copy_templates(DOMAIN_TEMPLATE_ROOT, vault_root / "domain")

        write_if_missing(
            vault_root / "global/project-index.md",
            "# Project Index\n\n| Project | Knowledge Repository | Sharing Boundary | Status | Notes |\n| --- | --- | --- | --- | --- |\n",
        )
        write_if_missing(
            vault_root / "global/access-boundaries.md",
            "# Access Boundaries\n\n此文件记录项目 knowledge 仓库的访问边界和协作范围，不复制项目事实结论。\n\n",
        )
        write_if_missing(
            vault_root / "global/sync-status.md",
            "# Sync Status\n\n| Project | Local Path | Remote | Last Sync | Notes |\n| --- | --- | --- | --- | --- |\n",
        )
    if initialize_git:
        init_git_repo(vault_root)
        if initial_commit:
            generated_files = repository_files(vault_root) - existing_files
            commit_git_repo(vault_root, "Initialize portfolio knowledge index", generated_files)


def ensure_profile(profile: str) -> None:
    if profile not in PROFILES:
        raise SystemExit(f"Unknown profile: {profile}. Expected one of: {', '.join(sorted(PROFILES))}")


def init_project_root(
    project_root: Path,
    project_id: str,
    name: str,
    profile: str,
    domains: list[str] | None = None,
    include_repository_dirs: bool = True,
    initialize_git: bool = True,
    initial_commit: bool = True,
    adopt_existing: bool = False,
) -> None:
    ensure_profile(profile)
    ensure_project_root_boundary(project_root, adopt_existing=adopt_existing)
    existing_files = repository_files(project_root)
    selected_domains = domains or DOMAINS
    knowledge_root = project_root / "knowledge"
    project_dirs = ["meetings"]
    if include_repository_dirs:
        project_dirs.extend(["inbox", "archive/superseded"])
    for rel in project_dirs:
        (project_root / rel).mkdir(parents=True, exist_ok=True)
    knowledge_root.mkdir(parents=True, exist_ok=True)
    write_if_missing(project_root / ".gitignore", PROJECT_GITIGNORE)

    write_if_missing(
        project_root / "project.md",
        f"""# 项目

## 基本信息

- Project ID: {project_id}
- Project Name: {name}
- Owner: unknown
- Status: draft
- Start Date: {date.today().isoformat()}

## 背景

- unknown

## 目标

- unknown

## 相关方

| Name | Role | Notes |
| --- | --- | --- |
| unknown | unknown | unknown |

## 协作与共享边界

- 默认共享范围：仅本项目参与者。
- 访问边界：由本项目 knowledge 仓库的本地/远端访问权限决定，不存在隐式全局共享。
- 跨项目引用：必须保留明确来源链接，并经用户确认后才可进入另一个项目的当前结论。
- 远端策略：只有多人协作、同步、备份或审计需要时才配置 remote 或 push。

## 当前范围

- unknown

## 不在范围内

- unknown

## 链接

- unknown
""",
    )
    write_if_missing(project_root / "project-config.yaml", make_project_config(profile, selected_domains))

    write_if_missing(
        knowledge_root / "current-summary.md",
        "# 当前摘要\n\n## 快照\n\n- 当前状态：draft\n- 最近更新：unknown\n- 当前来源：unknown\n\n",
    )
    write_if_missing(knowledge_root / "current-decisions.md", "# 当前决定\n\n")
    write_if_missing(knowledge_root / "current-open-questions.md", "# 当前未决事项\n\n")
    write_if_missing(knowledge_root / "current-todos.md", "# 当前 Todo\n\n")
    write_if_missing(knowledge_root / "timeline.md", "# Timeline\n\n")
    copy_template_if_missing(KNOWLEDGE_INDEX_TEMPLATE, knowledge_root / "index.md")
    write_project_log_if_missing(
        knowledge_root / "log.md",
        "init-project",
        project_id,
        ["Created: project knowledge repository scaffold"],
    )
    copy_template_if_missing(BRIEF_TEMPLATE, knowledge_root / "briefs" / "_template.md")
    if profile == "advanced":
        (project_root / "domain").mkdir(parents=True, exist_ok=True)
        copy_templates(DOMAIN_TEMPLATE_ROOT, project_root / "domain")
        write_if_missing(knowledge_root / "by-domain.md", make_by_domain_template(selected_domains))
        copy_templates(PROJECT_KNOWLEDGE_TEMPLATE_ROOT, knowledge_root)
    if initialize_git:
        init_git_repo(project_root)
        if initial_commit:
            generated_files = repository_files(project_root) - existing_files
            commit_git_repo(project_root, f"Initialize {project_id} knowledge repository", generated_files)


def new_project(vault_root: Path, project_id: str, name: str, profile: str | None) -> None:
    selected_profile = profile or vault_profile(vault_root)
    ensure_profile(selected_profile)
    init_vault(vault_root, selected_profile, initial_commit=False)
    project_root = vault_root / "projects" / project_id
    init_project_root(
        project_root,
        project_id,
        name,
        selected_profile,
        parse_domains(vault_root / "vault.yaml"),
        include_repository_dirs=False,
        initialize_git=False,
        initial_commit=False,
        adopt_existing=True,
    )


def make_by_domain_template(domains: list[str] | None = None) -> str:
    selected_domains = domains or DOMAINS
    sections = ["# By Domain\n"]
    for domain in selected_domains:
        sections.append(
            f"""## {domain}

### 当前状态

- unknown

### 决定 / Todo / 未决事项

- unknown
"""
        )
    return "\n".join(sections)


def append_missing_domain_sections(by_domain_path: Path, domains: list[str]) -> None:
    existing = read_text(by_domain_path)
    additions: list[str] = []
    for domain in domains:
        if f"## {domain}" not in existing:
            additions.append(
                f"""## {domain}

### 当前状态

- unknown

### 决定 / Todo / 未决事项

- unknown
"""
            )
    if additions:
        separator = "\n\n" if existing.strip() else ""
        by_domain_path.write_text(existing.rstrip() + separator + "\n\n".join(additions) + "\n", encoding="utf-8")


def is_placeholder_by_domain(path: Path) -> bool:
    if not path.exists():
        return True
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped in {"- unknown", "> `Domain` 是项目知识的分面视图。下面是通用默认分类；如果你的团队有更明确的业务场景，可以在项目创建时替换，但项目开始后应保持稳定。"}:
            continue
        return False
    return True


def set_project_root_domains(project_root: Path, domains: list[str]) -> None:
    if not domains:
        raise SystemExit("At least one domain is required")
    if not project_root.exists():
        raise SystemExit(f"Project does not exist: {project_root}")
    profile = project_profile(project_root, "minimal")
    write_project_config(project_root, profile, domains)
    taxonomy_path = project_root / "knowledge" / "project-taxonomy.md"
    if taxonomy_path.exists():
        current = read_text(taxonomy_path)
        domain_table = "\n".join(f"| `{domain}` |  |  |" for domain in domains)
        marker = "## 当前项目 Domain\n"
        block = f"{marker}\n| Domain | Use For | Notes |\n| --- | --- | --- |\n{domain_table}\n"
        if marker in current:
            before = current.split(marker, 1)[0].rstrip()
            taxonomy_path.write_text(before + "\n\n" + block, encoding="utf-8")
        else:
            taxonomy_path.write_text(current.rstrip() + "\n\n" + block, encoding="utf-8")
    by_domain_path = project_root / "knowledge" / "by-domain.md"
    if by_domain_path.exists():
        if is_placeholder_by_domain(by_domain_path):
            by_domain_path.write_text(make_by_domain_template(domains), encoding="utf-8")
        else:
            append_missing_domain_sections(by_domain_path, domains)


def set_project_domains(vault_root: Path, project_id: str, domains: list[str]) -> None:
    set_project_root_domains(vault_root / "projects" / project_id, domains)


def sanitize_part(value: str) -> str:
    cleaned = value.strip().replace("/", "-").replace("\\", "-")
    cleaned = "-".join(cleaned.split())
    return cleaned or "unknown"


def new_meeting_in_project(
    project_root: Path,
    project_id: str,
    meeting_date: str,
    location: str,
    topic: str,
    transcript: Path | None,
) -> Path:
    if not project_root.exists():
        raise SystemExit(f"Project does not exist: {project_root}")

    location_part = sanitize_part(location)
    topic_part = sanitize_part(topic)
    year = meeting_date[:4]
    meeting_id = f"{meeting_date}_{location_part}_{topic_part}"
    meeting_root = project_root / "meetings" / year / meeting_id
    artifacts_root = meeting_root / "artifacts"
    artifacts_root.mkdir(parents=True, exist_ok=True)

    write_if_missing(
        meeting_root / "metadata.yaml",
        f"""project_id: "{project_id}"
meeting_id: "{meeting_id}"
topic: "{topic}"
location: "{location}"
meeting_datetime: "{meeting_date}"
time_confidence: "date_only"
received_datetime: "unknown"
participants: []
source:
  transcript: "transcript.md"
  artifacts: []
tags: []
notes: ""
""",
    )

    transcript_path = meeting_root / "transcript.md"
    if transcript:
        shutil.copyfile(transcript, transcript_path)
    else:
        write_if_missing(
            transcript_path,
            "# Transcript\n\n## Source\n\n- Source file: unknown\n\n## Content\n\n",
        )

    write_if_missing(meeting_root / "analysis.md", "# 会议分析\n\n")
    copy_template_if_missing(ARTIFACT_MANIFEST_TEMPLATE, artifacts_root / "manifest.yaml")
    try:
        meeting_relative = meeting_root.relative_to(project_root)
    except ValueError:
        meeting_relative = meeting_root
    append_project_log(
        project_root / "knowledge" / "log.md",
        "new-meeting",
        meeting_id,
        [f"Created: {meeting_relative.as_posix()}"],
    )
    return meeting_root


def new_meeting(
    vault_root: Path,
    project_id: str,
    meeting_date: str,
    location: str,
    topic: str,
    transcript: Path | None,
) -> Path:
    return new_meeting_in_project(
        vault_root / "projects" / project_id,
        project_id,
        meeting_date,
        location,
        topic,
        transcript,
    )


class ValidationResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def print(self) -> None:
        for message in self.errors:
            print(f"ERROR: {message}")
        for message in self.warnings:
            print(f"WARN: {message}")
        if not self.errors and not self.warnings:
            print("OK")


def validate_required(path: Path, result: ValidationResult, label: str | None = None) -> None:
    if not path.exists():
        result.error(f"Missing {label or path}")


def validate_markdown_domains(path: Path, allowed_domains: set[str], result: ValidationResult) -> None:
    if not path.exists():
        return
    lines = read_text(path).splitlines()
    domain_index: int | None = None
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if "Domain" in cells:
            domain_index = cells.index("Domain")
            continue
        if domain_index is None or len(cells) <= domain_index:
            continue
        if set(cells) == {"---"}:
            continue
        domain = cells[domain_index]
        if not domain or domain == "<Domain>":
            result.warn(f"{path}: empty Domain cell")
        elif domain not in allowed_domains and not domain.startswith("<"):
            result.error(f"{path}: unknown Domain '{domain}'")


def markdown_table_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    headers: list[str] | None = None
    rows: list[dict[str, str]] = []
    for line in read_text(path).splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if set(cells) == {"---"}:
            continue
        if headers is None:
            headers = cells
            continue
        if all(cell.startswith("---") for cell in cells):
            continue
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        rows.append(dict(zip(headers, cells)))
    return rows


def lint_duplicate_open_todos(project_root: Path, result: ValidationResult) -> None:
    todos_path = project_root / "knowledge" / "current-todos.md"
    seen: dict[tuple[str, str], str] = {}
    for row in markdown_table_rows(todos_path):
        if row.get("Status") != "open":
            continue
        key = (row.get("Todo", "").strip().casefold(), row.get("Source", "").strip())
        if not key[0]:
            continue
        existing_id = seen.get(key)
        current_id = row.get("ID", "")
        if existing_id:
            result.warn(f"{todos_path}: duplicate open todo '{row.get('Todo')}' ({existing_id}, {current_id})")
        else:
            seen[key] = current_id


def lint_active_decisions_with_supersedes(project_root: Path, result: ValidationResult) -> None:
    decisions_path = project_root / "knowledge" / "current-decisions.md"
    for row in markdown_table_rows(decisions_path):
        if row.get("Status") != "active":
            continue
        supersedes = row.get("Supersedes", "").strip()
        if supersedes:
            result.warn(
                f"{decisions_path}: active decision has Supersedes '{supersedes}' ({row.get('ID', '')})"
            )


def lint_missing_source_links(project_root: Path, result: ValidationResult) -> None:
    knowledge_root = project_root / "knowledge"
    for filename in ["current-decisions.md", "current-open-questions.md", "current-todos.md"]:
        path = knowledge_root / filename
        for row in markdown_table_rows(path):
            source = row.get("Source", "").strip()
            if not source or source == "<source>" or source == "unknown":
                continue
            if "](" not in source:
                row_id = row.get("ID", "unknown")
                result.warn(f"{path}: missing markdown source link ({row_id})")
                continue
            for target in MARKDOWN_LINK_RE.findall(source):
                if "://" in target or target.startswith("#"):
                    continue
                target_path = (path.parent / target).resolve()
                try:
                    target_path.relative_to(project_root.resolve())
                except ValueError:
                    result.warn(f"{path}: markdown source link escapes project root ({target})")
                    continue
                if not target_path.exists():
                    row_id = row.get("ID", "unknown")
                    result.warn(f"{path}: broken markdown source link ({row_id} -> {target})")


def lint_open_questions_without_timeline_reference(project_root: Path, result: ValidationResult) -> None:
    questions_path = project_root / "knowledge" / "current-open-questions.md"
    timeline_text = read_text(project_root / "knowledge" / "timeline.md")
    for row in markdown_table_rows(questions_path):
        if row.get("Status") != "open":
            continue
        question_id = row.get("ID", "").strip()
        if question_id and question_id not in timeline_text:
            result.warn(f"{questions_path}: open question not referenced in timeline ({question_id})")


def lint_repeated_terms_missing_from_context(project_root: Path, result: ValidationResult) -> None:
    if project_profile(project_root, "minimal") != "advanced":
        return
    term_counts: dict[str, int] = {}
    for analysis_path in sorted((project_root / "meetings").glob("*/*/analysis.md")):
        for line in read_text(analysis_path).splitlines():
            if "术语：" not in line:
                continue
            term = line.split("术语：", 1)[1].strip(" -`")
            if term:
                term_counts[term] = term_counts.get(term, 0) + 1
    if not term_counts:
        return
    context_text = "\n".join(
        read_text(path)
        for path in [
            project_root / "domain" / "glossary.md",
            project_root / "domain" / "entity-registry.md",
            project_root / "knowledge" / "domain-context.md",
            project_root / "knowledge" / "entity-aliases.md",
            project_root / "knowledge" / "project-taxonomy.md",
        ]
    )
    for term, count in sorted(term_counts.items()):
        if count >= 2 and term not in context_text:
            result.warn(f"{project_root / 'meetings'}: repeated term missing from domain/context '{term}'")


def section_has_markdown_link(text: str, section: str) -> bool:
    marker = f"## {section}"
    if marker not in text:
        return False
    section_text = text.split(marker, 1)[1]
    next_heading = section_text.find("\n## ")
    if next_heading != -1:
        section_text = section_text[:next_heading]
    return "](" in section_text


def lint_query_archive_briefs(project_root: Path, result: ValidationResult) -> None:
    briefs_root = project_root / "knowledge" / "briefs"
    if not briefs_root.exists():
        return
    for brief in sorted(briefs_root.glob("*.md")):
        if brief.name == "_template.md":
            continue
        text = read_text(brief)
        if "Type: query-archive-brief" not in text:
            result.warn(f"{brief}: brief missing Type: query-archive-brief")
        if not section_has_markdown_link(text, "Cited Project Sources"):
            result.warn(f"{brief}: brief missing Cited Project Sources")
        if not section_has_markdown_link(text, "Cited Meeting Or Artifact Sources"):
            result.warn(f"{brief}: brief missing Cited Meeting Or Artifact Sources")


def health_lint_project_root(project_root: Path) -> ValidationResult:
    result = ValidationResult()
    if not project_root.exists():
        result.error(f"Project does not exist: {project_root}")
        return result
    lint_duplicate_open_todos(project_root, result)
    lint_active_decisions_with_supersedes(project_root, result)
    lint_missing_source_links(project_root, result)
    lint_open_questions_without_timeline_reference(project_root, result)
    lint_repeated_terms_missing_from_context(project_root, result)
    lint_query_archive_briefs(project_root, result)
    return result


def validate_sources(path: Path, result: ValidationResult) -> None:
    if not path.exists():
        return
    text = read_text(path)
    if "<source>" in text or "unknown" in text:
        result.warn(f"{path}: contains placeholder source or unknown values")


def validate_knowledge_index(path: Path, result: ValidationResult) -> None:
    validate_required(path, result)
    if not path.exists():
        return
    text = read_text(path)
    for section in KNOWLEDGE_INDEX_REQUIRED_SECTIONS:
        if section not in text:
            result.error(f"{path}: missing section {section}")


def validate_knowledge_log(path: Path, result: ValidationResult) -> None:
    validate_required(path, result)
    if not path.exists():
        return
    headings = [line for line in read_text(path).splitlines() if line.startswith("## ")]
    for heading in headings:
        if not KNOWLEDGE_LOG_HEADING_RE.match(heading):
            result.error(f"{path}: malformed log heading {heading}")


def parse_simple_yaml_value(value: str) -> str | int | list[str]:
    stripped = value.strip()
    if stripped == "[]":
        return []
    if stripped.startswith(("\"", "'")) and stripped.endswith(("\"", "'")) and len(stripped) >= 2:
        return stripped[1:-1]
    if stripped.isdigit():
        return int(stripped)
    return stripped


def parse_artifact_manifest(path: Path, result: ValidationResult) -> list[dict[str, str | int]]:
    if not path.exists():
        return []
    artifacts_seen = False
    artifacts_inline_empty = False
    entries: list[dict[str, str | int]] = []
    current: dict[str, str | int] | None = None

    for line_number, line in enumerate(read_text(path).splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("artifacts:"):
            artifacts_seen = True
            value = stripped.split(":", 1)[1].strip()
            artifacts_inline_empty = value == "[]"
            if value and value != "[]":
                result.error(f"{path}:{line_number}: artifacts must be a list")
            continue
        if not artifacts_seen or artifacts_inline_empty:
            continue
        if not line.startswith(" "):
            current = None
            continue
        if stripped.startswith("- "):
            current = {}
            entries.append(current)
            rest = stripped[2:].strip()
            if rest:
                if ":" not in rest:
                    result.error(f"{path}:{line_number}: malformed artifact entry")
                    continue
                key, value = rest.split(":", 1)
                current[key.strip()] = parse_simple_yaml_value(value)
            continue
        if current is None:
            result.error(f"{path}:{line_number}: artifact field without list item")
            continue
        if ":" not in stripped:
            result.error(f"{path}:{line_number}: malformed artifact field")
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = parse_simple_yaml_value(value)

    if not artifacts_seen:
        result.error(f"{path}: missing artifacts list")
    return entries


def validate_artifact_manifest(
    artifact_manifest: Path,
    artifacts_root: Path,
    result: ValidationResult,
    strict_hashes: bool = False,
) -> None:
    entries = parse_artifact_manifest(artifact_manifest, result)
    filenames: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        missing_fields = ARTIFACT_MANIFEST_REQUIRED_FIELDS - set(entry)
        for field in sorted(missing_fields):
            result.error(f"{artifact_manifest}: artifact entry {index} missing {field}")
        filename = entry.get("filename")
        if isinstance(filename, str):
            if filename in filenames:
                result.error(f"{artifact_manifest}: duplicate artifact filename {filename}")
            filenames.add(filename)
        sha256 = entry.get("sha256")
        if isinstance(sha256, str):
            valid_hash = len(sha256) == 64 and all(char in "0123456789abcdefABCDEF" for char in sha256)
            if sha256 == "pending":
                if strict_hashes:
                    result.error(f"{artifact_manifest}: artifact entry {index} has pending sha256")
                else:
                    result.warn(f"{artifact_manifest}: artifact entry {index} has pending sha256")
            elif not valid_hash:
                result.error(f"{artifact_manifest}: artifact entry {index} has invalid sha256")
        size_bytes = entry.get("size_bytes")
        if not isinstance(size_bytes, int):
            result.error(f"{artifact_manifest}: artifact entry {index} size_bytes must be an integer")
        git_policy = entry.get("git_policy")
        if isinstance(git_policy, str) and git_policy not in ARTIFACT_GIT_POLICIES:
            result.error(f"{artifact_manifest}: artifact entry {index} has invalid git_policy '{git_policy}'")
        artifact_path = entry.get("path")
        local_path: Path | None = None
        if isinstance(artifact_path, str):
            relative_path = Path(artifact_path)
            if relative_path.is_absolute() or ".." in relative_path.parts:
                result.error(f"{artifact_manifest}: artifact entry {index} path must be relative to the meeting directory")
            else:
                local_path = artifact_manifest.parents[1] / relative_path
        if strict_hashes and isinstance(git_policy, str) and git_policy in LOCAL_ARTIFACT_POLICIES:
            if local_path is None or not local_path.exists():
                result.error(f"{artifact_manifest}: artifact entry {index} local file is missing for git_policy {git_policy}")
            elif local_path.is_file():
                if isinstance(size_bytes, int) and local_path.stat().st_size != size_bytes:
                    result.error(f"{artifact_manifest}: artifact entry {index} size_bytes does not match {artifact_path}")
                if isinstance(sha256, str) and sha256 != "pending":
                    digest = hashlib.sha256(local_path.read_bytes()).hexdigest()
                    if digest.lower() != sha256.lower():
                        result.error(f"{artifact_manifest}: artifact entry {index} sha256 does not match {artifact_path}")

    artifact_files = []
    if artifacts_root.exists():
        artifact_files = sorted(path for path in artifacts_root.iterdir() if path.is_file() and path.name != "manifest.yaml")
    for artifact in artifact_files:
        if artifact.name not in filenames:
            result.error(f"{artifact_manifest}: missing manifest entry for {artifact.name}")


def validate_meeting(meeting_root: Path, result: ValidationResult, strict_artifact_hashes: bool = False) -> None:
    metadata = meeting_root / "metadata.yaml"
    transcript = meeting_root / "transcript.md"
    analysis = meeting_root / "analysis.md"
    artifacts_root = meeting_root / "artifacts"
    artifact_manifest = artifacts_root / "manifest.yaml"
    validate_required(metadata, result)
    validate_required(transcript, result)
    validate_required(analysis, result)
    validate_required(artifact_manifest, result)
    metadata_text = read_text(metadata)
    for key in ["project_id:", "meeting_id:", "meeting_datetime:", "time_confidence:"]:
        if key not in metadata_text:
            result.error(f"{metadata}: missing {key}")
    if 'meeting_datetime: "unknown"' in metadata_text or "meeting_datetime: unknown" in metadata_text:
        result.error(f"{metadata}: meeting_datetime is unknown")
    if "received_datetime:" in metadata_text and "meeting_datetime:" in metadata_text:
        # Guardrail only: received_datetime is allowed, but should not be the only useful date.
        pass
    validate_artifact_manifest(artifact_manifest, artifacts_root, result, strict_hashes=strict_artifact_hashes)


def validate_project_root(
    project_root: Path,
    fallback_profile: str = "minimal",
    require_repository_dirs: bool = True,
    strict_artifact_hashes: bool = False,
    legacy_compat: bool = False,
) -> ValidationResult:
    result = ValidationResult()
    if not project_root.exists():
        result.error(f"Project does not exist: {project_root}")
        return result

    profile = project_profile(project_root, fallback_profile)
    allowed_domains = set(parse_domains(project_root / "project-config.yaml"))
    knowledge_root = project_root / "knowledge"

    if require_repository_dirs:
        validate_required(project_root / "inbox", result)
        validate_required(project_root / "archive", result)
    validate_required(project_root / "project.md", result)
    validate_required(project_root / "project-config.yaml", result)
    project_text = read_text(project_root / "project.md")
    if not legacy_compat and "## 协作与共享边界" not in project_text:
        result.error(f"{project_root / 'project.md'}: missing 协作与共享边界 section")
    config_text = read_text(project_root / "project-config.yaml")
    if legacy_compat:
        result.warn(
            f"{project_root}: legacy vault project layout detected; validate-project is running in compatibility mode. "
            "Use migrate-project --dry-run before splitting this project into an independent knowledge repository."
        )
    else:
        for key in [
            "repository_role:",
            "collaboration_scope:",
            "remote_policy:",
            "cross_project_references:",
            "artifact_git_policy:",
            "raw_media_default:",
            "large_binary_default:",
            "max_default_artifact_size_mb:",
        ]:
            if key not in config_text:
                result.error(f"{project_root / 'project-config.yaml'}: missing {key}")
        repository_role = parse_scalar_config(project_root / "project-config.yaml", "repository_role", "")
        if repository_role != "project_knowledge":
            result.error(f"{project_root / 'project-config.yaml'}: repository_role must be project_knowledge")
    for filename in [
        "current-summary.md",
        "current-decisions.md",
        "current-open-questions.md",
        "current-todos.md",
        "timeline.md",
    ]:
        validate_required(knowledge_root / filename, result)
    validate_knowledge_index(knowledge_root / "index.md", result)
    validate_knowledge_log(knowledge_root / "log.md", result)

    if profile == "advanced":
        for filename in [
            "glossary.md",
            "taxonomy.md",
            "entity-registry.md",
            "decision-types.md",
            "writing-style.md",
        ]:
            if not legacy_compat:
                validate_required(project_root / "domain" / filename, result)
        for filename in [
            "by-domain.md",
            "domain-context.md",
            "entity-aliases.md",
            "project-taxonomy.md",
            "source-map.md",
        ]:
            validate_required(knowledge_root / filename, result)

    for filename in [
        "current-decisions.md",
        "current-open-questions.md",
        "current-todos.md",
    ]:
        path = knowledge_root / filename
        validate_markdown_domains(path, allowed_domains, result)
        validate_sources(path, result)

    meetings_root = project_root / "meetings"
    if meetings_root.exists():
        for meeting_dir in sorted(path for path in meetings_root.glob("*/*") if path.is_dir()):
            validate_meeting(meeting_dir, result, strict_artifact_hashes=strict_artifact_hashes)
            validate_markdown_domains(meeting_dir / "analysis.md", allowed_domains, result)
            validate_sources(meeting_dir / "analysis.md", result)
    return result


def validate_project(vault_root: Path, project_id: str) -> ValidationResult:
    return validate_project_root(
        vault_root / "projects" / project_id,
        vault_profile(vault_root),
        require_repository_dirs=False,
        legacy_compat=True,
    )


def has_legacy_global_registers(vault_root: Path) -> bool:
    return any(
        (vault_root / "global" / filename).exists()
        for filename in [
            "current-summary.md",
            "decision-register.md",
            "open-question-register.md",
            "todo-register.md",
            "timeline.md",
        ]
    )


def validate_vault(vault_root: Path) -> ValidationResult:
    result = ValidationResult()
    validate_required(vault_root / "vault.yaml", result)
    validate_required(vault_root / "inbox", result)
    validate_required(vault_root / "projects", result)
    validate_required(vault_root / "archive", result)
    profile = vault_profile(vault_root)
    if profile == "advanced":
        for filename in [
            "glossary.md",
            "taxonomy.md",
            "entity-registry.md",
            "decision-types.md",
            "writing-style.md",
        ]:
            validate_required(vault_root / "domain" / filename, result)
        if has_legacy_global_registers(vault_root):
            result.warn(
                f"{vault_root}: legacy global fact registers detected; validate-vault is running in compatibility mode. "
                "Use migrate-project --dry-run before splitting projects into independent knowledge repositories."
            )
        else:
            validate_required(vault_root / "global/project-index.md", result)
            validate_required(vault_root / "global/access-boundaries.md", result)
            validate_required(vault_root / "global/sync-status.md", result)

    projects_root = vault_root / "projects"
    if projects_root.exists():
        for project_dir in sorted(path for path in projects_root.iterdir() if path.is_dir()):
            project_result = validate_project(vault_root, project_dir.name)
            result.errors.extend(project_result.errors)
            result.warnings.extend(project_result.warnings)
    return result


def migrate_project_dry_run(vault_root: Path, project_id: str, project_root: Path) -> None:
    source_root = vault_root / "projects" / project_id
    if not source_root.exists():
        raise SystemExit(f"Project does not exist in legacy/portfolio vault: {project_id}")
    print(f"DRY RUN: migrate {source_root} -> {project_root}")
    print("Planned copy scope:")
    for item in sorted(repository_files(source_root)):
        print(f"- {item}")

    result = validate_project(vault_root, project_id)
    if result.errors:
        print("Validation issues to fix before migration:")
        result.print()
    else:
        print("Source project validation: OK")

    legacy_global_paths = [
        vault_root / "global/decision-register.md",
        vault_root / "global/open-question-register.md",
        vault_root / "global/todo-register.md",
        vault_root / "global/current-summary.md",
        vault_root / "global/timeline.md",
    ]
    existing_global_paths = [path for path in legacy_global_paths if path.exists()]
    if existing_global_paths:
        print("WARN: legacy global fact files exist. Review dependencies before splitting:")
        for path in existing_global_paths:
            print(f"- {path.relative_to(vault_root)}")

    print("Next manual steps:")
    print("1. Create the target project knowledge repo with --project-root init-project, or copy this project into an empty target root.")
    print("2. Copy only this project's files; do not copy sibling projects or global fact registers.")
    print("3. Ensure project.md collaboration boundary and project-config artifact/collaboration fields are present.")
    print("4. Run --project-root validate-project.")
    print("5. Create a local baseline commit in the new project repo.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Meeting knowledge repository scaffolding helper. "
            "Default new-project workflow: use --project-root init-project. "
            "--vault-root commands are for portfolio/index or legacy vaults."
        )
    )
    root_group = parser.add_mutually_exclusive_group()
    root_group.add_argument("--project-root", type=Path, help="Root of one project's knowledge repository.")
    root_group.add_argument("--vault-root", type=Path, help="Root of a portfolio/index or legacy vault.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_project_parser = subparsers.add_parser(
        "init-project",
        help="Initialize one project's knowledge repository. Default for new projects.",
        description="Initialize one project's knowledge repository. This is the default entry point for new projects.",
    )
    init_project_parser.add_argument("--project-id")
    init_project_parser.add_argument("--name")
    init_project_parser.add_argument("--profile", choices=sorted(PROFILES), default="minimal")
    init_project_parser.add_argument("--no-git", action="store_true", help="Create files without initializing local Git.")
    init_project_parser.add_argument("--no-initial-commit", action="store_true", help="Initialize Git without creating the baseline commit.")
    init_project_parser.add_argument(
        "--adopt-existing",
        action="store_true",
        help="Allow initializing in an existing Git worktree or boundary after explicit confirmation.",
    )

    init_parser = subparsers.add_parser(
        "init-vault",
        help="Initialize a portfolio/index or legacy vault. Not the default new-project path.",
        description="Initialize a portfolio/index or legacy vault. Use only for cross-project indexes or legacy structures.",
    )
    init_parser.add_argument("--profile", choices=sorted(PROFILES), default="minimal")
    init_parser.add_argument("--no-git", action="store_true", help="Create files without initializing local Git.")
    init_parser.add_argument("--no-initial-commit", action="store_true", help="Initialize Git without creating the baseline commit.")

    project_parser = subparsers.add_parser(
        "new-project",
        help="Create a project inside a portfolio/index or legacy vault. Prefer --project-root init-project for new projects.",
        description="Create a project inside a portfolio/index or legacy vault. Prefer --project-root init-project for new projects.",
    )
    project_parser.add_argument("project_id")
    project_parser.add_argument("--name", required=True)
    project_parser.add_argument("--profile", choices=sorted(PROFILES))

    meeting_parser = subparsers.add_parser(
        "new-meeting",
        help="Create a meeting directory. Use --project-root by default; --vault-root is legacy/portfolio only.",
    )
    meeting_parser.add_argument("project_id", nargs="?")
    meeting_parser.add_argument("--date", required=True)
    meeting_parser.add_argument("--location", required=True)
    meeting_parser.add_argument("--topic", required=True)
    meeting_parser.add_argument("--transcript", type=Path)

    validate_project_parser = subparsers.add_parser(
        "validate-project",
        help="Validate one project knowledge repository, or a project inside a legacy/portfolio vault.",
    )
    validate_project_parser.add_argument("project_id", nargs="?")

    subparsers.add_parser(
        "validate-vault",
        help="Validate a portfolio/index or legacy vault.",
    )

    subparsers.add_parser(
        "health-lint",
        help="Report project knowledge consistency warnings without modifying files.",
    )

    domains_parser = subparsers.add_parser(
        "set-project-domains",
        help="Set domains for a project inside a portfolio/index or legacy vault.",
    )
    domains_parser.add_argument("project_id")
    domains_parser.add_argument("domains", nargs="+")

    project_domains_parser = subparsers.add_parser(
        "set-domains",
        help="Set domains for one project knowledge repository. Default for new projects.",
    )
    project_domains_parser.add_argument("domains", nargs="+")

    commit_parser = subparsers.add_parser(
        "commit",
        help="Validate and create a local commit. Use --project-root by default; --vault-root is legacy/portfolio only.",
    )
    commit_parser.add_argument("-m", "--message", required=True)
    commit_parser.add_argument(
        "--allow-invalid",
        action="store_true",
        help="Commit without running validation. Use only for explicit WIP or migration checkpoints.",
    )
    commit_parser.add_argument(
        "--legacy-fact-vault",
        action="store_true",
        help="Allow --vault-root commit to include projects/* facts or global fact registers. Use only for explicit legacy/special-case vault maintenance.",
    )
    commit_parser.add_argument(
        "--include-artifacts",
        action="store_true",
        help="Allow committing raw or large inbox/artifact files. Use only after confirming the project artifact Git policy.",
    )
    commit_parser.add_argument(
        "--allow-pending-artifacts",
        action="store_true",
        help="Allow committing artifact manifest entries with sha256: pending. Use only for explicit incomplete checkpoints.",
    )
    commit_parser.add_argument(
        "--include-extra",
        action="store_true",
        help="Allow committing paths outside the validated knowledge surface. Use only after explicit user confirmation.",
    )

    migrate_parser = subparsers.add_parser(
        "migrate-project",
        help="Dry-run checks for splitting one legacy vault project into its own project knowledge repository.",
    )
    migrate_parser.add_argument("project_id")
    migrate_parser.add_argument("--target-project-root", required=True, type=Path)
    migrate_parser.add_argument("--dry-run", action="store_true", required=True)

    return parser


def resolve_required_root(root: Path | None, name: str) -> Path:
    if root is None:
        raise SystemExit(f"{name} is required for this command")
    return root.expanduser().resolve()


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "init-project":
        project_root = resolve_required_root(args.project_root, "--project-root")
        project_id = args.project_id or project_root.name
        name = args.name or project_id
        init_project_root(
            project_root,
            project_id,
            name,
            args.profile,
            initialize_git=not args.no_git,
            initial_commit=not args.no_initial_commit,
            adopt_existing=args.adopt_existing,
        )
        print(project_root)
    elif args.command == "init-vault":
        vault_root = resolve_required_root(args.vault_root, "--vault-root")
        init_vault(
            vault_root,
            args.profile,
            initialize_git=not args.no_git,
            initial_commit=not args.no_initial_commit,
        )
        print(vault_root)
    elif args.command == "new-project":
        vault_root = resolve_required_root(args.vault_root, "--vault-root")
        new_project(vault_root, args.project_id, args.name, args.profile)
        print(vault_root / "projects" / args.project_id)
    elif args.command == "new-meeting":
        transcript = args.transcript.expanduser().resolve() if args.transcript else None
        if args.project_root:
            project_root = args.project_root.expanduser().resolve()
            project_id = args.project_id or project_id_from_root(project_root)
            meeting_root = new_meeting_in_project(
                project_root,
                project_id,
                args.date,
                args.location,
                args.topic,
                transcript,
            )
        else:
            vault_root = resolve_required_root(args.vault_root, "--vault-root")
            if not args.project_id:
                raise SystemExit("project_id is required when using --vault-root")
            meeting_root = new_meeting(
                vault_root,
                args.project_id,
                args.date,
                args.location,
                args.topic,
                transcript,
            )
        print(meeting_root)
    elif args.command == "validate-project":
        if args.project_root:
            result = validate_project_root(args.project_root.expanduser().resolve())
        else:
            vault_root = resolve_required_root(args.vault_root, "--vault-root")
            if not args.project_id:
                raise SystemExit("project_id is required when using --vault-root")
            result = validate_project(vault_root, args.project_id)
        result.print()
        raise SystemExit(1 if result.errors else 0)
    elif args.command == "validate-vault":
        vault_root = resolve_required_root(args.vault_root, "--vault-root")
        result = validate_vault(vault_root)
        result.print()
        raise SystemExit(1 if result.errors else 0)
    elif args.command == "health-lint":
        if args.project_root:
            result = health_lint_project_root(args.project_root.expanduser().resolve())
        else:
            raise SystemExit("--project-root is required for health-lint")
        result.print()
        raise SystemExit(1 if result.errors else 0)
    elif args.command == "set-project-domains":
        vault_root = resolve_required_root(args.vault_root, "--vault-root")
        set_project_domains(vault_root, args.project_id, args.domains)
        print(vault_root / "projects" / args.project_id / "project-config.yaml")
    elif args.command == "set-domains":
        project_root = resolve_required_root(args.project_root, "--project-root")
        set_project_root_domains(project_root, args.domains)
        print(project_root / "project-config.yaml")
    elif args.command == "commit":
        project_commit_paths = None
        project_commit_force_paths = None
        if args.project_root:
            repo_root = args.project_root.expanduser().resolve()
            if not args.allow_invalid:
                result = validate_project_root(
                    repo_root,
                    strict_artifact_hashes=not args.allow_pending_artifacts,
                )
                result.print()
                if result.errors:
                    raise SystemExit(1)
            changed_paths = git_changed_paths(repo_root)
            risky_paths = risky_artifact_paths(repo_root, changed_paths)
            if risky_paths and not args.include_artifacts:
                print(
                    "ERROR: refusing to commit raw or large inbox/artifact files by default. "
                    "Store controlled source links/hashes instead, or pass --include-artifacts only after confirming the project artifact Git policy."
                )
                for path in risky_paths:
                    print(f"ERROR: risky artifact path: {path}")
                raise SystemExit(1)
            allowed_paths = [path for path in changed_paths if is_project_knowledge_path(path)]
            ignored_artifact_paths: list[Path] = []
            if args.include_artifacts:
                allowed_paths.extend(path for path in changed_paths if is_artifact_or_inbox_path(path))
                ignored_artifact_paths = [
                    path for path in git_ignored_untracked_paths(repo_root) if is_artifact_or_inbox_path(path)
                ]
                allowed_paths.extend(ignored_artifact_paths)
                project_commit_force_paths = ignored_artifact_paths
            unknown_paths = sorted(set(changed_paths) - set(allowed_paths))
            if unknown_paths and not args.include_extra:
                print(
                    "ERROR: refusing to commit paths outside the validated knowledge surface. "
                    "Move them into a controlled meeting/knowledge path, register artifacts in manifest, "
                    "or pass --include-extra only after explicit user confirmation."
                )
                for path in unknown_paths:
                    print(f"ERROR: unknown path: {path}")
                raise SystemExit(1)
            project_commit_paths = changed_paths + ignored_artifact_paths if args.include_extra else allowed_paths
        elif args.vault_root:
            repo_root = args.vault_root.expanduser().resolve()
            if not args.allow_invalid:
                result = validate_vault(repo_root)
                result.print()
                if result.errors:
                    raise SystemExit(1)
            changed_paths = git_changed_paths(repo_root)
            risky_paths = [path for path in changed_paths if not is_portfolio_metadata_path(path)]
            if risky_paths and not args.legacy_fact_vault:
                print(
                    "ERROR: --vault-root commit is limited to portfolio/index metadata by default. "
                    "Use --project-root commit for project knowledge repositories, or pass "
                    "--legacy-fact-vault only when explicitly maintaining a legacy/special-case fact vault."
                )
                for path in risky_paths:
                    print(f"ERROR: refusing to commit non-portfolio path: {path}")
                raise SystemExit(1)
        else:
            repo_root = resolve_required_root(None, "--project-root or --vault-root")
        did_commit = commit_git_repo(
            repo_root,
            args.message,
            project_commit_paths if args.project_root else None,
            project_commit_force_paths if args.project_root else None,
        )
        print("Committed" if did_commit else "No changes to commit")
    elif args.command == "migrate-project":
        vault_root = resolve_required_root(args.vault_root, "--vault-root")
        migrate_project_dry_run(
            vault_root,
            args.project_id,
            args.target_project_root.expanduser().resolve(),
        )


if __name__ == "__main__":
    main()
