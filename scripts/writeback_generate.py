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
    transcript_lines: list[str] = []
    summary_path = base_dir / "summary.md"
    highlights_path = base_dir / "highlights.md"
    transcript_path = base_dir / "transcript.md"
    if summary_path.exists():
        summary_content = read_section(read_file(summary_path), "Content")
        summary_lines = [line.strip() for line in summary_content.splitlines() if line.strip()]
    if highlights_path.exists():
        highlights_content = read_section(read_file(highlights_path), "Content")
        highlights_lines = [line.strip() for line in highlights_content.splitlines() if line.strip()]
    if transcript_path.exists():
        transcript_content = read_section(read_file(transcript_path), "Content")
        transcript_lines = [
            line.strip()
            for line in transcript_content.splitlines()
            if line.strip().startswith("[")
        ]
    return {
        "summary": summary_lines,
        "highlights": highlights_lines,
        "transcript": transcript_lines,
    }


def build_evidence_candidates(slug: str) -> list[dict[str, str]]:
    evidence = collect_evidence_for_episode(slug)
    candidates: list[dict[str, str]] = []
    for line in evidence["highlights"]:
        candidates.append(
            {
                "slug": slug,
                "source_kind": "highlight",
                "text": strip_number_prefix(line),
            }
        )
    for line in evidence["transcript"]:
        candidates.append(
            {
                "slug": slug,
                "source_kind": "transcript",
                "text": strip_number_prefix(line),
            }
        )
    for line in evidence["summary"]:
        candidates.append(
            {
                "slug": slug,
                "source_kind": "summary",
                "text": line.strip(),
            }
        )
    return candidates


def require_pilot_evidence(slug: str, evidence: dict[str, list[str]]) -> None:
    if not evidence["highlights"]:
        raise SystemExit(f"missing highlights evidence for pilot slug: {slug}")
    if not evidence["summary"]:
        raise SystemExit(f"missing summary evidence for pilot slug: {slug}")
    if slug in PILOT_TRANSCRIPT_QUOTE_SLUGS and not evidence["transcript"]:
        raise SystemExit(f"missing transcript evidence for pilot slug: {slug}")


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


def is_pilot_integrated_team_paradigm(intake_text: str) -> bool:
    return read_field(intake_text, "intake_id") == "intake-integrated-team-paradigm"


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


PILOT_REVIEW_PACK_CLUSTER_SCHEMAS = [
    {
        "id": "execution_control",
        "title": "执行控制层",
        "source_episode_slugs": [
            "podwise-ai-7758431-2cd3ef48",
            "podwise-ai-7368984-f9a0fefa",
        ],
        "role_labels": {
            "anchor": "控制闭环",
            "support": "审核与回退",
            "counter_signal": "边界提醒",
        },
        "role_hints": {
            "anchor": ["写代码", "管理复杂度", "代码审核"],
            "support": ["自动化测试", "自动化的测试", "代码审核", "提交", "Approve", "harness", "沙箱", "权限"],
            "counter_signal": ["产出很多", "成果很少", "保守", "事故", "错误"],
        },
        "summary_frame": "这一组材料先把控制层讲清楚：代码审核、自动化测试和权限边界不是附属工具，而是 agent 能否稳定执行的前提。",
        "paraphrase_frame": "执行控制层的关键不是让 agent 更快做事，而是先把每一步动作都放进可测试、可审核、可回退的执行框架里。",
        "why_frame": "这说明 multi-agent 的关键约束不是模型本身，而是 harness、测试和审核是否已经变成默认产品能力。",
        "counter_signal_frame": "如果只追求产出，不把结果、审核与回退一起设计，控制层就会反过来变成瓶颈。",
    },
    {
        "id": "collaboration_roles",
        "title": "协作与角色层",
        "source_episode_slugs": [
            "podwise-ai-7718625-7d0dc7d1",
            "podwise-ai-7635732-bdfba3f3",
            "podwise-ai-7368984-f9a0fefa",
        ],
        "role_labels": {
            "anchor": "协作瓶颈",
            "support": "员工化分工",
            "counter_signal": "组织缩放",
        },
        "role_hints": {
            "anchor": ["瓶颈", "协作", "自主性", "角色"],
            "support": ["把一个人当一个员工", "员工时", "分工", "协议层", "团队", "角色演化"],
            "counter_signal": ["组织会缩小", "和人沟通的效率更高", "跟 AI 沟通", "世界的割裂", "割裂"],
        },
        "summary_frame": "这一组材料讨论的是人和 agent 如何分工：谁来提问、谁来调度、谁来承担协作中的角色边界。",
        "paraphrase_frame": "协作与角色层讲的是：一旦任务被交给 agent，人就不再只是使用者，而会变成提示、约束、审核和分工的一部分。",
        "why_frame": "这条线索把“更聪明的工具”推进成“可协作的团队结构”，也解释了为什么角色定义会先于功能堆叠变成核心问题。",
        "counter_signal_frame": "如果组织和沟通边界仍然模糊，协作就很容易退回到效率更高但关系更割裂的单向调用。",
    },
    {
        "id": "governance_frontstage_ux",
        "title": "治理与前台 UX 外显层",
        "source_episode_slugs": [
            "podwise-ai-7504915-91b52a0e",
            "podwise-ai-7368984-f9a0fefa",
            "podwise-ai-7758431-2cd3ef48",
        ],
        "role_labels": {
            "anchor": "治理外显",
            "support": "工作环境",
            "counter_signal": "所有权边界",
        },
        "role_hints": {
            "anchor": ["一百人的公司", "工作环境", "权限", "治理"],
            "support": ["工作环境", "沙箱", "安全", "塑造"],
            "counter_signal": ["我拥有 AI", "AI 拥有我", "封闭的系统", "持续付费", "搬不走数据"],
        },
        "summary_frame": "这一组材料把治理从后台规则推到前台体验：工作环境、权限和组织方式开始被显式地描述出来。",
        "paraphrase_frame": "治理与前台 UX 外显层的重点，是把权限、环境和组织结构做成用户可感知的产品体验，而不是只放在后台约束里。",
        "why_frame": "当治理被前台化，用户看到的就不只是一个会做事的 agent，而是一个可以被组织、被约束、也能被持续协作的工作环境。",
        "counter_signal_frame": "如果没有清晰的所有权边界，前台化治理最后会变成锁定系统而不是赋能工作台。",
    },
]


