# Product Ontology Profile For Evidence To Writeback

This file is an example repo profile that narrows the generic `product-ontological-analysis` skill to one concrete workspace.

Use it to answer one practical question:

`How does this repo turn approved material into a review pack and then into writeback without losing provenance?`

## Repository Contract

The repo-level docs define two related chains:

- conceptual evidence chain: `Source -> Artifact -> Event -> Claim -> Pattern -> Thesis`
- writeback chain: `Source -> Artifact -> Candidate -> Review/Verdict -> Writeback Intake -> Writeback`

In the current implementation, the live report path is more specific:

- generic artifact-driven path:
  `approved source -> source/artifact records -> research direction -> intake -> review pack -> writeback`
- podcast pilot path:
  `podwise artifact bundle -> shared synthesis -> intake -> review pack -> longform writeback`

Do not assume every conceptual layer is materialized as its own file. Some candidate and review objects are still in-memory generation objects rather than durable records.

## Active Entry Paths

### 1. Manual link or approved-source path

Main scripts:
- `scripts/link_to_report.py`
- `scripts/link_to_report_lib.py`
- `scripts/writeback_generate.py`

Stable flow:
1. `discover-web` or `search-*` finds candidates.
2. `approve-sources` or `approve-search-candidates` hands approved URLs into ingestion.
3. `ingest-links` writes normalized `source_path` and `artifact_paths`.
4. `propose-direction` creates `library/sessions/link-to-report/<bundle-id>/direction.md`.
5. `generate-report` blocks pending directions, then writes:
   - `library/writeback-intakes/link-to-report/<bundle-id>.md`
   - `library/review-packs/link-to-report/<bundle-id>.md`
   - `library/writebacks/link-to-report/<bundle-id>.md`

### 2. Podcast pilot path

Main scripts:
- `scripts/podcast_import.py`
- `scripts/podcast_candidates.py`
- `scripts/writeback_intake.py`
- `scripts/writeback_generate.py`

Stable flow:
1. Import episode artifacts from Podwise.
2. Optionally extract and promote event or claim candidates.
3. Build or update a shared synthesis record.
4. Create a writeback intake.
5. Render a review pack.
6. Render the longform writeback.

Important:
- candidate extraction and promotion exist, but current report generation does not require durable promoted event or claim records
- the real report path is artifact-driven

## What Counts As First-Hand Here

In this repo, "first-hand" is an operating preference, not a claim that every artifact is raw primary text.

Treat the strongest approved normalized artifact as the working evidence base:
- podcasts: imported Podwise transcript, summary, highlights
- xiaohongshu: imported `full_text`, optional `transcript`, optional `comment_batch`
- official: imported `full_text` only when a real fetcher exists

Do not treat arbitrary browser text, copied excerpts, or speculative summaries as first-hand just because they sound authoritative.

## Channel Rules And Artifact Priority

The current artifact-driven generator uses these priorities:

- podcasts: `summary -> highlights -> transcript`
- xiaohongshu: `full_text -> transcript -> comment_batch`
- official: `full_text`

This means the repo is currently `artifact-first with first-hand preference`, not `raw transcript first` by default.

## Generation Surfaces

### Generic artifact-driven generation

Key modules:
- `scripts/artifact_evidence.py`
- `scripts/writeback_generate.py`

What happens:
1. Collect artifact files by channel.
2. Extract evidence candidates with:
   - `quote`
   - `paraphrase`
   - `artifact_ref`
   - `claim_role`
   - `confidence`
3. Cluster them into up to three themes.
4. Build the review pack from those clusters.
5. Build the writeback either from the review pack or directly from the same clusters.

### Podcast pilot generation

The `integrated-team-paradigm` path is intentionally special-cased.

Current gate:
- `scripts/writeback_generate.py` checks for `intake_id == intake-integrated-team-paradigm`

When that gate matches, the generator uses:
- pilot-only cluster schemas
- evidence-role assignment
- review objects
- final section objects for judgment, problem statement, assumptions, and AI-native UX

Do not generalize that pilot-only composer to every input without making the contract explicit first.

## Direction And Intake Rules

- intake is mandatory for writeback generation
- `direction_status == system_suggested_pending` must block final report generation
- `extra_questions`, `target_audience`, `collaboration_mode`, and preserved tensions are report constraints, not decoration
- writeback should be derived from approved direction plus artifact evidence, not from a title alone

## Verification Checklist

Before claiming the workflow is complete:

1. Check that every referenced artifact path exists.
2. Check that the review pack still contains the evidence shape:
   - `Direct quote`
   - `Paraphrase`
   - `Evidence`
   - `Why it matters`
3. Check that counter-signals survived into the review pack or final writeback.
4. Check that the final writeback contains no placeholders.
5. Run targeted tests when touching the generator.

Example commands used in this repo:

```bash
uv run --offline --with pytest python -m pytest tests/test_artifact_evidence.py -q
uv run --offline --with pytest python -m pytest tests/test_writeback_generate.py -q
uv run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_matrix.py -q
```

## Minimum Mental Model

When you work on this repo, think in this order:

`approved material -> normalized artifacts -> evidence candidates -> theme clusters or review objects -> intake-constrained review pack -> traceable writeback`

If a proposed shortcut skips one of those gates, assume it is wrong until proven otherwise.
