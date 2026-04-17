# Link-to-Report Real Ingestion Design

## Goal

Upgrade the existing short-term `link-to-report` CLI from a workflow proof to a real content-production entrypoint.

The target chain is:

`user provides a few links -> system performs real ingestion into source/artifact -> system proposes or accepts one research direction -> user approves direction when needed -> system generates one real review pack -> system generates one real writeback`

This design intentionally upgrades only the short-term manual-links path.

It does not expand to scheduled crawling, feed polling, or multi-report batching.

## Why This Upgrade Exists

The current `link-to-report` CLI already proves the control flow:
- it accepts links
- records one bundle
- records one direction
- blocks pending directions from continuing
- writes one intake, one review pack, and one writeback

But the current implementation still uses placeholder content in the report-generation stages.

Specifically:
- `ingest-links` mostly records bundle metadata instead of consistently producing real source/artifact outputs
- `propose-direction` does not yet derive its direction from real ingested material
- `generate-report` writes MVP placeholder review-pack and writeback bodies instead of calling the existing research-direction-first reporting chain

The correct next step is not to redesign writeback again.

It is to make `link-to-report` consume the ingestion and reporting machinery that already exists elsewhere in the repository.

## Scope

This design covers:
- real ingestion for a limited set of link types
- bundle-level tracking of real source/artifact outputs
- research direction proposal from ingested records
- generation of a real review pack and a real writeback through existing mechanisms
- human-in-the-loop approval at the research-direction boundary

This design does not cover:
- WeChat automation in the short-term CLI
- scheduled crawlers
- topic ranking across many bundles
- automatic generation of many reports
- reworking the writeback ontology itself

## Supported Inputs In This Phase

The first real-ingestion upgrade should recognize exactly three link families:

- `podwise`
- `xiaohongshu`
- `official`

### 1. Podwise

Expected real outputs:
- one real podcast `Source`
- real `transcript`
- real `summary`
- real `highlights`

### 2. Xiaohongshu

Expected real outputs:
- one real Xiaohongshu `Source`
- real `full_text`
- optional already-existing `transcript`
- optional already-existing `comment_batch`

The CLI should not require transcript generation in this phase.

If transcript or comments already exist for the same source slug, they should be discoverable and included in the bundle summary.

### 3. Official

Expected behavior in this phase:
- recognize approved official targets
- keep a reserved adapter surface for later real ingestion
- fail transparently when real page content is unavailable

This phase does not require a shipped official success path.

The short-term requirement is honesty:
- no fabricated official `full_text`
- no false `success` result when content is unavailable

## Core Design

The upgraded chain should be:

`links -> adapter routing -> real source/artifact outputs -> approved research direction -> real review pack -> real writeback`

This is different from the current MVP chain:

`links -> run summary -> direction -> placeholder review pack -> placeholder writeback`

The key change is that `link-to-report` becomes an orchestration layer over existing importers and report-generation utilities.

It should not remain a standalone placeholder pipeline.

## Architecture

## 1. Thin CLI, Reusable Library

The public entrypoint should remain:

`python3 scripts/link_to_report.py`

It should still expose:
- `ingest-links`
- `propose-direction`
- `generate-report`

But the real behavior should live in `scripts/link_to_report_lib.py`.

`link_to_report.py` should stay thin.

## 2. Adapter Routing Layer

`link_to_report_lib.py` should become a registry-based orchestration layer.

For each detected link type, it should route to a concrete ingestion adapter.

The routing table in this phase should cover:
- `podcast -> podcast importer`
- `xiaohongshu -> xiaohongshu importer`
- `official -> reserved official ingestion path with transparent failure until a real fetcher exists`

The routing layer should return structured ingestion results instead of only strings.

Each per-link result should include:
- `link`
- `link_type`
- `status`
- `source_path`
- `artifact_paths`
- `failure_reason`

## 3. Real Ingestion Through Existing Capabilities

This phase should reuse existing logic instead of recreating parallel importers.

### Podwise path

`link-to-report` should call the existing podcast import capability and capture its real outputs.

Expected integration target:
- existing podcast import functions that already create source/artifact files under `library/sources/podcasts/` and `library/artifacts/podcasts/`

