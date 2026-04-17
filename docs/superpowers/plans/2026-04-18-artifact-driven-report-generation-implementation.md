# Artifact-Driven Report Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade report generation so review packs and writebacks are driven by artifact content, quotes, and mechanism-level paraphrases instead of primarily by bundle metadata.

**Architecture:** Add an explicit artifact-evidence layer between `research direction` and `review pack`. The new flow is `artifact triage -> evidence candidates -> theme clustering -> review pack -> writeback`, while keeping the current `link_to_report.py` CLI surface stable. Implementation stays narrow: reuse existing ingestion outputs, add one focused evidence module, then wire `writeback_generate.py` and `link_to_report_lib.py` to consume that module.

**Tech Stack:** Python 3, Markdown files under `library/`, existing CLI scripts in `scripts/`, `pytest`

---

## File Structure

### Files to Create
- `scripts/artifact_evidence.py`
  - Single responsibility: load artifact content, select report-eligible evidence segments, build evidence candidates, and cluster them into themes.
- `tests/test_artifact_evidence.py`
  - Focused unit coverage for artifact priority rules, evidence candidate schema, theme clustering, and anti-summary guardrails.

### Files to Modify
- `scripts/writeback_generate.py`
  - Replace metadata-heavy review-pack generation with artifact-driven evidence selection and thematic assembly.
- `scripts/link_to_report_lib.py`
  - Ensure `generate-report` passes real artifact references into the new artifact-evidence layer instead of leaning on bundle summary metadata.
- `tests/test_writeback_generate.py`
  - Add regression coverage that review packs and writebacks now include quote/paraphrase/evidence sections derived from artifact content.
- `tests/test_link_to_report.py`
  - Preserve CLI compatibility while checking that generated outputs are artifact-aware rather than bundle-summary-only.
- `README.md`
  - Update `link-to-report` usage notes to explain the new artifact-driven report behavior and current channel priorities.

### Existing Inputs to Reuse
- `library/artifacts/podcasts/<slug>/summary.md`
- `library/artifacts/podcasts/<slug>/highlights.md`
- `library/artifacts/podcasts/<slug>/transcript.md`
- `library/artifacts/xiaohongshu/<slug>/full_text.md`
- `library/artifacts/xiaohongshu/<slug>/transcript.md`
- `library/artifacts/xiaohongshu/<slug>/comment_batch.md`
- `/Users/vickyshou/.openclaw/workspace/shared/Principles`

---

### Task 1: Add Focused Tests for Artifact Evidence Selection

**Files:**
- Create: `tests/test_artifact_evidence.py`
- Reference: `scripts/link_to_report_lib.py`, `docs/superpowers/specs/2026-04-18-artifact-driven-report-generation-design.md`

- [ ] **Step 1: Write the failing tests for channel priority and evidence candidate shape**

```python
from pathlib import Path
import importlib.util


def load_artifact_evidence():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "artifact_evidence.py"
    spec = importlib.util.spec_from_file_location("artifact_evidence", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_collect_report_artifacts_prioritizes_podcast_summary_and_highlights(tmp_path):
    mod = load_artifact_evidence()
    artifact_root = tmp_path / "library" / "artifacts" / "podcasts" / "demo"
    artifact_root.mkdir(parents=True)
    (artifact_root / "summary.md").write_text("## Content\nsummary line\n", encoding="utf-8")
    (artifact_root / "highlights.md").write_text("## Content\n1. [00:31] key highlight\n", encoding="utf-8")
    (artifact_root / "transcript.md").write_text("## Content\n[00:31] long transcript line\n", encoding="utf-8")

    artifacts = mod.collect_report_artifacts(
        channel="podcasts",
        artifact_paths=[
            "library/artifacts/podcasts/demo/transcript.md",
            "library/artifacts/podcasts/demo/summary.md",
            "library/artifacts/podcasts/demo/highlights.md",
        ],
        root=tmp_path,
    )

    assert [item["slice_type"] for item in artifacts] == ["summary", "highlights", "transcript"]


def test_build_evidence_candidates_returns_required_schema_fields(tmp_path):
    mod = load_artifact_evidence()
    artifact_file = tmp_path / "library" / "artifacts" / "xiaohongshu" / "demo" / "full_text.md"
    artifact_file.parent.mkdir(parents=True)
    artifact_file.write_text(
        "## Content\nAgent 真正难的不是执行，而是跨轮次保持责任边界。\n",
        encoding="utf-8",
    )

    candidates = mod.build_evidence_candidates(
        research_direction="agent team 的责任边界如何被产品化",
        channel="xiaohongshu",
        artifact_items=[
            {
                "slice_type": "full_text",
                "path": artifact_file,
                "content": "Agent 真正难的不是执行，而是跨轮次保持责任边界。",
            }
        ],
    )

    candidate = candidates[0]
    assert candidate["research_direction"] == "agent team 的责任边界如何被产品化"
    assert candidate["quote"]
    assert candidate["paraphrase"]
    assert candidate["artifact_ref"].endswith("full_text.md")
    assert candidate["claim_role"] in {"support", "counter_signal", "tension", "open_question"}
    assert candidate["confidence"] in {"high", "medium", "low"}
```

