from __future__ import annotations

import re
from typing import Any


ONTOLOGY_HINTS: dict[str, list[str]] = {
    "capability": ["能力", "capability", "功能边界"],
    "workflow": ["workflow", "工作流", "跨应用", "一步直达", "执行"],
    "governance": ["治理", "权限", "审核", "控制", "责任"],
    "trust": ["信任", "解释", "前台", "可解释"],
    "coordination": ["协作", "角色", "分工", "protocol", "协调"],
    "device_boundary": ["设备", "生态", "robot phone", "人车家", "系统级"],
}

AUTHORITY_SCORES = {
    "official": 3,
    "first_hand_operator": 2,
    "structured_commentary": 1,
    "social_signal": 0,
}


def _text(candidate: dict[str, Any]) -> str:
    return " ".join(str(candidate.get(key, "")) for key in ("title", "summary", "body", "notes")).lower()


def _matches(text: str, items: list[str]) -> list[str]:
    return [item for item in items if item and item.lower() in text]


def _topic_matches(text: str, topic: str, research_direction: str, watch_profile: dict[str, Any]) -> list[str]:
    matches: list[str] = []
    for section in ("domains", "brands", "active_topics"):
        matches.extend(_matches(text, list(watch_profile.get(section, []))))
    if topic and topic.lower() in text:
        matches.append(topic)
    if research_direction:
        for token in re.split(r"[\s，,。；;]+", research_direction):
            if token and token.lower() in text:
                matches.append(token)
    return sorted(set(matches))


def _ontology_matches(text: str) -> list[str]:
    return [name for name, hints in ONTOLOGY_HINTS.items() if any(hint.lower() in text for hint in hints)]


def _authority_level(candidate: dict[str, Any]) -> str:
    return str(candidate.get("authority_level") or candidate.get("authority") or "social_signal")


def _authority_bonus(candidate: dict[str, Any], watch_profile: dict[str, Any]) -> int:
    rules = watch_profile.get("authority_rules", {}) or {}
    bonus = 0

    speaker_role = str(candidate.get("speaker_role") or "").strip()
    if speaker_role:
        bonus += int((rules.get("speaker_roles", {}) or {}).get(speaker_role, 0))

    authority_type = str(candidate.get("authority_rule_type") or candidate.get("source_type") or "").strip()
    if authority_type:
        bonus += int((rules.get("source_types", {}) or {}).get(authority_type, 0))

    preferred_sources = watch_profile.get("preferred_sources", {}) or {}
    channel_name = str(candidate.get("channel_name") or candidate.get("podcast_name") or "").strip()
    if channel_name and channel_name in list(preferred_sources.get("channels", []) or []):
        bonus += int(rules.get("preferred_channel_bonus", 0))

    speaker_name = str(candidate.get("speaker_name") or candidate.get("author") or "").strip()
    if speaker_name and speaker_name in list(preferred_sources.get("speakers", []) or []):
        bonus += int(rules.get("preferred_speaker_bonus", 0))

    return bonus


def _evidence_richness(candidate: dict[str, Any]) -> int:
    score = 0
    if candidate.get("has_transcript"):
        score += 2
    if candidate.get("has_highlights"):
        score += 1
    if candidate.get("has_full_text") or candidate.get("body"):
        score += 1
    return score


def _hype_penalty(text: str, watch_profile: dict[str, Any]) -> tuple[int, list[str]]:
    phrases = list(watch_profile.get("candidate_rules", {}).get("downgrade_if_contains", []))
    reasons = [phrase for phrase in phrases if phrase and phrase.lower() in text]
    return len(reasons), reasons


def score_candidate(
    candidate: dict[str, Any],
    *,
    topic: str,
    research_direction: str,
    watch_profile: dict[str, Any],
) -> dict[str, Any]:
    text = _text(candidate)
    topic_matches = _topic_matches(text, topic, research_direction, watch_profile)
    ontology_matches = _ontology_matches(text)
    authority_level = _authority_level(candidate)
    authority_score = AUTHORITY_SCORES.get(authority_level, 0) + _authority_bonus(candidate, watch_profile)
    evidence_richness = _evidence_richness(candidate)
    hype_penalty, downgrade_reasons = _hype_penalty(text, watch_profile)

    relevance_score = len(topic_matches) + len(ontology_matches) + authority_score + evidence_richness - hype_penalty

    return {
        **candidate,
        "relevance_score": relevance_score,
        "topic_matches": topic_matches,
        "ontology_matches": ontology_matches,
        "authority_level": authority_level,
        "authority_score": authority_score,
        "evidence_richness": evidence_richness,
        "hype_penalty": hype_penalty,
        "downgrade_reasons": downgrade_reasons,
    }


def balance_candidates(candidates: list[dict[str, Any]], *, comparative: bool) -> list[dict[str, Any]]:
    ordered = sorted(candidates, key=lambda item: item.get("relevance_score", 0), reverse=True)
    if not comparative:
        return ordered

    unique_brands = {str(item.get("brand") or "unknown").strip().lower() for item in ordered}

    selected: list[dict[str, Any]] = []
    brand_counts: dict[str, int] = {}
    platform_seen: set[str] = set()
    source_type_seen: set[str] = set()
    authority_seen: set[str] = set()

    for candidate in ordered:
        brand = str(candidate.get("brand") or "unknown")
        brand_key = brand.strip().lower()
        platform = str(candidate.get("platform") or "unknown").strip().lower()
        source_type = str(candidate.get("source_type") or "unknown").strip().lower()
        authority = str(candidate.get("authority_level") or "social_signal").strip().lower()
        if len(unique_brands) >= 3 and brand_counts.get(brand_key, 0) >= 2:
            continue
        selected.append(candidate)
        brand_counts[brand_key] = brand_counts.get(brand_key, 0) + 1
        platform_seen.add(platform)
        source_type_seen.add(source_type)
        authority_seen.add(authority)

    if len(selected) < min(len(ordered), 3):
        return ordered
    if len(platform_seen) < 2 and len(ordered) >= 3:
        return ordered
    if len(source_type_seen) < 2 and len({str(item.get("source_type") or "unknown").strip().lower() for item in ordered}) >= 2:
        return ordered
    if len(authority_seen) < 2 and len({str(item.get("authority_level") or "social_signal").strip().lower() for item in ordered}) >= 2:
        return ordered
    return selected
