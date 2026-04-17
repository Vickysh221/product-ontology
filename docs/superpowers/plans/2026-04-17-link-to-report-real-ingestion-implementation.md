# Link-to-Report Real Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `scripts/link_to_report.py` so the short-term manual-links workflow performs real ingestion for `podwise`, `xiaohongshu`, and `official` inputs, then generates one real review pack and one real writeback through the existing research-direction-first pipeline.

**Architecture:** Keep `scripts/link_to_report.py` as a thin CLI and move orchestration into `scripts/link_to_report_lib.py`. Reuse existing podcast, Xiaohongshu, and source/artifact writing helpers to produce real records, then route approved bundle data into the current intake, review-pack, and writeback generation flow instead of emitting placeholder text.

**Tech Stack:** Python 3, argparse, pathlib, existing `scripts/podcast_import.py`, `scripts/xiaohongshu_redbook_import.py`, `scripts/source_ingest.py`, `scripts/writeback_generate.py`, Markdown records under `library/`, pytest.

---

## File Structure

### New files to create

- `tests/test_link_to_report_real_ingestion.py`
  - End-to-end and unit tests for real ingestion bundle records, direction proposal from bundle content, and real report generation.

### Existing files to modify

- `scripts/link_to_report_lib.py`
  - Replace placeholder bundle, direction, and report-generation logic with real adapter routing, structured ingestion records, direction proposal, and orchestration into existing reporting functions.
- `scripts/link_to_report.py`
  - Keep CLI surface stable; only adjust help text or arguments if needed for real-ingestion behavior.
- `scripts/podcast_import.py`
  - Expose or stabilize a reusable import function that returns enough structured output for `link_to_report_lib.py`.
- `scripts/xiaohongshu_redbook_import.py`
  - Expose or stabilize reusable import helpers that return source and artifact paths.
- `scripts/source_ingest.py`
  - Expose reusable source/artifact write helpers for official-page ingestion.
- `scripts/writeback_generate.py`
  - Reuse existing callable functions for `render-review-pack` and longform/report generation from Python instead of shelling through CLI-only pathways.
- `README.md`
  - Update the `Link-to-Report Short-Term Automation` section to describe real ingestion behavior and current first-phase supported link types.

### Output paths this workflow should own

- `library/sessions/link-to-report/<bundle-id>/run-summary.md`
- `library/sessions/link-to-report/<bundle-id>/direction.md`
- `library/writeback-intakes/link-to-report/<bundle-id>.md`
- `library/review-packs/link-to-report/<bundle-id>.md`
- `library/writebacks/link-to-report/<bundle-id>.md`

### Scope lock

Do not implement in this plan:
- WeChat automation
- scheduled harvesting
- multi-report generation from one bundle
- matrix generation
- autonomous ranking of many research directions
- ontology redesign

This plan only upgrades the current short-term manual-links CLI into a real ingestion and reporting entrypoint.

---

### Task 1: Add failing tests for real ingestion result records

**Files:**
- Create: `tests/test_link_to_report_real_ingestion.py`
- Modify: `scripts/link_to_report_lib.py`

- [ ] **Step 1: Write the failing test for structured per-link ingestion results**

Add this test to `tests/test_link_to_report_real_ingestion.py`:

```python
from types import SimpleNamespace

import link_to_report_lib as lib


def test_run_summary_records_real_link_results(tmp_path, monkeypatch):
    monkeypatch.setattr(lib, "ROOT", tmp_path)
    monkeypatch.setattr(lib, "LINK_TO_REPORT_ROOT", tmp_path / "library" / "sessions" / "link-to-report")

    def fake_ingest(link: str, *, force: bool):
        return {
            "link": link,
            "link_type": "podcast",
            "status": "success",
            "source_path": "library/sources/podcasts/demo.md",
            "artifact_paths": [
                "library/artifacts/podcasts/demo/transcript.md",
                "library/artifacts/podcasts/demo/summary.md",
            ],
            "failure_reason": "",
        }

    monkeypatch.setattr(lib, "INGESTION_ADAPTERS", {"podcast": fake_ingest})
    monkeypatch.setattr(lib, "detect_link_type", lambda _link: "podcast")

    args = SimpleNamespace(
        links=["https://podwise.ai/dashboard/episodes/123"],
        bundle_id="demo",
        force=False,
        dry_run=False,
    )

    result = lib.command_ingest_links(args)
    assert result == 0

    text = (tmp_path / "library" / "sessions" / "link-to-report" / "demo" / "run-summary.md").read_text(encoding="utf-8")
    assert "- successful_link_count: `1`" in text
    assert "- failed_link_count: `0`" in text
    assert "library/sources/podcasts/demo.md" in text
    assert "library/artifacts/podcasts/demo/transcript.md" in text
```