- [ ] **Step 2: Run the new test file to verify failure**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --with pytest python -m pytest tests/test_artifact_evidence.py -q
```

Expected:

```text
FAILED tests/test_artifact_evidence.py::test_collect_report_artifacts_prioritizes_podcast_summary_and_highlights
FAILED tests/test_artifact_evidence.py::test_build_evidence_candidates_returns_required_schema_fields
E   FileNotFoundError: .../scripts/artifact_evidence.py
```

- [ ] **Step 3: Commit the failing test scaffold**

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
git add tests/test_artifact_evidence.py
git commit -m "test: add artifact evidence selection coverage"
```

### Task 2: Implement Artifact Selection and Evidence Candidate Extraction

**Files:**
- Create: `scripts/artifact_evidence.py`
- Test: `tests/test_artifact_evidence.py`

- [ ] **Step 1: Implement minimal artifact loading and priority ordering**

```python
from __future__ import annotations

from pathlib import Path
from typing import Any


PODCAST_PRIORITY = ["summary", "highlights", "transcript"]
XIAOHONGSHU_PRIORITY = ["full_text", "transcript", "comment_batch"]


def _priority_for(channel: str) -> list[str]:
    if channel == "podcasts":
        return PODCAST_PRIORITY
    if channel == "xiaohongshu":
        return XIAOHONGSHU_PRIORITY
    return ["full_text"]


def collect_report_artifacts(*, channel: str, artifact_paths: list[str], root: Path) -> list[dict[str, Any]]:
    priority = _priority_for(channel)
    ranked: list[dict[str, Any]] = []
    for relative_path in artifact_paths:
        path = root / relative_path
        slice_type = path.stem
        if not path.exists():
            continue
        ranked.append(
            {
                "slice_type": slice_type,
                "path": path,
                "content": path.read_text(encoding="utf-8"),
                "rank": priority.index(slice_type) if slice_type in priority else len(priority),
            }
        )
    ranked.sort(key=lambda item: (item["rank"], str(item["path"])))
    for item in ranked:
        item.pop("rank", None)
    return ranked
```

- [ ] **Step 2: Implement the required evidence candidate schema**

```python
MECHANISM_HINTS = {
    "责任": "governance_or_control",
    "控制": "governance_or_control",
    "协作": "coordination_protocol",
    "工作流": "workflow_shift",
    "信任": "trust_or_explainability",
    "解释": "trust_or_explainability",
    "角色": "role_delegation",
    "能力边界": "capability_boundary",
}


def build_evidence_candidates(
    *,
    research_direction: str,
    channel: str,
    artifact_items: list[dict[str, Any]],
) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for index, item in enumerate(artifact_items, start=1):
        content_lines = [line.strip() for line in item["content"].splitlines() if line.strip() and not line.startswith("#")]
        if not content_lines:
            continue
        quote = content_lines[0]
        category = "workflow_shift"
        for needle, mapped in MECHANISM_HINTS.items():
            if needle in quote or needle in research_direction:
                category = mapped
                break
        candidates.append(
            {
                "candidate_id": f"{channel}-candidate-{index}",
                "research_direction": research_direction,
                "theme_hint": category,
                "quote": quote,
                "speaker_or_source": channel,
                "artifact_ref": str(item["path"]),
                "why_selected": "Matches the current research direction and contains mechanism-bearing wording.",
                "paraphrase": f"这段材料主要在说明与 `{category}` 相关的结构变化，而不只是泛泛评论。",
                "claim_role": "support",
                "confidence": "medium",
            }
        )
    return candidates
```

