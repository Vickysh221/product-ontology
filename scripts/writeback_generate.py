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
    source_episode_slugs = read_list_field(synthesis_text, "source_episode_slugs")
    if source_episode_slugs:
        return source_episode_slugs

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


def collect_evidence_for_episode(slug: str) -> dict[str, list[str]]:
    base_dir = Path("library/artifacts/podcasts") / slug
    summary_lines: list[str] = []
    highlights_lines: list[str] = []
    summary_path = base_dir / "summary.md"
    highlights_path = base_dir / "highlights.md"
    if summary_path.exists():
        summary_content = read_section(read_file(summary_path), "Content")
        summary_lines = [line.strip() for line in summary_content.splitlines() if line.strip()][:8]
    if highlights_path.exists():
        highlights_content = read_section(read_file(highlights_path), "Content")
        highlights_lines = [line.strip() for line in highlights_content.splitlines() if line.strip()][:8]
    return {
        "summary": summary_lines,
        "highlights": highlights_lines,
    }


def build_longform_outline(intake_text: str, synthesis_text: str) -> dict[str, object]:
    collaboration_mode = read_field(intake_text, "collaboration_mode")
    target_audience = read_field(intake_text, "target_audience")
    extra_questions = read_list_field(intake_text, "extra_questions")
    core_judgment = read_section(synthesis_text, "核心综合判断")
    stable_themes = parse_bullets(read_section(synthesis_text, "稳定主题"))
    preserved_tensions = parse_bullets(read_section(synthesis_text, "保留张力"))
    return {
        "collaboration_mode": collaboration_mode,
        "target_audience": target_audience,
        "extra_questions": extra_questions,
        "core_judgment": core_judgment,
        "stable_themes": stable_themes,
        "preserved_tensions": preserved_tensions,
    }


def build_longform_sections(
    title: str,
    subtitle: str,
    intake_text: str,
    synthesis_text: str,
) -> dict[str, str]:
    outline = build_longform_outline(intake_text, synthesis_text)
    role_map = build_episode_role_map(synthesis_text)
    episode_slugs = collect_episode_slugs(synthesis_text)
    evidence_lines: list[str] = []
    for slug in episode_slugs:
        role = role_map.get(slug, "")
        evidence = collect_evidence_for_episode(slug)
        anchor = ""
        if evidence["highlights"]:
            anchor = evidence["highlights"][0]
        elif evidence["summary"]:
            anchor = evidence["summary"][0]
        evidence_lines.append(f"- `{slug}`：{role} 证据锚点：{anchor}")

    summary = (
        "这篇报告围绕五条一线播客语料，回答 multi-agent 是否正在从更强的工作流包装，"
        "走向可治理的 Agent Team 结构。对于团队协作来说，关键变化不只是 agent 数量增加，"
        "而是 harness engineering、角色边界、权限控制和异步协作被收束进同一条产品主链。"
    )
    judgment = str(outline["core_judgment"])
    mechanism = (
        "这组材料共同显示，agent orchestration 的价值并不在于把多个智能体机械排队，"
        "而在于把测试、容器、权限、审核与任务分工嵌入执行机制里。"
        "一旦这些控制层被稳定地纳入系统设计，multi-agent 就不再只是编排技巧，"
        "而开始接近产品能力边界的重新定义。"
    )
    workflow = (
        "对团队而言，这种变化直接影响工作流。系统从单 agent 响应工具，"
        "变成可以在明确边界下分派、回收、校验和交接工作的执行网络。"
        "这会把原本隐性的协作约束，例如谁负责审批、谁能调用什么资源、"
        "哪些结果需要复核，变成产品结构的一部分。"
    )
    extra = (
        "就本次追问而言，现有证据已经足以说明这不是简单的 feature 堆叠。"
        "五条语料都在重复同一件事：当 agent 需要稳定承担不同角色、"
        "在不同权限层运行，并且接受测试与治理约束时，产品形态就从单体助手转向 Agent Team。"
        "但这条范式迁移是否已经完全稳定，仍取决于这些控制层能否持续成为默认产品结构，"
        "而不是只出现在工程演示或高成熟团队的局部实践中。"
    )
    tensions = "\n".join(f"- {item}" for item in outline["preserved_tensions"])
    return {
        "summary": summary,
        "judgment": judgment,
        "mechanism": mechanism,
        "workflow": workflow,
        "extra": extra,
        "evidence": "\n".join(evidence_lines),
        "tensions": tensions,
    }


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
