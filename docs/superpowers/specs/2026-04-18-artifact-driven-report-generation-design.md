# Artifact-Driven Report Generation Design

## Goal

Redesign report generation so that the system produces research-grade writebacks from artifact content rather than primarily from bundle metadata.

The target change is:

`artifact content -> evidence selection -> theme clustering -> quote/paraphrase extraction -> review pack -> writeback`

instead of:

`bundle metadata -> direction -> generalized review pack -> generalized writeback`

This design exists to make reports more like literature reviews and less like structured summaries.

## Core Position

The current `link-to-report` automation chain is now good enough at:
- taking user-provided links
- producing bundle-scoped source/artifact records
- enforcing a research-direction approval boundary
- emitting one review pack and one writeback

But the writeback still starts too high in the stack.

It still leans too much on:
- source paths
- artifact paths
- link types
- bundle-level metadata

That means the system can produce a structurally correct report while still failing to:
- preserve high-value original wording
- cluster evidence by mechanism rather than by source order
- distinguish quote from paraphrase from synthesis
- ground `problem statement` and `assumptions` in artifact content

The next meaningful step is not to make reports longer.

It is to make report generation consume artifact content as the primary evidence substrate.

## Scope

This design covers:
- which artifacts should be eligible to enter reports
- the artifact triage rules that determine what enters the evidence set
- the schema for `direct quote`, `paraphrase`, `evidence`, and `why it matters`
- guardrails that prevent the report from regressing into a summary
- the fixed insertion point for the MVP `AI-native UX` lens

This design does not yet cover:
- new ingestion adapters
- full multi-lens review rendering
- automatic ranking across many research directions
- generic support for every content channel
- matrix expansion back to 12+ output variants

## Why Artifact-Driven Generation Is Needed

The current system already has:
- normalized `Source`
- normalized `Artifact`
- a `research direction`
- a review-pack stage
- a writeback stage

But it still risks producing a report that says:
- what kinds of materials exist
- what general topic those materials are about
- what the system thinks they imply

instead of a report that shows:
- what the source actually said
- which exact statements were selected
- why those statements matter for the current research question
- which parts are evidence, interpretation, and unresolved tension

Without an artifact-driven evidence layer, the system will continue to drift back toward:
- summary-style writing
- flattened speaker voice
- generic synthesis

This design is therefore about moving the report center of gravity downward, from metadata to evidence.

## New Primary Chain

The new report-generation chain should be:

`research direction -> artifact triage -> evidence candidates -> theme clustering -> review pack -> writeback`

This introduces two new explicit objects:

### 1. Evidence Candidates

An `Evidence Candidate` is a report-eligible unit extracted from artifact content.

It is not yet a final review-pack entry.

Its purpose is to say:
- this quote is relevant
- this paraphrase is justified
- this artifact reference supports a theme

### 2. Theme Cluster

A `Theme Cluster` is the grouping unit used in the review pack.

It should be built from evidence candidates that all bear on the same mechanism-level question.

The system should never write the review pack directly from source order.

## Artifact Selection Rules

The system must not treat all artifacts equally.

If all artifacts enter the report body by default, the result will regress into a sequential summary.

The system should therefore use artifact selection rules.

## Initial Priority By Channel

### Podcast

Preferred input order:
1. `summary`
2. `highlights`
3. `transcript` only for quote recovery, context check, and timestamp backfill

Rationale:
- `summary` and `highlights` are high-density and easier to cluster by theme
- full `transcript` is too verbose to act as the first-pass report substrate

### Xiaohongshu

Preferred input order:
1. `full_text`
2. `transcript` when available
3. `comment_batch` only as supplementary tension or counter-signal material

Rationale:
- `full_text` usually contains the author’s primary framing
- `transcript` helps when the real insight lives in spoken content
- comments are useful, but should not become the main evidence layer in MVP

### Official

When official success paths exist later, preferred input order should be:
1. `full_text`
2. optional structured page sections if available

Official artifacts should still go through the same evidence-candidate gate rather than automatically entering the report body.

## Artifact Triage Rules

An artifact segment should enter the report evidence pool only if it satisfies all of the following:

1. It is relevant to the current `research direction`
2. It can be assigned to at least one plausible theme cluster
3. It contributes one of these roles:
   - `direct quote`
   - `mechanism paraphrase source`
   - `counter-signal`
   - `tension`
4. It is specific enough to support later citation

An artifact segment should be excluded from the report evidence pool if it is:
- generic background text
- repeated marketing language with no mechanism signal
- a weakly related tangent
- emotionally loud but structurally irrelevant commentary

## Evidence Candidate Schema

Each evidence candidate should contain at least these fields:

- `candidate_id`
- `research_direction`
- `theme_hint`
- `quote`
- `speaker_or_source`
- `artifact_ref`
- `why_selected`
- `paraphrase`
- `claim_role`
- `confidence`

### Field meanings

#### `quote`

This should preserve a short, strong original expression from the source material.

It should:
- retain speaker force
- stay as close as practical to the artifact wording
- avoid quote-like rewrites

#### `paraphrase`

This should not restate the quote in simpler words.

It must translate the quote into a mechanism-level interpretation.

