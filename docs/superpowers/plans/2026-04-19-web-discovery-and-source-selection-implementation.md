# Web Discovery And Source Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a discovery layer that turns a topic, brand, or research direction into a reviewed list of source candidates before ingestion and reporting.

**Architecture:** Extend the existing `link-to-report` system with a discovery-first pre-ingestion stage. The new layer will generate normalized source candidates, classify them by authority and mode (`discovery`, `official-update`, `research-guided collection`), and hand approved URLs into the existing ingestion pipeline instead of bypassing it.

**Tech Stack:** Python 3, existing CLI scripts under `scripts/`, Markdown/YAML seed files under `seed/` and `library/sessions/`, `pytest`

---

## File Structure

### Files to Create
- `scripts/web_discovery.py`
  - Single responsibility: turn a discovery request into normalized source candidates and write them to a bundle-scoped discovery record.
- `tests/test_web_discovery.py`
  - Focused coverage for normalization, authority classification, mode handling, and candidate record rendering.
- `seed/discovery-topics.yaml`
  - Curated topic bootstrap file for common domains, brands, and source preferences.

### Files to Modify
- `scripts/link_to_report.py`
  - Add discovery-oriented subcommands without breaking current `ingest-links / propose-direction / generate-report`.
- `scripts/link_to_report_lib.py`
  - Reuse bundle/session roots and connect approved discovery results to `ingest-links`.
- `README.md`
  - Explain the new `web discovery -> source selection -> ingest -> report` flow.
- `tests/test_link_to_report.py`
  - Add CLI coverage for discovery subcommands and approved-source handoff.

### Existing Inputs to Reuse
- `seed/official-sources.yaml`
- `seed/watch-profile.yaml`
- `scripts/source_ingest.py`
- `scripts/link_to_report.py`
- `scripts/link_to_report_lib.py`

---

### Task 1: Add Failing Tests for Discovery Candidate Normalization

**Files:**
- Create: `tests/test_web_discovery.py`
- Reference: `scripts/link_to_report_lib.py`, `seed/official-sources.yaml`

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path
import importlib.util


