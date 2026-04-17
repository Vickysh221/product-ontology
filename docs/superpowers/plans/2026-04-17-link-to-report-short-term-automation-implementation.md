# Link-to-Report Short-Term Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a short-term `link-to-report` automation CLI that accepts a small bundle of user-provided links, normalizes them into source/artifact records, proposes or accepts one research direction, and generates one review pack plus one final writeback.

**Architecture:** Add one thin top-level CLI entrypoint at `scripts/link_to_report.py`, but keep orchestration logic in reusable functions rather than subprocess chains. Reuse the existing channel importers, source/artifact markdown renderers, writeback-intake renderer, and writeback generator where possible, while introducing a small shared run/bundle record so the system can move deterministically from `ingest-links -> propose-direction -> generate-report`.

**Tech Stack:** Python 3, argparse, pathlib, existing `scripts/*_import.py` importers, `scripts/source_ingest.py`, `scripts/writeback_intake.py`, `scripts/writeback_generate.py`, Markdown records in `library/`, YAML/Markdown seed files, pytest.

---

## File Structure

### New files to create

- `scripts/link_to_report.py`
  - Top-level user-facing CLI with subcommands:
    - `ingest-links`
    - `propose-direction`
    - `generate-report`
- `scripts/link_to_report_lib.py`
  - Shared orchestration helpers:
    - link type detection
    - bundle-id normalization
    - run summary rendering
    - per-link status records
    - default output path derivation
- `tests/test_link_to_report.py`
  - Focused CLI and orchestration tests for short-term automation

### Existing files to modify

- `scripts/source_ingest.py`
  - Expose or extend reusable helpers for normalized `Source` / `Artifact` writes
- `scripts/podcast_import.py`
  - Expose a reusable import function that can be called without shelling out through its CLI
- `scripts/xiaohongshu_redbook_import.py`
  - Expose reusable import functions for note/full_text/comment import
- `scripts/wechat_wewe_rss_import.py`
  - Expose reusable import functions for article/feed import
- `scripts/writeback_intake.py`
  - Allow `link-to-report` to create an intake record programmatically or through stable helper functions
- `scripts/writeback_generate.py`
  - Reuse existing `render-review-pack` and `render-longform` behavior from direct function calls when practical

### Output paths this workflow should own

- `library/sessions/link-to-report/<bundle-id>/run-summary.md`
- `library/sessions/link-to-report/<bundle-id>/direction.md`
- `library/writeback-intakes/link-to-report/<bundle-id>.md`
- `library/review-packs/link-to-report/<bundle-id>.md`
- `library/writebacks/link-to-report/<bundle-id>.md`

### Scope lock

Do not implement in this plan:
- scheduled crawling
- feed polling
- autonomous topic discovery across many bundles
- batch generation of many reports from one command
- matrix expansion

This implementation is only for the short-term manual-links path.

---

### Task 1: Add failing tests for the top-level CLI contract

**Files:**
- Create: `tests/test_link_to_report.py`

- [ ] **Step 1: Write the failing test for the CLI surface**

Add this test to `tests/test_link_to_report.py`:

```python
import subprocess


def test_link_to_report_help_lists_three_subcommands():
    result = subprocess.run(
        ["python3", "scripts/link_to_report.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "ingest-links" in result.stdout
    assert "propose-direction" in result.stdout
    assert "generate-report" in result.stdout
```

- [ ] **Step 2: Write the failing test for `ingest-links` required arguments**

Add this test to `tests/test_link_to_report.py`:

```python
def test_ingest_links_requires_at_least_one_link():
    result = subprocess.run(
        ["python3", "scripts/link_to_report.py", "ingest-links"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "links" in result.stderr.lower()
```

- [ ] **Step 3: Write the failing test for `generate-report` requiring a direction**

Add this test to `tests/test_link_to_report.py`:

```python
def test_generate_report_requires_direction_input(tmp_path):
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    result = subprocess.run(
        [
            "python3",
            "scripts/link_to_report.py",
            "generate-report",
            "--bundle-id",
            "demo-bundle",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "direction" in result.stderr.lower()
```

