#!/usr/bin/env python3
"""Import WeChat Official Account articles exposed through wewe-rss."""

from __future__ import annotations

import argparse
import email.utils
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from source_ingest import ROOT, write_artifact_record, write_source_record


SEED_FILE = ROOT / "seed" / "wechat-sources.yaml"


def read_text_from_url(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8", errors="replace")


def iso_from_pubdate(value: str) -> str:
    if not value:
        return "unknown"
    parsed = email.utils.parsedate_to_datetime(value)
    return parsed.isoformat() if parsed else "unknown"


def content_from_item(item: ET.Element) -> str:
    namespaces = {"content": "http://purl.org/rss/1.0/modules/content/"}
    for tag in ("description", "content:encoded"):
        node = item.find(tag, namespaces)
        if node is not None and node.text:
            return node.text.strip()
    return ""


def import_feed(feed_url: str, source_label: str, limit: int, force: bool) -> list[Path]:
    xml_text = read_text_from_url(feed_url)
    root = ET.fromstring(xml_text)
    channel = root.find("./channel")
    if channel is None:
        raise ValueError("Unsupported RSS format: missing channel")

    written: list[Path] = []
    item_count = 0
    for item in channel.findall("./item"):
        if item_count >= limit:
            break
        title = (item.findtext("title") or source_label).strip()
        link = (item.findtext("link") or feed_url).strip()
        published_at = iso_from_pubdate((item.findtext("pubDate") or "").strip())
        body = content_from_item(item)
        if not body:
            continue

        source_id, source_path, _artifact_dir = write_source_record(
            channel="wechat",
            source_label=source_label,
            url=link,
            source_type="wechat_article",
            ingestion_method="wewe_rss",
            publisher=source_label,
            author_or_speaker=source_label,
            published_at=published_at,
            title=title,
            canonical_url=link,
            perspective="official_product",
            notes=[
                f"Imported from wewe-rss feed: {feed_url}",
                "Full article text is stored as a full_text artifact.",
            ],
        )
        artifact_path = write_artifact_record(
            channel="wechat",
            source_label=source_label,
            source_url=link,
            slice_type="full_text",
            location="article_body",
            perspective="wechat_article",
            why_relevant="Stores the imported WeChat article body for later candidate extraction.",
            body=body,
        )
        written.extend([source_path, artifact_path])
        item_count += 1
    return written


def import_article(args: argparse.Namespace) -> int:
    body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else args.body
    if not body.strip():
        raise ValueError("Article body is required.")
    source_id, source_path, _artifact_dir = write_source_record(
        channel="wechat",
        source_label=args.source_label,
        url=args.url,
        source_type="wechat_article",
        ingestion_method="wewe_rss_manual",
        publisher=args.publisher or args.source_label,
        author_or_speaker=args.author_or_speaker or args.source_label,
        published_at=args.published_at,
        title=args.title,
        canonical_url=args.url,
        perspective=args.perspective,
        notes=["Imported from a manually provided wewe-rss article body."],
    )
    artifact_path = write_artifact_record(
        channel="wechat",
        source_label=args.source_label,
        source_url=args.url,
        slice_type="full_text",
        location="article_body",
        perspective="wechat_article",
        why_relevant="Stores the imported WeChat article body for later candidate extraction.",
        body=body,
    )
    print(f"initialized {source_id}")
    print(source_path.relative_to(ROOT))
    print(artifact_path.relative_to(ROOT))
    return 0


def add_feed(args: argparse.Namespace) -> int:
    seed_text = SEED_FILE.read_text(encoding="utf-8") if SEED_FILE.exists() else "accounts:\n"
    with SEED_FILE.open("a", encoding="utf-8") as handle:
        if not seed_text.endswith("\n"):
            handle.write("\n")
        handle.write(
            "\n".join(
                [
                    f"  - label: {args.label}",
                    f"    source_container: {args.source_container}",
                    f"    feed_url: {args.feed_url}",
                    f"    publisher: {args.publisher}",
                    f"    perspective: {args.perspective}",
                    "    ingestion_method: wewe_rss",
                    f"    notes: {args.notes}",
                    "",
                ]
            )
        )
    print(f"updated {SEED_FILE.relative_to(ROOT)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import WeChat articles from wewe-rss outputs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_feed_parser = subparsers.add_parser("add-feed", help="Append a wewe-rss feed target to seed/wechat-sources.yaml.")
    add_feed_parser.add_argument("label")
    add_feed_parser.add_argument("source_container")
    add_feed_parser.add_argument("feed_url")
    add_feed_parser.add_argument("--publisher", default="微信公众号")
    add_feed_parser.add_argument("--perspective", default="official_product")
    add_feed_parser.add_argument("--notes", default="Added manually for wewe-rss ingestion.")

    import_feed_parser = subparsers.add_parser("import-feed", help="Fetch an RSS feed URL from wewe-rss and import recent items.")
    import_feed_parser.add_argument("feed_url")
    import_feed_parser.add_argument("source_label")
    import_feed_parser.add_argument("--limit", type=int, default=5)
    import_feed_parser.add_argument("--force", action="store_true")

    import_article_parser = subparsers.add_parser("import-article", help="Import one WeChat article from manual wewe-rss text output.")
    import_article_parser.add_argument("source_label")
    import_article_parser.add_argument("title")
    import_article_parser.add_argument("url")
    import_article_parser.add_argument("--published-at", default="unknown")
    import_article_parser.add_argument("--publisher", default="")
    import_article_parser.add_argument("--author-or-speaker", default="")
    import_article_parser.add_argument("--perspective", default="official_product")
    import_article_parser.add_argument("--body", default="")
    import_article_parser.add_argument("--body-file", default="")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "add-feed":
        return add_feed(args)
    if args.command == "import-feed":
        written = import_feed(args.feed_url, args.source_label, args.limit, args.force)
        for path in written:
            print(path.relative_to(ROOT))
        return 0
    if args.command == "import-article":
        return import_article(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
