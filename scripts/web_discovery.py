from __future__ import annotations

from pathlib import Path
from typing import Any


def normalize_source_candidate(
    *,
    title: str,
    url: str,
    source_type: str,
    platform: str,
    authority: str,
    why_relevant: str,
) -> dict[str, str]:
    return {
        "title": title.strip(),
        "url": url.strip(),
        "source_type": source_type.strip(),
        "platform": platform.strip(),
        "authority": authority.strip(),
        "why_relevant": why_relevant.strip(),
    }


def render_discovery_record(
    *,
    request_id: str,
    mode: str,
    topic: str,
    candidates: list[dict[str, str]],
) -> str:
    grouped: dict[str, list[dict[str, str]]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate["authority"], []).append(candidate)

    title_map = {
        "official": "Official",
        "first_hand_operator": "First-Hand Operator",
        "structured_commentary": "Structured Commentary",
        "social_signal": "Social Signal",
    }

    sections: list[str] = [
        "# Web Discovery Record",
        "",
        f"- request_id: `{request_id}`",
        f"- mode: `{mode}`",
        f"- topic: `{topic}`",
        "",
    ]
    for authority in ["official", "first_hand_operator", "structured_commentary", "social_signal"]:
        items = grouped.get(authority, [])
        if not items:
            continue
        sections.extend([f"## {title_map[authority]}", ""])
        for item in items:
            sections.extend(
                [
                    f"- [{item['title']}]({item['url']})",
                    f"  - source_type: `{item['source_type']}`",
                    f"  - platform: `{item['platform']}`",
                    f"  - why_relevant: {item['why_relevant']}",
                ]
            )
        sections.append("")
    return "\n".join(sections)


def load_discovery_topics(path: str | Path = "seed/discovery-topics.yaml") -> dict[str, list[str]]:
    data: dict[str, list[str]] = {"domains": [], "brands": [], "preferred_source_types": []}
    current_key: str | None = None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.endswith(":") and not stripped.startswith("-"):
            key = stripped[:-1]
            if key in data:
                current_key = key
            continue
        if stripped.startswith("- ") and current_key is not None:
            data[current_key].append(stripped[2:].strip())
    return data


def build_seeded_discovery_candidates(topic: str, seed_path: str | Path = "seed/discovery-topics.yaml") -> list[dict[str, Any]]:
    seeded = load_discovery_topics(seed_path)
    candidates: list[dict[str, Any]] = []
    for domain in seeded["domains"]:
        candidates.append(
            {
                "title": domain,
                "url": f"https://{domain}",
                "source_type": "structured_commentary",
                "platform": "web",
                "authority": "structured_commentary",
                "why_relevant": f"Bootstrap source candidate for {topic}.",
            }
        )
    return candidates


def _slugify(value: str) -> str:
    normalized = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    normalized = "-".join(part for part in normalized.split("-") if part)
    return normalized or "bundle"


def build_discovery_candidates(topic: str, mode: str, brands: list[str]) -> list[dict[str, str]]:
    normalized_brands = [brand.strip() for brand in brands if brand.strip()]
    candidates: list[dict[str, str]] = []
    topic_slug = _slugify(topic)

    if mode == "official-update":
        titles = normalized_brands or [topic]
        for title in titles:
            candidates.append(
                normalize_source_candidate(
                    title=f"{title} Official Update",
                    url=f"manual://official/{_slugify(title)}",
                    source_type="official_update",
                    platform="official_site",
                    authority="official",
                    why_relevant=f"Official update candidate for {title} in topic {topic}.",
                )
            )
        return candidates

    if mode == "research-guided-collection":
        titles = normalized_brands or [topic]
        for title in titles:
            candidates.append(
                normalize_source_candidate(
                    title=f"{title} Structured Commentary",
                    url=f"manual://research/{_slugify(title)}",
                    source_type="structured_commentary",
                    platform="web",
                    authority="structured_commentary",
                    why_relevant=f"Research-guided commentary candidate for {title} in topic {topic}.",
                )
            )
        if not candidates:
            candidates.append(
                normalize_source_candidate(
                    title=f"{topic} Social Signal",
                    url=f"manual://social/{topic_slug}",
                    source_type="social_signal",
                    platform="web",
                    authority="social_signal",
                    why_relevant=f"Social signal candidate for topic {topic}.",
                )
            )
        return candidates

    candidates.append(
        normalize_source_candidate(
            title=f"{topic} Structured Commentary",
            url=f"manual://discovery/{topic_slug}",
            source_type="structured_commentary",
            platform="web",
            authority="structured_commentary",
            why_relevant=f"Discovery candidate for topic {topic}.",
        )
    )
    for brand in normalized_brands:
        candidates.append(
            normalize_source_candidate(
                title=f"{brand} Social Signal",
                url=f"manual://social/{_slugify(brand)}",
                source_type="social_signal",
                platform="web",
                authority="social_signal",
                why_relevant=f"Discovery signal around {brand} for topic {topic}.",
            )
        )
    return candidates