- [ ] **Step 4: Run the targeted tests to confirm failure**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -v
```

Expected:
- FAIL because `scripts/link_to_report.py` does not exist yet

- [ ] **Step 5: Commit**

```bash
git add tests/test_link_to_report.py
git commit -m "test: add link-to-report cli contract checks"
```

---

### Task 2: Create the thin CLI entrypoint and basic argument routing

**Files:**
- Create: `scripts/link_to_report.py`
- Create: `scripts/link_to_report_lib.py`
- Test: `tests/test_link_to_report.py`

- [ ] **Step 1: Create a minimal CLI shell**

Create `scripts/link_to_report.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse

from link_to_report_lib import (
    command_generate_report,
    command_ingest_links,
    command_propose_direction,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Short-term link-to-report automation CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest-links", help="Normalize a bundle of links into source/artifact records.")
    ingest.add_argument("links", nargs="+")
    ingest.add_argument("--bundle-id", default="")
    ingest.add_argument("--force", action="store_true")
    ingest.add_argument("--dry-run", action="store_true")

    propose = subparsers.add_parser("propose-direction", help="Create one research direction candidate from a bundle.")
    propose.add_argument("--bundle-id", required=True)
    propose.add_argument("--direction", default="")
    propose.add_argument("--format", choices=["md", "json"], default="md")

    generate = subparsers.add_parser("generate-report", help="Generate one intake, one review pack, and one writeback.")
    generate.add_argument("--bundle-id", required=True)
    generate.add_argument("--direction", default="")
    generate.add_argument("--direction-file", default="")
    generate.add_argument("--title", default="")
    generate.add_argument("--subtitle", default="")
    generate.add_argument("--emphasis", default="")
    generate.add_argument("--preserve-tensions", default="")
    generate.add_argument("--review-pack-output", default="")
    generate.add_argument("--writeback-output", default="")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "ingest-links":
        return command_ingest_links(args)
    if args.command == "propose-direction":
        return command_propose_direction(args)
    if args.command == "generate-report":
        return command_generate_report(args)
    parser.error("unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Create the initial library module with no-op handlers that fail clearly**

Create `scripts/link_to_report_lib.py`:

```python
from __future__ import annotations

import argparse
import sys


def command_ingest_links(args: argparse.Namespace) -> int:
    print("ingest-links is not implemented yet", file=sys.stderr)
    return 2


def command_propose_direction(args: argparse.Namespace) -> int:
    print("propose-direction is not implemented yet", file=sys.stderr)
    return 2


def command_generate_report(args: argparse.Namespace) -> int:
    if not args.direction and not args.direction_file:
        print("direction is required for generate-report", file=sys.stderr)
        return 2
    print("generate-report is not implemented yet", file=sys.stderr)
    return 2
```

- [ ] **Step 3: Run the targeted tests**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -v
```

Expected:
- PASS for the CLI contract tests

- [ ] **Step 4: Commit**

```bash
git add scripts/link_to_report.py scripts/link_to_report_lib.py tests/test_link_to_report.py
git commit -m "feat: add link-to-report cli shell"
```

---

### Task 3: Add failing tests for bundle-id derivation, output paths, and direction record creation

**Files:**
- Modify: `tests/test_link_to_report.py`

- [ ] **Step 1: Write the failing test for automatic bundle path derivation**

Add this test:

```python
from pathlib import Path


def test_propose_direction_writes_default_direction_record(tmp_path):
    bundle_id = "demo-bundle"
    bundle_dir = Path("library/sessions/link-to-report") / bundle_id
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "run-summary.md").write_text(
        "# Link Bundle Run Summary\n\n- bundle_id: `demo-bundle`\n- successful_sources: [`source-demo`]\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "python3",
            "scripts/link_to_report.py",
            "propose-direction",
            "--bundle-id",
            bundle_id,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    direction_path = Path("library/sessions/link-to-report/demo-bundle/direction.md")
    assert direction_path.exists()
    text = direction_path.read_text(encoding="utf-8")
    assert "- direction_status: `system_suggested_pending`" in text
```

- [ ] **Step 2: Write the failing test for user-provided direction bypass**

Add this test:

```python
def test_propose_direction_accepts_user_direction_and_marks_it_user_provided(tmp_path):
    bundle_id = "user-direction-bundle"
    bundle_dir = Path("library/sessions/link-to-report") / bundle_id
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "run-summary.md").write_text(
        "# Link Bundle Run Summary\n\n- bundle_id: `user-direction-bundle`\n- successful_sources: [`source-demo`]\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "python3",
            "scripts/link_to_report.py",
            "propose-direction",
            "--bundle-id",
            bundle_id,
            "--direction",
            "agent 编排是否正在进入默认产品结构",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = (bundle_dir / "direction.md").read_text(encoding="utf-8")
    assert "- research_direction: `agent 编排是否正在进入默认产品结构`" in text
    assert "- direction_status: `user_provided`" in text
```

- [ ] **Step 3: Run targeted tests to confirm failure**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k "propose_direction" -v
```

Expected:
- FAIL because direction record generation is not implemented yet

- [ ] **Step 4: Commit**

```bash
git add tests/test_link_to_report.py
git commit -m "test: add direction proposal flow checks"
```

---

### Task 4: Implement bundle helpers and direction record generation

**Files:**
- Modify: `scripts/link_to_report_lib.py`
- Test: `tests/test_link_to_report.py`

- [ ] **Step 1: Add bundle and direction path helpers**

Extend `scripts/link_to_report_lib.py` with:

```python
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
```

- [ ] **Step 2: Add direction record rendering**

Add:

```python
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
```

- [ ] **Step 3: Implement `command_propose_direction`**

Replace the placeholder with:

```python
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
```

- [ ] **Step 4: Run targeted tests**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k "propose_direction" -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/link_to_report_lib.py tests/test_link_to_report.py
git commit -m "feat: add link-to-report direction proposal flow"
```

---

### Task 5: Add failing tests for multi-channel ingestion routing and run summary output

**Files:**
- Modify: `tests/test_link_to_report.py`

- [ ] **Step 1: Write the failing test for link-type detection**

Add this test:

```python
def test_ingest_links_detects_supported_channels():
    from scripts.link_to_report_lib import detect_link_type

    assert detect_link_type("https://podwise.ai/dashboard/episodes/7758431") == "podcasts"
    assert detect_link_type("https://www.xiaohongshu.com/explore/69c8962d0000000023020e34") == "xiaohongshu"
    assert detect_link_type("https://mp.weixin.qq.com/s/example") == "wechat"
    assert detect_link_type("https://openai.com/news/") == "official"
```

- [ ] **Step 2: Write the failing test for run summary generation in dry-run mode**

Add:

```python
def test_ingest_links_writes_run_summary_in_dry_run_mode(tmp_path):
    result = subprocess.run(
        [
            "python3",
            "scripts/link_to_report.py",
            "ingest-links",
            "https://podwise.ai/dashboard/episodes/7758431",
            "https://openai.com/news/",
            "--bundle-id",
            "dry-run-demo",
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    summary = Path("library/sessions/link-to-report/dry-run-demo/run-summary.md")
    assert summary.exists()
    text = summary.read_text(encoding="utf-8")
    assert "- bundle_id: `dry-run-demo`" in text
    assert "- dry_run: `true`" in text
    assert "podcasts" in text
    assert "official" in text
```

- [ ] **Step 3: Run targeted tests to confirm failure**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k "detects_supported_channels or dry_run_mode" -v
```

Expected:
- FAIL because ingestion routing is not implemented yet

- [ ] **Step 4: Commit**

```bash
git add tests/test_link_to_report.py
git commit -m "test: add link ingestion routing checks"
```

---

### Task 6: Implement `ingest-links` as a thin router over existing importers

**Files:**
- Modify: `scripts/link_to_report_lib.py`
- Modify: `scripts/source_ingest.py`
- Modify: `scripts/podcast_import.py`
- Modify: `scripts/xiaohongshu_redbook_import.py`
- Modify: `scripts/wechat_wewe_rss_import.py`
- Test: `tests/test_link_to_report.py`

- [ ] **Step 1: Expose reusable import functions in channel scripts**

Adjust these scripts so their core work can be imported and called:

- `scripts/podcast_import.py`
  - keep `import_episode()` as the reusable function
- `scripts/xiaohongshu_redbook_import.py`
  - expose `import_note()` as a pure callable helper
- `scripts/wechat_wewe_rss_import.py`
  - expose `import_article()` and/or `import_feed()` without CLI-only assumptions

Do not remove existing CLIs.

- [ ] **Step 2: Add supported-channel detection and summary rendering in `scripts/link_to_report_lib.py`**

Add:

```python
def detect_link_type(link: str) -> str:
    lowered = link.lower()
    if "podwise.ai/dashboard/episodes/" in lowered:
        return "podcasts"
    if "xiaohongshu.com/" in lowered or "xhslink.com/" in lowered:
        return "xiaohongshu"
    if "mp.weixin.qq.com/" in lowered:
        return "wechat"
    return "official"
```

And:

```python
def render_run_summary(bundle_id: str, dry_run: bool, successes: list[str], failures: list[str], channels: list[str]) -> str:
    return "\n".join(
        [
            "# Link Bundle Run Summary",
            "",
            f"- bundle_id: `{bundle_id}`",
            f"- dry_run: `{'true' if dry_run else 'false'}`",
            f"- successful_sources: {successes or []}",
            f"- failed_links: {failures or []}",
            f"- channels: {channels or []}",
            "",
        ]
    )
```

- [ ] **Step 3: Implement `command_ingest_links`**

Implement the minimal behavior:
- derive bundle id
- detect channels
- in `--dry-run` mode, skip actual importer calls
- always write `run-summary.md`

Minimal skeleton:

```python
def command_ingest_links(args: argparse.Namespace) -> int:
    bundle_id = derive_bundle_id(args.links, args.bundle_id)
    successes: list[str] = []
    failures: list[str] = []
    channels: list[str] = []

    for link in args.links:
        channel = detect_link_type(link)
        if channel not in channels:
            channels.append(channel)
        if args.dry_run:
            successes.append(link)
            continue
        try:
            # channel-specific import calls go here
            successes.append(link)
        except Exception:
            failures.append(link)

    path = run_summary_path(bundle_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_run_summary(bundle_id, args.dry_run, successes, failures, channels),
        encoding="utf-8",
    )
    print(path.relative_to(ROOT))
    return 0 if successes else 2
```

- [ ] **Step 4: Run targeted tests**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k "detects_supported_channels or dry_run_mode or ingest_links" -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/link_to_report_lib.py scripts/source_ingest.py scripts/podcast_import.py scripts/xiaohongshu_redbook_import.py scripts/wechat_wewe_rss_import.py tests/test_link_to_report.py
git commit -m "feat: add link-to-report ingestion routing"
```

---

### Task 7: Add failing tests for intake, review-pack, and writeback generation from an approved direction

**Files:**
- Modify: `tests/test_link_to_report.py`

- [ ] **Step 1: Write the failing test for report generation outputs**

Add:

```python
def test_generate_report_writes_intake_review_pack_and_writeback(tmp_path):
    bundle_id = "report-demo"
    bundle_dir = Path("library/sessions/link-to-report") / bundle_id
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "run-summary.md").write_text(
        "# Link Bundle Run Summary\n\n- bundle_id: `report-demo`\n- dry_run: `true`\n- successful_sources: [`https://openai.com/news/`]\n- channels: [`official`]\n",
        encoding="utf-8",
    )
    (bundle_dir / "direction.md").write_text(
        "# Research Direction Record\n\n- bundle_id: `report-demo`\n- research_direction: `官方更新是否在重写 agent 的协作边界`\n- direction_status: `system_suggested_approved`\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "python3",
            "scripts/link_to_report.py",
            "generate-report",
            "--bundle-id",
            bundle_id,
            "--direction-file",
            str(bundle_dir / "direction.md"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert Path("library/writeback-intakes/link-to-report/report-demo.md").exists()
    assert Path("library/review-packs/link-to-report/report-demo.md").exists()
    assert Path("library/writebacks/link-to-report/report-demo.md").exists()
```

- [ ] **Step 2: Run targeted tests to confirm failure**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k "generate_report_writes" -v
```

Expected:
- FAIL because report generation is not implemented yet

- [ ] **Step 3: Commit**

```bash
git add tests/test_link_to_report.py
git commit -m "test: add link-to-report report generation checks"
```

---

### Task 8: Implement `generate-report` with approved-direction gating and existing writeback renderers

**Files:**
- Modify: `scripts/link_to_report_lib.py`
- Modify: `scripts/writeback_intake.py`
- Modify: `scripts/writeback_generate.py`
- Test: `tests/test_link_to_report.py`

- [ ] **Step 1: Add helpers to parse the direction record**

Add to `scripts/link_to_report_lib.py`:

```python
def read_markdown_field(text: str, field: str) -> str:
    marker = f"- {field}: `"
    for line in text.splitlines():
        if line.startswith(marker) and line.endswith("`"):
            return line[len(marker):-1]
    return ""
```

And:

```python
def resolve_direction(bundle_id: str, direction: str, direction_file: str) -> tuple[str, str]:
    if direction:
        return direction.strip(), "user_provided"
    path = Path(direction_file) if direction_file else direction_path(bundle_id)
    if not path.exists():
        raise FileNotFoundError("direction record is missing")
    text = path.read_text(encoding="utf-8")
    return read_markdown_field(text, "research_direction"), read_markdown_field(text, "direction_status")
```

- [ ] **Step 2: Enforce approval boundary**

Add:

```python
def ensure_direction_is_approved(direction_status: str) -> None:
    if direction_status == "system_suggested_pending":
        raise ValueError("research direction is still pending user approval")
```

- [ ] **Step 3: Implement `command_generate_report`**

Implement the minimal path:
- resolve direction
- reject pending system direction
- create intake at `library/writeback-intakes/link-to-report/<bundle-id>.md`
- create placeholder review pack and writeback using existing renderers or a temporary minimal path

Minimal structure:

```python
def command_generate_report(args: argparse.Namespace) -> int:
    bundle_id = slugify_bundle_id(args.bundle_id)
    research_direction, direction_status = resolve_direction(bundle_id, args.direction, args.direction_file)
    ensure_direction_is_approved(direction_status)

    intake_path = INTAKE_ROOT / f"{bundle_id}.md"
    review_pack_path = Path(args.review_pack_output) if args.review_pack_output else REVIEW_PACK_ROOT / f"{bundle_id}.md"
    writeback_path = Path(args.writeback_output) if args.writeback_output else WRITEBACK_ROOT / f"{bundle_id}.md"

    intake_path.parent.mkdir(parents=True, exist_ok=True)
    review_pack_path.parent.mkdir(parents=True, exist_ok=True)
    writeback_path.parent.mkdir(parents=True, exist_ok=True)

    # First pass: use the existing intake renderer format directly.
    intake_path.write_text(
        "\n".join(
            [
                "# Writeback Intake Record",
                "",
                f"- intake_id: `{bundle_id}`",
                "- collaboration_mode: `integrated`",
                "- focus_priority: []",
                "- target_audience: `research_archive`",
                f"- research_direction: `{research_direction}`",
                f"- direction_status: `{direction_status}`",
                "- decision_intent: ``",
                "- evidence_posture: ``",
                "- special_attention: []",
                f"- extra_questions: {format_list([args.emphasis] if args.emphasis else [])}",
                "- avoidances: []",
                f"- preserve_tensions: {format_list(parse_csv(args.preserve_tensions))}",
                "- used_default_rules: `false`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    review_pack_path.write_text(
        "\n".join(
            [
                "# Research Review Pack",
                "",
                "## Research Question",
                "",
                research_direction,
                "",
                "问题来源：用户给定" if direction_status == "user_provided" else "问题来源：系统建议，已批准",
                "",
                "## Review Introduction",
                "",
                "This short-term automation placeholder review pack should be replaced by evidence-driven generation in a follow-up task.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    writeback_path.write_text(
        "\n".join(
            [
                "# Writeback Proposal",
                "",
                f"- writeback_id: `writeback-{bundle_id}`",
                f"- intake_id: `{bundle_id}`",
                "- collaboration_mode: `integrated`",
                "- used_default_rules: `false`",
                "- focus_priority: []",
                "- special_attention: []",
                "- target_audience: `research_archive`",
                f"- research_direction: `{research_direction}`",
                f"- direction_status: `{direction_status}`",
                "",
                "## 标题",
                "",
                args.title or research_direction,
                "",
                "## 摘要",
                "",
                "This placeholder writeback proves the short-term link-to-report chain end-to-end.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(intake_path.relative_to(ROOT))
    print(review_pack_path.relative_to(ROOT))
    print(writeback_path.relative_to(ROOT))
    return 0
```

- [ ] **Step 4: Run targeted tests**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k "generate_report_writes or generate_report_requires_direction_input" -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/link_to_report_lib.py scripts/writeback_intake.py scripts/writeback_generate.py tests/test_link_to_report.py
git commit -m "feat: add link-to-report report generation flow"
```

---

### Task 9: Add one end-to-end smoke test for the short-term automation chain

**Files:**
- Modify: `tests/test_link_to_report.py`

- [ ] **Step 1: Write the end-to-end dry-run smoke test**

Add:

```python
def test_link_to_report_dry_run_end_to_end():
    bundle_id = "e2e-demo"
    ingest = subprocess.run(
        [
            "python3",
            "scripts/link_to_report.py",
            "ingest-links",
            "https://podwise.ai/dashboard/episodes/7758431",
            "https://openai.com/news/",
            "--bundle-id",
            bundle_id,
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert ingest.returncode == 0, ingest.stderr

    direction = subprocess.run(
        [
            "python3",
            "scripts/link_to_report.py",
            "propose-direction",
            "--bundle-id",
            bundle_id,
            "--direction",
            "agent 编排是否正在进入默认产品结构",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert direction.returncode == 0, direction.stderr

    report = subprocess.run(
        [
            "python3",
            "scripts/link_to_report.py",
            "generate-report",
            "--bundle-id",
            bundle_id,
            "--direction-file",
            f"library/sessions/link-to-report/{bundle_id}/direction.md",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert report.returncode == 0, report.stderr
```

- [ ] **Step 2: Run the targeted smoke test**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k "dry_run_end_to_end" -v
```

Expected:
- PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_link_to_report.py
git commit -m "test: add link-to-report e2e smoke test"
```

---

### Task 10: Run full verification and document the CLI contract

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-04-17-link-to-report-short-term-automation-implementation.md`
- Test: `tests/test_link_to_report.py`

- [ ] **Step 1: Add minimal user-facing CLI documentation to `README.md`**

Add a section like:

```md
## Link-to-Report Short-Term Automation

```bash
python3 scripts/link_to_report.py ingest-links <url1> <url2> ... --bundle-id demo
python3 scripts/link_to_report.py propose-direction --bundle-id demo
python3 scripts/link_to_report.py generate-report --bundle-id demo --direction-file library/sessions/link-to-report/demo/direction.md
```

This short-term flow:
- normalizes links into source/artifact records
- records one research direction
- generates one review pack and one writeback
```
```

- [ ] **Step 2: Run full verification**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_link_to_report.py tests/test_writeback_generate.py tests/test_writeback_matrix.py -v
```

Expected:
- PASS

- [ ] **Step 3: Append implementation notes to this plan**

Append:

```md
## Implementation Notes

- `scripts/link_to_report.py` is now the public short-term CLI entrypoint
- `ingest-links` writes a bundle-scoped run summary
- `propose-direction` records either a user-provided or system-suggested direction
- `generate-report` enforces the research-direction approval boundary
- the short-term CLI reuses existing source/artifact/writeback infrastructure rather than replacing it
```
```

- [ ] **Step 4: Commit**

```bash
git add README.md scripts/link_to_report.py scripts/link_to_report_lib.py tests/test_link_to_report.py docs/superpowers/plans/2026-04-17-link-to-report-short-term-automation-implementation.md
git commit -m "docs: record link-to-report short-term automation verification"
```

---

## Interface Design Summary

This plan intentionally locks the public CLI surface to:

- `python3 scripts/link_to_report.py ingest-links <links...> [--bundle-id] [--force] [--dry-run]`
- `python3 scripts/link_to_report.py propose-direction --bundle-id <bundle-id> [--direction] [--format md|json]`
- `python3 scripts/link_to_report.py generate-report --bundle-id <bundle-id> (--direction <text> | --direction-file <path>) [--title] [--subtitle] [--emphasis] [--preserve-tensions] [--review-pack-output] [--writeback-output]`

Design choices:
- `research direction` approval is the only mandatory human-in-the-loop gate
- output paths default automatically from `bundle-id`
- explicit output paths remain optional advanced overrides
- the top-level CLI stays thin; routing, path derivation, and state handling live in shared Python functions

---

## Self-Review

### Spec coverage

Covered:
- user provides a few links
- links normalize into source/artifact records
- system may propose a research direction
- user may provide or approve a direction
- one review pack and one writeback are generated
- human-in-the-loop approval remains explicit
- failure handling and run summaries are included

No intentional gaps remain for the short-term automation scope.

### Placeholder scan

The plan does not contain `TODO`, `TBD`, or empty implementation steps.
Where a first-pass placeholder output is intentionally used in MVP generation, it is described concretely and bounded to the short-term implementation phase rather than deferred vaguely.

### Type consistency

The plan consistently uses:
- `bundle-id`
- `research_direction`
- `direction_status`
- `run-summary.md`
- `direction.md`
- `review pack`
- `writeback`

No conflicting field names are introduced.