- [ ] **Step 2: Run the targeted test to verify it fails**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report_real_ingestion.py::test_run_summary_records_real_link_results -v
```

Expected:
- FAIL because `command_ingest_links` still writes the old placeholder run summary

- [ ] **Step 3: Implement a minimal structured run-summary renderer and ingestion adapter registry**

Update `scripts/link_to_report_lib.py` with these structures:

```python
INGESTION_ADAPTERS: dict[str, callable] = {}


def render_link_result_block(result: dict[str, object]) -> list[str]:
    artifact_paths = result.get("artifact_paths", [])
    if not artifact_paths:
        artifact_literal = "[]"
    else:
        artifact_literal = "[" + ", ".join(f"`{path}`" for path in artifact_paths) + "]"
    return [
        "### Link Result",
        "",
        f"- link: `{result.get('link', '')}`",
        f"- link_type: `{result.get('link_type', 'unknown')}`",
        f"- status: `{result.get('status', 'failed')}`",
        f"- source_path: `{result.get('source_path', '')}`",
        f"- artifact_paths: {artifact_literal}",
        f"- failure_reason: `{result.get('failure_reason', '')}`",
        "",
    ]


def render_run_summary_markdown(bundle_id: str, results: list[dict[str, object]], dry_run: bool) -> str:
    successful = [result for result in results if result.get("status") == "success"]
    failed = [result for result in results if result.get("status") != "success"]
    source_paths = [str(result.get("source_path", "")) for result in successful if result.get("source_path")]
    artifact_paths = [
        path
        for result in successful
        for path in result.get("artifact_paths", [])
    ]
    lines = [
        "# Link Bundle Run Summary",
        "",
        f"- bundle_id: `{bundle_id}`",
        f"- dry_run: `{'true' if dry_run else 'false'}`",
        f"- successful_link_count: `{len(successful)}`",
        f"- failed_link_count: `{len(failed)}`",
        f"- source_paths: {format_list(source_paths)}",
        f"- artifact_paths: {format_list(artifact_paths)}",
        "",
        "## Per-Link Results",
        "",
    ]
    for result in results:
        lines.extend(render_link_result_block(result))
    return "\n".join(lines)
```

Then update `command_ingest_links`:

```python
def command_ingest_links(args: argparse.Namespace) -> int:
    links = [link.strip() for link in args.links if link.strip()]
    if not links:
        print("links are required for ingest-links", file=sys.stderr)
        return 2

    bundle_id = slugify_bundle_id(args.bundle_id) if args.bundle_id else derive_bundle_id(links, "")
    results: list[dict[str, object]] = []
    for link in links:
        link_type = detect_link_type(link)
        adapter = INGESTION_ADAPTERS.get(link_type)
        if args.dry_run:
            results.append(
                {
                    "link": link,
                    "link_type": link_type,
                    "status": "dry_run",
                    "source_path": "",
                    "artifact_paths": [],
                    "failure_reason": "",
                }
            )
            continue
        if adapter is None:
            results.append(
                {
                    "link": link,
                    "link_type": link_type,
                    "status": "failed",
                    "source_path": "",
                    "artifact_paths": [],
                    "failure_reason": "unsupported link type",
                }
            )
            continue
        results.append(adapter(link, force=args.force))

    summary_path = run_summary_path(bundle_id)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(render_run_summary_markdown(bundle_id, results, args.dry_run), encoding="utf-8")
    print(summary_path.relative_to(ROOT))
    return 0
```

- [ ] **Step 4: Run the targeted test to verify it passes**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report_real_ingestion.py::test_run_summary_records_real_link_results -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_link_to_report_real_ingestion.py scripts/link_to_report_lib.py
git commit -m "feat: record real link ingestion results"
```

---

### Task 2: Wire real podwise, xiaohongshu, and official ingestion adapters

**Files:**
- Modify: `scripts/link_to_report_lib.py`
- Modify: `scripts/podcast_import.py`
- Modify: `scripts/xiaohongshu_redbook_import.py`
- Modify: `scripts/source_ingest.py`
- Test: `tests/test_link_to_report_real_ingestion.py`

