#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml


def load_config(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text())


def make_intake(output_dir: Path, row: dict) -> None:
    output = output_dir / f"{row['output_slug']}.md"
    subprocess.run(
        [
            "python3",
            "scripts/writeback_intake.py",
            "create",
            "--intake-id",
            f"intake-{row['output_slug']}",
            "--output",
            str(output),
            "--collaboration-mode",
            row["collaboration_mode"],
            "--target-audience",
            row["target_audience"],
            "--extra-questions",
            row["extra_question_theme"],
        ],
        check=True,
    )


def make_writeback(writeback_dir: Path, intake_dir: Path, config: dict, row: dict) -> None:
    intake = intake_dir / f"{row['output_slug']}.md"
    output = writeback_dir / f"{row['output_slug']}.md"
    subprocess.run(
        [
            "python3",
            "scripts/writeback_generate.py",
            "render",
            "--writeback-id",
            f"writeback-{row['output_slug']}",
            "--intake-file",
            str(intake),
            "--output",
            str(output),
            "--title",
            config["title"],
            "--subtitle",
            row["subtitle"],
            "--summary",
            "基于共享综合判断底座生成的矩阵测试写作版本。",
            "--synthesis-ref",
            config["synthesis_id"],
        ],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    intake_cmd = subparsers.add_parser("generate-intakes")
    intake_cmd.add_argument("--config", required=True)
    intake_cmd.add_argument("--output-dir", required=True)

    all_cmd = subparsers.add_parser("generate-all")
    all_cmd.add_argument("--config", required=True)
    all_cmd.add_argument("--intake-dir", required=True)
    all_cmd.add_argument("--writeback-dir", required=True)

    args = parser.parse_args()
    config = load_config(args.config)

    if args.command == "generate-intakes":
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for row in config["matrix"]:
            make_intake(output_dir, row)
        return 0

    if args.command == "generate-all":
        intake_dir = Path(args.intake_dir)
        writeback_dir = Path(args.writeback_dir)
        intake_dir.mkdir(parents=True, exist_ok=True)
        writeback_dir.mkdir(parents=True, exist_ok=True)
        for row in config["matrix"]:
            make_intake(intake_dir, row)
            make_writeback(writeback_dir, intake_dir, config, row)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