It should answer:
- what this means structurally for the product, workflow, governance, or UX problem

#### `artifact_ref`

This should be traceable enough to recover the source later, for example:
- file path
- timestamp
- sentence or section id

#### `why_selected`

This should explain why this quote is worth pulling into the review pack instead of remaining buried in the raw artifact.

#### `claim_role`

Suggested initial roles:
- `support`
- `counter_signal`
- `tension`
- `open_question`

#### `confidence`

Suggested initial levels:
- `high`
- `medium`
- `low`

This confidence is about extraction and relevance, not global product truth.

## Allowed Mechanism Categories For Paraphrase

To stop paraphrase from becoming freeform summary, the system should constrain it to a small set of mechanism categories.

The initial set should be:
- `capability_boundary`
- `workflow_shift`
- `governance_or_control`
- `trust_or_explainability`
- `role_delegation`
- `coordination_protocol`

Every paraphrase should map to at least one of these categories.

If it does not, it probably belongs in background notes rather than the report body.

## Theme Clustering Rules

The review pack must be written by theme, not by source order.

The system should therefore cluster evidence candidates into a small number of themes before review-pack generation.

### Theme-count guardrail

Each round should default to `2-4` theme clusters.

The preferred default is `3`.

If the system produces too many themes, the report almost always collapses back into:
- one-source-at-a-time summary
- checklist-style note dumping

### Theme design principle

Themes must be mechanism-bearing, not content-bucket labels.

Good theme examples:
- `执行控制层`
- `协作与角色层`
- `治理与前台 UX 外显层`

Bad theme examples:
- `播客 A 观点`
- `作者观点总结`
- `一些补充信息`

## Review Pack Structure Under This Design

The existing research-direction-first review pack still applies, but its internal evidence source changes.

The thematic review section should be assembled from artifact-driven evidence candidates.

Each theme must contain:
- one or more `Direct quote`
- one or more `Paraphrase`
- explicit `Evidence`
- explicit `Why it matters`

The review pack must not be generated directly from:
- source order
- source count
- artifact file lists alone

## Anti-Summary Guardrails

To prevent regression into summary-style output, the system should enforce these guardrails.

### 1. One question per report

Every report must answer exactly one `research direction`.

If the system tries to answer multiple questions at once, it will revert into recap mode.

### 2. Theme-first, not source-first

No report body should be organized primarily by:
- source order
- platform order
- ingestion order

### 3. No synthesis before review

The system must not emit a major conclusion before the thematic review has been formed from evidence candidates.

### 4. Quote before paraphrase before synthesis

The expected order is:
1. quote
2. paraphrase
3. synthesis

If synthesis appears without preserved quote force, the report is probably flattening speakers into system voice again.

### 5. Limit the evidence set

More evidence is not always better.

The report should select high-signal evidence rather than trying to preserve everything.

The right behavior is:
- less total material
- more selective signal
- stronger traceability

### 6. Preserve counter-signals

At least some evidence candidates should be able to enter the review pack as:
- `counter_signal`
- `tension`
- `open_question`

Otherwise the report becomes a support brief rather than analysis.

## AI-native UX Lens Insertion Point

The MVP `AI-native UX` lens should not be applied at the raw artifact-selection stage.

It should not decide what counts as evidence in the first place.

Instead, the correct insertion point is:

`artifact triage -> theme clustering -> review pack draft -> AI-native UX interpretation -> final writeback`

That means:
- evidence is gathered first
- themes are formed second
- AI-native UX enters as a constrained interpretation layer

This avoids turning UX into a premature filter that distorts what the material is actually saying.

## AI-native UX Lens Responsibilities In MVP

The MVP UX layer should answer questions like:
- what responsibility surface is becoming visible
- what behavior contract is implied between user and agent
- what should become a foreground attention object
- where handoff / rollback / escalation should become explicit
- how user goal loops change when agent coordination becomes productized

It should not degrade into:
- generic usability commentary
- “this should be easier to use”
- disconnected design opinion

The UX lens pack for this phase should be derived from:
- `/Users/vickyshou/.openclaw/workspace/shared/Principles`

That folder should be treated as the reference source for extracting:
- responsibility and behavior-contract principles
- attention arbitration principles
- handoff / rollback / escalation principles
- AI-native collaboration and agent UX principles

This design does not require the full folder to be injected wholesale into generation.

Instead, implementation should compress those materials into a bounded MVP UX lens pack used only at the interpretation stage.

## Success Criteria

This design succeeds if the next report-generation system can:

1. Choose a bounded set of report-eligible artifact segments.
2. Preserve high-value original quote force.
3. Generate mechanism-level paraphrases rather than summary restatements.
4. Cluster evidence by theme rather than source order.
5. Produce a review pack whose thematic section is clearly artifact-driven.
6. Keep `problem statement`, `assumptions`, and `AI-native UX` grounded in reviewed evidence.
7. Avoid falling back into summary-style writing.

## Non-Goals

Do not treat this phase as:
- a full channel expansion project
- a multi-lens rendering project
- a matrix-output project
- a full retrieval engine redesign

This phase is only about changing the evidence substrate of report generation:

from metadata-driven

to artifact-driven.