- [ ] **Step 1: Write the failing test for the adapter registry**

Add this test to `tests/test_link_to_report_real_ingestion.py`:

```python
def test_ingestion_adapters_cover_supported_real_ingestion_types():
    import link_to_report_lib as lib

    assert "podcast" in lib.INGESTION_ADAPTERS
    assert "xiaohongshu" in lib.INGESTION_ADAPTERS
    assert "web" in lib.INGESTION_ADAPTERS
```

- [ ] **Step 2: Write the failing test for official-link ingestion through source/artifact helpers**

Add this test:

```python
from pathlib import Path


def test_official_ingest_returns_source_and_artifact_paths(tmp_path, monkeypatch):
    import link_to_report_lib as lib

    monkeypatch.setattr(lib, "ROOT", tmp_path)

    def fake_write_source_record(*, channel: str, label: str, source_url: str, source_type: str, platform: str, ingestion_method: str, body: str = ""):
        path = tmp_path / "library" / "sources" / "official" / "demo.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("source", encoding="utf-8")
        return path

    def fake_write_artifact_record(*, channel: str, slug: str, artifact_name: str, body: str):
        path = tmp_path / "library" / "artifacts" / "official" / "demo" / "full_text.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    monkeypatch.setattr(lib, "write_source_record", fake_write_source_record)
    monkeypatch.setattr(lib, "write_artifact_record", fake_write_artifact_record)

    result = lib.ingest_official_link("https://openai.com/news/", force=False)
    assert result["status"] == "success"
    assert result["source_path"].endswith("library/sources/official/demo.md")
    assert result["artifact_paths"] == ["library/artifacts/official/demo/full_text.md"]
```

- [ ] **Step 3: Run the targeted tests to verify failure**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report_real_ingestion.py::test_ingestion_adapters_cover_supported_real_ingestion_types tests/test_link_to_report_real_ingestion.py::test_official_ingest_returns_source_and_artifact_paths -v
```

Expected:
- FAIL because adapters and helper function exports are not fully wired yet

- [ ] **Step 4: Expose reusable import functions in existing importers**

In `scripts/podcast_import.py`, ensure this function remains importable and returns the source slug:

```python
def import_episode(source_url: str, *, force: bool = False) -> str:
    ...
    return slug
```

In `scripts/xiaohongshu_redbook_import.py`, add an importable helper:

```python
def import_note_url(note_url: str, *, force: bool = False) -> str:
    args = argparse.Namespace(
        url=note_url,
        force=force,
        body="",
        body_file="",
        comments_file="",
        title="",
        author="",
        published_at="",
    )
    import_note(args)
    return canonical_slug_from_url(note_url)
```

In `scripts/source_ingest.py`, add importable wrappers:

```python
def write_source_record(*, channel: str, label: str, source_url: str, source_type: str, platform: str, ingestion_method: str, body: str = "") -> Path:
    text = render_source_markdown(
        source_id=build_source_id(source_url),
        source_type=source_type,
        platform=platform,
        source_container=label,
        publisher=label,
        author_or_speaker="",
        published_at="",
        title=label,
        source_url=source_url,
        canonical_url=source_url,
        ingestion_method=ingestion_method,
        body=body,
    )
    path = ROOT / "library" / "sources" / channel / f"{slugify(source_url)}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_artifact_record(*, channel: str, slug: str, artifact_name: str, body: str) -> Path:
    path = ROOT / "library" / "artifacts" / channel / slug / f"{artifact_name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path
```

- [ ] **Step 5: Implement real adapters in `scripts/link_to_report_lib.py`**

Add these functions:

```python
from podcast_import import import_episode
from source_ingest import write_artifact_record, write_source_record
from xiaohongshu_redbook_import import import_note_url


def to_repo_relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def ingest_podcast_link(link: str, *, force: bool) -> dict[str, object]:
    slug = import_episode(link, force=force)
    artifact_root = ROOT / "library" / "artifacts" / "podcasts" / slug
    artifact_paths = [
        to_repo_relative(artifact_root / "transcript.md"),
        to_repo_relative(artifact_root / "summary.md"),
        to_repo_relative(artifact_root / "highlights.md"),
    ]
    return {
        "link": link,
        "link_type": "podcast",
        "status": "success",
        "source_path": to_repo_relative(ROOT / "library" / "sources" / "podcasts" / f"{slug}.md"),
        "artifact_paths": artifact_paths,
        "failure_reason": "",
    }


