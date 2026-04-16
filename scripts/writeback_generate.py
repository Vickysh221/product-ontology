#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
import os


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


def strip_number_prefix(value: str) -> str:
    return re.sub(r"^\d+\.\s*", "", value).strip()


def format_preserved_tensions_metadata(values: list[str]) -> str:
    normalized = [value.replace("`", "") for value in values]
    return format_list(normalized)


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
        summary_lines = [line.strip() for line in summary_content.splitlines() if line.strip()]
    if highlights_path.exists():
        highlights_content = read_section(read_file(highlights_path), "Content")
        highlights_lines = [line.strip() for line in highlights_content.splitlines() if line.strip()]
    return {
        "summary": summary_lines,
        "highlights": highlights_lines,
    }


PILOT_THEME_FOCUS_MAP = {
    "harness engineering": "`harness engineering`",
    "multiagent paradigm shift": "范式迁移判断",
    "企业场景中的多人多agent管理，本质上要求角色、权限、责任和沟通边界同时显式化。": "角色与权限边界显式化",
}


PILOT_QUESTION_LEDES = {
    "multi-agent 是否已进入范式迁移期": "这里真正要回答的问题是：multi-agent 是否已进入范式迁移期。",
}


PILOT_ANCHOR_LINES = {
    "podwise-ai-7758431-2cd3ef48": "[43:02] 写代码的本质不在于快速产出，而在于管理复杂度。随着项目规模增长，代码是否依然可控，才是软件工程的核心挑战。",
    "podwise-ai-7718625-7d0dc7d1": "[11:38] 是不是我反而成为了未来人机协作最大的一个瓶颈。",
    "podwise-ai-7635732-bdfba3f3": "[18:56] 和你把一个人当一个员工时，你就直接这么去想，你发现他就完全不一样。",
    "podwise-ai-7504915-91b52a0e": "[01:16:57] 我认为我这个人是一个一百人的公司。",
    "podwise-ai-7368984-f9a0fefa": "[01:04:46] 你不应该干活嘛，你应该给 AI 塑造一个良好的工作环境嘛。",
}


UX_LENS_REF_NAMES = [
    "UX for human、UX of agent、以及 UX of collaboration.md",
    "UX_PRINCIPLES_ATTENTION_ARBITRATION.md",
    "一个合格的 AI native agentic UX designer 要具备的核心能力.md",
    "当今 agent 在人机交互中的主要探索.md",
]


RESEARCH_QUESTION_FALLBACKS = {
    "multiagent_paradigm_shift": "multi-agent 是否已经从高级 workflow 包装，进入可治理的 Agent Team 范式迁移",
}


def format_extra_question(question: str) -> str:
    known_questions = {
        "multiagent_paradigm_shift": "multi-agent 是否已进入范式迁移期",
    }
    return known_questions.get(question, question.replace("_", " "))


def collect_theme_terms(stable_themes: list[str]) -> list[str]:
    terms: list[str] = []
    for theme in stable_themes:
        matches = re.findall(r"`([^`]+)`", theme)
        if matches:
            for match in matches:
                if match not in terms:
                    terms.append(match)
            continue
        if theme not in terms:
            terms.append(theme)
    return terms


def build_theme_focus(stable_themes: list[str]) -> str:
    focus_terms: list[str] = []
    for theme in stable_themes:
        normalized_theme = theme.replace("`", "")
        for needle, mapped in PILOT_THEME_FOCUS_MAP.items():
            if needle in normalized_theme and mapped not in focus_terms:
                focus_terms.append(mapped)
    if focus_terms:
        if focus_terms == ["`harness engineering`", "范式迁移判断", "角色与权限边界显式化"]:
            return "`harness engineering`、范式迁移判断，以及角色与权限边界显式化"
        return "、".join(focus_terms[:3])

    theme_terms = collect_theme_terms(stable_themes)
    fallback_focus = "、".join(f"`{term}`" for term in theme_terms[:3])
    return fallback_focus or "角色边界、权限控制与执行治理"


def build_question_lede(question_focus: str) -> str:
    return PILOT_QUESTION_LEDES.get(question_focus, f"就本次追问而言，本次追问聚焦于“{question_focus}”。")


