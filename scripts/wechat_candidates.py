#!/usr/bin/env python3
"""Generate and promote WeChat candidates from imported article artifacts."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

import podcast_candidates as pc
from podcast_candidates import (
    Candidate,
    ROOT,
    Segment,
    WATCH_PROFILE,
    make_claim_candidate,
    make_event_candidate,
    parse_simple_yaml,
    read_markdown_content,
    read_source_metadata,
)


SOURCES_DIR = ROOT / "library" / "sources" / "wechat"
ARTIFACTS_DIR = ROOT / "library" / "artifacts" / "wechat"
SESSIONS_DIR = ROOT / "library" / "sessions" / "candidates" / "wechat"
EVENTS_DIR = ROOT / "library" / "events" / "wechat"
CLAIMS_DIR = ROOT / "library" / "claims" / "wechat"


for keyword in ["Agent", "智能体", "工作流", "模型", "自动驾驶", "OTA", "更新", "助手", "Claude", "OpenAI", "Gemini"]:
    if keyword not in pc.CAPABILITY_KEYWORDS:
        pc.CAPABILITY_KEYWORDS.append(keyword)

for keyword in ["工作流", "编排", "协作", "更新", "上线", "接入", "调用", "升级", "发布", "适配"]:
    if keyword not in pc.CHANGE_LAYER_KEYWORDS["workflow"]:
        pc.CHANGE_LAYER_KEYWORDS["workflow"].append(keyword)

for keyword in ["智能体", "AgentOS", "座舱", "OTA", "大模型", "驾驶", "编排", "助手"]:
    if keyword not in pc.CHANGE_LAYER_KEYWORDS["capability"]:
        pc.CHANGE_LAYER_KEYWORDS["capability"].append(keyword)

for keyword in ["信任", "透明", "稳定性", "效率", "成本", "安全"]:
    if keyword not in pc.PROBLEM_KEYWORDS:
        pc.PROBLEM_KEYWORDS.append(keyword)


def split_full_text_segments(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    parts = re.split(r"(?<=[。！？!?])\s*", normalized)
    segments = [part.strip() for part in parts if part.strip()]
    return [segment for segment in segments if len(segment) >= 8]


def render_candidates_markdown(kind: str, slug: str, candidates: list[Candidate], profile: dict[str, Any]) -> str:
    title = "Event Candidates" if kind == "event" else "Claim Candidates"
    lines = [
        f"# {title}",
        "",
        f"- wechat_slug: `{slug}`",
        f"- watch_profile: `{WATCH_PROFILE.relative_to(ROOT)}`",
        f"- extraction_inputs: `full_text`",
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


def collect_segments(slug: str) -> tuple[dict[str, str], list[Segment]]:
    source_meta = read_source_metadata(SOURCES_DIR / f"{slug}.md")
    full_text = read_markdown_content(ARTIFACTS_DIR / slug / "full_text.md")
    segments = [
        Segment("full_text.md", sentence, f"sentence-{index}", None)
        for index, sentence in enumerate(split_full_text_segments(full_text), start=1)
    ]
    return source_meta, segments


def extract_candidates(slug: str, force: bool) -> tuple[Path, Path]:
    profile = parse_simple_yaml(WATCH_PROFILE.read_text(encoding="utf-8"))
    candidate_rules = profile.setdefault("candidate_rules", {})
    candidate_rules["min_event_score"] = min(int(candidate_rules.get("min_event_score", 4)), 3)
    candidate_rules["min_claim_score"] = min(int(candidate_rules.get("min_claim_score", 5)), 4)
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

    destination = SESSIONS_DIR / slug
    destination.mkdir(parents=True, exist_ok=True)
    event_path = destination / "event-candidates.md"
    claim_path = destination / "claim-candidates.md"
    if (event_path.exists() or claim_path.exists()) and not force:
        raise FileExistsError(f"Candidate files already exist for {slug}; re-run with --force to overwrite.")
    event_path.write_text(render_candidates_markdown("event", slug, event_candidates, profile), encoding="utf-8")
    claim_path.write_text(render_candidates_markdown("claim", slug, claim_candidates, profile), encoding="utf-8")
    return event_path, claim_path


def render_list_literal(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + ", ".join(f"`{item}`" for item in items) + "]"


def safe_filename(candidate_id: str) -> str:
    return candidate_id.replace("candidate-", "")


def infer_product_id(slug: str, source_meta: dict[str, str]) -> str:
    text = "\n".join(
        [
            source_meta.get("title", ""),
            source_meta.get("publisher", ""),
            read_markdown_content(ARTIFACTS_DIR / slug / "full_text.md"),
        ]
    )
    brand_map = {
        "OpenAI": "product-openai",
        "Claude": "product-claude-code",
        "Anthropic": "product-anthropic",
        "Gemini": "product-gemini",
        "小鹏": "product-xiaopeng",
        "理想": "product-li-auto",
        "小米汽车": "product-xiaomi-auto",
    }
    for brand, product_id in brand_map.items():
        if brand.lower() in text.lower():
            return product_id
    return f"product-{slug}"


def score_to_confidence(score: int) -> str:
    if score >= 10:
        return "high"
    if score >= 7:
        return "medium"
    return "low"


def render_event_record(product_id: str, candidate: Candidate) -> str:
    body = candidate.body
    event_id = safe_filename(body["candidate_id"])
    return "\n".join(
        [
            "# Product Event Card",
            "",
            f"- event_id: `{event_id}`",
            f"- product_id: `{product_id}`",
            f"- title: `{candidate.title}`",
            "- event_type: `wechat_candidate_promoted`",
            f"- date_detected: `{pc.utc_now().split('T')[0]}`",
            "- time_window: `wechat-article`",
            f"- what_changed: `{body['可观察变化']}`",
            f"- change_layer: `{body['变化层']}`",
            f"- affected_capabilities: {render_list_literal(body['受影响能力'])}",
            f"- target_problems: {render_list_literal(body['目标问题'])}",
            f"- evidence_refs: {render_list_literal([body['证据定位']])}",
            "- status: `candidate_promoted`",
            "",
            "## 解释",
            "",
            f"- 中文解释: `{body['可观察变化']}`",
            f"- 命中主题: {render_list_literal(body['命中主题'])}",
            f"- 命中规则: {render_list_literal(body['命中规则'])}",
            "",
        ]
    )


def render_claim_record(product_id: str, candidate: Candidate) -> str:
    body = candidate.body
    claim_id = safe_filename(body["candidate_id"])
    related_event = claim_id.replace("claim-", "event-", 1) if claim_id.startswith("claim-") else ""
    about_objects = sorted(set(body["命中主题"] + [product_id]))
    return "\n".join(
        [
            "# Claim Record",
            "",
            f"- claim_id: `{claim_id}`",
            f"- claim_text: `{body['候选判断']}`",
            f"- about_objects: {render_list_literal(about_objects)}",
            f"- event_refs: {render_list_literal([related_event] if related_event else [])}",
            f"- artifact_refs: {render_list_literal([body['证据定位']])}",
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
            "",
        ]
    )


def build_candidate_maps(slug: str) -> tuple[dict[str, Candidate], dict[str, Candidate], dict[str, str]]:
    profile = parse_simple_yaml(WATCH_PROFILE.read_text(encoding="utf-8"))
    candidate_rules = profile.setdefault("candidate_rules", {})
    candidate_rules["min_event_score"] = min(int(candidate_rules.get("min_event_score", 4)), 3)
    candidate_rules["min_claim_score"] = min(int(candidate_rules.get("min_claim_score", 5)), 4)
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
    return event_map, claim_map, source_meta


def append_promotion_log(slug: str, event_ids: list[str], claim_ids: list[str]) -> Path:
    log_path = SESSIONS_DIR / slug / "promotion-log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else "# Promotion Log\n\n"
    lines = [existing.rstrip(), "", f"## {pc.utc_now()}", ""]
    if event_ids:
        lines.append(f"- promoted_events: {render_list_literal(event_ids)}")
    if claim_ids:
        lines.append(f"- promoted_claims: {render_list_literal(claim_ids)}")
    lines.append("- mode: `manual`")
    lines.append("")
    log_path.write_text("\n".join(lines), encoding="utf-8")
    return log_path


def promote_candidates(slug: str, event_ids: list[str], claim_ids: list[str], force: bool) -> list[Path]:
    event_map, claim_map, source_meta = build_candidate_maps(slug)
    product_id = infer_product_id(slug, source_meta)
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
        path.write_text(render_event_record(product_id, candidate), encoding="utf-8")
        written.append(path)
    for candidate_id in claim_ids:
        candidate = claim_map.get(candidate_id)
        if not candidate:
            raise KeyError(f"Unknown claim candidate id: {candidate_id}")
        path = CLAIMS_DIR / f"{safe_filename(candidate_id)}.md"
        if path.exists() and not force:
            raise FileExistsError(f"{path.relative_to(ROOT)} already exists; re-run with --force to overwrite.")
        path.write_text(render_claim_record(product_id, candidate), encoding="utf-8")
        written.append(path)
    written.append(append_promotion_log(slug, event_ids, claim_ids))
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate and promote WeChat candidates from imported article artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    extract_parser = subparsers.add_parser("extract", help="Extract candidates for one imported WeChat slug.")
    extract_parser.add_argument("slug", help="Imported WeChat slug under library/artifacts/wechat/")
    extract_parser.add_argument("--force", action="store_true", help="Overwrite existing candidate files.")
    promote_parser = subparsers.add_parser("promote", help="Manually promote WeChat event/claim candidates into durable records.")
    promote_parser.add_argument("slug", help="Imported WeChat slug under library/artifacts/wechat/")
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
