# Human-in-the-Loop Writeback Intake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a human-in-the-loop writeback intake step that records user intent before report generation, allows empty input with default fallback, and upgrades the current writeback flow to show multi-lens review traces.

**Architecture:** Introduce a small writeback-intake record layer plus one dedicated generator script instead of spreading intake logic across candidate-import scripts. Keep review data and writeback rendering separate: review files store critique, intake files store user intent, and the generator combines both into a final writeback. Use one upgraded sample writeback to prove the workflow before expanding to more channels.

**Tech Stack:** Markdown templates, JSON Schema, Python 3 scripts with `argparse` and `pathlib`, `pytest` for workflow tests

---

## File Map

### New Files

- `schemas/writeback-intake.schema.json`
  Defines the intake record shape with required `intake_id`, optional structured fields, open fields, and a `used_default_rules` flag.
- `templates/writeback-intake.md`
  Canonical Markdown template for a stored intake record.
- `templates/writeback-proposal.md`
  Replace the current empty placeholder with a real writeback template that exposes intake metadata, review refs, verdict refs, and preserved tensions.
- `scripts/writeback_intake.py`
  Small CLI to create a writeback intake record from explicit flags or empty/default mode.
- `scripts/writeback_generate.py`
  Generates a writeback from existing event/claim/review/verdict/intake inputs and enforces “no intake, no writeback”.
- `tests/test_writeback_intake.py`
  Verifies intake record creation, default fallback, and schema-friendly output.
- `tests/test_writeback_generate.py`
  Verifies generator behavior for `integrated`, `sectioned`, and `appendix` modes, and verifies default-mode rendering.
- `library/reviews/podcasts/review-product-podwise-ai-7650271-dfb97270-16.md`
  Product-lens review sample for the existing promoted podwise claim.
- `library/reviews/podcasts/review-ux-podwise-ai-7650271-dfb97270-16.md`
  UX-collaboration review sample for the same claim.
- `library/reviews/podcasts/review-contrarian-podwise-ai-7650271-dfb97270-16.md`
  Contrarian review sample for the same claim.
- `library/verdicts/podcasts/verdict-podwise-ai-7650271-dfb97270-16.md`
  Judge-level verdict summary that links the above reviews into one outcome.
- `library/writeback-intakes/podcasts/intake-podwise-ai-7650271-dfb97270-default.md`
  Default/fallback intake sample for the current podwise writeback.

### Modified Files

- `README.md`
  Document the new required intake step and generator commands.
- `library/_operating-notes.md`
  Add `Writeback Intake` to the operating chain and document default fallback behavior.
- `ontology/jury-review-ontology.md`
  Clarify that review traces feed writeback generation only after intake.
- `docs/superpowers/specs/2026-04-17-human-in-the-loop-writeback-intake-design.md`
  Keep in sync only if implementation reveals naming mismatches.
- `library/writebacks/2026-04-16-xiaopeng-v2a-explainability-writeback.md`
  Upgrade the sample writeback to include intake metadata and multi-lens review sections.

---

### Task 1: Add Writeback Intake Schema And Templates

**Files:**
- Create: `schemas/writeback-intake.schema.json`
- Create: `templates/writeback-intake.md`
- Modify: `templates/writeback-proposal.md`
- Modify: `README.md`
- Modify: `library/_operating-notes.md`

- [ ] **Step 1: Write the failing schema/template test**

Create `tests/test_writeback_intake.py` with:

```python
from pathlib import Path
import json


def test_writeback_intake_schema_exists():
    path = Path("schemas/writeback-intake.schema.json")
    assert path.exists(), "missing writeback intake schema"


def test_writeback_templates_are_not_placeholders():
    intake_template = Path("templates/writeback-intake.md").read_text()
    writeback_template = Path("templates/writeback-proposal.md").read_text()
    assert "intake_id" in intake_template
    assert "collaboration_mode" in writeback_template
    assert "used_default_rules" in writeback_template
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_writeback_intake.py -v`
Expected: FAIL because the schema file and intake template do not exist, and `writeback-proposal.md` is still a placeholder.