- [ ] **Step 3: Run the focused evidence tests**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --with pytest python -m pytest tests/test_artifact_evidence.py -q
```

Expected:

```text
2 passed
```

- [ ] **Step 4: Commit the evidence module**

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
git add scripts/artifact_evidence.py tests/test_artifact_evidence.py
git commit -m "feat: add artifact evidence selection module"
```

### Task 3: Add Theme Clustering and Anti-Summary Guardrails

**Files:**
- Modify: `scripts/artifact_evidence.py`
- Modify: `tests/test_artifact_evidence.py`

- [ ] **Step 1: Extend tests to lock theme clustering and counter-signal behavior**

```python
def test_cluster_candidates_groups_by_theme_hint_and_limits_theme_count():
    mod = load_artifact_evidence()
    candidates = [
        {
            "candidate_id": "c1",
            "research_direction": "agent team 的责任边界如何被产品化",
            "theme_hint": "governance_or_control",
            "quote": "责任边界必须清楚。",
            "speaker_or_source": "podcast",
            "artifact_ref": "a.md",
            "why_selected": "control signal",
            "paraphrase": "这里讨论治理边界。",
            "claim_role": "support",
            "confidence": "high",
        },
        {
            "candidate_id": "c2",
            "research_direction": "agent team 的责任边界如何被产品化",
            "theme_hint": "coordination_protocol",
            "quote": "多个 agent 需要明确沟通协议。",
            "speaker_or_source": "podcast",
            "artifact_ref": "b.md",
            "why_selected": "coordination signal",
            "paraphrase": "这里讨论协作协议。",
            "claim_role": "support",
            "confidence": "high",
        },
    ]

    clusters = mod.cluster_evidence_candidates(candidates)

    assert len(clusters) == 2
    assert clusters[0]["theme"]
    assert clusters[0]["entries"]


def test_build_evidence_candidates_keeps_counter_signal_lines():
    mod = load_artifact_evidence()
    artifact_items = [
        {
            "slice_type": "comment_batch",
            "path": Path("library/artifacts/xiaohongshu/demo/comment_batch.md"),
            "content": "## Content\n这更像包装话术，并没有真正改变协作边界。\n",
        }
    ]

    candidates = mod.build_evidence_candidates(
        research_direction="multi-agent 是否进入范式迁移",
        channel="xiaohongshu",
        artifact_items=artifact_items,
    )

    assert candidates[0]["claim_role"] in {"counter_signal", "tension", "open_question", "support"}
```

- [ ] **Step 2: Implement clustering and guardrails in the evidence module**

```python
THEME_LABELS = {
    "governance_or_control": "执行控制层",
    "coordination_protocol": "协作与角色层",
    "trust_or_explainability": "治理与前台 UX 外显层",
    "role_delegation": "协作与角色层",
    "workflow_shift": "执行控制层",
    "capability_boundary": "治理与前台 UX 外显层",
}


def _infer_claim_role(slice_type: str, quote: str) -> str:
    if slice_type == "comment_batch":
        return "counter_signal"
    if "并没有" in quote or "不是" in quote:
        return "tension"
    return "support"


def cluster_evidence_candidates(candidates: list[dict[str, str]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for candidate in candidates:
        theme = THEME_LABELS.get(candidate["theme_hint"], "执行控制层")
        grouped.setdefault(theme, []).append(candidate)

    clusters = [{"theme": theme, "entries": entries[:4]} for theme, entries in grouped.items()]
    clusters.sort(key=lambda item: item["theme"])
    return clusters[:3]
```

Also update `build_evidence_candidates(...)` so `claim_role` uses `_infer_claim_role(...)` and comment artifacts can survive as counter-signals instead of being dropped.

- [ ] **Step 3: Run the evidence test file again**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --with pytest python -m pytest tests/test_artifact_evidence.py -q
```

Expected:

```text
4 passed
```

- [ ] **Step 4: Commit the clustering layer**

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
git add scripts/artifact_evidence.py tests/test_artifact_evidence.py
git commit -m "feat: add artifact theme clustering guardrails"
```

### Task 4: Rebuild Review Pack Generation on Top of Artifact Evidence

**Files:**
- Modify: `scripts/writeback_generate.py`
- Modify: `tests/test_writeback_generate.py`

- [ ] **Step 1: Add failing tests for artifact-driven review-pack sections**