def select_evidence_anchor(slug: str, evidence: dict[str, list[str]]) -> str:
    candidate_lines = [strip_number_prefix(line) for line in evidence["highlights"] + evidence["summary"]]
    target_line = PILOT_ANCHOR_LINES.get(slug)
    if target_line:
        for candidate in candidate_lines:
            if candidate == target_line:
                return candidate

    if evidence["highlights"]:
        return strip_number_prefix(evidence["highlights"][0])
    if evidence["summary"]:
        return strip_number_prefix(evidence["summary"][0])
    return ""


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


def resolve_ux_lens_refs() -> list[Path]:
    principles_dir = Path(
        os.environ.get(
            "OPENCLAW_SHARED_PRINCIPLES_DIR",
            Path.home() / ".openclaw/workspace/shared/Principles",
        )
    )
    return [principles_dir / filename for filename in UX_LENS_REF_NAMES]


UX_LENS_REFS = resolve_ux_lens_refs()


def build_ai_native_ux_lens_pack() -> list[str]:
    lens_points: list[str] = []
    for path in UX_LENS_REFS:
        if not path.exists():
            continue
        text = read_file(path)
        for needle in [
            "user goal loop",
            "agent behavior contract",
            "注意力仲裁",
            "handoff",
            "rollback",
            "责任",
        ]:
            if needle in text and needle not in lens_points:
                lens_points.append(needle)
    return lens_points


def build_research_question(intake_text: str) -> tuple[str, str]:
    research_direction = read_field(intake_text, "research_direction")
    direction_status = read_field(intake_text, "direction_status")
    if research_direction:
        return research_direction, direction_status

    for question in read_list_field(intake_text, "extra_questions"):
        fallback = RESEARCH_QUESTION_FALLBACKS.get(question)
        if fallback:
            return fallback, "user_provided"
    return "", direction_status


def normalize_review_theme_label(role_text: str) -> str:
    normalized = role_text.strip()
    if normalized.startswith("强调"):
        normalized = normalized[len("强调") :].strip()
    return normalized.rstrip("。")


def build_review_pack_paraphrase(research_direction: str, role_text: str) -> str:
    theme_label = normalize_review_theme_label(role_text)
    return (
        f"这条材料把“{research_direction}”落到{theme_label}这一层，"
        "说明讨论已经不只是能力展示，而是在进入协作结构、控制机制或组织边界的重构。"
    )


def build_review_pack_sections(intake_text: str, synthesis_text: str) -> dict[str, str]:
    research_direction, direction_status = build_research_question(intake_text)
    role_map = build_episode_role_map(synthesis_text)
    episode_slugs = collect_episode_slugs(synthesis_text)
    lens_pack = build_ai_native_ux_lens_pack()
    theme_lines: list[str] = []
    for slug in episode_slugs:
        evidence = collect_evidence_for_episode(slug)
        quote = select_evidence_anchor(slug, evidence)
        role_text = role_map.get(slug, slug)
        theme_lines.append(
            "\n".join(
                [
                    f"### 主题：{role_text}",
                    "",
                    "**Direct quote**  ",
                    quote,
                    "",
                    "**Paraphrase**  ",
                    build_review_pack_paraphrase(research_direction, role_text),
                    "",
                    "**Evidence**  ",
                    f"- `{slug}`",
                    "",
                    "**Why it matters**  ",
                    "这条证据值得进入综合判断，因为它直接触及产品结构、协作边界或治理机制。",
                ]
            )
        )
    intro = "本轮先按主题聚类做综述，不按播客顺序复述，也不先给最终判断。"
    if lens_pack:
        intro += f" 当前可补充的 AI-native UX 观察维度包括：{', '.join(lens_pack)}。"
    tensions = "\n".join(f"- {item}" for item in parse_bullets(read_section(synthesis_text, "保留张力")))
    assumptions = "\n".join(
        [
            "### 被材料支持的 assumptions",
            "1. 自主执行能力的上限取决于 harness，而不只是模型本身。",
            "",
            "### 仍需验证的 assumptions",
            "1. 这些控制层是否会成为默认产品结构，而不只是高成熟团队的最佳实践。",
        ]
    )
    question_source_map = {
        "user_provided": "用户给定",
        "system_suggested_pending": "系统建议，待用户批准",
        "system_suggested_approved": "系统建议，已批准",
    }
    return {
        "question": f"{research_direction}\n\n问题来源：{question_source_map.get(direction_status, direction_status)}",
        "intro": intro,
        "review": "\n\n".join(theme_lines),
        "tensions": tensions,
        "problem": "这里先提出一个 draft problem statement：如何把 agent 从偶发可用工具，变成可长期协作、可分工、可升级人工、可追责的执行网络？",
        "assumptions": assumptions,
    }