- [ ] **Step 3: Write minimal schema and templates**

Create `schemas/writeback-intake.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "WritebackIntakeRecord",
  "type": "object",
  "required": ["intake_id", "used_default_rules"],
  "properties": {
    "intake_id": { "type": "string" },
    "collaboration_mode": {
      "type": ["string", "null"],
      "enum": ["integrated", "sectioned", "appendix", null]
    },
    "focus_priority": {
      "type": "array",
      "items": { "type": "string" }
    },
    "target_audience": { "type": ["string", "null"] },
    "decision_intent": { "type": ["string", "null"] },
    "evidence_posture": { "type": ["string", "null"] },
    "special_attention": { "type": "array", "items": { "type": "string" } },
    "extra_questions": { "type": "array", "items": { "type": "string" } },
    "avoidances": { "type": "array", "items": { "type": "string" } },
    "preserve_tensions": { "type": "array", "items": { "type": "string" } },
    "used_default_rules": { "type": "boolean" }
  }
}
```

Create `templates/writeback-intake.md`:

```md
# Writeback Intake Record

- intake_id: ``
- collaboration_mode: ``
- focus_priority: []
- target_audience: ``
- decision_intent: ``
- evidence_posture: ``
- special_attention: []
- extra_questions: []
- avoidances: []
- preserve_tensions: []
- used_default_rules: ``
```

Replace `templates/writeback-proposal.md` with:

```md
# Writeback Proposal

- writeback_id: ``
- intake_id: ``
- collaboration_mode: ``
- used_default_rules: ``
- focus_priority: []
- special_attention: []
- review_refs: []
- verdict_refs: []
- preserved_tensions: []

## 标题

## 摘要

## 主判断

## 评审视角

## 证据锚点

## 保留分歧
```

Update `README.md` and `library/_operating-notes.md` so the operating chain includes:

```md
`Source -> Artifact -> Candidate -> Review/Verdict -> Writeback Intake -> Writeback`
```

and explicitly document:

```md
- writeback generation always passes through intake
- the user may leave intake fields empty
- default report rules are applied when no extra guidance is provided
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_writeback_intake.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_writeback_intake.py schemas/writeback-intake.schema.json templates/writeback-intake.md templates/writeback-proposal.md README.md library/_operating-notes.md
git commit -m "feat: add writeback intake schema and templates"
```

### Task 2: Build The Intake Record CLI With Default Fallback

**Files:**
- Create: `scripts/writeback_intake.py`
- Test: `tests/test_writeback_intake.py`

- [ ] **Step 1: Extend tests with CLI expectations**

Append to `tests/test_writeback_intake.py`:

```python
import subprocess


def test_writeback_intake_cli_writes_default_record(tmp_path):
    target = tmp_path / "intake.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_intake.py",
            "create",
            "--intake-id",
            "intake-demo",
            "--output",
            str(target),
            "--use-defaults",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- intake_id: `intake-demo`" in text
    assert "- used_default_rules: `true`" in text


def test_writeback_intake_cli_preserves_user_fields(tmp_path):
    target = tmp_path / "intake.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_intake.py",
            "create",
            "--intake-id",
            "intake-demo",
            "--output",
            str(target),
            "--collaboration-mode",
            "sectioned",
            "--focus-priority",
            "mechanism,user_trust",
            "--special-attention",
            "memory continuity",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- collaboration_mode: `sectioned`" in text
    assert "- used_default_rules: `false`" in text
    assert "`mechanism`" in text and "`user_trust`" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_writeback_intake.py -v`
Expected: FAIL with `scripts/writeback_intake.py` missing.

- [ ] **Step 3: Write minimal intake CLI**

