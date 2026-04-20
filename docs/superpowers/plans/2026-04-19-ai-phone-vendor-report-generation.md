# AI Phone Vendor Report Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Discover official AI-phone vendor sources, normalize them into source/artifact records, and generate one artifact-driven report comparing vendors and product characteristics.

**Architecture:** Use web discovery to select six official vendor pages, store curated official excerpts as `official` artifacts, assemble a manual `link-to-report` bundle, then run the existing `generate-report` flow with an approved research direction. No framework changes in this pass; the output is a real report built on current ingestion and writeback infrastructure.

**Tech Stack:** Markdown records, existing `source_ingest.py`/`link_to_report.py`, artifact-driven writeback generation, official web sources.

---

### Task 1: Create the research bundle inputs

**Files:**
- Create: `library/artifacts/official/*.md`
- Create: `library/sessions/link-to-report/ai-phone-vendor-landscape/run-summary.md`
- Create: `library/sessions/link-to-report/ai-phone-vendor-landscape/direction.md`

- [ ] Gather six official vendor sources and initialize source/artifact directories.
- [ ] Curate one `full_text.md` artifact per vendor with direct excerpts and concise evidence lines.
- [ ] Create the bundle `run-summary.md` with successful per-link results and real artifact paths.
- [ ] Create an approved `direction.md` that locks one research question for this report.

### Task 2: Generate the report

**Files:**
- Create: `library/writeback-intakes/link-to-report/ai-phone-vendor-landscape.md`
- Create: `library/review-packs/link-to-report/ai-phone-vendor-landscape.md`
- Create: `library/writebacks/link-to-report/ai-phone-vendor-landscape.md`

- [ ] Run `python3 scripts/link_to_report.py generate-report --bundle-id ai-phone-vendor-landscape --direction-file library/sessions/link-to-report/ai-phone-vendor-landscape/direction.md`.
- [ ] Verify intake, review pack, and writeback were created at the expected paths.

### Task 3: Verify output quality

**Files:**
- Inspect: `library/review-packs/link-to-report/ai-phone-vendor-landscape.md`
- Inspect: `library/writebacks/link-to-report/ai-phone-vendor-landscape.md`

- [ ] Confirm the review pack contains direct quotes, paraphrases, evidence refs, and thematic clustering.
- [ ] Confirm the final writeback answers a single research question and compares vendors on product characteristics instead of source-order summary.
- [ ] Record any obvious quality limits in the final handoff.