The CLI should record the returned source slug or file paths into the bundle summary.

### Xiaohongshu path

`link-to-report` should call the existing Xiaohongshu import capability and capture its real outputs.

Expected integration target:
- existing Xiaohongshu note import flow that creates source and `full_text`

If related transcript or comment artifacts already exist for that slug, the bundle summary should include them.

This design does not require the CLI to trigger transcript generation.

### Official path

`link-to-report` should keep an explicit official-path adapter surface.

If real page extraction is not available for a given link in this phase, the command must fail transparently with a classified failure reason rather than silently fabricating content.

## 4. Bundle Summary As A Real Orchestration Record

`run-summary.md` must stop being only a list of links and detected types.

It should become the bundle’s authoritative processing record.

For each link, it should record:
- link
- detected type
- status
- source path
- artifact paths
- failure reason when applicable

At the bundle level, it should record:
- bundle id
- successful link count
- failed link count
- normalized source paths
- normalized artifact paths

This summary should be the handoff object from ingestion to direction proposal.

## 5. Research Direction From Real Bundle Content

`propose-direction` should stop proposing one generic direction from link metadata alone.

Instead, it should derive a candidate from the real ingested bundle record.

The MVP upgrade should remain conservative:
- produce one candidate direction
- do not rank many directions
- do not try to synthesize across all possible topics

The candidate should be grounded in:
- the real input types present in the bundle
- the visible themes from source/artifact outputs
- the research-direction-first reporting discipline already established in the repository

If the user passes `--direction`, that still overrides proposal behavior and becomes:
- `user_provided`

If the system proposes a direction, it must remain:
- `system_suggested_pending`

and must still require user approval before report generation.

## 6. Real Report Generation Through Existing Reporting Mechanisms

`generate-report` should no longer render placeholder review-pack and writeback content directly in `link_to_report_lib.py`.

Instead, it should orchestrate the repository’s current reporting chain:

`approved research direction -> writeback intake -> review pack -> writeback`

The exact writeback mechanism should remain the repository’s current default research-direction-first pipeline.

This means:
- one report answers one research question
- review pack is generated before final writeback
- evidence lineage remains explicit
- AI-native UX remains the MVP analysis lens

The CLI’s role is orchestration, not re-implementation of reporting logic.

## Human-in-the-Loop Rules

The upgraded CLI must preserve human control at the same boundary as before.

### Required gate

If the direction is system-generated:
- the system must stop at the direction record
- the user must approve, revise, or replace it before `generate-report`

### Optional guidance

If the user provides extra emphasis, side questions, or preserved tensions:
- the CLI may pass those through to the intake/writeback stages

If the user provides nothing:
- default reporting rules still apply

## Failure Handling

This phase must fail clearly.

Per-link failures should be classified at least as:
- unsupported link type
- adapter execution failure
- access or network issue
- source returned empty content
- platform limitation

The bundle may continue when:
- at least one link succeeds
- and there is enough real material for one report

The workflow must stop when:
- all links fail
- no meaningful source/artifact records were created
- the direction remains `system_suggested_pending`

## Success Criteria

This upgrade succeeds if the following are true:

1. `ingest-links` creates a real bundle record from mixed links.
2. Supported real-ingestion links produce real normalized source/artifact records.
3. `run-summary.md` records real ingestion outputs, not just raw links.
4. `propose-direction` uses real bundle outputs rather than only generic metadata.
5. `generate-report` produces a real intake, real review pack, and real writeback through existing report-generation machinery.
6. The CLI remains human-in-the-loop at the research-direction approval boundary.

For this phase, “supported real-ingestion links” means:
- `podwise`
- `xiaohongshu`

`official` remains recognized but may fail explicitly until a real fetch path is added.

## Non-Goals

Do not add in this phase:
- WeChat automation
- scheduled harvesting
- autonomous direction ranking across many candidates
- multi-report generation from one bundle
- matrix-based output generation
- new ontology layers

The only goal of this phase is to turn `link-to-report` into a real manual-links entrypoint that consumes the repository’s existing ingestion and writeback systems.