PILOT_TRANSCRIPT_QUOTE_SLUGS = {
    "podwise-ai-7368984-f9a0fefa",
    "podwise-ai-7635732-bdfba3f3",
    "podwise-ai-7504915-91b52a0e",
    "podwise-ai-7718625-7d0dc7d1",
}


FINAL_WRITEBACK_UX_OBJECTS = [
    {
        "name": "责任状态卡",
        "description": "把当前任务的责任人、待确认项、已接手项和可升级边界放在同一张卡里，避免团队只看到一个会动的 agent，看不到谁对结果负责。",
    },
    {
        "name": "分级决策卡",
        "description": "把哪些决策可自动通过、哪些需要人确认、哪些必须升级到团队负责人做成分级入口，让决策路径在前台显式可见。",
    },
    {
        "name": "异步沟通面板",
        "description": "把提醒、评论、追问、回执和跨时区跟进集中在一个异步沟通面板里，减少把协作重新拉回同步会议的冲动。",
    },
    {
        "name": "审计与证据抽屉",
        "description": "把操作日志、引用证据、回退点和历史决策收进抽屉式证据面板，保证用户随时能回看为什么系统这样做。",
    },
]


def build_pilot_review_pack_cluster(cluster: dict[str, object]) -> str:
    quote_blocks = []
    for quote in cluster["quotes"]:
        quote_blocks.append("\n".join(["**Direct quote**  ", str(quote)]))
    return "\n".join(
        [
            f"### 主题：{cluster['title']}",
            "",
            str(cluster["summary"]),
            "",
            "\n\n".join(quote_blocks),
            "",
            "**Paraphrase**  ",
            str(cluster["paraphrase"]),
            "",
            "**Evidence**  ",
            "\n".join(f"- `{slug}`" for slug in cluster["evidence"]),
            "",
            "**Why it matters**  ",
            str(cluster["why"]),
        ]
    )


def assign_evidence_role(
    candidate: dict[str, str],
    cluster_schema: dict[str, object],
    role_text: str,
) -> tuple[str, int]:
    role_hints = cluster_schema["role_hints"]
    role_order = list(role_hints)
    best_role = "support"
    best_score = 0
    candidate_text = candidate["text"]
    for role in role_order:
        score = 0
        for needle in role_hints[role]:
            if needle in candidate_text:
                score += 2
            if role_text and needle in role_text:
                score += 1
        if score > 0 and candidate["source_kind"] == "highlight" and role != "counter_signal":
            score += 1
        if score > best_score:
            best_role = role
            best_score = score
    return best_role, best_score


def pick_evidence_candidate(
    candidates: list[dict[str, str]],
    target_role: str,
    source_order: list[str],
    *,
    strict: bool = False,
) -> dict[str, str]:
    if not candidates:
        if strict:
            raise SystemExit(f"no evidence candidates available for required role: {target_role}")
        return {"slug": "", "source_kind": "summary", "text": "", "role": target_role}
    matching = [candidate for candidate in candidates if candidate["role"] == target_role]
    if not matching:
        if strict:
            raise SystemExit(f"no evidence candidates matched required role: {target_role}")
        matching = candidates

    def sort_key(candidate: dict[str, str]) -> tuple[int, int, int, int]:
        role_priority = 0 if candidate["role"] == target_role else 1
        source_priority = 0 if candidate["source_kind"] == "highlight" else 1
        score_priority = -int(candidate.get("role_score", 0))
        slug_priority = source_order.index(candidate["slug"]) if candidate["slug"] in source_order else len(source_order)
        text_priority = -len(candidate["text"])
        return (role_priority, score_priority, source_priority, slug_priority, text_priority)

    return sorted(matching, key=sort_key)[0]