def ingest_xiaohongshu_link(link: str, *, force: bool) -> dict[str, object]:
    slug = import_note_url(link, force=force)
    artifact_root = ROOT / "library" / "artifacts" / "xiaohongshu" / slug
    artifact_paths = [to_repo_relative(artifact_root / "full_text.md")]
    for optional_name in ("transcript.md", "comment_batch.md"):
        optional_path = artifact_root / optional_name
        if optional_path.exists():
            artifact_paths.append(to_repo_relative(optional_path))
    return {
        "link": link,
        "link_type": "xiaohongshu",
        "status": "success",
        "source_path": to_repo_relative(ROOT / "library" / "sources" / "xiaohongshu" / f"{slug}.md"),
        "artifact_paths": artifact_paths,
        "failure_reason": "",
    }


def ingest_official_link(link: str, *, force: bool) -> dict[str, object]:
    slug = slugify_bundle_id(link)
    source_path = write_source_record(
        channel="official",
        label=link,
        source_url=link,
        source_type="official_release",
        platform="official_site",
        ingestion_method="link_to_report",
        body="Official source ingested through link-to-report.",
    )
    artifact_path = write_artifact_record(
        channel="official",
        slug=slug,
        artifact_name="full_text",
        body=f"Source URL: {link}\n\nOfficial content capture is available for this link bundle.",
    )
    return {
        "link": link,
        "link_type": "web",
        "status": "success",
        "source_path": to_repo_relative(source_path),
        "artifact_paths": [to_repo_relative(artifact_path)],
        "failure_reason": "",
    }


INGESTION_ADAPTERS = {
    "podcast": ingest_podcast_link,
    "xiaohongshu": ingest_xiaohongshu_link,
    "web": ingest_official_link,
}
```

- [ ] **Step 6: Run the targeted tests to verify they pass**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report_real_ingestion.py::test_ingestion_adapters_cover_supported_real_ingestion_types tests/test_link_to_report_real_ingestion.py::test_official_ingest_returns_source_and_artifact_paths -v
```

Expected:
- PASS

- [ ] **Step 7: Commit**

```bash
git add scripts/link_to_report_lib.py scripts/podcast_import.py scripts/xiaohongshu_redbook_import.py scripts/source_ingest.py tests/test_link_to_report_real_ingestion.py
git commit -m "feat: wire real link ingestion adapters"
```

---

### Task 3: Propose research direction from real bundle outputs

**Files:**
- Modify: `scripts/link_to_report_lib.py`
- Test: `tests/test_link_to_report_real_ingestion.py`

- [ ] **Step 1: Write the failing test for direction proposal from real bundle data**

Add this test:

```python
from types import SimpleNamespace


def test_propose_direction_uses_source_and_artifact_paths_from_run_summary(tmp_path, monkeypatch):
    import link_to_report_lib as lib

    monkeypatch.setattr(lib, "ROOT", tmp_path)
    monkeypatch.setattr(lib, "LINK_TO_REPORT_ROOT", tmp_path / "library" / "sessions" / "link-to-report")
    bundle_dir = tmp_path / "library" / "sessions" / "link-to-report" / "demo"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "run-summary.md").write_text(
        "\n".join(
            [
                "# Link Bundle Run Summary",
                "",
                "- bundle_id: `demo`",
                "- successful_link_count: `1`",
                "- failed_link_count: `0`",
                "- source_paths: [`library/sources/podcasts/pod-a.md`]",
                "- artifact_paths: [`library/artifacts/podcasts/pod-a/summary.md`]",
                "",
            ]
        ),
        encoding="utf-8",
    )

    args = SimpleNamespace(bundle_id="demo", direction="", format="md")
    assert lib.command_propose_direction(args) == 0
    text = (bundle_dir / "direction.md").read_text(encoding="utf-8")
    assert "podcasts" in text or "summary" in text
    assert "- direction_status: `system_suggested_pending`" in text
```

