#!/usr/bin/env python3
from __future__ import annotations

import argparse

from link_to_report_lib import (
    command_generate_report,
    command_ingest_links,
    command_propose_direction,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Short-term link-to-report automation CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser(
        "ingest-links",
        help="Normalize a bundle of links into source/artifact records.",
    )
    ingest.add_argument("links", nargs="+")
    ingest.add_argument("--bundle-id", default="")
    ingest.add_argument("--force", action="store_true")
    ingest.add_argument("--dry-run", action="store_true")

    propose = subparsers.add_parser(
        "propose-direction",
        help="Create one research direction candidate from a bundle.",
    )
    propose.add_argument("--bundle-id", required=True)
    propose.add_argument("--direction", default="")
    propose.add_argument("--format", choices=["md", "json"], default="md")

    generate = subparsers.add_parser(
        "generate-report",
        help="Generate one intake, one review pack, and one writeback.",
    )
    generate.add_argument("--bundle-id", required=True)
    direction_group = generate.add_mutually_exclusive_group(required=True)
    direction_group.add_argument("--direction", default="")
    direction_group.add_argument("--direction-file", default="")
    generate.add_argument("--title", default="")
    generate.add_argument("--subtitle", default="")
    generate.add_argument("--emphasis", default="")
    generate.add_argument("--preserve-tensions", default="")
    generate.add_argument("--review-pack-output", default="")
    generate.add_argument("--writeback-output", default="")

    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "ingest-links":
        return command_ingest_links(args)
    if args.command == "propose-direction":
        return command_propose_direction(args)
    if args.command == "generate-report":
        return command_generate_report(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
