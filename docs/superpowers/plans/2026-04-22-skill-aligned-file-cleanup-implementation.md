# Skill-Aligned File Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align `product-ontology` around two skill-triggered entry surfaces, archive redundant legacy prompt files, retire the placeholder writeback CLI path, and clearly separate active runtime layers from future ontology layers.

**Architecture:** Keep the active evidence-driven runtime intact: `approved material -> source/artifact -> intake -> review pack -> writeback`. Introduce one missing collaboration-trace skill, archive the old `agents/*.md` trigger documents they replace, and downgrade only the obsolete placeholder `render` path in `scripts/writeback_generate.py` instead of touching the live artifact-driven and pilot flows.

**Tech Stack:** Markdown docs, skill docs under `/Users/vickyshou/.agents/skills/`, Python 3, argparse, pytest, git file moves, repo-local library artifacts.

---

## File Structure

### New files to create

- `/Users/vickyshou/.agents/skills/collaboration-trace/SKILL.md`
  - The second trigger skill for structured collaboration progression recording.
- `docs/archive/agents/README.md`
  - Archive note explaining which old prompt files were superseded and by which skill.

### Existing files to modify

- [`README.md`](./README.md)
  - Mark the two active skill entrypoints, distinguish active runtime layers from future ontology layers, and remove any implication that the legacy placeholder writeback path is still a recommended entry.
- [`library/_operating-notes.md`](./library/_operating-notes.md)
  - Mirror the active-vs-future layer distinction and note the skill-aligned trigger surface.
- [`docs/research-principles/product-ontology-evidence-writeback-profile.md`](./docs/research-principles/product-ontology-evidence-writeback-profile.md)
  - Clarify which files remain active, which are archived, and that the placeholder `render` path is no longer a live surface.
- [`scripts/writeback_generate.py`](./scripts/writeback_generate.py)
  - Replace the legacy placeholder `render` implementation with an explicit deprecation error.
- [`tests/test_writeback_generate.py`](./tests/test_writeback_generate.py)
  - Replace tests that bless the placeholder `render` output with tests that assert deprecation behavior.
- [`.gitignore`](./.gitignore)
  - Ignore `.superpowers/` so local tool residue stops polluting `git status`.

### Existing files to move into archive

- [`agents/source-scout agent.md`](./agents/source-scout%20agent.md)
  - Move to `docs/archive/agents/source-scout agent.md`
- [`agents/claim-extractor agent.md`](./agents/claim-extractor%20agent.md)
  - Move to `docs/archive/agents/claim-extractor agent.md`
- [`agents/jury-synthesizer agent.md`](./agents/jury-synthesizer%20agent.md)
  - Move to `docs/archive/agents/jury-synthesizer agent.md`
- [`agents/collaboration-trace-synthesizer agent.md`](./agents/collaboration-trace-synthesizer%20agent.md)
  - Move to `docs/archive/agents/collaboration-trace-synthesizer agent.md`
- [`agents/collaboration-trace-synthesizer output contract.md`](./agents/collaboration-trace-synthesizer%20output%20contract.md)
  - Move to `docs/archive/agents/collaboration-trace-synthesizer output contract.md`
- [`agents/协作推进记录 agent.md`](./agents/%E5%8D%8F%E4%BD%9C%E6%8E%A8%E8%BF%9B%E8%AE%B0%E5%BD%95%20agent.md)
  - Move to `docs/archive/agents/协作推进记录 agent.md`
- [`library/writebacks/podcasts/matrix/integrated-team-paradigm v0.2.md`](./library/writebacks/podcasts/matrix/integrated-team-paradigm%20v0.2.md)
  - Move to `library/writebacks/podcasts/matrix/backups/integrated-team-paradigm.v0.2.md`

### Files to retain explicitly

Do not delete these in this cleanup:

- [`templates/writeback-intake.md`](./templates/writeback-intake.md)
- [`templates/writeback-proposal.md`](./templates/writeback-proposal.md)
- [`docs/research-principles/multiagent-human-coexistence-framework.md`](./docs/research-principles/multiagent-human-coexistence-framework.md)
- [`docs/research-principles/multiagent-role-mapping.md`](./docs/research-principles/multiagent-role-mapping.md)
- Empty ontology-layer directories under `library/` such as `products/`, `patterns/`, `methods/`, `questions/`, `hypotheses/`, `counterclaims/`, and `theses/`

### Scope lock

Do not do any of the following in this cleanup:

- redesign the artifact-driven writeback flow
- remove the pilot-specific `integrated-team-paradigm` generation logic
- delete template files that tests treat as contract docs
- rewrite historical implementation plans under `docs/superpowers/`
- delete arbitrary untracked user folders beyond `.superpowers/`

---

### Task 1: Add the second collaboration-trace skill and wire the target trigger model