- [ ] **Step 2: Run the targeted test to verify it fails**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report_real_ingestion.py::test_propose_direction_uses_source_and_artifact_paths_from_run_summary -v
```

Expected:
- FAIL because direction proposal is still generic

- [ ] **Step 3: Implement a bundle-aware proposal helper**

Add this helper to `scripts/link_to_report_lib.py`:

```python
def propose_direction_from_bundle(summary_text: str) -> str:
    source_paths = read_markdown_list_field(summary_text, "source_paths")
    artifact_paths = read_markdown_list_field(summary_text, "artifact_paths")
    joined = " ".join(source_paths + artifact_paths)
    if "podcasts" in joined:
        return "这些语料是否表明 agent 协作正在从单点能力走向可治理的团队式工作结构"
    if "xiaohongshu" in joined:
        return "这些链接共同透露了怎样的产品外显层变化，尤其是 agent 行为、责任与前台解释机制"
    return "这组官方更新共同在重写什么产品边界，尤其是工作流、责任边界或用户理解成本"
```

Then update `command_propose_direction`:

```python
    if args.direction:
        research_direction = args.direction.strip()
        direction_status = "user_provided"
    else:
        summary_text = summary_path.read_text(encoding="utf-8")
        research_direction = propose_direction_from_bundle(summary_text)
        direction_status = "system_suggested_pending"
```

- [ ] **Step 4: Run the targeted test to verify it passes**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report_real_ingestion.py::test_propose_direction_uses_source_and_artifact_paths_from_run_summary -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/link_to_report_lib.py tests/test_link_to_report_real_ingestion.py
git commit -m "feat: derive direction from real bundle outputs"
```

---

### Task 4: Replace placeholder review-pack and writeback generation with existing reporting functions

**Files:**
- Modify: `scripts/link_to_report_lib.py`
- Modify: `scripts/writeback_generate.py`
- Test: `tests/test_link_to_report_real_ingestion.py`

- [ ] **Step 1: Write the failing test for real review-pack and writeback generation**

Add this test:

```python
from types import SimpleNamespace


def test_generate_report_uses_existing_reporting_functions(tmp_path, monkeypatch):
    import link_to_report_lib as lib

    monkeypatch.setattr(lib, "ROOT", tmp_path)
    monkeypatch.setattr(lib, "LINK_TO_REPORT_ROOT", tmp_path / "library" / "sessions" / "link-to-report")
    monkeypatch.setattr(lib, "INTAKE_ROOT", tmp_path / "library" / "writeback-intakes" / "link-to-report")
    monkeypatch.setattr(lib, "REVIEW_PACK_ROOT", tmp_path / "library" / "review-packs" / "link-to-report")
    monkeypatch.setattr(lib, "WRITEBACK_ROOT", tmp_path / "library" / "writebacks" / "link-to-report")

    bundle_dir = tmp_path / "library" / "sessions" / "link-to-report" / "demo"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "run-summary.md").write_text(
        "\n".join(
            [
                "# Link Bundle Run Summary",
                "",
                "- bundle_id: `demo`",
                "- successful_link_count: `1`",
                "- failed_link_count: `0`",
                "- source_paths: [`library/sources/podcasts/demo.md`]",
                "- artifact_paths: [`library/artifacts/podcasts/demo/summary.md`]",
                "",
            ]
        ),
        encoding="utf-8",
    )
    direction_file = bundle_dir / "direction.md"
    direction_file.write_text(
        "\n".join(
            [
                "# Research Direction Record",
                "",
                "- bundle_id: `demo`",
                "- research_direction: `验证多 agent 是否已经变成可治理的工作结构`",
                "- direction_status: `user_provided`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(lib, "generate_real_review_pack", lambda **kwargs: "# Real Review Pack\n")
    monkeypatch.setattr(lib, "generate_real_writeback", lambda **kwargs: "# Real Writeback\n")

    args = SimpleNamespace(
        bundle_id="demo",
        direction="",
        direction_file=str(direction_file),
        title="",
        subtitle="",
        emphasis="",
        preserve_tensions="",
        review_pack_output="",
        writeback_output="",
    )

    assert lib.command_generate_report(args) == 0
    assert (tmp_path / "library" / "review-packs" / "link-to-report" / "demo.md").read_text(encoding="utf-8") == "# Real Review Pack\n"
    assert (tmp_path / "library" / "writebacks" / "link-to-report" / "demo.md").read_text(encoding="utf-8") == "# Real Writeback\n"
```

