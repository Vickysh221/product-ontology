#!/usr/bin/env python3
"""Import Xiaohongshu notes and comments from redbook outputs or manual exports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from source_ingest import ROOT, build_source_slug, write_artifact_record, write_source_record


SEED_FILE = ROOT / "seed" / "xiaohongshu-sources.yaml"


def load_text(body: str, body_file: str) -> str:
    if body_file:
        return Path(body_file).read_text(encoding="utf-8")
    return body


def canonical_slug_from_url(note_url: str) -> str:
    return build_source_slug(note_url)


def add_target(args: argparse.Namespace) -> int:
    seed_text = SEED_FILE.read_text(encoding="utf-8") if SEED_FILE.exists() else "targets:\n"
    with SEED_FILE.open("a", encoding="utf-8") as handle:
        if not seed_text.endswith("\n"):
            handle.write("\n")
        handle.write(
            "\n".join(
                [
                    f"  - label: {args.label}",
                    f"    note_url: {args.note_url}",
                    f"    query: {args.query}",
                    "    publisher: 小红书",
                    f"    perspective: {args.perspective}",
                    "    ingestion_method: redbook_cli",
                    f"    notes: {args.notes}",
                    "",
                ]
            )
        )
    print(f"updated {SEED_FILE.relative_to(ROOT)}")
    return 0


def import_note(args: argparse.Namespace) -> int:
    note_body = load_text(args.body, args.body_file)
    if not note_body.strip():
        raise ValueError("Note body is required.")

    source_id, source_path, _artifact_dir = write_source_record(
        channel="xiaohongshu",
        source_label=args.source_label,
        url=args.note_url,
        source_type="xiaohongshu_note",
        ingestion_method="redbook_manual",
        publisher="小红书",
        author_or_speaker=args.author or "unknown",
        published_at=args.published_at,
        title=args.title,
        canonical_url=args.note_url,
        perspective=args.perspective,
        notes=["Imported from a manual redbook note export."],
    )
    text_artifact = write_artifact_record(
        channel="xiaohongshu",
        source_label=args.source_label,
        source_url=args.note_url,
        slice_type="full_text",
        location="note_body",
        perspective="creator_commentary",
        why_relevant="Stores the imported Xiaohongshu note body for later candidate extraction.",
        body=note_body,
    )
    print(f"initialized {source_id}")
    print(source_path.relative_to(ROOT))
    print(text_artifact.relative_to(ROOT))

    comments_body = load_text(args.comments_body, args.comments_file)
    if comments_body.strip():
        comment_artifact = write_artifact_record(
            channel="xiaohongshu",
            source_label=args.source_label,
            source_url=args.note_url,
            slice_type="comment_batch",
            location="comments",
            perspective="audience_feedback",
            why_relevant="Stores imported Xiaohongshu comments for audience-signal analysis.",
            body=comments_body,
        )
        print(comment_artifact.relative_to(ROOT))
    return 0


def import_note_url(note_url: str, *, force: bool = False, include_comments: bool = True) -> str:
    slug = canonical_slug_from_url(note_url)
    source_path = ROOT / "library" / "sources" / "xiaohongshu" / f"{slug}.md"
    if source_path.exists() and not force:
        return slug

    args = argparse.Namespace(
        source_label=slug,
        title=slug,
        note_url=note_url,
        author="unknown",
        published_at="unknown",
        perspective="creator_commentary",
        include_comments=include_comments,
        body="",
        body_file="",
        comments_body="",
        comments_file="",
    )
    pull_with_redbook(args)
    return slug


def import_redbook_json(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
    title = payload.get("title") or args.title or args.source_label
    body = payload.get("content") or payload.get("body") or ""
    author = payload.get("author") or payload.get("nickname") or "unknown"
    comments = payload.get("comments") or []
    comments_text = "\n".join(str(item) for item in comments)
    args.title = title
    args.body = body
    args.author = author
    args.comments_body = comments_text
    args.body_file = ""
    args.comments_file = ""
    return import_note(args)


def pull_with_redbook(args: argparse.Namespace) -> int:
    read_output = subprocess.run(
        ["redbook", "read", args.note_url],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    comments_output = ""
    if args.include_comments:
        comments_output = subprocess.run(
            ["redbook", "comments", args.note_url],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    args.body = read_output
    args.comments_body = comments_output
    args.body_file = ""
    args.comments_file = ""
    return import_note(args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import Xiaohongshu note data from redbook outputs or manual exports.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_target_parser = subparsers.add_parser("add-target", help="Append a Xiaohongshu target to seed/xiaohongshu-sources.yaml.")
    add_target_parser.add_argument("label")
    add_target_parser.add_argument("--note-url", default="")
    add_target_parser.add_argument("--query", default="")
    add_target_parser.add_argument("--perspective", default="creator_commentary")
    add_target_parser.add_argument("--notes", default="Added manually for redbook ingestion.")

    import_note_parser = subparsers.add_parser("import-note", help="Import one Xiaohongshu note from manual text or files.")
    import_note_parser.add_argument("source_label")
    import_note_parser.add_argument("title")
    import_note_parser.add_argument("note_url")
    import_note_parser.add_argument("--author", default="unknown")
    import_note_parser.add_argument("--published-at", default="unknown")
    import_note_parser.add_argument("--perspective", default="creator_commentary")
    import_note_parser.add_argument("--body", default="")
    import_note_parser.add_argument("--body-file", default="")
    import_note_parser.add_argument("--comments-body", default="")
    import_note_parser.add_argument("--comments-file", default="")

    import_json_parser = subparsers.add_parser("import-redbook-json", help="Import one Xiaohongshu note from a saved redbook JSON payload.")
    import_json_parser.add_argument("source_label")
    import_json_parser.add_argument("note_url")
    import_json_parser.add_argument("json_file")
    import_json_parser.add_argument("--title", default="")
    import_json_parser.add_argument("--published-at", default="unknown")
    import_json_parser.add_argument("--perspective", default="creator_commentary")
    import_json_parser.add_argument("--author", default="unknown")
    import_json_parser.add_argument("--body", default="")
    import_json_parser.add_argument("--comments-body", default="")
    import_json_parser.add_argument("--body-file", default="")
    import_json_parser.add_argument("--comments-file", default="")

    pull_parser = subparsers.add_parser("pull-with-redbook", help="Call `redbook read/comments` directly when the CLI is installed.")
    pull_parser.add_argument("source_label")
    pull_parser.add_argument("title")
    pull_parser.add_argument("note_url")
    pull_parser.add_argument("--author", default="unknown")
    pull_parser.add_argument("--published-at", default="unknown")
    pull_parser.add_argument("--perspective", default="creator_commentary")
    pull_parser.add_argument("--include-comments", action="store_true")
    pull_parser.add_argument("--body", default="")
    pull_parser.add_argument("--comments-body", default="")
    pull_parser.add_argument("--body-file", default="")
    pull_parser.add_argument("--comments-file", default="")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "add-target":
        return add_target(args)
    if args.command == "import-note":
        return import_note(args)
    if args.command == "import-redbook-json":
        return import_redbook_json(args)
    if args.command == "pull-with-redbook":
        return pull_with_redbook(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