**Files:**
- Create: `/Users/vickyshou/.agents/skills/collaboration-trace/SKILL.md`
- Modify: `README.md`
- Modify: `library/_operating-notes.md`

- [ ] **Step 1: Write the missing `collaboration-trace` skill**

Create `/Users/vickyshou/.agents/skills/collaboration-trace/SKILL.md` with this content:

```md
---
name: collaboration-trace
description: Use when a human-agent or agent-agent session must be recorded as a structured progression record that preserves ownership, decisions, open questions, and writeback eligibility.
---

# Collaboration Trace

## Overview

Use this skill when collaboration itself is the object that needs to be preserved.

Core rule:

`Record the move, the owner, the state change, and the next entry point.`

## When To Use

Use this skill when:
- a human-agent session needs a durable progression record
- an agent-agent handoff needs a clean continuation contract
- the system must separate original intent, structuring moves, decisions, and unresolved questions
- the output may later justify writeback, but should not become writeback by default

Do not use this skill for:
- generic meeting summaries
- source ingestion
- artifact-level evidence extraction
- final review-pack or writeback generation

## Required Output Shape

- focus object
- intent owner
- decision owner
- structuring owner
- execution owner
- current problem definition
- subproblems
- proposals
- decisions made
- open questions
- assumptions
- memory candidates
- next entry point
- writeback eligibility

## Guardrails

- Do not flatten unconfirmed interpretation into final judgment.
- Do not lose who owns a decision.
- Do not replace a progression record with prose-only summary.
- Do not update object-level continuity directly from a session trace.

## Repo Note

When working in `/Users/vickyshou/Documents/trae_projects/product-ontology`, treat the archived `agents/collaboration-*` prompt files as historical references only.
```

- [ ] **Step 2: Verify the skill file exists and has valid trigger metadata**

Run:

```bash
test -f '/Users/vickyshou/.agents/skills/collaboration-trace/SKILL.md' && rg -n '^name: collaboration-trace$|^description: Use when' '/Users/vickyshou/.agents/skills/collaboration-trace/SKILL.md'
```

Expected:
- exit code `0`
- one `name:` match
- one `description:` match

- [ ] **Step 3: Update `README.md` to state the two active trigger surfaces**

Insert this block after the opening operating-model bullets in `README.md`:

```md
## Active Trigger Surfaces

This repo now treats two skill-triggered surfaces as the primary human entrypoints:

- `evidence-to-writeback` for approved material -> artifact -> intake -> review pack -> writeback
- `collaboration-trace` for structured human-agent or agent-agent progression recording

Older prompt files under `agents/` are retained only as archived historical references once the cleanup is complete.
```

- [ ] **Step 4: Update `library/_operating-notes.md` to mirror the same trigger model**

Add this block near the top of `library/_operating-notes.md`:

```md
## Current Trigger Model

- `evidence-to-writeback` is the active trigger for research and writeback generation.
- `collaboration-trace` is the active trigger for structured session progression recording.
- Archived prompt files are historical references, not active operating entrypoints.
```

- [ ] **Step 5: Verify the repo now documents the new trigger model**

Run:

```bash
rg -n "evidence-to-writeback|collaboration-trace|Active Trigger Surfaces|Current Trigger Model" README.md library/_operating-notes.md
```

Expected:
- matches in both files
- no placeholder text like `TBD` or `TODO`

- [ ] **Step 6: Commit the trigger-surface setup**

Run:

```bash
git add README.md library/_operating-notes.md '/Users/vickyshou/.agents/skills/collaboration-trace/SKILL.md'
git commit -m "docs: define two active skill trigger surfaces"
```

Expected:
- one documentation commit with the new skill and trigger-model docs

---

### Task 2: Archive the redundant legacy `agents/*.md` trigger documents

**Files:**
- Create: `docs/archive/agents/README.md`
- Move: `agents/source-scout agent.md`
- Move: `agents/claim-extractor agent.md`
- Move: `agents/jury-synthesizer agent.md`
- Move: `agents/collaboration-trace-synthesizer agent.md`
- Move: `agents/collaboration-trace-synthesizer output contract.md`
- Move: `agents/协作推进记录 agent.md`

- [ ] **Step 1: Create the archive note**

Create `docs/archive/agents/README.md` with this content:

```md
# Legacy Agent Prompt Archive

These files were originally used as prompt-level trigger surfaces.

They are archived because the active trigger model now lives in two skills:

- `evidence-to-writeback`
- `collaboration-trace`

Archive mapping:

- `source-scout agent.md` -> superseded by `evidence-to-writeback`
- `claim-extractor agent.md` -> superseded by `evidence-to-writeback`
- `jury-synthesizer agent.md` -> superseded by `evidence-to-writeback`
- `collaboration-trace-synthesizer agent.md` -> superseded by `collaboration-trace`
- `collaboration-trace-synthesizer output contract.md` -> superseded by `collaboration-trace`
- `协作推进记录 agent.md` -> superseded by `collaboration-trace`

Historical implementation plans under `docs/superpowers/` may still reference the original paths. Those references are historical and should not be treated as active runtime entrypoints.
```

