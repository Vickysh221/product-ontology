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