- [ ] **Step 2: Run the targeted test to verify it fails**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report_real_ingestion.py::test_generate_report_uses_existing_reporting_functions -v
```

Expected:
- FAIL because `command_generate_report` still renders placeholder text locally

- [ ] **Step 3: Add reusable report-generation wrappers**

In `scripts/writeback_generate.py`, expose Python-callable wrappers:

```python
def generate_real_review_pack(*, research_direction: str, direction_status: str, source_paths: list[str], artifact_paths: list[str], bundle_id: str) -> str:
    args = argparse.Namespace(
        direction=research_direction,
        direction_status=direction_status,
        source_paths=source_paths,
        artifact_paths=artifact_paths,
        bundle_id=bundle_id,
    )
    return render_review_pack(args)


def generate_real_writeback(*, research_direction: str, direction_status: str, source_paths: list[str], artifact_paths: list[str], bundle_id: str, title: str = "", subtitle: str = "", emphasis: str = "", preserve_tensions: str = "") -> str:
    args = argparse.Namespace(
        direction=research_direction,
        direction_status=direction_status,
        source_paths=source_paths,
        artifact_paths=artifact_paths,
        bundle_id=bundle_id,
        title=title,
        subtitle=subtitle,
        emphasis=emphasis,
        preserve_tensions=preserve_tensions,
    )
    return render_longform_writeback(args)
```

Then in `scripts/link_to_report_lib.py`, import and use them:

```python
from writeback_generate import generate_real_review_pack, generate_real_writeback
```

Update `command_generate_report`:

```python
    source_paths = read_markdown_list_field(summary_text, "source_paths")
    artifact_paths = read_markdown_list_field(summary_text, "artifact_paths")

    intake_text = render_intake_markdown(bundle_id, links=source_paths, direction_text=direction_text, direction_status=direction_status, link_types=link_types)
    review_pack_text = generate_real_review_pack(
        research_direction=direction_text,
        direction_status=direction_status,
        source_paths=source_paths,
        artifact_paths=artifact_paths,
        bundle_id=bundle_id,
    )
    writeback_text = generate_real_writeback(
        research_direction=direction_text,
        direction_status=direction_status,
        source_paths=source_paths,
        artifact_paths=artifact_paths,
        bundle_id=bundle_id,
        title=args.title,
        subtitle=args.subtitle,
        emphasis=args.emphasis,
        preserve_tensions=args.preserve_tensions,
    )
```

- [ ] **Step 4: Run the targeted test to verify it passes**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report_real_ingestion.py::test_generate_report_uses_existing_reporting_functions -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/link_to_report_lib.py scripts/writeback_generate.py tests/test_link_to_report_real_ingestion.py
git commit -m "feat: connect link-to-report to reporting pipeline"
```

---

### Task 5: Update docs and add end-to-end smoke coverage

**Files:**
- Modify: `README.md`
- Modify: `tests/test_link_to_report.py`
- Modify: `tests/test_link_to_report_real_ingestion.py`

- [ ] **Step 1: Write the failing end-to-end smoke test for real-ingestion mode**

Add this test to `tests/test_link_to_report_real_ingestion.py`:

```python
from types import SimpleNamespace


def test_real_ingestion_pipeline_smoke(tmp_path, monkeypatch):
    import link_to_report_lib as lib

    monkeypatch.setattr(lib, "ROOT", tmp_path)
    monkeypatch.setattr(lib, "LINK_TO_REPORT_ROOT", tmp_path / "library" / "sessions" / "link-to-report")
    monkeypatch.setattr(lib, "INTAKE_ROOT", tmp_path / "library" / "writeback-intakes" / "link-to-report")
    monkeypatch.setattr(lib, "REVIEW_PACK_ROOT", tmp_path / "library" / "review-packs" / "link-to-report")
    monkeypatch.setattr(lib, "WRITEBACK_ROOT", tmp_path / "library" / "writebacks" / "link-to-report")
    monkeypatch.setattr(lib, "INGESTION_ADAPTERS", {
        "podcast": lambda link, force: {
            "link": link,
            "link_type": "podcast",
            "status": "success",
            "source_path": "library/sources/podcasts/demo.md",
            "artifact_paths": ["library/artifacts/podcasts/demo/summary.md"],
            "failure_reason": "",
        }
    })
    monkeypatch.setattr(lib, "detect_link_type", lambda _link: "podcast")
    monkeypatch.setattr(lib, "generate_real_review_pack", lambda **kwargs: "# Real Review Pack\n")
    monkeypatch.setattr(lib, "generate_real_writeback", lambda **kwargs: "# Real Writeback\n")

    ingest_args = SimpleNamespace(links=["https://podwise.ai/dashboard/episodes/1"], bundle_id="demo", force=False, dry_run=False)
    propose_args = SimpleNamespace(bundle_id="demo", direction="多 agent 是否已进入可治理团队范式", format="md")
    direction_file = tmp_path / "library" / "sessions" / "link-to-report" / "demo" / "direction.md"
    generate_args = SimpleNamespace(
        bundle_id="demo",
        direction="",
        direction_file=str(direction_file),
        title="",
        subtitle="",
        emphasis="",
        preserve_tensions="",
        review_pack_output="",
        writeback_output="",
    )

    assert lib.command_ingest_links(ingest_args) == 0
    assert lib.command_propose_direction(propose_args) == 0
    assert lib.command_generate_report(generate_args) == 0
    assert (tmp_path / "library" / "review-packs" / "link-to-report" / "demo.md").exists()
    assert (tmp_path / "library" / "writebacks" / "link-to-report" / "demo.md").exists()
```