Create `scripts/writeback_intake.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def format_list(values: list[str]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(f"`{value}`" for value in values) + "]"


def build_markdown(args: argparse.Namespace) -> str:
    used_default_rules = args.use_defaults or not any(
        [
            args.collaboration_mode,
            args.focus_priority,
            args.target_audience,
            args.decision_intent,
            args.evidence_posture,
            args.special_attention,
            args.extra_questions,
            args.avoidances,
            args.preserve_tensions,
        ]
    )
    focus_priority = parse_csv(args.focus_priority)
    special_attention = parse_csv(args.special_attention)
    extra_questions = parse_csv(args.extra_questions)
    avoidances = parse_csv(args.avoidances)
    preserve_tensions = parse_csv(args.preserve_tensions)
    return f\"\"\"# Writeback Intake Record

- intake_id: `{args.intake_id}`
- collaboration_mode: `{args.collaboration_mode or ''}`
- focus_priority: {format_list(focus_priority)}
- target_audience: `{args.target_audience or ''}`
- decision_intent: `{args.decision_intent or ''}`
- evidence_posture: `{args.evidence_posture or ''}`
- special_attention: {format_list(special_attention)}
- extra_questions: {format_list(extra_questions)}
- avoidances: {format_list(avoidances)}
- preserve_tensions: {format_list(preserve_tensions)}
- used_default_rules: `{'true' if used_default_rules else 'false'}`
\"\"\"


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("--intake-id", required=True)
    create.add_argument("--output", required=True)
    create.add_argument("--use-defaults", action="store_true")
    create.add_argument("--collaboration-mode")
    create.add_argument("--focus-priority")
    create.add_argument("--target-audience")
    create.add_argument("--decision-intent")
    create.add_argument("--evidence-posture")
    create.add_argument("--special-attention")
    create.add_argument("--extra-questions")
    create.add_argument("--avoidances")
    create.add_argument("--preserve-tensions")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_markdown(args))
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_writeback_intake.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/writeback_intake.py tests/test_writeback_intake.py
git commit -m "feat: add writeback intake cli"
```

### Task 3: Add Multi-Lens Review Samples And Verdict Records

**Files:**
- Create: `library/reviews/podcasts/review-product-podwise-ai-7650271-dfb97270-16.md`
- Create: `library/reviews/podcasts/review-ux-podwise-ai-7650271-dfb97270-16.md`
- Create: `library/reviews/podcasts/review-contrarian-podwise-ai-7650271-dfb97270-16.md`
- Create: `library/verdicts/podcasts/verdict-podwise-ai-7650271-dfb97270-16.md`
- Modify: `ontology/jury-review-ontology.md`

- [ ] **Step 1: Write the failing review-content test**

Create `tests/test_writeback_generate.py` with:

```python
from pathlib import Path


def test_sample_reviews_exist_for_promoted_podcast_claim():
    assert Path("library/reviews/podcasts/review-product-podwise-ai-7650271-dfb97270-16.md").exists()
    assert Path("library/reviews/podcasts/review-ux-podwise-ai-7650271-dfb97270-16.md").exists()
    assert Path("library/reviews/podcasts/review-contrarian-podwise-ai-7650271-dfb97270-16.md").exists()
    assert Path("library/verdicts/podcasts/verdict-podwise-ai-7650271-dfb97270-16.md").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_writeback_generate.py::test_sample_reviews_exist_for_promoted_podcast_claim -v`
Expected: FAIL because the review and verdict files do not exist.

- [ ] **Step 3: Create sample review and verdict records**

Create `library/reviews/podcasts/review-product-podwise-ai-7650271-dfb97270-16.md`:

```md
# Review Record

- review_id: `review-product-podwise-ai-7650271-dfb97270-16`
- lens: `product`
- target_type: `claim`
- target_id: `claim-podwise-ai-7650271-dfb97270-16`
- produces_verdict_id: `verdict-podwise-ai-7650271-dfb97270-16`
- evidence_refs: [`summary.md:sentence-16`, `transcript:01:07:28`]
- review_notes: `这不是单纯 feature 增量，而是把解释能力拉进智驾主能力闭环，并影响责任边界。`
```

Create `library/reviews/podcasts/review-ux-podwise-ai-7650271-dfb97270-16.md`:

```md
# Review Record

- review_id: `review-ux-podwise-ai-7650271-dfb97270-16`
- lens: `ux_collaboration`
- target_type: `claim`
- target_id: `claim-podwise-ai-7650271-dfb97270-16`
- produces_verdict_id: `verdict-podwise-ai-7650271-dfb97270-16`
- evidence_refs: [`highlights.md:10:10`, `highlights.md:01:10:38`]
- review_notes: `解释能力被强调了，但还缺真实界面或交互证据来证明用户看见并理解了它。`
```

Create `library/reviews/podcasts/review-contrarian-podwise-ai-7650271-dfb97270-16.md`:

```md
# Review Record

- review_id: `review-contrarian-podwise-ai-7650271-dfb97270-16`
- lens: `contrarian`
- target_type: `claim`
- target_id: `claim-podwise-ai-7650271-dfb97270-16`
- produces_verdict_id: `verdict-podwise-ai-7650271-dfb97270-16`
- evidence_refs: [`summary.md:sentence-16`]
- review_notes: `当前证据仍可能是评论性解读，必须保留“可解释性是否真实用户可见”的疑问。`
```

Create `library/verdicts/podcasts/verdict-podwise-ai-7650271-dfb97270-16.md`:

```md
# Verdict Record

- verdict_id: `verdict-podwise-ai-7650271-dfb97270-16`
- target_type: `claim`
- target_id: `claim-podwise-ai-7650271-dfb97270-16`
- outcome: `supported_with_preserved_tension`
- rationale: `Product lens supports structural significance; UX and contrarian lenses preserve visibility and evidence concerns.`
- evidence_refs: [`summary.md:sentence-16`, `transcript:01:07:28`, `highlights.md:10:10`, `highlights.md:01:10:38`]
- judge: `judge-sample`
- status_change: `retain_as_candidate_promoted`
```

Update `ontology/jury-review-ontology.md` to include:

```md
5. Writeback intake and rendering.
   Review traces may only influence a final writeback after the user passes through intake. Writeback rendering must preserve disagreements rather than flatten them.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_writeback_generate.py::test_sample_reviews_exist_for_promoted_podcast_claim -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_writeback_generate.py library/reviews/podcasts/review-product-podwise-ai-7650271-dfb97270-16.md library/reviews/podcasts/review-ux-podwise-ai-7650271-dfb97270-16.md library/reviews/podcasts/review-contrarian-podwise-ai-7650271-dfb97270-16.md library/verdicts/podcasts/verdict-podwise-ai-7650271-dfb97270-16.md ontology/jury-review-ontology.md
git commit -m "feat: add sample multi-lens reviews for writebacks"
```

### Task 4: Build The Writeback Generator And Enforce Intake

**Files:**
- Create: `scripts/writeback_generate.py`
- Test: `tests/test_writeback_generate.py`

- [ ] **Step 1: Extend generator tests**

Append to `tests/test_writeback_generate.py`:

```python
import subprocess


def test_writeback_generate_requires_intake(tmp_path):
    target = tmp_path / "writeback.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_generate.py",
            "render",
            "--writeback-id",
            "writeback-demo",
            "--output",
            str(target),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "intake" in result.stderr.lower()


def test_writeback_generate_with_default_intake(tmp_path):
    intake = tmp_path / "intake.md"
    intake.write_text(
        \"\"\"# Writeback Intake Record
- intake_id: `intake-demo`
- collaboration_mode: ``
- focus_priority: []
- target_audience: ``
- decision_intent: ``
- evidence_posture: ``
- special_attention: []
- extra_questions: []
- avoidances: []
- preserve_tensions: []
- used_default_rules: `true`
\"\"\"
    )
    target = tmp_path / "writeback.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_generate.py",
            "render",
            "--writeback-id",
            "writeback-demo",
            "--intake-file",
            str(intake),
            "--output",
            str(target),
            "--title",
            "Demo",
            "--summary",
            "Demo summary",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- intake_id: `intake-demo`" in text
    assert "- used_default_rules: `true`" in text
    assert "## 评审视角" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_writeback_generate.py -v`
Expected: FAIL because `scripts/writeback_generate.py` does not exist.

- [ ] **Step 3: Implement the minimal generator**