def trim_evidence_quote(quote: str) -> str:
    return strip_number_prefix(quote).rstrip("。")


def extract_timestamp(value: str) -> str:
    match = re.match(r"^(\[[^\]]+\])", value.strip())
    return match.group(1) if match else ""


def select_evidence_quote(
    candidate: dict[str, str],
    cluster_schema: dict[str, object],
    evidence: dict[str, list[str]],
) -> str:
    if candidate["source_kind"] == "highlight" and candidate["slug"] not in PILOT_TRANSCRIPT_QUOTE_SLUGS:
        return trim_evidence_quote(candidate["text"])

    role_hints = cluster_schema["role_hints"].get(candidate["role"], [])
    candidate_text = trim_evidence_quote(candidate["text"])
    timestamp = extract_timestamp(candidate_text)
    if timestamp:
        for line in evidence["transcript"]:
            normalized_line = line.strip()
            if normalized_line.startswith(timestamp):
                return normalized_line

    for line in evidence["transcript"] + evidence["highlights"]:
        normalized_line = trim_evidence_quote(line)
        if normalized_line == candidate_text:
            return line.strip()

    for line in evidence["transcript"] + evidence["highlights"]:
        normalized_line = trim_evidence_quote(line)
        if any(needle in normalized_line for needle in role_hints):
            return line.strip()

    if evidence["summary"]:
        for line in evidence["summary"]:
            normalized_line = line.strip()
            if any(needle in normalized_line for needle in role_hints):
                return normalized_line
    return candidate_text


def build_pilot_review_pack_clusters(intake_text: str, synthesis_text: str) -> list[dict[str, object]]:
    role_map = build_episode_role_map(synthesis_text)
    clusters: list[dict[str, object]] = []
    for cluster_schema in PILOT_REVIEW_PACK_CLUSTER_SCHEMAS:
        source_episode_slugs = list(cluster_schema["source_episode_slugs"])
        annotated_candidates: list[dict[str, str]] = []
        for slug in source_episode_slugs:
            evidence = collect_evidence_for_episode(slug)
            require_pilot_evidence(slug, evidence)
            for candidate in build_evidence_candidates(slug):
                role, role_score = assign_evidence_role(candidate, cluster_schema, role_map.get(slug, ""))
                annotated_candidates.append(
                    {
                        **candidate,
                        "role_text": role_map.get(slug, ""),
                        "role": role,
                        "role_score": role_score,
                    }
                )

        primary = pick_evidence_candidate(annotated_candidates, "anchor", source_episode_slugs, strict=True)
        secondary = pick_evidence_candidate(annotated_candidates, "support", source_episode_slugs, strict=True)
        counter_signal_candidate = pick_evidence_candidate(
            annotated_candidates,
            "counter_signal",
            source_episode_slugs,
            strict=True,
        )
        if not primary["text"] or not secondary["text"] or not counter_signal_candidate["text"]:
            raise SystemExit(f"incomplete pilot evidence-role assignment for cluster: {cluster_schema['title']}")

        primary_evidence = collect_evidence_for_episode(primary["slug"])
        secondary_evidence = collect_evidence_for_episode(secondary["slug"])
        counter_signal_evidence = collect_evidence_for_episode(counter_signal_candidate["slug"])
        primary_quote = select_evidence_quote(primary, cluster_schema, primary_evidence)
        secondary_quote = select_evidence_quote(secondary, cluster_schema, secondary_evidence)
        counter_signal_quote = select_evidence_quote(counter_signal_candidate, cluster_schema, counter_signal_evidence)
        evidence_slugs = []
        for slug in [primary["slug"], secondary["slug"], counter_signal_candidate["slug"]]:
            if slug and slug not in evidence_slugs:
                evidence_slugs.append(slug)

        clusters.append(
            {
                "id": cluster_schema["id"],
                "title": cluster_schema["title"],
                "summary": (
                    f"{cluster_schema['summary_frame']} 这组证据分别对应"
                    f"{cluster_schema['role_labels']['anchor']}与{cluster_schema['role_labels']['support']}。"
                ),
                "quotes": [primary_quote, secondary_quote],
                "evidence": evidence_slugs,
                "paraphrase": (
                    f"{cluster_schema['paraphrase_frame']} 具体落点分别是"
                    f"“{trim_evidence_quote(primary_quote)}”和“{trim_evidence_quote(secondary_quote)}”。"
                ),
                "paraphrase_sentence": str(cluster_schema["paraphrase_frame"]),
                "why": (
                    f"{cluster_schema['why_frame']} 另一个边界信号是"
                    f"“{trim_evidence_quote(counter_signal_quote)}”。"
                ),
                "why_sentence": str(cluster_schema["why_frame"]),
                "counter_signal": (
                    f"{trim_evidence_quote(counter_signal_quote)}。{cluster_schema['counter_signal_frame']}"
                    if counter_signal_quote
                    else str(cluster_schema["counter_signal_frame"])
                ),
                "counter_signal_sentence": trim_evidence_quote(counter_signal_quote),
                "counter_signal_implication": str(cluster_schema["counter_signal_frame"]),
                "evidence_roles": [
                    {
                        "role": primary["role"],
                        "slug": primary["slug"],
                        "text": trim_evidence_quote(primary_quote),
                    },
                    {
                        "role": secondary["role"],
                        "slug": secondary["slug"],
                        "text": trim_evidence_quote(secondary_quote),
                    },
                    {
                        "role": counter_signal_candidate["role"],
                        "slug": counter_signal_candidate["slug"],
                        "text": trim_evidence_quote(counter_signal_quote),
                    },
                ],
            }
        )
    return clusters


