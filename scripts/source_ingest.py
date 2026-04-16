#!/usr/bin/env python3
"""Shared ingestion skeleton for normalized multi-source records."""

from __future__ import annotations

import argparse
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SOURCES_ROOT = ROOT / "library" / "sources"
ARTIFACTS_ROOT = ROOT / "library" / "artifacts"

CHANNELS = {"podcasts", "wechat", "xiaohongshu", "official"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-") or "source"
    normalized = normalized[:48].strip("-") or "source"
    return f"{normalized}-{digest}"


def guess_publisher(url: str) -> str:
    return re.sub(r"^www\.", "", urlparse(url).netloc.lower()) or "unknown"


def render_source_markdown(
    *,
    source_id: str,
    source_type: str,
    platform: str,
    source_container: str,
    publisher: str,
    author_or_speaker: str,
    published_at: str,
    title: str,
    url_or_ref: str,
    source_url: str,
    canonical_url: str,
    perspective: str,
    confidence: str,
    ingestion_method: str,
    notes: list[str],
) -> str:
    lines = [
        "# Source Record",
        "",
        f"- source_id: `{source_id}`",
        f"- source_type: `{source_type}`",
        f"- platform: `{platform}`",
        f"- source_container: `{source_container}`",
        f"- publisher: `{publisher}`",
        f"- author_or_speaker: `{author_or_speaker}`",
        f"- published_at: `{published_at}`",
        f"- title: `{title}`",
        f"- url_or_ref: `{url_or_ref}`",
        f"- source_url: `{source_url}`",
        f"- canonical_url: `{canonical_url}`",
        f"- perspective: `{perspective}`",
        f"- confidence: `{confidence}`",
        f"- ingestion_method: `{ingestion_method}`",
        "",
        "## Import Metadata",
        "",
        f"- imported_at: `{utc_now()}`",
        "- dedupe_key: `source_url`",
        "",
        "## Notes",
        "",
    ]
    for note in notes:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def render_artifact_markdown(
    *,
    artifact_id: str,
    source_id: str,
    slice_type: str,
    location: str,
    perspective: str,
    why_relevant: str,
    source_url: str,
    body: str,
) -> str:
    return "\n".join(
        [
            "# Artifact Record",
            "",
            f"- artifact_id: `{artifact_id}`",
            f"- source_id: `{source_id}`",
            f"- slice_type: `{slice_type}`",
            f"- quote_or_segment: `{slice_type}`",
            f"- location: `{location}`",
            f"- perspective: `{perspective}`",
            f"- why_relevant: `{why_relevant}`",
            "",
            "## Import Metadata",
            "",
            f"- imported_at: `{utc_now()}`",
            f"- source_url: `{source_url}`",
            "",
            "## Content",
            "",
            body.strip(),
            "",
        ]
    )


def write_source_record(
    *,
    channel: str,
    source_label: str,
    url: str,
    source_type: str,
    ingestion_method: str,
    publisher: str | None = None,
    author_or_speaker: str = "unknown",
    published_at: str = "unknown",
    title: str | None = None,
    canonical_url: str | None = None,
    perspective: str = "unknown",
    confidence: str = "medium",
    notes: list[str] | None = None,
) -> tuple[str, Path, Path]:
    if channel not in CHANNELS:
        raise ValueError(f"Unsupported channel: {channel}")
    slug = slugify(url or source_label)
    source_id = f"source-{channel}-{slug}"
    source_path = SOURCES_ROOT / channel / f"{slug}.md"
    artifact_dir = ARTIFACTS_ROOT / channel / slug
    source_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    source_path.write_text(
        render_source_markdown(
            source_id=source_id,
            source_type=source_type,
            platform=channel,
            source_container=source_label,
            publisher=publisher or (guess_publisher(url) if url else source_label),
            author_or_speaker=author_or_speaker,
            published_at=published_at,
            title=title or source_label,
            url_or_ref=url or source_label,
            source_url=url or source_label,
            canonical_url=canonical_url or url or source_label,
            perspective=perspective,
            confidence=confidence,
            ingestion_method=ingestion_method,
            notes=notes or ["This record was initialized by the shared ingestion skeleton."],
        ),
        encoding="utf-8",
    )
    return source_id, source_path, artifact_dir


def write_artifact_record(
    *,
    channel: str,
    source_label: str,
    source_url: str,
    slice_type: str,
    location: str,
    perspective: str,
    why_relevant: str,
    body: str,
) -> Path:
    slug = slugify(source_url or source_label)
    source_id = f"source-{channel}-{slug}"
    artifact_dir = ARTIFACTS_ROOT / channel / slug
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / f"{slice_type}.md"
    artifact_path.write_text(
        render_artifact_markdown(
            artifact_id=f"artifact-{slice_type}-{slug}",
            source_id=source_id,
            slice_type=slice_type,
            location=location,
            perspective=perspective,
            why_relevant=why_relevant,
            source_url=source_url or source_label,
            body=body,
        ),
        encoding="utf-8",
    )
    return artifact_path


def init_record(channel: str, source_label: str, url: str, source_type: str, ingestion_method: str) -> tuple[str, Path, Path]:
    return write_source_record(
        channel=channel,
        source_label=source_label,
        url=url,
        source_type=source_type,
        ingestion_method=ingestion_method,
    )


def command_init_source(args: argparse.Namespace) -> int:
    source_id, source_path, artifact_dir = init_record(
        channel=args.channel,
        source_label=args.source_label,
        url=args.url,
        source_type=args.source_type,
        ingestion_method=args.ingestion_method,
    )
    print(f"initialized {source_id}")
    print(source_path.relative_to(ROOT))
    print(artifact_dir.relative_to(ROOT))
    return 0


def command_add_artifact(args: argparse.Namespace) -> int:
    artifact_path = write_artifact_record(
        channel=args.channel,
        source_label=args.source_label,
        source_url=args.source_url,
        slice_type=args.slice_type,
        location=args.location,
        perspective=args.perspective,
        why_relevant=args.why_relevant,
        body=args.body,
    )
    print(f"wrote {artifact_path.relative_to(ROOT)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Shared skeleton for multi-source ingestion.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-source", help="Initialize a normalized source record for a channel.")
    init_parser.add_argument("channel", choices=sorted(CHANNELS))
    init_parser.add_argument("source_label")
    init_parser.add_argument("--url", default="")
    init_parser.add_argument("--source-type", required=True)
    init_parser.add_argument("--ingestion-method", required=True)

    artifact_parser = subparsers.add_parser("add-artifact", help="Add a normalized artifact record under a channel source slug.")
    artifact_parser.add_argument("channel", choices=sorted(CHANNELS))
    artifact_parser.add_argument("source_label")
    artifact_parser.add_argument("--source-url", default="")
    artifact_parser.add_argument("--slice-type", required=True)
    artifact_parser.add_argument("--location", default="full_text")
    artifact_parser.add_argument("--perspective", default="unknown")
    artifact_parser.add_argument("--why-relevant", default="Stores imported content for later candidate extraction.")
    artifact_parser.add_argument("--body", required=True)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "init-source":
        return command_init_source(args)
    if args.command == "add-artifact":
        return command_add_artifact(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
