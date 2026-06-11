#!/usr/bin/env python3
"""Small scaffolding helper for file-based meeting knowledge vaults."""

from __future__ import annotations

import argparse
import shutil
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
PROFILES = {"minimal", "advanced"}


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


def make_yaml_list(values: Iterable[str], indent: int = 2) -> str:
    prefix = " " * indent
    return "\n".join(f'{prefix}- "{value}"' for value in values)


def make_vault_config(profile: str) -> str:
    advanced = "true" if profile == "advanced" else "false"
    return f"""version: 1
profile: "{profile}"
language: "zh-CN"
source_policy: "meeting_or_artifact_required"
time_policy: "meeting_datetime_only"
domains:
{make_yaml_list(DOMAINS)}
enabled_layers:
  domain_knowledge: {advanced}
  global_registers: {advanced}
"""


def make_project_config(profile: str, domains: list[str] | None = None) -> str:
    selected_domains = domains or DOMAINS
    advanced = "true" if profile == "advanced" else "false"
    advanced_required = ""
    if profile == "advanced":
        advanced_required = '  - "by-domain.md"\n  - "domain-context.md"\n  - "entity-aliases.md"\n  - "project-taxonomy.md"\n  - "source-map.md"\n'
    return f"""version: 1
profile: "{profile}"
language: "zh-CN"
domains:
{make_yaml_list(selected_domains)}
required_current_files:
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


def init_vault(vault_root: Path, profile: str) -> None:
    ensure_profile(profile)
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
            vault_root / "global/current-summary.md",
            "# 全局当前摘要\n\n## 快照\n\n- 当前状态：draft\n- 最近更新：unknown\n\n",
        )
        write_if_missing(vault_root / "global/decision-register.md", "# Decision Register\n\n")
        write_if_missing(vault_root / "global/open-question-register.md", "# Open Question Register\n\n")
        write_if_missing(vault_root / "global/todo-register.md", "# Todo Register\n\n")
        write_if_missing(vault_root / "global/timeline.md", "# Global Timeline\n\n")


def ensure_profile(profile: str) -> None:
    if profile not in PROFILES:
        raise SystemExit(f"Unknown profile: {profile}. Expected one of: {', '.join(sorted(PROFILES))}")


def new_project(vault_root: Path, project_id: str, name: str, profile: str | None) -> None:
    selected_profile = profile or vault_profile(vault_root)
    ensure_profile(selected_profile)
    init_vault(vault_root, selected_profile)
    project_root = vault_root / "projects" / project_id
    knowledge_root = project_root / "knowledge"
    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "meetings").mkdir(parents=True, exist_ok=True)
    knowledge_root.mkdir(parents=True, exist_ok=True)

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

## 当前范围

- unknown

## 不在范围内

- unknown

## 链接

- unknown
""",
    )
    write_if_missing(project_root / "project-config.yaml", make_project_config(selected_profile, parse_domains(vault_root / "vault.yaml")))

    write_if_missing(
        knowledge_root / "current-summary.md",
        "# 当前摘要\n\n## 快照\n\n- 当前状态：draft\n- 最近更新：unknown\n- 当前来源：unknown\n\n",
    )
    write_if_missing(knowledge_root / "current-decisions.md", "# 当前决定\n\n")
    write_if_missing(knowledge_root / "current-open-questions.md", "# 当前未决事项\n\n")
    write_if_missing(knowledge_root / "current-todos.md", "# 当前 Todo\n\n")
    write_if_missing(knowledge_root / "timeline.md", "# Timeline\n\n")
    if selected_profile == "advanced":
        write_if_missing(knowledge_root / "by-domain.md", make_by_domain_template(parse_domains(project_root / "project-config.yaml")))
        copy_templates(PROJECT_KNOWLEDGE_TEMPLATE_ROOT, knowledge_root)


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


def set_project_domains(vault_root: Path, project_id: str, domains: list[str]) -> None:
    if not domains:
        raise SystemExit("At least one domain is required")
    project_root = vault_root / "projects" / project_id
    if not project_root.exists():
        raise SystemExit(f"Project does not exist: {project_id}")
    profile = project_profile(project_root, vault_profile(vault_root))
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


def sanitize_part(value: str) -> str:
    cleaned = value.strip().replace("/", "-").replace("\\", "-")
    cleaned = "-".join(cleaned.split())
    return cleaned or "unknown"


def new_meeting(
    vault_root: Path,
    project_id: str,
    meeting_date: str,
    location: str,
    topic: str,
    transcript: Path | None,
) -> Path:
    project_root = vault_root / "projects" / project_id
    if not project_root.exists():
        raise SystemExit(f"Project does not exist: {project_id}")

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
    return meeting_root


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


