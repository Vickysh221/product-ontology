#!/usr/bin/env python3
"""Queue and import transcript artifacts for Xiaohongshu video sources."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from source_ingest import ROOT, slugify, write_artifact_record


SOURCES_DIR = ROOT / "library" / "sources" / "xiaohongshu"
ARTIFACTS_DIR = ROOT / "library" / "artifacts" / "xiaohongshu"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def find_source_file(note_url: str) -> Path:
    slug = slugify(note_url)
    path = SOURCES_DIR / f"{slug}.md"
    if not path.exists():
        raise FileNotFoundError(f"No Xiaohongshu source found for {note_url}")
    return path


def read_source_metadata(path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- ") and ": `" in line and line.endswith("`"):
            key, value = line[2:].split(": `", 1)
            metadata[key.strip()] = value[:-1]
    return metadata


def transcript_request_path(note_url: str) -> Path:
    slug = slugify(note_url)
    return ARTIFACTS_DIR / slug / "transcript-request.md"


def queue_request(args: argparse.Namespace) -> int:
    source_path = find_source_file(args.note_url)
    meta = read_source_metadata(source_path)
    request_path = transcript_request_path(args.note_url)
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(
        "\n".join(
            [
                "# Transcript Request",
                "",
                f"- source_id: `{meta.get('source_id', 'unknown')}`",
                f"- source_url: `{args.note_url}`",
                f"- canonical_url: `{meta.get('canonical_url', args.note_url)}`",
                f"- title: `{meta.get('title', 'unknown')}`",
                f"- author_or_speaker: `{meta.get('author_or_speaker', 'unknown')}`",
                "- channel: `xiaohongshu`",
                "- artifact_type: `transcript`",
                "- transcript_status: `pending`",
                f"- requested_at: `{utc_now()}`",
                f"- requested_by: `{args.requested_by}`",
                f"- preferred_asr_tool: `{args.preferred_asr_tool}`",
                f"- notes: `{args.notes}`",
                "",
                "## Context",
                "",
                "- This request reserves a transcript artifact slot for later ASR import.",
                "- The final transcript can come from any ASR tool and should be imported with `import-transcript`.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"wrote {request_path.relative_to(ROOT)}")
    return 0


def import_transcript(args: argparse.Namespace) -> int:
    source_path = find_source_file(args.note_url)
    meta = read_source_metadata(source_path)
    body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else args.body
    if not body.strip():
        raise ValueError("Transcript body is required.")

    artifact_path = write_artifact_record(
        channel="xiaohongshu",
        source_label=meta.get("source_container", "xiaohongshu-video"),
        source_url=args.note_url,
        slice_type="transcript",
        location="video_transcript",
        perspective="asr_transcript",
        why_relevant="Stores the imported transcript for a Xiaohongshu video source.",
        body=body,
    )

    request_path = transcript_request_path(args.note_url)
    if request_path.exists():
        request_path.write_text(
            "\n".join(
                [
                    "# Transcript Request",
                    "",
                    f"- source_id: `{meta.get('source_id', 'unknown')}`",
                    f"- source_url: `{args.note_url}`",
                    f"- canonical_url: `{meta.get('canonical_url', args.note_url)}`",
                    f"- title: `{meta.get('title', 'unknown')}`",
                    f"- author_or_speaker: `{meta.get('author_or_speaker', 'unknown')}`",
                    "- channel: `xiaohongshu`",
                    "- artifact_type: `transcript`",
                    "- transcript_status: `imported`",
                    f"- requested_at: `see git history`",
                    f"- imported_at: `{utc_now()}`",
                    f"- imported_by: `{args.imported_by}`",
                    f"- asr_tool: `{args.asr_tool}`",
                    f"- transcript_artifact: `{artifact_path.relative_to(ROOT)}`",
                    "",
                    "## Context",
                    "",
                    "- Transcript has been imported into the artifact directory.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    print(f"wrote {artifact_path.relative_to(ROOT)}")
    if request_path.exists():
        print(f"updated {request_path.relative_to(ROOT)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Queue and import transcript artifacts for Xiaohongshu video sources.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    queue_parser = subparsers.add_parser("queue", help="Create a transcript request file for a Xiaohongshu video source.")
    queue_parser.add_argument("note_url")
    queue_parser.add_argument("--requested-by", default="manual")
    queue_parser.add_argument("--preferred-asr-tool", default="unassigned")
    queue_parser.add_argument("--notes", default="Awaiting transcript generation from a future ASR run.")

    import_parser = subparsers.add_parser("import-transcript", help="Import a completed transcript artifact for a Xiaohongshu video source.")
    import_parser.add_argument("note_url")
    import_parser.add_argument("--body", default="")
    import_parser.add_argument("--body-file", default="")
    import_parser.add_argument("--imported-by", default="manual")
    import_parser.add_argument("--asr-tool", default="unknown")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "queue":
        return queue_request(args)
    if args.command == "import-transcript":
        return import_transcript(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