def build_pilot_review_pack_sections(intake_text: str, synthesis_text: str) -> dict[str, str]:
    sections = build_review_pack_sections(intake_text, synthesis_text)
    if not is_pilot_integrated_team_paradigm(intake_text):
        sections["clusters"] = []
        return sections
    clusters = build_pilot_review_pack_clusters(intake_text, synthesis_text)
    sections["review"] = "\n\n".join(build_pilot_review_pack_cluster(cluster) for cluster in clusters)
    sections["clusters"] = clusters
    return sections


def build_pilot_review_pack_tensions(
    clusters: list[dict[str, object]],
    synthesis_text: str,
) -> str:
    if not clusters:
        return "\n".join(f"- {item}" for item in parse_bullets(read_section(synthesis_text, "保留张力")))
    tension_lines: list[str] = []
    seen: set[str] = set()
    for cluster in clusters:
        counter_signal = str(cluster["counter_signal"]).strip()
        if not counter_signal:
            continue
        line = f"- {cluster['title']}：{counter_signal}"
        if line not in seen:
            seen.add(line)
            tension_lines.append(line)

    for item in parse_bullets(read_section(synthesis_text, "保留张力")):
        line = f"- {item}"
        if line not in seen:
            seen.add(line)
            tension_lines.append(line)
    return "\n".join(tension_lines)


def normalize_longform_quote(quote: str) -> str:
    return re.sub(r"^(\[[^\]]+\])\s*-\s*[^:：]+[:：]\s*", r"\1 ", quote).strip()


def build_final_longform_review_section(review_text: str) -> str:
    sections: list[str] = []
    for index, block in enumerate(parse_review_theme_blocks(review_text), start=1):
        quote_1 = normalize_longform_quote(block["quotes"][0]) if block["quotes"] else ""
        quote_2 = normalize_longform_quote(block["quotes"][1]) if len(block["quotes"]) > 1 else ""
        sections.append(
            "\n".join(
                [
                    f"### 主题 {index}：{block['title']}",
                    "",
                    f"代表引文 1：{quote_1}",
                    "",
                    f"代表引文 2：{quote_2}",
                    "",
                    f"观察：{block['paraphrase']}",
                    "",
                    "证据来源：",
                    block["evidence"],
                    "",
                    f"为什么重要：{block['why']}",
                ]
            )
        )
    return "\n\n".join(sections)


def clean_clause(text: str) -> str:
    return text.strip().rstrip("。；，, ")


def build_pilot_final_review_object(intake_text: str, synthesis_text: str) -> dict[str, object]:
    review_sections = build_pilot_review_pack_sections(intake_text, synthesis_text)
    if not review_sections["clusters"]:
        raise SystemExit("pilot final writeback requires integrated-team-paradigm review clusters")
    outline = build_longform_outline(intake_text, synthesis_text)
    question = str(review_sections["question"])
    question_source = ""
    if "\n\n问题来源：" in question:
        question, question_source = question.split("\n\n问题来源：", 1)
    return {
        "question": question,
        "question_source": question_source.strip(),
        "intro": review_sections["intro"],
        "clusters": review_sections["clusters"],
        "review": review_sections["review"],
        "tensions": build_pilot_review_pack_tensions(review_sections["clusters"], synthesis_text),
        "core_judgment": str(outline["core_judgment"]),
        "preserved_tensions": [str(item) for item in outline["preserved_tensions"]],
    }


