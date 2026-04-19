#!/usr/bin/env python3
"""Import podcast episode materials via podwise into source/artifact records."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SEED_FILE = ROOT / "seed" / "podcast-import-list.md"
SOURCES_DIR = ROOT / "library" / "sources" / "podcasts"
ARTIFACTS_DIR = ROOT / "library" / "artifacts" / "podcasts"

URL_PATTERN = re.compile(r"https?://[^\s)>\]]+")
PROCESSING_PENDING_NEEDLE = "episode has not been processed yet"
PODWISE_GET_RETRIES = 12
PODWISE_RETRY_DELAY_SECONDS = 5


@dataclass(frozen=True)
class EpisodeRecord:
    source_url: str
    slug: str
    source_id: str
    source_path: Path
    artifact_dir: Path


def extract_urls(text: str) -> list[str]:
    seen: set[str] = set()
    urls: list[str] = []
    for match in URL_PATTERN.findall(text):
        cleaned = match.rstrip(".,)")
        if cleaned not in seen:
            seen.add(cleaned)
            urls.append(cleaned)
    return urls


def load_seed_urls() -> list[str]:
    if not SEED_FILE.exists():
        return []
    return extract_urls(SEED_FILE.read_text(encoding="utf-8"))


def append_urls_to_seed(urls: Iterable[str]) -> int:
    existing = load_seed_urls()
    existing_set = set(existing)
    additions = [url for url in urls if url not in existing_set]
    if not additions:
        return 0

    if not SEED_FILE.exists():
        SEED_FILE.parent.mkdir(parents=True, exist_ok=True)
        SEED_FILE.write_text(
            "# Podcast Import List\n\n## Queue\n",
            encoding="utf-8",
        )

    with SEED_FILE.open("a", encoding="utf-8") as handle:
        for url in additions:
            handle.write(f"- {url}\n")
    return len(additions)


def slugify_source_url(source_url: str) -> str:
    parsed = urlparse(source_url)
    host = re.sub(r"^www\.", "", parsed.netloc.lower())
    host = re.sub(r"[^a-z0-9]+", "-", host).strip("-") or "source"

    path_parts = [part for part in parsed.path.split("/") if part]
    tail = path_parts[-1] if path_parts else "episode"
    if tail == "watch" and parsed.query:
        query_match = re.search(r"(?:^|&)v=([^&]+)", parsed.query)
        if query_match:
            tail = query_match.group(1)
    tail = re.sub(r"[^a-zA-Z0-9]+", "-", tail).strip("-").lower() or "episode"

    digest = hashlib.sha1(source_url.encode("utf-8")).hexdigest()[:8]
    return f"{host}-{tail}-{digest}"


def build_episode_record(source_url: str) -> EpisodeRecord:
    slug = slugify_source_url(source_url)
    source_id = f"source-podcast-{slug}"
    return EpisodeRecord(
        source_url=source_url,
        slug=slug,
        source_id=source_id,
        source_path=SOURCES_DIR / f"{slug}.md",
        artifact_dir=ARTIFACTS_DIR / slug,
    )


def run_podwise(args: list[str]) -> str:
    cmd = ["podwise", *args]
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def run_podwise_get_when_ready(args: list[str]) -> str:
    for attempt in range(PODWISE_GET_RETRIES):
        try:
            return run_podwise(args)
        except subprocess.CalledProcessError as error:
            stderr = (error.stderr or "").lower()
            if PROCESSING_PENDING_NEEDLE not in stderr or attempt == PODWISE_GET_RETRIES - 1:
                raise
            time.sleep(PODWISE_RETRY_DELAY_SECONDS)
    raise RuntimeError("unreachable")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def guess_publisher(source_url: str) -> str:
    host = urlparse(source_url).netloc.lower()
    return re.sub(r"^www\.", "", host) or "unknown"


def guess_title_from_slug(slug: str) -> str:
    title = slug.rsplit("-", 1)[0]
    title = title.replace("-", " ").strip()
    return title or slug


def render_source_markdown(record: EpisodeRecord, imported_at: str) -> str:
    title = guess_title_from_slug(record.slug)
    publisher = guess_publisher(record.source_url)
    return "\n".join(
        [
            "# Source Record",
            "",
            f"- source_id: `{record.source_id}`",
            "- source_type: `podcast_episode`",
            "- platform: `podwise`",
            "- source_container: `podwise`",
            f"- publisher: `{publisher}`",
            "- author_or_speaker: `unknown`",
            "- published_at: `unknown`",
            f"- title: `{title}`",
            f"- url_or_ref: `{record.source_url}`",
            f"- source_url: `{record.source_url}`",
            f"- canonical_url: `{record.source_url}`",
            "- perspective: `podcast_host_or_guest`",
            "- confidence: `medium`",
            "- ingestion_method: `podwise_cli`",
            "",
            "## Import Metadata",
            "",
            f"- imported_at: `{imported_at}`",
            "- importer: `scripts/podcast_import.py`",
            "- dedupe_key: `source_url`",
            "",
            "## Notes",
            "",
            "- Metadata is sourced from the import URL and can be refined later.",
            "- Transcript, summary, and highlights are stored as separate artifacts.",
            "",
        ]
    )


def render_artifact_markdown(
    *,
    record: EpisodeRecord,
    artifact_kind: str,
    imported_at: str,
    body: str,
) -> str:
    artifact_id = f"artifact-{artifact_kind}-{record.slug}"
    headline = {
        "transcript": "Full transcript generated by Podwise for this episode.",
        "summary": "Episode summary generated by Podwise.",
        "highlights": "Episode highlights generated by Podwise.",
    }[artifact_kind]
    location = {
        "transcript": "full_episode",
        "summary": "summary",
        "highlights": "highlights",
    }[artifact_kind]

    return "\n".join(
        [
            "# Artifact Record",
            "",
            f"- artifact_id: `{artifact_id}`",
            f"- source_id: `{record.source_id}`",
            f"- slice_type: `{artifact_kind}`",
            f"- quote_or_segment: `{headline}`",
            f"- location: `{location}`",
            "- perspective: `podwise_generated`",
            f"- why_relevant: `Stores the imported {artifact_kind} for later event and claim extraction.`",
            "",
            "## Import Metadata",
            "",
            f"- imported_at: `{imported_at}`",
            f"- source_url: `{record.source_url}`",
            "",
            "## Content",
            "",
            body.strip(),
            "",
        ]
    )


def import_episode(source_url: str, *, force: bool = False) -> str:
    record = build_episode_record(source_url)
    if record.source_path.exists() and not force:
        return record.slug

    imported_at = utc_now()
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    record.artifact_dir.mkdir(parents=True, exist_ok=True)

    run_podwise(["process", source_url])
    transcript = run_podwise_get_when_ready(["get", "transcript", source_url])
    summary = run_podwise_get_when_ready(["get", "summary", source_url])
    highlights = run_podwise_get_when_ready(["get", "highlights", source_url])

    record.source_path.write_text(
        render_source_markdown(record, imported_at),
        encoding="utf-8",
    )
    (record.artifact_dir / "transcript.md").write_text(
        render_artifact_markdown(
            record=record,
            artifact_kind="transcript",
            imported_at=imported_at,
            body=transcript,
        ),
        encoding="utf-8",
    )
    (record.artifact_dir / "summary.md").write_text(
        render_artifact_markdown(
            record=record,
            artifact_kind="summary",
            imported_at=imported_at,
            body=summary,
        ),
        encoding="utf-8",
    )
    (record.artifact_dir / "highlights.md").write_text(
        render_artifact_markdown(
            record=record,
            artifact_kind="highlights",
            imported_at=imported_at,
            body=highlights,
        ),
        encoding="utf-8",
    )
    return record.slug


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import podcast episode materials from podwise into source and artifact records.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add-url", help="Append one or more URLs to the Markdown import list.")
    add_parser.add_argument("urls", nargs="+", help="Episode URLs to add to the import list.")

    import_parser = subparsers.add_parser("import-list", help="Import every URL from the Markdown import list.")
    import_parser.add_argument(
        "--force",
        action="store_true",
        help="Re-import URLs even when a source record already exists.",
    )

    return parser.parse_args()


def command_add_url(urls: list[str]) -> int:
    invalid = [url for url in urls if not URL_PATTERN.fullmatch(url)]
    if invalid:
        print("invalid URLs:", ", ".join(invalid), file=sys.stderr)
        return 1
    added = append_urls_to_seed(urls)
    print(f"added {added} url(s) to {SEED_FILE.relative_to(ROOT)}")
    return 0


def command_import_list(force: bool) -> int:
    urls = load_seed_urls()
    if not urls:
        print(f"no URLs found in {SEED_FILE.relative_to(ROOT)}", file=sys.stderr)
        return 1

    failures = 0
    for url in urls:
        try:
            print(import_episode(url, force=force))
        except subprocess.CalledProcessError as exc:
            failures += 1
            stderr = exc.stderr.strip() if exc.stderr else str(exc)
            print(f"error {url}: {stderr}", file=sys.stderr)
        except Exception as exc:  # pragma: no cover - defensive guard for CLI runs
            failures += 1
            print(f"error {url}: {exc}", file=sys.stderr)

    return 1 if failures else 0


def main() -> int:
    args = parse_args()
    if args.command == "add-url":
        return command_add_url(args.urls)
    if args.command == "import-list":
        return command_import_list(args.force)
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