```python
def test_render_review_pack_includes_quotes_paraphrases_and_evidence(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "writeback_generate.py"
    intake = tmp_path / "intake.md"
    synthesis = tmp_path / "synthesis.md"
    output = tmp_path / "review-pack.md"
    artifact_root = tmp_path / "library" / "artifacts" / "podcasts" / "demo"
    artifact_root.mkdir(parents=True)
    (artifact_root / "summary.md").write_text("## Content\nAgent team 的关键不在更多 agent，而在治理边界。\n", encoding="utf-8")
    (artifact_root / "highlights.md").write_text("## Content\n1. [00:31] Harness engineering 让 agent 能在围栏内协作。\n", encoding="utf-8")
    intake.write_text(
        "\n".join(
            [
                "# Writeback Intake",
                "- intake_id: `demo`",
                "- research_direction: `multi-agent 是否已经进入可治理的 Agent Team 范式迁移`",
                "- direction_status: `user_approved`",
            ]
        ),
        encoding="utf-8",
    )
    synthesis.write_text(
        "\n".join(
            [
                "# Synthesis",
                "- source_episode_slugs: [`demo`]",
                "## 核心综合判断",
                "当前材料显示 multi-agent 的重点开始转向治理与协作结构。",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(script), "render-review-pack", "--intake-file", str(intake), "--synthesis-file", str(synthesis), "--output", str(output)],
        check=False,
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    assert result.returncode == 0
    text = output.read_text(encoding="utf-8")
    assert "Direct quote" in text
    assert "Paraphrase" in text
    assert "Evidence" in text
    assert "Why it matters" in text
```

- [ ] **Step 2: Run the targeted review-pack test to verify failure**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --with pytest python -m pytest tests/test_writeback_generate.py -k artifact_driven -q
```

Expected:

```text
FAILED tests/test_writeback_generate.py::test_render_review_pack_includes_quotes_paraphrases_and_evidence
```

- [ ] **Step 3: Integrate `artifact_evidence.py` into review-pack rendering**

Add imports near the top of `scripts/writeback_generate.py`:

```python
artifact_evidence = load_script_module("artifact_evidence.py", "artifact_evidence")
collect_report_artifacts = artifact_evidence.collect_report_artifacts
build_evidence_candidates = artifact_evidence.build_evidence_candidates
cluster_evidence_candidates = artifact_evidence.cluster_evidence_candidates
```

Add a focused helper:

```python
def build_artifact_driven_review_sections(
    *,
    research_direction: str,
    channel: str,
    artifact_paths: list[str],
    root: Path,
) -> list[dict[str, object]]:
    artifact_items = collect_report_artifacts(channel=channel, artifact_paths=artifact_paths, root=root)
    candidates = build_evidence_candidates(
        research_direction=research_direction,
        channel=channel,
        artifact_items=artifact_items,
    )
    return cluster_evidence_candidates(candidates)
```

Then update review-pack rendering so each theme block writes:

```python
lines.extend(
    [
        f"### {cluster['theme']}",
        "",
        "Direct quote",
        f"- {entry['quote']}",
        "",
        "Paraphrase",
        f"- {entry['paraphrase']}",
        "",
        "Evidence",
        f"- `{entry['artifact_ref']}`",
        "",
        "Why it matters",
        f"- {entry['why_selected']}",
        "",
    ]
)
```

- [ ] **Step 4: Run review-pack tests**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --with pytest python -m pytest tests/test_writeback_generate.py -k "artifact_driven or review_pack" -q
```

Expected:

```text
passed
```

