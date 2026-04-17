from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LINK_TO_REPORT_ROOT = ROOT / "library" / "sessions" / "link-to-report"
INTAKE_ROOT = ROOT / "library" / "writeback-intakes" / "link-to-report"
REVIEW_PACK_ROOT = ROOT / "library" / "review-packs" / "link-to-report"
WRITEBACK_ROOT = ROOT / "library" / "writebacks" / "link-to-report"


def slugify_bundle_id(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized or "bundle"


def derive_bundle_id(links: list[str], requested: str) -> str:
    if requested:
        return slugify_bundle_id(requested)
    digest = hashlib.sha1("|".join(sorted(links)).encode("utf-8")).hexdigest()[:8]
    return f"bundle-{digest}"


def bundle_dir(bundle_id: str) -> Path:
    return LINK_TO_REPORT_ROOT / bundle_id


def direction_path(bundle_id: str) -> Path:
    return bundle_dir(bundle_id) / "direction.md"


def run_summary_path(bundle_id: str) -> Path:
    return bundle_dir(bundle_id) / "run-summary.md"


def render_direction_markdown(bundle_id: str, research_direction: str, direction_status: str) -> str:
    return "\n".join(
        [
            "# Research Direction Record",
            "",
            f"- bundle_id: `{bundle_id}`",
            f"- research_direction: `{research_direction}`",
            f"- direction_status: `{direction_status}`",
            "",
        ]
    )


def command_ingest_links(args: argparse.Namespace) -> int:
    print("ingest-links is not implemented yet", file=sys.stderr)
    return 2


def command_propose_direction(args: argparse.Namespace) -> int:
    bundle_id = slugify_bundle_id(args.bundle_id)
    summary_path = run_summary_path(bundle_id)
    if not summary_path.exists():
        print("bundle run summary is missing", file=sys.stderr)
        return 2

    if args.direction:
        research_direction = args.direction.strip()
        direction_status = "user_provided"
    else:
        research_direction = "这组链接共同指向的产品问题是什么，尤其是它们是否在重写协作边界、责任边界或工作流结构"
        direction_status = "system_suggested_pending"

    path = direction_path(bundle_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_direction_markdown(bundle_id, research_direction, direction_status),
        encoding="utf-8",
    )
    print(path.relative_to(ROOT))
    return 0


def command_generate_report(args: argparse.Namespace) -> int:
    if not args.direction and not args.direction_file:
        print("direction is required for generate-report", file=sys.stderr)
        return 2
    print("generate-report is not implemented yet", file=sys.stderr)
    return 2
