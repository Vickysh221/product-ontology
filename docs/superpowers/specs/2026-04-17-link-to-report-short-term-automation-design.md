# Link-to-Report Short-Term Automation Design

## Goal

Define the short-term automation path for this project:

`user provides a few links -> system ingests source/artifact -> system proposes or accepts one research direction -> system generates review pack -> system generates final writeback`

This design intentionally focuses on the short-term human-in-the-loop workflow.

It does not yet attempt to automate link discovery or scheduled content harvesting.

## Core Position

The short-term system should optimize for:
- reliable ingestion from a small number of user-provided links
- a unified source/artifact pipeline across channels
- research-direction-first analysis
- one qualified report per round

The short-term system should not optimize for:
- unattended content discovery
- feed crawling at scale
- always-on monitoring
- batch generation of many reports from one click

The correct near-term problem is not "how to automatically scrape the internet."

It is:

`how to take a small bundle of user-provided links and deterministically turn them into one traceable analysis report`

## Scope

This design covers:
- short-term automation from manual links to final report
- supported input types and normalization
- the orchestration steps from ingestion to report output
- human-in-the-loop approval points
- failure handling

This design does not yet cover:
- scheduled crawlers
- feed polling or ranking
- automatic topic discovery
- autonomous report generation without user approval

## Supported Short-Term Inputs

The short-term system should accept a small list of links supplied by the user.

Supported input categories are:
- `podwise episode`
- `xiaohongshu note`
- `wechat article` or already-accessible WeChat text source
- `official page` such as blog post, release note, changelog, OTA note, product update page

The user experience should assume:
- the user may paste 1 to N links
- different links may belong to different platforms
- some links may fail to ingest

The system must handle each link independently and report per-link outcomes.

## Architecture

The short-term automation chain should be:

`links -> source records -> artifact records -> research direction -> review pack -> writeback`

Each stage has a distinct responsibility.

### 1. Link Intake

The user provides a list of links.

The system should:
- detect link type
- route each link to the correct adapter
- keep a normalized per-link processing status

### 2. Source / Artifact Normalization

Every successfully processed link must become:
- one normalized `Source`
- one or more normalized `Artifact`

This is mandatory.

The system must not generate reports directly from raw links.

Examples:
- `podwise`
  - `Source`
  - `transcript`
  - `summary`
  - `highlights`
- `xiaohongshu`
  - `Source`
  - `full_text`
  - optional `transcript`
  - optional `comment_batch`
- `wechat`
  - `Source`
  - `full_text`
- `official`
  - `Source`
  - `full_text`

### 3. Research Direction Selection

No report should be generated without a single research direction.

There are two valid modes:
- user provides the direction directly
- system proposes one candidate direction from the ingested material

If the system proposes the direction, it must be marked:
- `待用户批准`

The user must be able to:
- approve it
- revise it
- replace it

This stage is the main human-in-the-loop boundary in the short-term workflow.

### 4. Research Review Pack

Once the direction is approved, the system generates one `Research Review Pack`.

The review pack must:
- cluster evidence by theme
- preserve direct quote and paraphrase
- cite the source evidence explicitly
- surface `why it matters`
- produce draft `problem statement`
- produce draft `assumptions`
- preserve tensions and counter-signals

The review pack is not the final report.

It is the constraint layer between evidence and writeback.

### 5. Final Writeback

The final report is generated from the review pack, not directly from raw artifacts.

The writeback should keep the current research-direction-first behavior:
- one report answers one question
- evidence remains visible
- final conclusions must grow from the review pack
- AI-native UX is the MVP analysis lens

## Human-in-the-Loop Rules

The short-term automation flow must remain human-in-the-loop in two places.

### Required Approval 1: Research Direction

If direction is system-generated:
- user approval is required before review-pack generation

If direction is user-provided:
- no extra approval is needed

### Optional Guidance 2: Report Emphasis

Before final writeback generation, the user may optionally provide:
- emphasis
- side questions
- objections
- tensions that must be preserved

If the user provides nothing:
- the default writeback rules apply

## Output Objects

The short-term system should produce these visible outputs.

### 1. Ingestion Result

A short structured run summary:
- links succeeded
- links failed
- normalized source ids
- normalized artifact ids

### 2. Research Direction Record

Either:
- user-specified direction
- or system-suggested direction plus approval state

### 3. Research Review Pack

Saved into the existing review-pack area.

### 4. Final Writeback

Saved into the existing writeback area.

## Failure Handling

Short-term automation must fail transparently.

Per-link failures should be classified as:
- unsupported link type
- network / access issue
- source returned empty content
- platform limitation
- adapter execution failure

The system should still proceed if:
- at least one link was successfully ingested
- and there is enough material to support one research direction

The system should stop and ask the user if:
- all links fail
- there is not enough material for one meaningful report
- the proposed research direction is too weak or too broad

## Short-Term Success Criteria

The short-term automation path is successful if it can do the following deterministically:

1. Accept a mixed list of user-provided links.
2. Normalize successful links into source/artifact records.
3. Propose or accept exactly one research direction.
4. Wait for user approval when the direction is system-generated.
5. Produce one review pack.
6. Produce one writeback with explicit evidence lineage.

## Non-Goals For This Phase

Do not implement in this phase:
- automatic link discovery from feeds
- cron-style monitoring
- ranking many possible report topics
- autonomous multi-report production
- full multi-lens review rendering

Those belong to the long-term automation phase.

## Implementation Shape

The short-term system should likely be implemented as three top-level actions:

### 1. `ingest-links`

Input:
- a list of links

Output:
- normalized source/artifact records
- run summary

### 2. `propose-direction`

Input:
- the ingested source/artifact bundle

Output:
- one suggested research direction

### 3. `generate-report`

Input:
- one approved research direction
- one source/artifact bundle

Output:
- one review pack
- one final writeback

This separation keeps the short-term system debuggable and human-reviewable.

## Long-Term Relation

The long-term system should not replace this design.

It should only replace the first step:

`manual links`

with:

`scheduled or discovered sources`

The downstream chain should remain the same:

`source/artifact -> research direction -> review pack -> writeback`

That is why the short-term design must be correct before any long-term crawling or monitoring work begins.
