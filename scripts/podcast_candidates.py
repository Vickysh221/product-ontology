#!/usr/bin/env python3
"""Generate event and claim candidates from imported podcast artifacts."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WATCH_PROFILE = ROOT / "seed" / "watch-profile.yaml"
PODCAST_ARTIFACTS = ROOT / "library" / "artifacts" / "podcasts"
PODCAST_SOURCES = ROOT / "library" / "sources" / "podcasts"
PODCAST_CANDIDATES = ROOT / "library" / "sessions" / "podcast-candidates"
EVENTS_DIR = ROOT / "library" / "events" / "podcasts"
CLAIMS_DIR = ROOT / "library" / "claims" / "podcasts"


CHANGE_LAYER_KEYWORDS = {
    "capability": ["v2a", "vla", "vlm", "能力", "模型", "自动驾驶", "智驾", "物理 ai", "具身"],
    "workflow": ["协同", "工作流", "流程", "驾驶策略", "回路", "批评家", "分析师", "多智能体"],
    "trust": ["可解释", "信任", "透明度", "敢不敢用", "解释它为什么会变聪明"],
    "governance": ["监管", "保险", "审批", "责任", "安全要求"],
    "business_model": ["开放", "平台", "厨房", "封闭", "垂直整合"],
}

CAPABILITY_KEYWORDS = [
    "V2A",
    "自动驾驶",
    "智驾",
    "可解释性",
    "高精地图",
    "激光雷达",
    "机器人",
    "端到端",
    "3D 高斯",
    "物理 AI",
]

PROBLEM_KEYWORDS = [
    "信任",
    "主动权",
    "资源冲突",
    "幽灵刹车",
    "地图依赖",
    "透明度",
    "安全",
    "舒适",
]

EVENT_TRIGGERS = ["发布", "升级", "强调", "对比", "要求", "摆脱", "重构", "迁移", "转向"]
CLAIM_TRIGGERS = ["核心在于", "意味着", "说明", "表明", "倒逼", "关键", "预示", "从", "通过"]


@dataclass
class Segment:
    artifact_name: str
    text: str
    anchor: str
    transcript_timestamp: str | None = None


@dataclass
class Candidate:
    score: int
    title: str
    body: dict[str, Any]


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "true":
        return True
    if value == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse_simple_yaml(text: str) -> dict[str, Any]:
    entries: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        entries.append((indent, line.strip()))

    def parse_block(index: int, expected_indent: int) -> tuple[Any, int]:
        if index >= len(entries):
            return {}, index

        indent, stripped = entries[index]
        if indent != expected_indent:
            raise ValueError(f"Unexpected indentation near: {stripped}")

        if stripped.startswith("- "):
            items: list[Any] = []
            while index < len(entries):
                indent, stripped = entries[index]
                if indent < expected_indent:
                    break
                if indent != expected_indent or not stripped.startswith("- "):
                    raise ValueError(f"Invalid list structure near: {stripped}")
                items.append(parse_scalar(stripped[2:]))
                index += 1
            return items, index

        mapping: dict[str, Any] = {}
        while index < len(entries):
            indent, stripped = entries[index]
            if indent < expected_indent:
                break
            if indent != expected_indent:
                raise ValueError(f"Invalid mapping structure near: {stripped}")
            key, sep, remainder = stripped.partition(":")
            if not sep:
                raise ValueError(f"Invalid YAML line: {stripped}")
            key = key.strip()
            remainder = remainder.strip()
            if remainder:
                mapping[key] = parse_scalar(remainder)
                index += 1
                continue

            next_index = index + 1
            if next_index >= len(entries) or entries[next_index][0] <= expected_indent:
                mapping[key] = {}
                index = next_index
                continue

            child, index = parse_block(next_index, entries[next_index][0])
            mapping[key] = child
        return mapping, index

    parsed, next_index = parse_block(0, entries[0][0] if entries else 0)
    if next_index != len(entries):
        raise ValueError("Failed to consume the full YAML document.")
    if not isinstance(parsed, dict):
        raise ValueError("Top-level YAML document must be a mapping.")
    return parsed


def read_markdown_content(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    marker = "\n## Content\n\n"
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text.strip()


def read_source_metadata(path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- ") and ": `" in line and line.endswith("`"):
            key, value = line[2:].split(": `", 1)
            metadata[key.strip()] = value[:-1]
    return metadata


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def split_summary_segments(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？!?])\s*", text)
    return [part.strip() for part in parts if part.strip()]


def split_highlight_segments(text: str) -> list[tuple[str, str]]:
    segments: list[tuple[str, str]] = []
    for line in text.splitlines():
        match = re.match(r"\d+\.\s+\[([^\]]+)\]\s*(.+)", line.strip())
        if match:
            segments.append((match.group(1), match.group(2).strip()))
    return segments


def normalize(text: str) -> str:
    return text.lower()


def tokenize(text: str) -> list[str]:
    ascii_tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9+.-]*", text.lower())
    chinese_bigrams: list[str] = []
    contiguous = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    for block in contiguous:
        chinese_bigrams.extend(block[i : i + 2] for i in range(len(block) - 1))
    return ascii_tokens + chinese_bigrams


def read_transcript_lines(slug: str) -> list[tuple[str, str]]:
    transcript = read_markdown_content(PODCAST_ARTIFACTS / slug / "transcript.md")
    lines: list[tuple[str, str]] = []
    for raw_line in transcript.splitlines():
        match = re.match(r"\[([0-9:]+)\]\s*-\s*[^:]*:\s*(.+)", raw_line.strip())
        if match:
            lines.append((match.group(1), match.group(2).strip()))
    return lines


def best_transcript_timestamp(segment_text: str, transcript_lines: list[tuple[str, str]]) -> str | None:
    segment_tokens = tokenize(segment_text)
    if not segment_tokens:
        return None
    best_timestamp = None
    best_score = 0
    for timestamp, line_text in transcript_lines:
        line_tokens = set(tokenize(line_text))
        score = sum(1 for token in segment_tokens if token in line_tokens)
        if score > best_score:
            best_score = score
            best_timestamp = timestamp
    return best_timestamp if best_score > 0 else None


def count_matches(text: str, keywords: list[str]) -> tuple[int, list[str]]:
    normalized = normalize(text)
    hits = [keyword for keyword in keywords if keyword.lower() in normalized]
    return len(hits), hits


def score_topic_relevance(text: str, profile: dict[str, Any]) -> tuple[int, list[str]]:
    hits: list[str] = []
    score = 0
    for section in ("domains", "brands", "active_topics"):
        values = profile.get(section, [])
        count, matched = count_matches(text, values)
        score += count * (2 if section == "active_topics" else 1)
        hits.extend(matched)
    return score, hits


def score_ontology_relevance(text: str, required_signals: list[str]) -> tuple[int, list[str]]:
    hits: list[str] = []
    score = 0
    normalized = normalize(text)
    for signal in required_signals:
        signal_hits = CHANGE_LAYER_KEYWORDS.get(signal, [])
        if signal == "change":
            signal_hits = EVENT_TRIGGERS
        elif signal == "capability":
            signal_hits = CAPABILITY_KEYWORDS
        elif signal == "problem":
            signal_hits = PROBLEM_KEYWORDS
        if any(keyword.lower() in normalized for keyword in signal_hits):
            score += 2
            hits.append(signal)
    return score, hits


def score_authority(source_meta: dict[str, str], profile: dict[str, Any]) -> tuple[int, list[str]]:
    hits: list[str] = []
    score = 0
    title = source_meta.get("title", "")
    publisher = source_meta.get("publisher", "")
    for channel in profile.get("preferred_sources", {}).get("channels", []):
        if channel.lower() in title.lower() or channel.lower() in publisher.lower():
            score += int(profile.get("authority_rules", {}).get("preferred_channel_bonus", 0))
            hits.append(f"preferred_channel:{channel}")
    for speaker in profile.get("preferred_sources", {}).get("speakers", []):
        if speaker.lower() in title.lower():
            score += int(profile.get("authority_rules", {}).get("preferred_speaker_bonus", 0))
            hits.append(f"preferred_speaker:{speaker}")
    return score, hits


def contains_downgrade_phrase(text: str, profile: dict[str, Any]) -> bool:
    normalized = normalize(text)
    return any(phrase.lower() in normalized for phrase in profile.get("candidate_rules", {}).get("downgrade_if_contains", []))


def infer_change_layer(text: str) -> str:
    normalized = normalize(text)
    best_layer = "capability"
    best_hits = 0
    for layer, keywords in CHANGE_LAYER_KEYWORDS.items():
        hits = sum(1 for keyword in keywords if keyword.lower() in normalized)
        if hits > best_hits:
            best_layer = layer
            best_hits = hits
    return best_layer


def extract_keywords(text: str, keywords: list[str]) -> list[str]:
    normalized = normalize(text)
    return [keyword for keyword in keywords if keyword.lower() in normalized]


def make_event_candidate(index: int, slug: str, segment: Segment, profile: dict[str, Any], source_meta: dict[str, str]) -> Candidate | None:
    topic_score, topic_hits = score_topic_relevance(segment.text, profile)
    ontology_score, ontology_hits = score_ontology_relevance(
        segment.text, profile.get("candidate_rules", {}).get("required_ontology_signals", [])
    )
    authority_score, authority_hits = score_authority(source_meta, profile)
    trigger_bonus = 2 if any(trigger in segment.text for trigger in EVENT_TRIGGERS) else 0
    score = topic_score + ontology_score + authority_score + trigger_bonus
    if contains_downgrade_phrase(segment.text, profile):
        score -= 2
    min_score = int(profile.get("candidate_rules", {}).get("min_event_score", 4))
    if score < min_score:
        return None

    capabilities = extract_keywords(segment.text, CAPABILITY_KEYWORDS)
    problems = extract_keywords(segment.text, PROBLEM_KEYWORDS)
    title = segment.text[:36] + ("..." if len(segment.text) > 36 else "")
    return Candidate(
        score=score,
        title=title,
        body={
            "candidate_id": f"event-candidate-{slug}-{index}",
            "可观察变化": segment.text,
            "变化层": infer_change_layer(segment.text),
            "受影响能力": capabilities,
            "目标问题": problems,
            "信任信号": "是" if "可解释" in segment.text or "信任" in segment.text else "否",
            "治理信号": "是" if "监管" in segment.text or "保险" in segment.text else "否",
            "证据定位": f"{segment.artifact_name}:{segment.anchor}",
            "原文时间戳": segment.transcript_timestamp or "unknown",
            "命中主题": topic_hits,
            "命中规则": ontology_hits + authority_hits,
        },
    )


def make_claim_candidate(index: int, slug: str, segment: Segment, profile: dict[str, Any], source_meta: dict[str, str]) -> Candidate | None:
    topic_score, topic_hits = score_topic_relevance(segment.text, profile)
    ontology_score, ontology_hits = score_ontology_relevance(
        segment.text, profile.get("candidate_rules", {}).get("required_ontology_signals", [])
    )
    authority_score, authority_hits = score_authority(source_meta, profile)
    trigger_bonus = 2 if any(trigger in segment.text for trigger in CLAIM_TRIGGERS) else 0
    score = topic_score + ontology_score + authority_score + trigger_bonus
    if contains_downgrade_phrase(segment.text, profile):
        score -= 2
    min_score = int(profile.get("candidate_rules", {}).get("min_claim_score", 5))
    if score < min_score:
        return None

    layer = infer_change_layer(segment.text)
    title = segment.text[:36] + ("..." if len(segment.text) > 36 else "")
    return Candidate(
        score=score,
        title=title,
        body={
            "candidate_id": f"claim-candidate-{slug}-{index}",
            "候选判断": segment.text,
            "机制解释": infer_mechanism(segment.text, layer),
            "工作流含义": infer_workflow_implication(segment.text),
            "类别信号": infer_category_signal(segment.text),
            "为什么重要": infer_why_it_matters(segment.text),
            "缺失证据": infer_missing_evidence(segment.text),
            "反方观点": infer_counterargument(segment.text),
            "证据定位": f"{segment.artifact_name}:{segment.anchor}",
            "原文时间戳": segment.transcript_timestamp or "unknown",
            "命中主题": topic_hits,
            "命中规则": ontology_hits + authority_hits,
        },
    )


def infer_mechanism(text: str, layer: str) -> str:
    if "理解意图" in text or "看穿局势" in text:
        return "这段语料强调系统正在从看懂场景转向理解意图。"
    if "可解释" in text or "解释" in text:
        return "这段语料强调系统试图把决策理由说出来，以重建用户信任。"
    if "开放" in text or "平台" in text:
        return "这段语料把能力栈描述为开放平台，而不是封闭式垂直整合。"
    return f"这段语料指向一次 {layer} 层变化，并且可能带来后续产品影响。"


def infer_workflow_implication(text: str) -> str:
    if "批评家" in text or "分析师" in text or "司机" in text:
        return "这可能意味着驾驶系统内部正在转向多角色协同工作流。"
    if "主动权" in text:
        return "这说明更多决策控制权被保留在车企自己的能力栈里。"
    return "这条工作流含义还需要结合 transcript 上下文继续确认。"


def infer_category_signal(text: str) -> str:
    if "苹果与安卓" in text or "封闭式垂直整合" in text or "开放式平台" in text:
        return "这个类别可能正在分化为封闭式垂直整合和开放平台赋能两条路线。"
    if "机器人" in text or "物理 AI" in text:
        return "这里把汽车能力栈叙述成可迁移到机器人和具身智能领域的通用能力。"
    return "这段话可能指向类别变化，但仍需要跨产品对比来确认。"


def infer_why_it_matters(text: str) -> str:
    if "信任" in text or "敢不敢用" in text:
        return "这很重要，因为真实采用取决于用户是否敢用、能否校准信任，而不只是跑分表现。"
    if "主动权" in text:
        return "这很重要，因为能力栈控制权会影响路线速度和差异化空间。"
    if "高精地图" in text:
        return "这很重要，因为降低对高精地图的依赖会提升部署灵活性。"
    return "如果这段变化真的成立，它会影响能力边界、信任机制或控制边界。"


def infer_missing_evidence(text: str) -> str:
    if "可解释" in text:
        return "还需要产品侧证据来证明这些解释真的在实际驾驶体验中对用户可见。"
    if "更安全" in text or "安全" in text:
        return "还需要对比性的安全数据或接管数据，而不是停留在描述性表述。"
    return "还需要 transcript 上下文或更多来源来确认这是真机制，而不是包装话术。"


def infer_counterargument(text: str) -> str:
    if "理解意图" in text:
        return "除非节目给出具体行为差异，否则这仍可能只是营销语言。"
    if "开放" in text or "平台" in text:
        return "在下游采用真正出现之前，开放平台叙事可能会高估生态价值。"
    return "这段内容也可能只是评论性解读，而不是可沉淀的产品证据。"

def collect_segments(slug: str) -> tuple[dict[str, str], list[Segment]]:
    source_meta = read_source_metadata(PODCAST_SOURCES / f"{slug}.md")
    summary = read_markdown_content(PODCAST_ARTIFACTS / slug / "summary.md")
    highlights = read_markdown_content(PODCAST_ARTIFACTS / slug / "highlights.md")
    transcript_lines = read_transcript_lines(slug)

    segments: list[Segment] = []
    for index, sentence in enumerate(split_summary_segments(summary), start=1):
        segments.append(
            Segment(
                "summary.md",
                sentence,
                f"sentence-{index}",
                best_transcript_timestamp(sentence, transcript_lines),
            )
        )
    for timestamp, sentence in split_highlight_segments(highlights):
        segments.append(Segment("highlights.md", sentence, timestamp, timestamp))
    return source_meta, segments


def render_candidates_markdown(kind: str, slug: str, candidates: list[Candidate], profile: dict[str, Any]) -> str:
    title = "Event Candidates" if kind == "event" else "Claim Candidates"
    lines = [
        f"# {title}",
        "",
        f"- episode_slug: `{slug}`",
        f"- watch_profile: `{WATCH_PROFILE.relative_to(ROOT)}`",
        f"- extraction_inputs: `summary + highlights`",
        "",
        "## Focus",
        "",
    ]

    focus_key = "priority_event_slots" if kind == "event" else "priority_claim_slots"
    for item in profile.get("extraction_focus", {}).get(focus_key, []):
        lines.append(f"- `{item}`")

    lines.extend(["", "## Candidates", ""])

    if not candidates:
        lines.append("No candidates met the current scoring threshold.")
        lines.append("")
        return "\n".join(lines)

    for candidate in sorted(candidates, key=lambda item: item.score, reverse=True):
        lines.append(f"### {candidate.title}")
        lines.append("")
        lines.append(f"- score: `{candidate.score}`")
        for key, value in candidate.body.items():
            if isinstance(value, list):
                rendered = ", ".join(f"`{item}`" for item in value) if value else "[]"
                lines.append(f"- {key}: {rendered}")
            else:
                lines.append(f"- {key}: `{value}`")
        lines.append("")
    return "\n".join(lines)


def extract_candidates(slug: str, force: bool) -> tuple[Path, Path]:
    profile = parse_simple_yaml(WATCH_PROFILE.read_text(encoding="utf-8"))
    source_meta, segments = collect_segments(slug)

    event_candidates: list[Candidate] = []
    claim_candidates: list[Candidate] = []
    for index, segment in enumerate(segments, start=1):
        event_candidate = make_event_candidate(index, slug, segment, profile, source_meta)
        if event_candidate:
            event_candidates.append(event_candidate)
        claim_candidate = make_claim_candidate(index, slug, segment, profile, source_meta)
        if claim_candidate:
            claim_candidates.append(claim_candidate)

    destination = PODCAST_CANDIDATES / slug
    destination.mkdir(parents=True, exist_ok=True)
    event_path = destination / "event-candidates.md"
    claim_path = destination / "claim-candidates.md"
    if (event_path.exists() or claim_path.exists()) and not force:
        raise FileExistsError(f"Candidate files already exist for {slug}; re-run with --force to overwrite.")

    event_path.write_text(
        render_candidates_markdown("event", slug, event_candidates, profile),
        encoding="utf-8",
    )
    claim_path.write_text(
        render_candidates_markdown("claim", slug, claim_candidates, profile),
        encoding="utf-8",
    )
    return event_path, claim_path


def slug_to_product_id(slug: str, text: str) -> str:
    brand_map = {
        "小鹏": "product-xiaopeng",
        "理想": "product-li-auto",
        "小米汽车": "product-xiaomi-auto",
        "Tesla": "product-tesla",
        "OpenAI": "product-openai",
        "Claude Code": "product-claude-code",
        "Gemini": "product-gemini",
    }
    for brand, product_id in brand_map.items():
        if brand.lower() in text.lower():
            return product_id
    return f"product-{slug}"


def infer_episode_product_id(slug: str, source_meta: dict[str, str]) -> str:
    summary = read_markdown_content(PODCAST_ARTIFACTS / slug / "summary.md")
    combined = "\n".join(
        [
            source_meta.get("title", ""),
            source_meta.get("publisher", ""),
            summary,
        ]
    )
    return slug_to_product_id(slug, combined)


def safe_filename(candidate_id: str) -> str:
    return candidate_id.replace("candidate-", "")


def render_event_record(slug: str, product_id: str, candidate: Candidate) -> str:
    body = candidate.body
    what_changed = body["可观察变化"]
    event_id = safe_filename(body["candidate_id"])
    evidence_parts = [body["证据定位"]]
    if body["原文时间戳"] != "unknown":
        evidence_parts.append(f"transcript:{body['原文时间戳']}")
    return "\n".join(
        [
            "# Product Event Card",
            "",
            f"- event_id: `{event_id}`",
            f"- product_id: `{product_id}`",
            f"- title: `{candidate.title}`",
            "- event_type: `podcast_candidate_promoted`",
            f"- date_detected: `{utc_now().split('T')[0]}`",
            "- time_window: `podcast-episode`",
            f"- what_changed: `{what_changed}`",
            f"- change_layer: `{body['变化层']}`",
            f"- affected_capabilities: {render_list_literal(body['受影响能力'])}",
            f"- target_problems: {render_list_literal(body['目标问题'])}",
            f"- evidence_refs: {render_list_literal(evidence_parts)}",
            "- status: `candidate_promoted`",
            "",
            "## 解释",
            "",
            f"- 中文解释: `{what_changed}`",
            f"- 时间戳证据锚点: `{body['原文时间戳']}`",
            f"- 命中主题: {render_list_literal(body['命中主题'])}",
            f"- 命中规则: {render_list_literal(body['命中规则'])}",
            "",
        ]
    )


def render_claim_record(slug: str, product_id: str, candidate: Candidate) -> str:
    body = candidate.body
    claim_id = safe_filename(body["candidate_id"])
    about_objects = sorted(set(body["命中主题"] + [product_id]))
    artifact_refs = [body["证据定位"]]
    if body["原文时间戳"] != "unknown":
        artifact_refs.append(f"transcript:{body['原文时间戳']}")
    related_event_id = claim_id.replace("claim-", "event-", 1) if claim_id.startswith("claim-") else ""
    return "\n".join(
        [
            "# Claim Record",
            "",
            f"- claim_id: `{claim_id}`",
            f"- claim_text: `{body['候选判断']}`",
            f"- about_objects: {render_list_literal(about_objects)}",
            f"- event_refs: {render_list_literal([related_event_id] if related_event_id else [])}",
            f"- artifact_refs: {render_list_literal(artifact_refs)}",
            "- counterevidence_refs: []",
            "- status: `candidate_promoted`",
            f"- confidence: `{score_to_confidence(candidate.score)}`",
            "",
            "## 解释",
            "",
            f"- 机制解释: `{body['机制解释']}`",
            f"- 工作流含义: `{body['工作流含义']}`",
            f"- 类别信号: `{body['类别信号']}`",
            f"- 为什么重要: `{body['为什么重要']}`",
            f"- 缺失证据: `{body['缺失证据']}`",
            f"- 反方观点: `{body['反方观点']}`",
            f"- 时间戳证据锚点: `{body['原文时间戳']}`",
            "",
        ]
    )


def render_list_literal(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(f"`{item}`" for item in items) + "]"


def score_to_confidence(score: int) -> str:
    if score >= 10:
        return "high"
    if score >= 7:
        return "medium"
    return "low"


def build_candidate_maps(slug: str) -> tuple[dict[str, Candidate], dict[str, Candidate]]:
    profile = parse_simple_yaml(WATCH_PROFILE.read_text(encoding="utf-8"))
    source_meta, segments = collect_segments(slug)
    event_map: dict[str, Candidate] = {}
    claim_map: dict[str, Candidate] = {}
    for index, segment in enumerate(segments, start=1):
        event_candidate = make_event_candidate(index, slug, segment, profile, source_meta)
        if event_candidate:
            event_map[event_candidate.body["candidate_id"]] = event_candidate
        claim_candidate = make_claim_candidate(index, slug, segment, profile, source_meta)
        if claim_candidate:
            claim_map[claim_candidate.body["candidate_id"]] = claim_candidate
    return event_map, claim_map


def append_promotion_log(slug: str, promoted_events: list[str], promoted_claims: list[str]) -> Path:
    log_path = PODCAST_CANDIDATES / slug / "promotion-log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else "# Promotion Log\n\n"
    lines = [existing.rstrip(), "", f"## {utc_now()}", ""]
    if promoted_events:
        lines.append(f"- promoted_events: {render_list_literal(promoted_events)}")
    if promoted_claims:
        lines.append(f"- promoted_claims: {render_list_literal(promoted_claims)}")
    lines.append("- mode: `manual`")
    lines.append("")
    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path


def promote_candidates(slug: str, event_ids: list[str], claim_ids: list[str], force: bool) -> list[Path]:
    event_map, claim_map = build_candidate_maps(slug)
    source_meta = read_source_metadata(PODCAST_SOURCES / f"{slug}.md")
    product_id = infer_episode_product_id(slug, source_meta)
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    CLAIMS_DIR.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for candidate_id in event_ids:
        candidate = event_map.get(candidate_id)
        if not candidate:
            raise KeyError(f"Unknown event candidate id: {candidate_id}")
        path = EVENTS_DIR / f"{safe_filename(candidate_id)}.md"
        if path.exists() and not force:
            raise FileExistsError(f"{path.relative_to(ROOT)} already exists; re-run with --force to overwrite.")
        path.write_text(render_event_record(slug, product_id, candidate), encoding="utf-8")
        written.append(path)

    for candidate_id in claim_ids:
        candidate = claim_map.get(candidate_id)
        if not candidate:
            raise KeyError(f"Unknown claim candidate id: {candidate_id}")
        path = CLAIMS_DIR / f"{safe_filename(candidate_id)}.md"
        if path.exists() and not force:
            raise FileExistsError(f"{path.relative_to(ROOT)} already exists; re-run with --force to overwrite.")
        path.write_text(render_claim_record(slug, product_id, candidate), encoding="utf-8")
        written.append(path)

    written.append(append_promotion_log(slug, event_ids, claim_ids))
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate podcast event and claim candidates from imported artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser("extract", help="Extract candidates for one imported episode slug.")
    extract_parser.add_argument("slug", help="Imported podcast slug under library/artifacts/podcasts/")
    extract_parser.add_argument("--force", action="store_true", help="Overwrite existing candidate files.")

    promote_parser = subparsers.add_parser("promote", help="Manually promote selected candidates into durable event/claim records.")
    promote_parser.add_argument("slug", help="Imported podcast slug under library/artifacts/podcasts/")
    promote_parser.add_argument("--event-ids", nargs="*", default=[], help="Event candidate ids to promote.")
    promote_parser.add_argument("--claim-ids", nargs="*", default=[], help="Claim candidate ids to promote.")
    promote_parser.add_argument("--force", action="store_true", help="Overwrite durable records if they already exist.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "extract":
        event_path, claim_path = extract_candidates(args.slug, args.force)
        print(f"wrote {event_path.relative_to(ROOT)}")
        print(f"wrote {claim_path.relative_to(ROOT)}")
        return 0
    if args.command == "promote":
        written = promote_candidates(args.slug, args.event_ids, args.claim_ids, args.force)
        for path in written:
            print(f"wrote {path.relative_to(ROOT)}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