def build_pilot_final_judgment_object(review_object: dict[str, object]) -> dict[str, object]:
    basis = build_pilot_cluster_basis(review_object)
    lead = str(review_object.get("core_judgment", "")).strip()
    if not lead:
        lead = "这组材料共同指向可治理的 Agent Team 成形，而不是单纯增加更多 agent。"
    signal_clauses: list[str] = []
    for cluster in basis:
        why = clean_clause(str(cluster.get("why", "")))
        if why:
            signal_clauses.append(f"{cluster['title']}把{why}推进到产品结构判断里")
    judgment_text = clean_clause(lead)
    if signal_clauses:
        judgment_text += "。" + "；".join(signal_clauses) + "。"
    if any(clean_clause(str(item["counter_signal"])) for item in basis):
        tensions = "；".join(
            f"{item['title']}的边界信号是{clean_clause(str(item['counter_signal']))}"
            for item in basis
            if clean_clause(str(item["counter_signal"]))
        )
        judgment_text += f"{tensions}。"
    return {
        "text": judgment_text.strip(),
        "basis": basis,
    }


def build_pilot_cluster_basis(review_object: dict[str, object]) -> list[dict[str, object]]:
    clusters = [cluster for cluster in review_object["clusters"] if isinstance(cluster, dict)]
    return [
        {
            "id": str(cluster.get("id", "")),
            "title": str(cluster.get("title", "")),
            "why": str(cluster.get("why_sentence", "")),
            "counter_signal": str(cluster.get("counter_signal_sentence", "")),
            "counter_implication": str(cluster.get("counter_signal_implication", "")),
            "evidence": list(cluster.get("evidence", [])),
        }
        for cluster in clusters
    ]


def build_pilot_final_problem_object(review_object: dict[str, object]) -> dict[str, object]:
    basis = build_pilot_cluster_basis(review_object)
    source_clusters = [item["title"] for item in basis]
    why_clauses = [clean_clause(str(item["why"])) for item in basis if clean_clause(str(item["why"]))]
    counter_clauses = [
        clean_clause(str(item["counter_signal"]))
        for item in basis
        if clean_clause(str(item["counter_signal"]))
    ]
    joined_clusters = "、".join(source_clusters)
    joined_whys = "；".join(why_clauses)
    joined_counters = "；".join(counter_clauses)
    return {
        "text": (
            "问题已经不再是再增加多少个 agent，而是如何把"
            f"{joined_clusters}同时收束成一套默认可用的团队工作台："
            f"{joined_whys}。"
            f"同时还要回应这些边界信号：{joined_counters}。"
        ),
        "source_clusters": source_clusters,
        "basis": basis,
        "why_clauses": why_clauses,
        "counter_clauses": counter_clauses,
    }


def build_pilot_final_assumptions_object(review_object: dict[str, object]) -> dict[str, object]:
    basis = build_pilot_cluster_basis(review_object)
    supported: list[dict[str, object]] = []
    pending: list[dict[str, object]] = []
    for item in basis:
        cluster_id = str(item["id"])
        title = str(item["title"])
        why = clean_clause(str(item["why"]))
        counter_signal = clean_clause(str(item["counter_signal"]))
        counter_implication = clean_clause(str(item["counter_implication"]))
        evidence = list(item["evidence"])
        if cluster_id == "execution_control":
            supported.append(
                {
                    "cluster": title,
                    "reason": why,
                    "text": f"从{title}看，{why}，因此 harness、权限和审核层不是附加治理，而是默认执行面的前置条件。",
                    "evidence": evidence,
                }
            )
            pending.append(
                {
                    "cluster": title,
                    "reason": counter_signal or counter_implication,
                    "text": f"从{title}暴露的边界信号看，{counter_signal or counter_implication}，因此仍需验证这些控制层是否会成为默认产品结构，而不只是高成熟团队的最佳实践。",
                    "evidence": evidence,
                }
            )
        elif cluster_id == "collaboration_roles":
            supported.append(
                {
                    "cluster": title,
                    "reason": why,
                    "text": f"从{title}看，{why}，因此角色边界与责任状态如果不能在 UI 上可见，团队协作就会退化为黑箱自动化。",
                    "evidence": evidence,
                }
            )
        elif cluster_id == "governance_frontstage_ux":
            supported.append(
                {
                    "cluster": title,
                    "reason": why,
                    "text": f"从{title}看，{why}，因此治理对象如果不能被用户操作和追踪，就不能算真正进入产品能力层。",
                    "evidence": evidence,
                }
            )
            pending.append(
                {
                    "cluster": title,
                    "reason": counter_signal or counter_implication,
                    "text": f"从{title}暴露的边界信号看，{counter_signal or counter_implication}，因此仍需验证前台化的治理对象是否能降低协作摩擦，还是会增加理解和操作成本。",
                    "evidence": evidence,
                }
            )
    expected_ids = {"execution_control", "collaboration_roles", "governance_frontstage_ux"}
    found_ids = {str(item["id"]) for item in basis}
    if found_ids != expected_ids:
        raise SystemExit(f"unexpected pilot cluster basis ids: {sorted(found_ids)}")
    return {
        "supported": supported,
        "pending": pending,
        "basis": basis,
    }


