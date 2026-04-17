from __future__ import annotations

import re
from pathlib import Path
from typing import Any


PODCAST_PRIORITY = ["summary", "highlights", "transcript"]
XIAOHONGSHU_PRIORITY = ["full_text", "transcript", "comment_batch"]
OFFICIAL_PRIORITY = ["full_text"]

THEME_LABELS = {
    "governance_or_control": "执行控制层",
    "coordination_protocol": "协作与角色层",
    "trust_or_explainability": "治理与前台 UX 外显层",
    "role_delegation": "协作与角色层",
    "workflow_shift": "执行控制层",
    "capability_boundary": "治理与前台 UX 外显层",
}

MECHANISM_HINTS = {
    "责任": "governance_or_control",
    "控制": "governance_or_control",
    "审核": "governance_or_control",
    "权限": "governance_or_control",
    "协作": "coordination_protocol",
    "沟通": "coordination_protocol",
    "角色": "role_delegation",
    "分工": "role_delegation",
    "信任": "trust_or_explainability",
    "解释": "trust_or_explainability",
    "前台": "trust_or_explainability",
    "体验": "trust_or_explainability",
    "边界": "capability_boundary",
    "工作流": "workflow_shift",
    "执行": "workflow_shift",
    "harness": "workflow_shift",
}


def _priority_for(channel: str) -> list[str]:
    if channel in {"podcast", "podcasts"}:
        return PODCAST_PRIORITY
    if channel == "xiaohongshu":
        return XIAOHONGSHU_PRIORITY
    if channel == "official":
        return OFFICIAL_PRIORITY
    return ["full_text"]


def detect_channel_from_artifact_path(path_text: str) -> str:
    normalized = path_text.replace("\\", "/")
    if "/artifacts/podcasts/" in normalized:
        return "podcasts"
    if "/artifacts/xiaohongshu/" in normalized:
        return "xiaohongshu"
    if "/artifacts/official/" in normalized:
        return "official"
    return "unknown"


def _read_content_section(text: str) -> str:
    lines = text.splitlines()
    start = 0
    for index, line in enumerate(lines):
        if line.strip() == "## Content":
            start = index + 1
            break
    return "\n".join(lines[start:]).strip()


def _meaningful_lines(slice_type: str, content: str) -> list[str]:
    text = _read_content_section(content) or content
    lines: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        stripped = re.sub(r"^\d+\.\s*", "", stripped)
        lines.append(stripped)

    if slice_type == "summary":
        return lines[:3]
    if slice_type == "highlights":
        return lines[:4]
    if slice_type == "transcript":
        return [line for line in lines if line.startswith("[")][:4] or lines[:2]
    if slice_type == "comment_batch":
        return lines[:2]
    return lines[:4]


def collect_report_artifacts(*, channel: str, artifact_paths: list[str], root: Path) -> list[dict[str, Any]]:
    priority = _priority_for(channel)
    ranked: list[dict[str, Any]] = []
    missing_paths: list[str] = []
    for relative_path in artifact_paths:
        path = root / relative_path
        if not path.exists():
            missing_paths.append(relative_path)
            continue
        slice_type = path.stem
        ranked.append(
            {
                "slice_type": slice_type,
                "path": path,
                "content": path.read_text(encoding="utf-8"),
                "rank": priority.index(slice_type) if slice_type in priority else len(priority),
            }
        )
    if missing_paths:
        raise FileNotFoundError(f"missing artifact paths: {', '.join(missing_paths)}")
    ranked.sort(key=lambda item: (item["rank"], str(item["path"])))
    for item in ranked:
        item.pop("rank", None)
    return ranked


def _infer_mechanism_category(quote: str, research_direction: str) -> str:
    haystack = f"{research_direction} {quote}".lower()
    for needle, mapped in MECHANISM_HINTS.items():
        if needle.lower() in haystack:
            return mapped
    return "workflow_shift"


def _infer_claim_role(slice_type: str, quote: str) -> str:
    if slice_type == "comment_batch":
        return "counter_signal"
    if any(token in quote for token in ["并没有", "不是", "未必", "怀疑", "问题在于"]):
        return "tension"
    if any(token in quote for token in ["为什么", "是否", "?", "？"]):
        return "open_question"
    return "support"


def _build_paraphrase(category: str, quote: str) -> str:
    if category == "governance_or_control":
        return f"这段原话强调的不是单点能力，而是 `{category}` 所代表的治理、权限或审核结构已经进入产品主流程。"
    if category == "coordination_protocol":
        return f"这段原话在指向 `{category}`：多个角色或多个 agent 之间需要稳定的沟通与协作协议。"
    if category == "role_delegation":
        return f"这段原话把问题收束到 `{category}`，也就是谁负责、谁执行、谁兜底必须被重新定义。"
    if category == "trust_or_explainability":
        return f"这段原话说明 `{category}` 已经不是附属说明，而是用户理解和判断 agent 行为的前台对象。"
    if category == "capability_boundary":
        return f"这段原话主要在暴露 `{category}`：产品需要清楚界定什么交给 agent，什么仍由人来把关。"
    return f"这段原话在说明 `{category}` 意义上的结构变化，而不是泛泛的趋势评论。"


def build_evidence_candidates(
    *,
    research_direction: str,
    channel: str,
    artifact_items: list[dict[str, Any]],
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    candidate_index = 1
    for item in artifact_items:
        slice_type = str(item["slice_type"])
        for line in _meaningful_lines(slice_type, str(item["content"])):
            category = _infer_mechanism_category(line, research_direction)
            claim_role = _infer_claim_role(slice_type, line)
            candidates.append(
                {
                    "candidate_id": f"{channel}-candidate-{candidate_index}",
                    "research_direction": research_direction,
                    "theme_hint": category,
                    "quote": line,
                    "speaker_or_source": channel,
                    "artifact_ref": str(item["path"]),
                    "why_selected": "Matches the current research direction and contains mechanism-bearing wording.",
                    "paraphrase": _build_paraphrase(category, line),
                    "claim_role": claim_role,
                    "confidence": "high" if slice_type in {"summary", "highlights", "full_text"} else "medium",
                }
            )
            candidate_index += 1
    return candidates


def cluster_evidence_candidates(candidates: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for candidate in candidates:
        theme = THEME_LABELS.get(candidate["theme_hint"], "执行控制层")
        grouped.setdefault(theme, []).append(candidate)

    preferred_order = ["执行控制层", "协作与角色层", "治理与前台 UX 外显层"]
    clusters: list[dict[str, Any]] = []
    for theme in preferred_order:
        entries = grouped.get(theme, [])
        if not entries:
            continue
        entries.sort(key=lambda item: (item["claim_role"] != "support", item["artifact_ref"], item["candidate_id"]))
        clusters.append({"theme": theme, "entries": entries[:4]})

    for theme, entries in grouped.items():
        if theme in preferred_order:
            continue
        clusters.append({"theme": theme, "entries": entries[:4]})

    return clusters[:3]