def load_web_discovery():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "web_discovery.py"
    spec = importlib.util.spec_from_file_location("web_discovery", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_normalize_source_candidate_contains_required_fields():
    mod = load_web_discovery()

    candidate = mod.normalize_source_candidate(
        title="Google Gemini on Android",
        url="https://blog.google/products/android/gemini-android/",
        source_type="official_update",
        platform="official_site",
        authority="official",
        why_relevant="Covers Gemini as an on-device/system AI entry point.",
    )

    assert candidate["title"] == "Google Gemini on Android"
    assert candidate["url"] == "https://blog.google/products/android/gemini-android/"
    assert candidate["source_type"] == "official_update"
    assert candidate["platform"] == "official_site"
    assert candidate["authority"] == "official"
    assert candidate["why_relevant"]


def test_render_discovery_record_groups_candidates_by_authority():
    mod = load_web_discovery()
    text = mod.render_discovery_record(
        request_id="ai-phone-demo",
        mode="discovery",
        topic="AI 手机",
        candidates=[
            {
                "title": "Apple Intelligence",
                "url": "https://www.apple.com/apple-intelligence/",
                "source_type": "official_update",
                "platform": "official_site",
                "authority": "official",
                "why_relevant": "Official product framing.",
            },
            {
                "title": "AI 手机综述",
                "url": "https://example.com/ai-phone-overview",
                "source_type": "structured_commentary",
                "platform": "web",
                "authority": "structured_commentary",
                "why_relevant": "Cross-vendor comparison.",
            },
        ],
    )

    assert "# Web Discovery Record" in text
    assert "## Official" in text
    assert "## Structured Commentary" in text
    assert "Apple Intelligence" in text
    assert "AI 手机综述" in text
```

- [ ] **Step 2: Run the new test file to verify failure**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_web_discovery.py -q
```

Expected:

```text
FAILED tests/test_web_discovery.py::test_normalize_source_candidate_contains_required_fields
FAILED tests/test_web_discovery.py::test_render_discovery_record_groups_candidates_by_authority
E   FileNotFoundError: .../scripts/web_discovery.py
```

- [ ] **Step 3: Commit the failing tests**

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
git add tests/test_web_discovery.py
git commit -m "test: add web discovery candidate coverage"
```

### Task 2: Implement the Discovery Candidate Module

**Files:**
- Create: `scripts/web_discovery.py`
- Create: `seed/discovery-topics.yaml`
- Test: `tests/test_web_discovery.py`

- [ ] **Step 1: Add the minimal discovery candidate implementation**

```python
from __future__ import annotations

from pathlib import Path
from typing import Any


def normalize_source_candidate(
    *,
    title: str,
    url: str,
    source_type: str,
    platform: str,
    authority: str,
    why_relevant: str,
) -> dict[str, str]:
    return {
        "title": title.strip(),
        "url": url.strip(),
        "source_type": source_type.strip(),
        "platform": platform.strip(),
        "authority": authority.strip(),
        "why_relevant": why_relevant.strip(),
    }


def render_discovery_record(
    *,
    request_id: str,
    mode: str,
    topic: str,
    candidates: list[dict[str, str]],
) -> str:
    grouped: dict[str, list[dict[str, str]]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate["authority"], []).append(candidate)

    sections: list[str] = [
        "# Web Discovery Record",
        "",
        f"- request_id: `{request_id}`",
        f"- mode: `{mode}`",
        f"- topic: `{topic}`",
        "",
    ]
    title_map = {
        "official": "Official",
        "first_hand_operator": "First-Hand Operator",
        "structured_commentary": "Structured Commentary",
        "social_signal": "Social Signal",
    }
    for authority in ["official", "first_hand_operator", "structured_commentary", "social_signal"]:
        items = grouped.get(authority, [])
        if not items:
            continue
        sections.extend([f"## {title_map[authority]}", ""])
        for item in items:
            sections.extend(
                [
                    f"- [{item['title']}]({item['url']})",
                    f"  - source_type: `{item['source_type']}`",
                    f"  - platform: `{item['platform']}`",
                    f"  - why_relevant: {item['why_relevant']}",
                ]
            )
        sections.append("")
    return "\n".join(sections)
```

- [ ] **Step 2: Add a small bootstrap topic file**

Create `seed/discovery-topics.yaml`:

```yaml
domains:
  - ai手机
  - agent手机
  - agentos
  - 具身智能

brands:
  - Apple
  - Google
  - Samsung
  - Xiaomi
  - Honor
  - OPPO
  - vivo
  - Huawei

preferred_source_types:
  - official_update
  - structured_commentary
  - social_signal
```

- [ ] **Step 3: Run the focused discovery tests**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_web_discovery.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 4: Commit the discovery module**

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
git add scripts/web_discovery.py seed/discovery-topics.yaml tests/test_web_discovery.py
git commit -m "feat: add web discovery candidate module"
```

### Task 3: Add CLI Discovery Commands

**Files:**
- Modify: `scripts/link_to_report.py`
- Modify: `scripts/link_to_report_lib.py`
- Modify: `tests/test_link_to_report.py`

- [ ] **Step 1: Add failing CLI tests for discovery subcommands**

```python
def test_link_to_report_help_shows_discovery_commands():
    result = subprocess.run(
        [sys.executable, "scripts/link_to_report.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "discover-web" in result.stdout
    assert "approve-sources" in result.stdout
```

- [ ] **Step 2: Run the targeted CLI test to verify failure**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k discovery -q
```

Expected:

```text
FAILED tests/test_link_to_report.py::test_link_to_report_help_shows_discovery_commands
```

- [ ] **Step 3: Extend the CLI surface**

Update `scripts/link_to_report.py` to add:

```python
from link_to_report_lib import (
    command_approve_sources,
    command_discover_web,
    command_generate_report,
    command_ingest_links,
    command_propose_direction,
)
```

Add new subcommands:

```python
discover = subparsers.add_parser("discover-web", help="Create a discovery record for a topic or brand.")
discover.add_argument("--request-id", required=True)
discover.add_argument("--mode", choices=["discovery", "official-update", "research-guided-collection"], default="discovery")
discover.add_argument("--topic", required=True)
discover.add_argument("--brands", default="")

approve = subparsers.add_parser("approve-sources", help="Approve selected candidate URLs into a link bundle.")
approve.add_argument("--request-id", required=True)
approve.add_argument("--bundle-id", required=True)
approve.add_argument("urls", nargs="+")
```

Wire them in `main()`:

```python
if args.command == "discover-web":
    return command_discover_web(args)
if args.command == "approve-sources":
    return command_approve_sources(args)
```

- [ ] **Step 4: Add minimal implementations in `link_to_report_lib.py`**

```python
web_discovery = load_script_module("web_discovery.py", "web_discovery")
normalize_source_candidate = web_discovery.normalize_source_candidate
render_discovery_record = web_discovery.render_discovery_record

DISCOVERY_ROOT = ROOT / "library" / "sessions" / "web-discovery"


def command_discover_web(args: argparse.Namespace) -> int:
    request_id = slugify_bundle_id(args.request_id)
    candidates = [
        normalize_source_candidate(
            title=args.topic,
            url="manual://candidate",
            source_type="structured_commentary",
            platform="web",
            authority="structured_commentary",
            why_relevant=f"Discovery placeholder for topic: {args.topic}",
        )
    ]
    record = render_discovery_record(
        request_id=request_id,
        mode=args.mode,
        topic=args.topic,
        candidates=candidates,
    )
    path = DISCOVERY_ROOT / request_id / "discovery.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(record, encoding="utf-8")
    print(path.relative_to(ROOT))
    return 0


def command_approve_sources(args: argparse.Namespace) -> int:
    return command_ingest_links(
        argparse.Namespace(
            links=list(args.urls),
            bundle_id=args.bundle_id,
            force=False,
            dry_run=False,
        )
    )
```

- [ ] **Step 5: Run the CLI test slice**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k "discovery or approve" -q
```

Expected:

```text
passed
```

- [ ] **Step 6: Commit the CLI expansion**

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
git add scripts/link_to_report.py scripts/link_to_report_lib.py tests/test_link_to_report.py
git commit -m "feat: add web discovery cli entry points"
```

### Task 4: Normalize Discovery Records Into Approved Link Bundles

**Files:**
- Modify: `tests/test_link_to_report.py`
- Modify: `scripts/link_to_report_lib.py`

- [ ] **Step 1: Add a failing test for approved-source handoff**

```python
def test_approve_sources_hands_urls_to_ingest_bundle(monkeypatch):
    lib = load_link_to_report_lib_module()
    captured = {}

    def fake_command_ingest_links(args):
        captured["links"] = args.links
        captured["bundle_id"] = args.bundle_id
        return 0

    monkeypatch.setattr(lib, "command_ingest_links", fake_command_ingest_links)

    result = lib.command_approve_sources(
        argparse.Namespace(
            request_id="ai-phone-demo",
            bundle_id="ai-phone-bundle",
            urls=["https://www.apple.com/apple-intelligence/"],
        )
    )

    assert result == 0
    assert captured["bundle_id"] == "ai-phone-bundle"
    assert captured["links"] == ["https://www.apple.com/apple-intelligence/"]
```

- [ ] **Step 2: Run the targeted test**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k approve_sources_hands_urls -q
```

Expected:

```text
FAILED before the handoff implementation is correct
```

- [ ] **Step 3: Harden approval behavior**

Update `command_approve_sources(...)` to:
- reject empty URL lists
- preserve URL order
- forward directly into `command_ingest_links(...)`

Keep the implementation:

```python
if not args.urls:
    print("urls are required for approve-sources", file=sys.stderr)
    return 2
```

- [ ] **Step 4: Re-run the targeted test**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k approve_sources_hands_urls -q
```

Expected:

```text
1 passed
```

- [ ] **Step 5: Commit the handoff logic**

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
git add scripts/link_to_report_lib.py tests/test_link_to_report.py
git commit -m "feat: hand approved discovery urls into bundles"
```

### Task 5: Document the Discovery-First Workflow

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add README usage section**

Append a short section like:

```md
## Web Discovery And Source Selection

Use discovery when you want to start from a topic, not from pre-collected links:

```bash
python3 scripts/link_to_report.py discover-web --request-id ai-phone --mode discovery --topic "AI 手机"
python3 scripts/link_to_report.py approve-sources --request-id ai-phone --bundle-id ai-phone-bundle https://www.apple.com/apple-intelligence/
python3 scripts/link_to_report.py propose-direction --bundle-id ai-phone-bundle
python3 scripts/link_to_report.py generate-report --bundle-id ai-phone-bundle --direction-file library/sessions/link-to-report/ai-phone-bundle/direction.md
```

The discovery stage creates candidate sources. It does not bypass `Source -> Artifact -> Review Pack -> Writeback`.
```

- [ ] **Step 2: Run a minimal CLI smoke test**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
python3 scripts/link_to_report.py --help
```

Expected:

```text
discover-web
approve-sources
ingest-links
propose-direction
generate-report
```

- [ ] **Step 3: Commit the docs update**

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
git add README.md
git commit -m "docs: add web discovery workflow usage"
```

### Task 6: Run the Full Relevant Test Slice

**Files:**
- Test: `tests/test_web_discovery.py`
- Test: `tests/test_link_to_report.py`
- Test: `tests/test_link_to_report_real_ingestion.py`

- [ ] **Step 1: Run the full relevant test slice**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_web_discovery.py tests/test_link_to_report.py tests/test_link_to_report_real_ingestion.py -q
```

Expected:

```text
all selected tests passed
```

- [ ] **Step 2: Commit the verified state**

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
git add scripts/web_discovery.py scripts/link_to_report.py scripts/link_to_report_lib.py seed/discovery-topics.yaml README.md tests/test_web_discovery.py tests/test_link_to_report.py
git commit -m "feat: add web discovery and source selection flow"
```

---

## Self-Review

### Spec coverage
- `websearch` boundary as discovery rather than crawler: Tasks 2, 3, 5.
- three working modes: Task 3 CLI surface.
- authority-based source normalization: Tasks 1-2.
- `web result -> Source -> Artifact` rather than direct report generation: Tasks 3-4 and README in Task 5.
- human-in-the-loop approval before ingestion/reporting: Task 4 and Task 5.

### Placeholder scan
- No `TODO`, `TBD`, or “implement later” placeholders remain in task steps.
- Each code step includes concrete code or explicit behavior.
- Each test step includes exact commands and expected outcomes.

### Type consistency
- Discovery object names remain consistent:
  - `normalize_source_candidate`
  - `render_discovery_record`
  - `command_discover_web`
  - `command_approve_sources`
- Existing `link-to-report` commands are preserved unchanged.