- [ ] **Step 2: Move the legacy prompt files into the archive**

Run:

```bash
mkdir -p docs/archive/agents
git mv 'agents/source-scout agent.md' 'docs/archive/agents/source-scout agent.md'
git mv 'agents/claim-extractor agent.md' 'docs/archive/agents/claim-extractor agent.md'
git mv 'agents/jury-synthesizer agent.md' 'docs/archive/agents/jury-synthesizer agent.md'
git mv 'agents/collaboration-trace-synthesizer agent.md' 'docs/archive/agents/collaboration-trace-synthesizer agent.md'
git mv 'agents/collaboration-trace-synthesizer output contract.md' 'docs/archive/agents/collaboration-trace-synthesizer output contract.md'
git mv 'agents/协作推进记录 agent.md' 'docs/archive/agents/协作推进记录 agent.md'
```

- [ ] **Step 3: Remove the now-empty `agents/` directory if it has no remaining tracked files**

Run:

```bash
find agents -maxdepth 1 -type f | sed -n '1,20p'
rmdir agents
```

Expected:
- `find` prints nothing
- `rmdir agents` succeeds

- [ ] **Step 4: Verify that active docs no longer present `agents/` as current trigger docs**

Run:

```bash
rg -n "agents/.*agent.md" README.md library/_operating-notes.md docs/research-principles/product-ontology-evidence-writeback-profile.md
```

Expected:
- no matches in active docs
- historical references may still remain under `docs/superpowers/`

- [ ] **Step 5: Commit the archive move**

Run:

```bash
git add docs/archive/agents
git commit -m "docs: archive legacy agent trigger prompts"
```

Expected:
- one commit moving the old prompt files into archive

---

### Task 3: Retire the placeholder `render` path in `scripts/writeback_generate.py`

**Files:**
- Modify: `scripts/writeback_generate.py`
- Modify: `tests/test_writeback_generate.py`

- [ ] **Step 1: Replace the current placeholder-path test with a failing deprecation test**

In `tests/test_writeback_generate.py`, replace `test_writeback_generate_with_default_intake` with:

```python
def test_writeback_generate_render_legacy_path_is_rejected(tmp_path):
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
            "--subtitle",
            "Demo subtitle",
            "--summary",
            "Demo summary",
            "--synthesis-ref",
            "synthesis-demo",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "legacy placeholder render path removed" in result.stderr
```

- [ ] **Step 2: Run the targeted test to verify failure**

Run:

```bash
'/Users/vickyshou/.local/bin/uv' run --offline --with pytest python -m pytest tests/test_writeback_generate.py::test_writeback_generate_render_legacy_path_is_rejected -q
```

Expected:
- FAIL because the current `render` command still succeeds

- [ ] **Step 3: Replace the placeholder implementation with an explicit deprecation error**

In `scripts/writeback_generate.py`, replace the current `render_writeback` function with:

```python
def render_writeback(_args: argparse.Namespace) -> str:
    raise SystemExit(
        "legacy placeholder render path removed; use render-review-pack + render-longform or scripts/link_to_report.py generate-report"
    )
```

Leave the `render` subcommand in place so the CLI returns a clear migration message instead of an opaque argparse failure.

- [ ] **Step 4: Run the targeted generator tests**

Run:

```bash
'/Users/vickyshou/.local/bin/uv' run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k "legacy_path_is_rejected or render_review_pack_creates_research_sections or render_longform_has_real_evidence_and_no_placeholders" -q
```

Expected:
- all selected tests PASS

- [ ] **Step 5: Commit the placeholder-path retirement**

Run:

```bash
git add scripts/writeback_generate.py tests/test_writeback_generate.py
git commit -m "refactor: retire placeholder writeback render path"
```

Expected:
- one commit removing the redundant placeholder writeback logic

---

### Task 4: Reclassify active runtime layers, future ontology layers, and template roles

**Files:**
- Modify: `README.md`
- Modify: `library/_operating-notes.md`
- Modify: `docs/research-principles/product-ontology-evidence-writeback-profile.md`

- [ ] **Step 1: Update `README.md` to distinguish active runtime layers from future layers**

Replace the current broad directory-responsibility bullets with:

```md
Directory responsibilities:
- Active runtime layers in the current repo are `sources/`, `artifacts/`, `sessions/`, `review-packs/`, `writeback-intakes/`, `writebacks/`, plus the currently used `events/`, `claims/`, `reviews/`, and `verdicts/` slices.
- Future or lightly populated ontology layers such as `products/`, `patterns/`, `methods/`, `questions/`, `hypotheses/`, `counterclaims/`, and `theses/` remain part of the repository model, but they are not the primary runtime path for the current writeback workflow.
- `templates/writeback-intake.md` and `templates/writeback-proposal.md` are contract-reference templates validated by tests; they are not the primary runtime source for generated outputs.
```

- [ ] **Step 2: Update `library/_operating-notes.md` to match the same active/future distinction**

Append this block after `## Object Storage Rules`:

```md
## Current Status Notes

- The current live writeback path is centered on `sources -> artifacts -> intake -> review pack -> writeback`.
- `events`, `claims`, `reviews`, and `verdicts` are present and partly used, but they are not required by every active report-generation path.
- `products`, `patterns`, `methods`, `questions`, `hypotheses`, `counterclaims`, and `theses` remain modeled layers rather than heavily populated active runtime layers.
- Template files under `templates/` are contract references and documentation aids, not direct runtime inputs for every generator path.
```

- [ ] **Step 3: Update the repo profile to reflect the same classifications**

Add this block to `docs/research-principles/product-ontology-evidence-writeback-profile.md` under `Known Limits`:

```md
## Classification Notes

- Archived prompt files under `docs/archive/agents/` are historical references only.
- `templates/writeback-intake.md` and `templates/writeback-proposal.md` remain as contract docs because tests validate their presence and field shape.
- Empty ontology-layer directories are intentionally retained; this cleanup only reclassifies them as future or lightly populated layers instead of pretending they are all equally active today.
```

- [ ] **Step 4: Verify the classification language is consistent**

Run:

```bash
rg -n "Active runtime layers|Future or lightly populated ontology layers|Current Status Notes|Classification Notes|contract-reference templates" README.md library/_operating-notes.md docs/research-principles/product-ontology-evidence-writeback-profile.md
```

Expected:
- all three files contain aligned classification language

- [ ] **Step 5: Commit the runtime-layer reclassification**

Run:

```bash
git add README.md library/_operating-notes.md docs/research-principles/product-ontology-evidence-writeback-profile.md
git commit -m "docs: distinguish active runtime layers from future ontology layers"
```

Expected:
- one docs commit that reduces model-vs-runtime ambiguity

---

### Task 5: Archive stale materialized output and ignore local tool residue

**Files:**
- Move: `library/writebacks/podcasts/matrix/integrated-team-paradigm v0.2.md`
- Modify: `.gitignore`

- [ ] **Step 1: Move the stale `v0.2` writeback into the existing backups area**

Run:

```bash
git mv 'library/writebacks/podcasts/matrix/integrated-team-paradigm v0.2.md' 'library/writebacks/podcasts/matrix/backups/integrated-team-paradigm.v0.2.md'
```

- [ ] **Step 2: Ignore `.superpowers/` in `.gitignore`**

Append this line to `.gitignore`:

```gitignore
.superpowers/
```

- [ ] **Step 3: Remove the empty local `.superpowers/` directories from the working tree if they still contain no files**

Run:

```bash
test ! -d .superpowers || find .superpowers -type f | sed -n '1,20p'
test ! -d .superpowers || find .superpowers -depth -type d -empty -exec rmdir {} + 2>/dev/null
```

Expected:
- `find` prints nothing if the directory tree is empty
- empty `.superpowers/` directories are removed if they exist

- [ ] **Step 4: Verify the working tree no longer shows `.superpowers/` noise and that the archived writeback path is correct**

Run:

```bash
git status --short
test -f 'library/writebacks/podcasts/matrix/backups/integrated-team-paradigm.v0.2.md'
test ! -f 'library/writebacks/podcasts/matrix/integrated-team-paradigm v0.2.md'
```

Expected:
- `.superpowers/` no longer appears in `git status`
- the old `v0.2` path is gone
- the backup path exists

- [ ] **Step 5: Commit the final cleanup pass**

Run:

```bash
git add .gitignore 'library/writebacks/podcasts/matrix/backups/integrated-team-paradigm.v0.2.md'
git commit -m "chore: archive stale outputs and ignore local tool residue"
```

Expected:
- one final cleanup commit

---

## Final Verification

- [ ] Run:

```bash
'/Users/vickyshou/.local/bin/uv' run --offline --with pytest python -m pytest tests/test_writeback_generate.py -q
```

Expected:
- the full `writeback_generate` test file passes

- [ ] Run:

```bash
git status --short
```

Expected:
- clean working tree after the last cleanup commit

- [ ] Run:

```bash
rg -n "待由 evidence|待补充" scripts/writeback_generate.py README.md library/_operating-notes.md docs/research-principles/product-ontology-evidence-writeback-profile.md
```

Expected:
- no matches in active runtime docs or generator code