def build_pilot_final_ux_object(review_object: dict[str, object]) -> dict[str, object]:
    cluster_basis = {
        str(item["id"]): item
        for item in build_pilot_cluster_basis(review_object)
    }
    proposition_schemas = [
        {
            "name": "责任状态卡",
            "source_cluster_ids": ["collaboration_roles", "governance_frontstage_ux"],
            "surface": "把当前责任状态、待确认项和升级边界集中呈现",
            "effect": "让前台直接显示谁在负责、何时需要人接手",
        },
        {
            "name": "分级决策卡",
            "source_cluster_ids": ["execution_control", "governance_frontstage_ux"],
            "surface": "把自动通过、待确认和必须升级的决策拆成分级入口",
            "effect": "让决策路径和治理边界可以被前台直接理解",
        },
        {
            "name": "异步沟通面板",
            "source_cluster_ids": ["collaboration_roles"],
            "surface": "把提醒、追问、回执和跨时区跟进收进同一块异步面板",
            "effect": "减少协作再次退回同步盯梢和临时打断",
        },
        {
            "name": "审计与证据抽屉",
            "source_cluster_ids": ["execution_control", "governance_frontstage_ux"],
            "surface": "把操作日志、证据引用和回退点折叠进可展开的证据抽屉",
            "effect": "让用户随时回看系统为什么这样执行",
        },
    ]
    propositions: list[dict[str, object]] = []
    for schema in proposition_schemas:
        source_evidence: list[str] = []
        cluster_notes: list[str] = []
        counter_notes: list[str] = []
        source_clusters: list[str] = []
        for cluster_id in schema["source_cluster_ids"]:
            cluster = cluster_basis.get(cluster_id)
            if cluster is None:
                raise SystemExit(f"missing pilot cluster basis for ux proposition: {schema['name']} -> {cluster_id}")
            source_clusters.append(str(cluster.get("title", cluster_id)))
            for slug in cluster.get("evidence", []):
                if slug not in source_evidence:
                    source_evidence.append(slug)
            why = clean_clause(str(cluster.get("why", "")))
            if why:
                cluster_notes.append(why)
            counter_signal = clean_clause(str(cluster.get("counter_signal", "")))
            if counter_signal:
                counter_notes.append(counter_signal)
        reason_clause = "；".join(cluster_notes)
        risk_clause = "；".join(counter_notes[:1])
        description = (
            f"{schema['surface']}，{schema['effect']}。"
            f"它直接回应的综述依据是：{reason_clause}。"
        )
        if risk_clause:
            description += f"同时也用来处理这样的边界信号：{risk_clause}。"
        propositions.append(
            {
                "name": schema["name"],
                "source_clusters": source_clusters,
                "source_cluster_ids": schema["source_cluster_ids"],
                "source_evidence": source_evidence,
                "cluster_notes": cluster_notes,
                "counter_notes": counter_notes,
                "reason_clause": reason_clause,
                "description": description,
            }
        )
    return {
        "intro": "从 AI-native UX 角度看，这组材料要求产品把责任、决策、沟通和审计都显式化为用户可见对象，而不是只把它们藏在模型调用和后台流程里。",
        "propositions": propositions,
    }


def build_pilot_final_writeback_objects(intake_text: str, synthesis_text: str) -> dict[str, object]:
    review_object = build_pilot_final_review_object(intake_text, synthesis_text)
    return {
        "review": review_object,
        "judgment": build_pilot_final_judgment_object(review_object),
        "problem": build_pilot_final_problem_object(review_object),
        "assumptions": build_pilot_final_assumptions_object(review_object),
        "ux": build_pilot_final_ux_object(review_object),
    }


def render_pilot_final_judgment(judgment_object: dict[str, object]) -> str:
    return str(judgment_object["text"])


def render_pilot_final_problem_statement(problem_object: dict[str, object]) -> str:
    return str(problem_object["text"])


def render_pilot_final_assumptions(assumptions_object: dict[str, object]) -> str:
    supported = assumptions_object["supported"]
    pending = assumptions_object["pending"]
    sections: list[str] = []
    if supported:
        sections.append("当前工作假设")
        sections.extend(f"- {item['text']}" for item in supported)
    if pending:
        if sections:
            sections.append("")
        sections.append("仍待验证")
        sections.extend(f"- {item['text']}" for item in pending)
    return "\n".join(sections)


def render_pilot_final_ux_section(ux_object: dict[str, object]) -> str:
    lines = [str(ux_object["intro"])]
    for item in ux_object["propositions"]:
        source_clusters = " / ".join(item["source_clusters"])
        suffix = f"（{source_clusters}）" if source_clusters else ""
        lines.append(f"- {item['name']}{suffix}：{item['description']}")
    return "\n".join(lines)


def build_final_problem_statement() -> str:
    return (
        "问题已经不再是再增加多少个 agent，而是如何把执行控制、角色分工、治理记录和前台操作收束成一套"
        "默认可用的团队工作台。"
    )