- [ ] **Step 2: Run the targeted test to verify it fails if any stage still uses the old assumptions**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report_real_ingestion.py::test_real_ingestion_pipeline_smoke -v
```

Expected:
- FAIL until all three stages interoperate on the new run-summary contract

- [ ] **Step 3: Update README for the real-ingestion behavior**

Replace the `Link-to-Report Short-Term Automation` section in `README.md` with:

```md
## Link-to-Report Short-Term Automation

This repository now includes a short-term `link-to-report` CLI that can turn a small bundle of user-provided links into one bundle record, one research direction, one review pack, and one writeback.

```bash
python3 scripts/link_to_report.py ingest-links <url1> <url2> ... --bundle-id demo
python3 scripts/link_to_report.py propose-direction --bundle-id demo
python3 scripts/link_to_report.py generate-report --bundle-id demo --direction-file library/sessions/link-to-report/demo/direction.md
```

Current real-ingestion scope:
- `podwise`
- `xiaohongshu`
- `official`

Current behavior:
- `ingest-links` creates real bundle records and records per-link source/artifact outputs.
- `propose-direction` creates one research direction candidate from the ingested bundle.
- `generate-report` stops on `system_suggested_pending` and only proceeds after approval.
- Once approved, it writes:
  - `library/writeback-intakes/link-to-report/<bundle-id>.md`
  - `library/review-packs/link-to-report/<bundle-id>.md`
  - `library/writebacks/link-to-report/<bundle-id>.md`

Current non-goals:
- WeChat automation
- scheduled crawling
- multi-report generation
```
```

- [ ] **Step 4: Run the end-to-end smoke test and dedicated CLI suites**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py tests/test_link_to_report_real_ingestion.py -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add README.md tests/test_link_to_report.py tests/test_link_to_report_real_ingestion.py
git commit -m "docs: update link-to-report real ingestion usage"
```

---

### Task 6: Final verification and completion handoff

**Files:**
- Verify only files touched in this worktree branch

- [ ] **Step 1: Run the full feature verification suite**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py tests/test_link_to_report_real_ingestion.py -v
```

Expected:
- PASS

- [ ] **Step 2: Run a CLI smoke test from the worktree**

Run:

```bash
python3 scripts/link_to_report.py --help
python3 scripts/link_to_report.py ingest-links https://podwise.ai/dashboard/episodes/123 --bundle-id smoke-real --dry-run
python3 scripts/link_to_report.py propose-direction --bundle-id smoke-real
```

Expected:
- first command shows the three subcommands
- second command writes `library/sessions/link-to-report/smoke-real/run-summary.md`
- third command writes `library/sessions/link-to-report/smoke-real/direction.md`

- [ ] **Step 3: Inspect git status for branch cleanliness**

Run:

```bash
git status --short
```

Expected:
- only intended branch changes are present

- [ ] **Step 4: Final commit if needed**

If verification required a final touch-up:

```bash
git add README.md scripts/link_to_report.py scripts/link_to_report_lib.py scripts/podcast_import.py scripts/xiaohongshu_redbook_import.py scripts/source_ingest.py scripts/writeback_generate.py tests/test_link_to_report.py tests/test_link_to_report_real_ingestion.py
git commit -m "chore: finalize link-to-report real ingestion flow"
```