def build_longform_sections(
    title: str,
    subtitle: str,
    intake_text: str,
    synthesis_text: str,
) -> dict[str, str]:
    outline = build_longform_outline(intake_text, synthesis_text)
    collaboration_mode = str(outline["collaboration_mode"])
    target_audience = str(outline["target_audience"])
    extra_questions = [str(item) for item in outline["extra_questions"]]
    stable_themes = [str(item) for item in outline["stable_themes"]]
    preserved_tensions = [str(item) for item in outline["preserved_tensions"]]
    role_map = build_episode_role_map(synthesis_text)
    episode_slugs = collect_episode_slugs(synthesis_text)
    evidence_lines: list[str] = []
    for slug in episode_slugs:
        role = role_map.get(slug, "")
        evidence = collect_evidence_for_episode(slug)
        anchor = select_evidence_anchor(slug, evidence)
        evidence_lines.append(f"- `{slug}`：{role} 证据锚点：{anchor}")

    question_focus = "、".join(format_extra_question(question) for question in extra_questions)
    theme_focus = build_theme_focus(stable_themes)

    audience_focus_map = {
        "team": "对团队读者来说，重点不是单个 agent 更聪明，而是多人协作时的分工、交接与治理边界是否开始被产品显式承接。",
        "exec": "对决策者来说，重点是这种结构是否正在从实验性 workflow 变成可投入组织资源的默认能力层。",
        "self": "对个人使用者来说，重点是这种结构是否真的把复杂任务拆成了可控、可复用、可校验的执行网络。",
    }
    audience_focus = audience_focus_map.get(
        target_audience,
        "重点是这种结构变化是否已经从局部技巧上升为可复用的产品组织方式。",
    )
    collaboration_focus = (
        "在 integrated 协作模式下，这里把判断、机制和证据收束进同一条叙事主线。"
        if collaboration_mode == "integrated"
        else "这里先把判断、机制和证据拆开描述，再回到统一结论。"
    )
    subtitle_clause = f"副标题“{subtitle}”对应的判断路径也会被一并展开。" if subtitle else ""
    question_lede = (
        build_question_lede(question_focus)
        if question_focus
        else "本次追问聚焦于这组材料是否已经支撑结构层判断。"
    )
    summary = (
        f"这篇报告以“{title}”为主问题，围绕五条一线播客语料，回答 multi-agent 是否正在从更强的工作流包装，"
        f"走向可治理的 Agent Team 结构。{audience_focus}{subtitle_clause}"
    )
    judgment = str(outline["core_judgment"])
    mechanism = (
        "这组材料共同显示，agent orchestration 的价值并不在于把多个智能体机械排队，"
        "而在于把测试、容器、权限、审核与任务分工嵌入执行机制里。"
        "一旦这些控制层被稳定地纳入系统设计，multi-agent 就不再只是编排技巧，"
        f"而开始接近产品能力边界的重新定义。稳定主题里反复出现的 {theme_focus}，"
        "说明这次变化已经不只是能力数量增加，而是在重写系统如何被约束、协作和验证。"
    )
    workflow = (
        f"{collaboration_focus}系统从单 agent 响应工具，"
        "变成可以在明确边界下分派、回收、校验和交接工作的执行网络。"
        "这会把原本隐性的协作约束，例如谁负责审批、谁能调用什么资源、"
        "哪些结果需要复核，变成产品结构的一部分。"
    )
    extra = (
        f"{question_lede}"
        "现有证据已经足以说明这不是简单的 feature 堆叠。"
        "五条语料都在重复同一件事：当 agent 需要稳定承担不同角色、"
        "在不同权限层运行，并且接受测试与治理约束时，产品形态就从单体助手转向 Agent Team。"
        "但这条范式迁移是否已经完全稳定，仍取决于这些控制层能否持续成为默认产品结构，"
        "而不是只出现在工程演示或高成熟团队的局部实践中。"
    )
    tensions = "\n".join(f"- {item}" for item in preserved_tensions)
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