Create `scripts/writeback_generate.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def read_field(text: str, field: str) -> str:
    match = re.search(rf"- {re.escape(field)}: `(.*?)`", text)
    return match.group(1) if match else ""


def render_writeback(args: argparse.Namespace) -> str:
    intake_text = Path(args.intake_file).read_text()
    intake_id = read_field(intake_text, "intake_id")
    if not intake_id:
        raise SystemExit("missing intake_id in intake record")
    collaboration_mode = read_field(intake_text, "collaboration_mode")
    used_default_rules = read_field(intake_text, "used_default_rules")
    review_refs = args.review_refs.split(",") if args.review_refs else []
    verdict_refs = args.verdict_refs.split(",") if args.verdict_refs else []
    preserved_tensions = args.preserved_tensions.split(",") if args.preserved_tensions else []
    return f\"\"\"# Writeback Proposal

- writeback_id: `{args.writeback_id}`
- intake_id: `{intake_id}`
- collaboration_mode: `{collaboration_mode}`
- used_default_rules: `{used_default_rules}`
- focus_priority: []
- special_attention: []
- review_refs: [{", ".join(f"`{item.strip()}`" for item in review_refs if item.strip())}]
- verdict_refs: [{", ".join(f"`{item.strip()}`" for item in verdict_refs if item.strip())}]
- preserved_tensions: [{", ".join(f"`{item.strip()}`" for item in preserved_tensions if item.strip())}]

## 标题

{args.title}

## 摘要

{args.summary}

## 主判断

待由 evidence、review 和 intake 共同约束的主判断。

## 评审视角

当前 writeback 已绑定 review 与 verdict 痕迹，后续可按 collaboration_mode 决定是整合呈现、分节呈现，还是附录呈现。

## 证据锚点

待补充。

## 保留分歧

{chr(10).join(f"- {item.strip()}" for item in preserved_tensions if item.strip()) or "- none recorded"}
\"\"\"


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    render = subparsers.add_parser("render")
    render.add_argument("--writeback-id", required=True)
    render.add_argument("--intake-file", required=True)
    render.add_argument("--output", required=True)
    render.add_argument("--title", required=True)
    render.add_argument("--summary", required=True)
    render.add_argument("--review-refs", default="")
    render.add_argument("--verdict-refs", default="")
    render.add_argument("--preserved-tensions", default="")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_writeback(args))
    print(f"wrote {output}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        if isinstance(exc.code, str):
            print(exc.code, file=sys.stderr)
            raise SystemExit(1)
        raise
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_writeback_generate.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/writeback_generate.py tests/test_writeback_generate.py
git commit -m "feat: add writeback generator with intake enforcement"
```

### Task 5: Upgrade The Existing Podwise Writeback To The New Flow

**Files:**
- Create: `library/writeback-intakes/podcasts/intake-podwise-ai-7650271-dfb97270-default.md`
- Modify: `library/writebacks/2026-04-16-xiaopeng-v2a-explainability-writeback.md`
- Modify: `README.md`

- [ ] **Step 1: Add a failing content test for the upgraded sample**

Append to `tests/test_writeback_generate.py`:

```python
def test_sample_writeback_records_intake_and_reviews():
    text = Path("library/writebacks/2026-04-16-xiaopeng-v2a-explainability-writeback.md").read_text()
    assert "- intake_id:" in text
    assert "- review_refs:" in text
    assert "- verdict_refs:" in text
    assert "## 评审视角" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_writeback_generate.py::test_sample_writeback_records_intake_and_reviews -v`
Expected: FAIL because the current sample writeback does not yet expose intake and review metadata.

- [ ] **Step 3: Create intake record and upgrade the sample writeback**

Create `library/writeback-intakes/podcasts/intake-podwise-ai-7650271-dfb97270-default.md`:

```md
# Writeback Intake Record

- intake_id: `intake-podwise-ai-7650271-dfb97270-default`
- collaboration_mode: ``
- focus_priority: []
- target_audience: ``
- decision_intent: ``
- evidence_posture: ``
- special_attention: []
- extra_questions: []
- avoidances: []
- preserve_tensions: [`真实用户是否看见并理解了解释能力`]
- used_default_rules: `true`
```