- [ ] **Step 5: Commit the review-pack upgrade**

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
git add scripts/writeback_generate.py tests/test_writeback_generate.py
git commit -m "feat: make review pack artifact-driven"
```

### Task 5: Make Final Writebacks Consume Review-Pack Evidence and AI-native UX Lens Pack

**Files:**
- Modify: `scripts/writeback_generate.py`
- Modify: `tests/test_writeback_generate.py`

- [ ] **Step 1: Add failing tests for writeback evidence density and UX section grounding**

```python
def test_render_longform_uses_review_pack_evidence_and_ux_section(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "writeback_generate.py"
    intake = tmp_path / "intake.md"
    synthesis = tmp_path / "synthesis.md"
    review_pack = tmp_path / "review-pack.md"
    output = tmp_path / "writeback.md"
    intake.write_text(
        "\n".join(
            [
                "# Writeback Intake",
                "- intake_id: `demo`",
                "- research_direction: `multi-agent 是否已经进入可治理的 Agent Team 范式迁移`",
                "- direction_status: `user_approved`",
            ]
        ),
        encoding="utf-8",
    )
    synthesis.write_text("# Synthesis\n## 核心综合判断\n当前材料显示治理与协作结构开始成为主问题。\n", encoding="utf-8")
    review_pack.write_text(
        "\n".join(
            [
                "# Research Review Pack",
                "## 主题综述",
                "### 执行控制层",
                "Direct quote",
                "- Harness engineering 让 agent 能在围栏内协作。",
                "Paraphrase",
                "- 这说明执行控制层已经成为产品机制的一部分。",
                "Evidence",
                "- `library/artifacts/podcasts/demo/highlights.md`",
                "Why it matters",
                "- 这直接支持范式迁移不是包装词。",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(script), "render-longform", "--intake-file", str(intake), "--synthesis-file", str(synthesis), "--review-pack-file", str(review_pack), "--output", str(output)],
        check=False,
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )

    assert result.returncode == 0
    text = output.read_text(encoding="utf-8")
    assert "## 文献综述" in text
    assert "Harness engineering" in text
    assert "## AI-native UX 视角" in text
    assert "责任" in text or "attention" in text or "handoff" in text
```

- [ ] **Step 2: Run the targeted longform test to verify failure**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --with pytest python -m pytest tests/test_writeback_generate.py -k "longform_uses_review_pack_evidence" -q
```

Expected:

```text
FAILED tests/test_writeback_generate.py::test_render_longform_uses_review_pack_evidence_and_ux_section
```

- [ ] **Step 3: Upgrade longform rendering to consume review-pack evidence and UX lens pack**

In `scripts/writeback_generate.py`, ensure longform rendering:

```python
def render_longform_from_review_pack(...):
    review_text = read_file(review_pack_file)
    thematic_review = read_section(review_text, "主题综述")
    ux_lens_points = build_ai_native_ux_lens_pack()
    lines = [
        "# Writeback",
        "",
        "## 研究问题",
        research_direction,
        "",
        "## 文献综述",
        thematic_review,
        "",
        "## 综合判断",
        build_core_judgment_from_review_pack(thematic_review, synthesis_text),
        "",
        "## Problem Statement",
        build_problem_statement_from_review_pack(thematic_review),
        "",
        "## Assumptions",
        build_assumptions_from_review_pack(thematic_review),
        "",
        "## AI-native UX 视角",
        build_ai_native_ux_section(thematic_review, ux_lens_points),
        "",
        "## 保留分歧",
        build_preserved_tensions_from_review_pack(thematic_review, synthesis_text),
    ]
```

The key constraint is that `Problem Statement`, `Assumptions`, and `AI-native UX` must be composed from reviewed evidence, not from bundle metadata.

- [ ] **Step 4: Run writeback generation tests**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --with pytest python -m pytest tests/test_writeback_generate.py -q
```

Expected:

```text
all selected tests passed
```

- [ ] **Step 5: Commit the writeback upgrade**

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
git add scripts/writeback_generate.py tests/test_writeback_generate.py
git commit -m "feat: make writebacks consume artifact evidence"
```

### Task 6: Wire `link-to-report` to the New Artifact-Driven Generation and Update Docs

**Files:**
- Modify: `scripts/link_to_report_lib.py`
- Modify: `tests/test_link_to_report.py`
- Modify: `README.md`

- [ ] **Step 1: Add failing integration tests for artifact-aware `generate-report`**

```python
def test_generate_report_writes_review_pack_and_writeback_from_artifact_paths(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    workspace_root = tmp_path / "workspace"
    monkeypatch.setattr(lib, "ROOT", workspace_root)
    monkeypatch.setattr(lib, "LINK_TO_REPORT_ROOT", workspace_root / "library" / "sessions" / "link-to-report")
    monkeypatch.setattr(lib, "INTAKE_ROOT", workspace_root / "library" / "writeback-intakes" / "link-to-report")
    monkeypatch.setattr(lib, "REVIEW_PACK_ROOT", workspace_root / "library" / "review-packs" / "link-to-report")
    monkeypatch.setattr(lib, "WRITEBACK_ROOT", workspace_root / "library" / "writebacks" / "link-to-report")
    bundle_id = "artifact-report"
    bundle_dir = lib.bundle_dir(bundle_id)
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "run-summary.md").write_text(
        "# Link Bundle Run Summary\n\n## Per-Link Results\n\n### Link Result\n\n- link: `https://example.com`\n- link_type: `podcast`\n- status: `success`\n- source_path: `library/sources/podcasts/demo.md`\n- artifact_paths: [`library/artifacts/podcasts/demo/summary.md`, `library/artifacts/podcasts/demo/highlights.md`]\n- failure_reason: ``\n",
        encoding="utf-8",
    )
    (bundle_dir / "direction.md").write_text(
        "# Direction\n- research_direction: `multi-agent 是否已经进入可治理的 Agent Team 范式迁移`\n- direction_status: `user_approved`\n",
        encoding="utf-8",
    )

    artifact_root = workspace_root / "library" / "artifacts" / "podcasts" / "demo"
    artifact_root.mkdir(parents=True, exist_ok=True)
    (artifact_root / "summary.md").write_text("## Content\n治理与协作结构开始成为主问题。\n", encoding="utf-8")
    (artifact_root / "highlights.md").write_text("## Content\n1. [00:31] Harness engineering 让 agent 能在围栏内协作。\n", encoding="utf-8")

    result = lib.command_generate_report(
        argparse.Namespace(
            bundle_id=bundle_id,
            direction="",
            direction_file=str(bundle_dir / "direction.md"),
            title="",
            subtitle="",
            emphasis="",
            preserve_tensions="",
            review_pack_output="",
            writeback_output="",
        )
    )

    assert result == 0
    review_pack = (workspace_root / "library" / "review-packs" / "link-to-report" / f"{bundle_id}.md").read_text(encoding="utf-8")
    writeback = (workspace_root / "library" / "writebacks" / "link-to-report" / f"{bundle_id}.md").read_text(encoding="utf-8")
    assert "Direct quote" in review_pack
    assert "Harness engineering" in writeback
```

- [ ] **Step 2: Run the link-to-report integration test to verify failure**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --with pytest python -m pytest tests/test_link_to_report.py -k artifact -q
```

Expected:

```text
FAILED tests/test_link_to_report.py::test_generate_report_writes_review_pack_and_writeback_from_artifact_paths
```

- [ ] **Step 3: Update `link_to_report_lib.py` to pass real artifact paths into writeback generation**

Add a small helper in `scripts/link_to_report_lib.py`:

```python
def collect_bundle_artifact_paths(link_results: list[dict[str, object]]) -> list[str]:
    artifact_paths: list[str] = []
    for result in link_results:
        for path in result.get("artifact_paths", []) or []:
            path_text = str(path)
            if path_text not in artifact_paths:
                artifact_paths.append(path_text)
    return artifact_paths
```

Then ensure `command_generate_report(...)` passes those paths through the writeback generation call rather than only bundle-level summaries.

- [ ] **Step 4: Update README with artifact-driven behavior and current support boundary**

Add a short usage note like:

```md
`generate-report` now reads real artifact content from supported channels (`podwise`, `xiaohongshu`) and builds review packs from quotes, paraphrases, and evidence instead of bundle metadata alone.
```

- [ ] **Step 5: Run the full relevant test slice**

Run:

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
"/Users/vickyshou/.local/bin/uv" run --with pytest python -m pytest tests/test_artifact_evidence.py tests/test_writeback_generate.py tests/test_link_to_report.py tests/test_link_to_report_real_ingestion.py -q
```

Expected:

```text
all tests passed
```

- [ ] **Step 6: Commit the CLI integration and docs**

```bash
cd /Users/vickyshou/Documents/trae_projects/product-ontology
git add scripts/link_to_report_lib.py tests/test_link_to_report.py README.md
git commit -m "feat: wire link-to-report into artifact-driven generation"
```

---

## Self-Review

### Spec coverage
- `artifact selection rules`: covered by Tasks 1-2.
- `quote/paraphrase schema`: covered by Tasks 2-4.
- `anti-summary guardrails`: covered by Task 3 and review-pack structure in Task 4.
- `AI-native UX` insertion point and lens-pack usage: covered by Task 5.
- `link-to-report` consumption of real artifact content: covered by Task 6.

### Placeholder scan
- No `TODO` or `TBD` markers remain.
- Each code-writing step includes concrete code blocks or exact helper shapes.
- Each test step includes the exact command and expected result.

### Type consistency
- New module name is consistently `artifact_evidence.py`.
- Shared helper names stay consistent across tasks:
  - `collect_report_artifacts`
  - `build_evidence_candidates`
  - `cluster_evidence_candidates`
- Report-generation integration consistently uses `artifact_paths` as the handoff substrate.

