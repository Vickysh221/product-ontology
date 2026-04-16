#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def read_file(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def read_field(text: str, field: str) -> str:
    match = re.search(rf"- {re.escape(field)}: `(.*?)`", text)
    return match.group(1) if match else ""


def read_list_field(text: str, field: str) -> list[str]:
    match = re.search(rf"- {re.escape(field)}: \[(.*?)\]", text)
    if not match:
        return []
    return [item.strip(" `") for item in match.group(1).split(",") if item.strip(" `")]


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def format_list(values: list[str]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(f"`{value}`" for value in values) + "]"


def read_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    heading_index = None
    heading_level = 0
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if match and match.group(2).strip() == heading:
            heading_index = index
            heading_level = len(match.group(1))
            break
    if heading_index is None:
        return ""

    section_lines: list[str] = []
    for line in lines[heading_index + 1 :]:
        match = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if match and len(match.group(1)) <= heading_level:
            break
        section_lines.append(line)
    return "\n".join(section_lines).strip()


def parse_bullets(section_text: str) -> list[str]:
    bullets: list[str] = []
    current: list[str] | None = None
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = re.match(r"^[-*]\s+(.*)$", stripped)
        if match:
            if current is not None:
                bullets.append(" ".join(current).strip())
            current = [match.group(1).strip()]
            continue
        if current is not None:
            current.append(stripped)
    if current is not None:
        bullets.append(" ".join(current).strip())
    return bullets


def collect_episode_slugs(synthesis_text: str) -> list[str]:
    evidence_section = read_section(synthesis_text, "证据汇总")
    slugs: list[str] = []
    for bullet in parse_bullets(evidence_section):
        match = re.search(r"`([^`]+)`", bullet)
        if not match:
            match = re.search(r"(podwise-ai-[a-z0-9-]+)", bullet)
        if not match:
            continue
        slug = match.group(1).strip()
        if slug not in slugs:
            slugs.append(slug)
    return slugs


def build_episode_role_map(synthesis_text: str) -> dict[str, str]:
    evidence_section = read_section(synthesis_text, "证据汇总")
    role_map: dict[str, str] = {}
    for bullet in parse_bullets(evidence_section):
        match = re.search(r"`([^`]+)`\s*(.*)$", bullet)
        if not match:
            match = re.search(r"(podwise-ai-[a-z0-9-]+)\s*(.*)$", bullet)
        if not match:
            continue
        slug = match.group(1).strip()
        role_text = match.group(2).strip()
        if role_text.startswith("：") or role_text.startswith(":"):
            role_text = role_text[1:].strip()
        if role_text.startswith("-"):
            role_text = role_text[1:].strip()
        role_map[slug] = role_text
    return role_map


def collect_evidence_for_episode(slug: str) -> list[str]:
    base_dir = Path("library/artifacts/podcasts") / slug
    summary_lines: list[str] = []
    highlights_lines: list[str] = []
    summary_path = base_dir / "summary.md"
    highlights_path = base_dir / "highlights.md"
    if summary_path.exists():
        summary_lines = [line.strip() for line in read_file(summary_path).splitlines() if line.strip()][:8]
    if highlights_path.exists():
        highlights_lines = [line.strip() for line in read_file(highlights_path).splitlines() if line.strip()][:8]
    return summary_lines + highlights_lines


def render_writeback(args: argparse.Namespace) -> str:
    intake_path = Path(args.intake_file)
    try:
        intake_text = read_file(intake_path)
    except OSError:
        raise SystemExit("missing or unreadable intake file")
    intake_id = read_field(intake_text, "intake_id")
    if not intake_id:
        raise SystemExit("missing intake_id in intake record")

    collaboration_mode = read_field(intake_text, "collaboration_mode")
    used_default_rules = read_field(intake_text, "used_default_rules")
    target_audience = read_field(intake_text, "target_audience")
    extra_questions = read_list_field(intake_text, "extra_questions")
    review_refs = parse_csv(args.review_refs)
    verdict_refs = parse_csv(args.verdict_refs)
    preserved_tensions = parse_csv(args.preserved_tensions)
    preserved_lines = [f"- {item}" for item in preserved_tensions] or ["- none recorded"]
    return f"""# Writeback Proposal

- writeback_id: `{args.writeback_id}`
- intake_id: `{intake_id}`
- collaboration_mode: `{collaboration_mode}`
- used_default_rules: `{used_default_rules}`
- focus_priority: []
- special_attention: []
- target_audience: `{target_audience}`
- extra_questions: {format_list(extra_questions)}
- synthesis_ref: `{args.synthesis_ref}`
- review_refs: {format_list(review_refs)}
- verdict_refs: {format_list(verdict_refs)}
- preserved_tensions: {format_list(preserved_tensions)}

## 标题

{args.title}

## 副标题

{args.subtitle}

## 摘要

{args.summary}

## 主判断

待由 evidence、review 和 intake 共同约束的主判断。

## 评审视角

当前 writeback 已绑定 review 与 verdict 痕迹，后续可按 collaboration_mode 决定是整合呈现、分节呈现，还是附录呈现。

## 证据锚点

待补充。

## 保留分歧

{chr(10).join(preserved_lines)}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    render = subparsers.add_parser("render")
    render.add_argument("--writeback-id", required=True)
    render.add_argument("--intake-file", required=True)
    render.add_argument("--output", required=True)
    render.add_argument("--title", required=True)
    render.add_argument("--subtitle", default="")
    render.add_argument("--summary", required=True)
    render.add_argument("--synthesis-ref", default="")
    render.add_argument("--review-refs", default="")
    render.add_argument("--verdict-refs", default="")
    render.add_argument("--preserved-tensions", default="")
    args = parser.parse_args()

    if args.command != "render":
        return 1

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_writeback(args))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit as exc:
        if isinstance(exc.code, str):
            print(exc.code, file=sys.stderr)
            raise SystemExit(1)
        raise