Update `library/writebacks/2026-04-16-xiaopeng-v2a-explainability-writeback.md` so the header contains:

```md
- intake_id: `intake-podwise-ai-7650271-dfb97270-default`
- collaboration_mode: ``
- used_default_rules: `true`
- review_refs: [`review-product-podwise-ai-7650271-dfb97270-16`, `review-ux-podwise-ai-7650271-dfb97270-16`, `review-contrarian-podwise-ai-7650271-dfb97270-16`]
- verdict_refs: [`verdict-podwise-ai-7650271-dfb97270-16`]
- preserved_tensions: [`真实用户是否看见并理解了解释能力`]
```

and replace the current prose-only trust/risk ending with a visible review-aware section:

```md
## 评审视角

### Product

`product` lens 支持当前主判断，认为可解释性已经从附属叙事进入能力闭环，并影响责任边界。

### UX Collaboration

`ux_collaboration` lens 认为方向成立，但仍缺真实界面或交互证据来证明用户真的看到并理解了解释能力。

### Contrarian

`contrarian` lens 要求保留一个核心分歧：当前证据仍可能主要来自评论性解读，而非用户侧可观察证据。
```

Update `README.md` with the new commands:

```bash
python3 scripts/writeback_intake.py create --intake-id <intake-id> --output <path> --use-defaults
python3 scripts/writeback_generate.py render --writeback-id <writeback-id> --intake-file <path> --output <path> --title <title> --summary <summary>
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_writeback_generate.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add library/writeback-intakes/podcasts/intake-podwise-ai-7650271-dfb97270-default.md library/writebacks/2026-04-16-xiaopeng-v2a-explainability-writeback.md README.md tests/test_writeback_generate.py
git commit -m "feat: upgrade sample writeback with intake and reviews"
```

### Task 6: Final Verification

**Files:**
- Verify only

- [ ] **Step 1: Validate the new schema**

Run: `python3 -m json.tool schemas/writeback-intake.schema.json >/dev/null`
Expected: command exits successfully with no output

- [ ] **Step 2: Run all writeback workflow tests**

Run: `python3 -m pytest tests/test_writeback_intake.py tests/test_writeback_generate.py -v`
Expected: PASS

- [ ] **Step 3: Smoke-test the default intake flow**

Run:

```bash
python3 scripts/writeback_intake.py create --intake-id intake-smoke --output /tmp/intake-smoke.md --use-defaults
python3 scripts/writeback_generate.py render --writeback-id writeback-smoke --intake-file /tmp/intake-smoke.md --output /tmp/writeback-smoke.md --title "Smoke" --summary "Smoke summary"
```

Expected:
- first command prints `wrote /tmp/intake-smoke.md`
- second command prints `wrote /tmp/writeback-smoke.md`
- `/tmp/writeback-smoke.md` contains `used_default_rules: \`true\``

- [ ] **Step 4: Review git diff for scope**

Run: `git diff --stat HEAD~5..HEAD`
Expected: only writeback-intake docs, templates, scripts, tests, sample reviews/verdicts, and sample writeback files changed

- [ ] **Step 5: Commit any remaining documentation sync**

```bash
git add README.md library/_operating-notes.md ontology/jury-review-ontology.md
git commit -m "docs: finalize writeback intake workflow"
```

---

## Self-Review

- Spec coverage:
  - human-in-the-loop intake step: Tasks 1, 2, 4, 5
  - empty input with default fallback: Tasks 1, 2, 4, 6
  - intake metadata recorded in writeback: Tasks 1, 4, 5
  - multi-lens review reflected in writeback: Tasks 3, 5
  - docs updated with the new chain: Tasks 1, 3, 5
- Placeholder scan:
  - No `TBD` or `TODO` placeholders remain in task steps
  - All code-writing steps include concrete code blocks
  - All test steps include exact commands and expected results
- Type consistency:
  - `intake_id`, `collaboration_mode`, `used_default_rules`, `review_refs`, `verdict_refs`, and `preserved_tensions` are used consistently across schema, template, CLI, generator, and sample writeback