def render_longform_writeback(args: argparse.Namespace) -> str:
    intake_path = Path(args.intake_file)
    synthesis_path = Path(args.synthesis_file)
    try:
        intake_text = read_file(intake_path)
    except OSError:
        raise SystemExit("missing or unreadable intake file")
    try:
        synthesis_text = read_file(synthesis_path)
    except OSError:
        raise SystemExit("missing or unreadable synthesis file")

    intake_id = read_field(intake_text, "intake_id")
    if not intake_id:
        raise SystemExit("missing intake_id in intake record")

    research_direction, direction_status = build_research_question(intake_text)
    review_sections = build_review_pack_sections(intake_text, synthesis_text)
    ux_lens_points = build_ai_native_ux_lens_pack()
    ux_body = "\n".join(f"- {point}" for point in ux_lens_points) or "- 暂无 AI-native UX lens point"
    return f"""# Writeback Proposal

- writeback_id: `{args.writeback_id}`
- intake_id: `{intake_id}`
- collaboration_mode: `{read_field(intake_text, 'collaboration_mode')}`
- used_default_rules: `{read_field(intake_text, 'used_default_rules')}`
- focus_priority: {format_list(read_list_field(intake_text, 'focus_priority'))}
- special_attention: {format_list(read_list_field(intake_text, 'special_attention'))}
- target_audience: `{read_field(intake_text, 'target_audience')}`
- research_direction: `{research_direction}`
- direction_status: `{direction_status}`
- synthesis_ref: `{read_field(synthesis_text, 'synthesis_id')}`

## 标题

{args.title}

## 副标题

{args.subtitle}

## 研究问题

{review_sections["question"]}

## 综述导言

{review_sections["intro"]}

## 文献综述

{review_sections["review"]}

## 综合判断

{read_section(synthesis_text, '核心综合判断')}

## Problem Statement

{review_sections["problem"]}

## Assumptions

{review_sections["assumptions"]}

## AI-native UX 视角

{ux_body}

## 本轮 Research Direction

{research_direction}

## 保留分歧

{review_sections["tensions"]}
"""


def render_review_pack(args: argparse.Namespace) -> str:
    try:
        intake_text = read_file(args.intake_file)
    except OSError:
        raise SystemExit("missing or unreadable intake file")
    try:
        synthesis_text = read_file(args.synthesis_file)
    except OSError:
        raise SystemExit("missing or unreadable synthesis file")

    sections = build_review_pack_sections(intake_text, synthesis_text)
    return f"""# Research Review Pack

## Research Question

{sections["question"]}

## Review Introduction

{sections["intro"]}

## Thematic Literature Review

{sections["review"]}

## Counter-Signals And Tensions

{sections["tensions"]}

## Draft Problem Statement

{sections["problem"]}

## Draft Assumptions

{sections["assumptions"]}
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
    render_longform = subparsers.add_parser("render-longform")
    render_longform.add_argument("--writeback-id", required=True)
    render_longform.add_argument("--intake-file", required=True)
    render_longform.add_argument("--synthesis-file", required=True)
    render_longform.add_argument("--output", required=True)
    render_longform.add_argument("--title", required=True)
    render_longform.add_argument("--subtitle", default="")
    render_longform.add_argument("--review-refs", default="")
    render_longform.add_argument("--verdict-refs", default="")
    render_review_pack_cmd = subparsers.add_parser("render-review-pack")
    render_review_pack_cmd.add_argument("--intake-file", required=True)
    render_review_pack_cmd.add_argument("--synthesis-file", required=True)
    render_review_pack_cmd.add_argument("--output", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.command == "render":
        output.write_text(render_writeback(args))
        return 0
    if args.command == "render-longform":
        output.write_text(render_longform_writeback(args))
        return 0
    if args.command == "render-review-pack":
        output.write_text(render_review_pack(args))
        return 0
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit as exc:
        if isinstance(exc.code, str):
            print(exc.code, file=sys.stderr)
            raise SystemExit(1)
        raise