def validate_sources(path: Path, result: ValidationResult) -> None:
    if not path.exists():
        return
    text = read_text(path)
    if "<source>" in text or "unknown" in text:
        result.warn(f"{path}: contains placeholder source or unknown values")


def validate_meeting(meeting_root: Path, result: ValidationResult) -> None:
    metadata = meeting_root / "metadata.yaml"
    transcript = meeting_root / "transcript.md"
    analysis = meeting_root / "analysis.md"
    validate_required(metadata, result)
    validate_required(transcript, result)
    validate_required(analysis, result)
    metadata_text = read_text(metadata)
    for key in ["project_id:", "meeting_id:", "meeting_datetime:", "time_confidence:"]:
        if key not in metadata_text:
            result.error(f"{metadata}: missing {key}")
    if 'meeting_datetime: "unknown"' in metadata_text or "meeting_datetime: unknown" in metadata_text:
        result.error(f"{metadata}: meeting_datetime is unknown")
    if "received_datetime:" in metadata_text and "meeting_datetime:" in metadata_text:
        # Guardrail only: received_datetime is allowed, but should not be the only useful date.
        pass


def validate_project(vault_root: Path, project_id: str) -> ValidationResult:
    result = ValidationResult()
    project_root = vault_root / "projects" / project_id
    if not project_root.exists():
        result.error(f"Project does not exist: {project_id}")
        return result

    fallback_profile = vault_profile(vault_root)
    profile = project_profile(project_root, fallback_profile)
    allowed_domains = set(parse_domains(project_root / "project-config.yaml") or parse_domains(vault_root / "vault.yaml"))
    knowledge_root = project_root / "knowledge"

    validate_required(project_root / "project.md", result)
    validate_required(project_root / "project-config.yaml", result)
    for filename in [
        "current-summary.md",
        "current-decisions.md",
        "current-open-questions.md",
        "current-todos.md",
        "timeline.md",
    ]:
        validate_required(knowledge_root / filename, result)

    if profile == "advanced":
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
            validate_meeting(meeting_dir, result)
            validate_markdown_domains(meeting_dir / "analysis.md", allowed_domains, result)
            validate_sources(meeting_dir / "analysis.md", result)
    return result


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
        validate_required(vault_root / "global/current-summary.md", result)
        validate_required(vault_root / "global/decision-register.md", result)
        validate_required(vault_root / "global/open-question-register.md", result)
        validate_required(vault_root / "global/todo-register.md", result)

    projects_root = vault_root / "projects"
    if projects_root.exists():
        for project_dir in sorted(path for path in projects_root.iterdir() if path.is_dir()):
            project_result = validate_project(vault_root, project_dir.name)
            result.errors.extend(project_result.errors)
            result.warnings.extend(project_result.warnings)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Meeting knowledge vault scaffolding helper.")
    parser.add_argument("--vault-root", required=True, type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-vault")
    init_parser.add_argument("--profile", choices=sorted(PROFILES), default="minimal")

    project_parser = subparsers.add_parser("new-project")
    project_parser.add_argument("project_id")
    project_parser.add_argument("--name", required=True)
    project_parser.add_argument("--profile", choices=sorted(PROFILES))

    meeting_parser = subparsers.add_parser("new-meeting")
    meeting_parser.add_argument("project_id")
    meeting_parser.add_argument("--date", required=True)
    meeting_parser.add_argument("--location", required=True)
    meeting_parser.add_argument("--topic", required=True)
    meeting_parser.add_argument("--transcript", type=Path)

    validate_project_parser = subparsers.add_parser("validate-project")
    validate_project_parser.add_argument("project_id")

    subparsers.add_parser("validate-vault")

    domains_parser = subparsers.add_parser("set-project-domains")
    domains_parser.add_argument("project_id")
    domains_parser.add_argument("domains", nargs="+")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    vault_root = args.vault_root.expanduser().resolve()

    if args.command == "init-vault":
        init_vault(vault_root, args.profile)
        print(vault_root)
    elif args.command == "new-project":
        new_project(vault_root, args.project_id, args.name, args.profile)
        print(vault_root / "projects" / args.project_id)
    elif args.command == "new-meeting":
        meeting_root = new_meeting(
            vault_root,
            args.project_id,
            args.date,
            args.location,
            args.topic,
            args.transcript.expanduser().resolve() if args.transcript else None,
        )
        print(meeting_root)
    elif args.command == "validate-project":
        result = validate_project(vault_root, args.project_id)
        result.print()
        raise SystemExit(1 if result.errors else 0)
    elif args.command == "validate-vault":
        result = validate_vault(vault_root)
        result.print()
        raise SystemExit(1 if result.errors else 0)
    elif args.command == "set-project-domains":
        set_project_domains(vault_root, args.project_id, args.domains)
        print(vault_root / "projects" / args.project_id / "project-config.yaml")


if __name__ == "__main__":
    main()