def build_final_assumptions() -> str:
    return "\n".join(
        [
            "当前工作假设",
            "- harness、权限和审核层不是附加治理，而是默认执行面的前置条件。",
            "- 角色边界与责任状态如果不能在 UI 上可见，团队协作就会退化为黑箱自动化。",
            "- 治理对象如果不能被用户操作和追踪，就不能算真正进入产品能力层。",
            "",
            "仍待验证",
            "- 这些控制层是否会成为默认产品结构，而不只是高成熟团队的最佳实践。",
            "- 前台化的治理对象是否能降低协作摩擦，还是会增加理解和操作成本。",
        ]
    )


def build_final_ai_native_ux_section() -> str:
    lines = [
        "从 AI-native UX 角度看，这组材料要求产品把责任、决策、沟通和审计都显式化为用户可见对象，而不是只把它们藏在模型调用和后台流程里。",
    ]
    for item in FINAL_WRITEBACK_UX_OBJECTS:
        lines.append(f"- {item['name']}：{item['description']}")
    return "\n".join(lines)


def parse_review_theme_blocks(review_text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    for chunk in review_text.split("### 主题：")[1:]:
        lines = chunk.strip().splitlines()
        if not lines:
            continue
        block = {
            "title": lines[0].strip(),
            "quotes": [],
            "paraphrase": "",
            "evidence": "",
            "why": "",
        }
        current_key = ""
        prelude_lines: list[str] = []
        for line in lines[1:]:
            stripped = line.strip()
            if stripped == "**Direct quote**":
                current_key = "quotes"
                continue
            if stripped == "**Paraphrase**":
                current_key = "paraphrase"
                continue
            if stripped == "**Evidence**":
                current_key = "evidence"
                continue
            if stripped == "**Why it matters**":
                current_key = "why"
                continue
            if not stripped:
                continue
            if not current_key:
                prelude_lines.append(stripped)
                continue
            if current_key == "quotes":
                block["quotes"].append(stripped)
                current_key = ""
                continue
            if block[current_key]:
                block[current_key] += "\n" + stripped
            else:
                block[current_key] = stripped
        if prelude_lines:
            prelude_text = " ".join(prelude_lines)
            block["paraphrase"] = (
                f"{prelude_text} {block['paraphrase']}".strip()
                if block["paraphrase"]
                else prelude_text
            )
        blocks.append(block)
    return blocks


def build_writeback_literature_review(review_text: str) -> str:
    sections: list[str] = []
    for index, block in enumerate(parse_review_theme_blocks(review_text), start=1):
        theme_label = normalize_review_theme_label(block["title"])
        evidence_ref = block["evidence"]
        if evidence_ref.startswith("- "):
            evidence_ref = evidence_ref[2:].strip()
        sections.append(
            "\n".join(
                [
                    f"### 线索 {index}：{theme_label}",
                    "",
                    f"代表引文：{block['quote']}",
                    "",
                    f"观察：{block['paraphrase']}",
                    "",
                    f"证据来源：{evidence_ref}",
                    "",
                    f"为什么重要：{block['why']}",
                ]
            )
        )
    return "\n\n".join(sections)


def build_writeback_assumptions(assumptions_text: str) -> str:
    supported: list[str] = []
    pending: list[str] = []
    target = None
    for line in assumptions_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "### 被材料支持的 assumptions":
            target = supported
            continue
        if stripped == "### 仍需验证的 assumptions":
            target = pending
            continue
        if target is not None:
            target.append(re.sub(r"^\d+\.\s*", "", stripped))

    sections: list[str] = []
    if supported:
        sections.append("当前工作假设\n" + "\n".join(f"- {item}" for item in supported))
    if pending:
        sections.append("仍待验证\n" + "\n".join(f"- {item}" for item in pending))
    return "\n\n".join(sections)


def build_writeback_problem(problem_text: str) -> str:
    draft_prefix = "这里先提出一个 draft problem statement："
    core_problem = problem_text
    if problem_text.startswith(draft_prefix):
        core_problem = problem_text[len(draft_prefix) :].strip()
    return (
        "如果把这组材料转写成一个真正的产品问题，核心已经不是再增加多少个 agent 或多少条自动化链路，"
        f"而是{core_problem}"
    )


def build_writeback_intro(review_intro: str, ux_lens_points: list[str]) -> str:
    intro_lead = review_intro.split(" 当前可补充的 AI-native UX 观察维度包括：")[0].strip()
    if not ux_lens_points:
        return intro_lead
    return (
        f"{intro_lead} 这意味着这份 writeback 不再把材料当成播客摘要，而是把它们视为同一产品方向的多点证据。"
        f"在阅读过程中，会特别参考 {', '.join(ux_lens_points[:3])} 等 AI-native UX 维度来判断协作与治理是否已经进入产品主结构。"
    )


def build_writeback_research_direction(research_direction: str, direction_status: str) -> str:
    question_source_map = {
        "user_provided": "用户给定",
        "system_suggested_pending": "系统建议，待用户批准",
        "system_suggested_approved": "系统建议，已批准",
    }
    return (
        "这轮 writeback 不把问题视为已经闭合的结论，而是把它保留成下一轮持续跟踪的研究方向：\n"
        f"- 研究方向：{research_direction}\n"
        f"- 当前状态：{question_source_map.get(direction_status, direction_status)}"
    )


def build_longform_sections(
    title: str,
    subtitle: str,
    intake_text: str,
    synthesis_text: str,
) -> dict[str, str]:
    research_direction, direction_status = build_research_question(intake_text)
    question_source_map = {
        "user_provided": "用户给定",
        "system_suggested_pending": "系统建议，待用户批准",
        "system_suggested_approved": "系统建议，已批准",
    }
    if is_pilot_integrated_team_paradigm(intake_text):
        final_objects = build_pilot_final_writeback_objects(intake_text, synthesis_text)
        review_object = final_objects["review"]
        subtitle_clause = f"副标题“{subtitle}”对应的判断路径也会被一并展开。" if subtitle else ""
        intro = (
            f"本轮先按三主题簇做综述，不按播客顺序复述，也不先给最终判断。"
            f"这份 writeback 直接把“{title}”当作同一产品方向下的结构性证据，而不是播客摘要。{subtitle_clause}"
        )
        return {
            "intro": intro,
            "question": (
                f"{review_object['question']}\n\n问题来源："
                f"{review_object.get('question_source') or question_source_map.get(direction_status, direction_status or '用户给定')}"
            ),
            "review": build_final_longform_review_section(review_object["review"]),
            "judgment": render_pilot_final_judgment(final_objects["judgment"]),
            "problem": render_pilot_final_problem_statement(final_objects["problem"]),
            "assumptions": render_pilot_final_assumptions(final_objects["assumptions"]),
            "ux": render_pilot_final_ux_section(final_objects["ux"]),
            "research_direction_value": research_direction,
            "direction_status_value": direction_status,
            "research_direction": build_writeback_research_direction(research_direction, direction_status),
            "tensions": review_object["tensions"],
        }

    outline = build_longform_outline(intake_text, synthesis_text)
    judgment = str(outline["core_judgment"])
    preserved_tensions = [str(item) for item in outline["preserved_tensions"]]
    review_sections = build_pilot_review_pack_sections(intake_text, synthesis_text)
    subtitle_clause = f"副标题“{subtitle}”对应的判断路径也会被一并展开。" if subtitle else ""
    intro = (
        f"本轮先按三主题簇做综述，不按播客顺序复述，也不先给最终判断。"
        f"这份 writeback 直接把“{title}”当作同一产品方向下的结构性证据，而不是播客摘要。{subtitle_clause}"
    )
    return {
        "intro": intro,
        "question": f"{research_direction}\n\n问题来源：{question_source_map.get(direction_status, direction_status or '用户给定')}",
        "review": build_final_longform_review_section(review_sections["review"]),
        "judgment": judgment,
        "problem": build_final_problem_statement(),
        "assumptions": build_final_assumptions(),
        "ux": build_final_ai_native_ux_section(),
        "research_direction_value": research_direction,
        "direction_status_value": direction_status,
        "research_direction": build_writeback_research_direction(research_direction, direction_status),
        "tensions": "\n".join(f"- {item}" for item in preserved_tensions),
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

    sections = build_longform_sections(args.title, args.subtitle, intake_text, synthesis_text)
    return f"""# Writeback Proposal

- writeback_id: `{args.writeback_id}`
- intake_id: `{intake_id}`
- collaboration_mode: `{read_field(intake_text, 'collaboration_mode')}`
- used_default_rules: `{read_field(intake_text, 'used_default_rules')}`
- focus_priority: {format_list(read_list_field(intake_text, 'focus_priority'))}
- special_attention: {format_list(read_list_field(intake_text, 'special_attention'))}
- target_audience: `{read_field(intake_text, 'target_audience')}`
- research_direction: `{sections["research_direction_value"]}`
- direction_status: `{sections["direction_status_value"]}`
- synthesis_ref: `{read_field(synthesis_text, 'synthesis_id')}`

## 标题

{args.title}

## 副标题

{args.subtitle}

## 研究问题

{sections["question"]}

## 综述导言

{sections["intro"]}

## 文献综述

{sections["review"]}

## 综合判断

{sections["judgment"]}

## Problem Statement

{sections["problem"]}

## Assumptions

{sections["assumptions"]}

## AI-native UX 视角

{sections["ux"]}

## 本轮 Research Direction

{sections["research_direction"]}

## 保留分歧

{sections["tensions"]}
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

    sections = build_pilot_review_pack_sections(intake_text, synthesis_text)
    tensions = build_pilot_review_pack_tensions(sections["clusters"], synthesis_text)
    return f"""# Research Review Pack

## Research Question

{sections["question"]}

## Review Introduction

{sections["intro"]}

## Thematic Literature Review

{sections["review"]}

## Counter-Signals And Tensions

{tensions}

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
