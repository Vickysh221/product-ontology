# Longform Writeback Generation Design

## Goal

Upgrade writeback generation from metadata-only placeholder outputs to real longform product-analysis articles.

The first implementation should not attempt to upgrade the entire 12-writeback matrix at once.
It should first prove that one matrix variant can be generated as a high-quality longform article from the existing knowledge base.

## Immediate Scope

This design covers:
- one new longform writeback generation path
- one representative pilot article
- one evidence-selection strategy
- one validation standard for longform quality

This design does not yet cover:
- upgrading all 12 matrix outputs in one pass
- generating new review data
- adding UI
- replacing the existing placeholder matrix renderer

## Core Position

The current matrix writebacks are working as infrastructure tests, not as final analytical reports.

That is acceptable for the matrix test itself, but it is not acceptable for the longform report experience.

The system now needs a second generation path:

- `render`
  - keeps producing lightweight placeholder outputs for matrix plumbing and metadata verification
- `render-longform`
  - produces an actual article from synthesis, intake, and evidence

This separation avoids breaking the matrix test while allowing the report system to grow into real narrative outputs.

## Why The Current Writebacks Are Short

The current generator does not yet synthesize evidence into narrative form.

It only:
- reads intake metadata
- fills a fixed writeback template
- inserts a title, subtitle, summary, and record references

It does not yet:
- read the synthesis body as article input
- extract or rank evidence snippets
- reorganize structure based on collaboration mode
- shift density and emphasis based on target audience
- pivot the argument based on extra questions

As a result, the current outputs are valid matrix artifacts but not meaningful analytical writebacks.

## First Target

The first longform pilot should be:

- `integrated-team-paradigm`

This is the best single test case because it simultaneously exercises:
- `integrated` collaboration mode
- `team` target audience
- `multiagent paradigm shift` extra-question focus

If the system cannot generate a convincing longform article for this case, it is not ready to scale to the rest of the matrix.

## Input Model

The longform generator should consume four input layers.

### 1. Intake Record

The intake record defines:
- `collaboration_mode`
- `target_audience`
- `extra_questions`
- whether default rules were used

The intake does not provide the report content by itself.
It constrains how the existing judgment base should be rendered.

### 2. Shared Synthesis

The synthesis record is the parent judgment base.

It should contribute:
- the core synthesized judgment
- the stable themes
- the evidence summary
- the preserved tensions

The longform article must not ignore the synthesis and write only from intake metadata.

### 3. Structured Evidence

Evidence should be pulled in this order:

1. synthesis evidence summary
2. episode `summary.md`
3. episode `highlights.md`
4. episode `transcript.md` for context recovery only

This ordering is intentional.
The goal is not transcript summarization. The goal is product analysis grounded in the highest-signal structured evidence available.

### 4. Optional Review Traces

If review and verdict references already exist, they may be included.
They are not required for the first pilot.

The first pilot may rely on:
- synthesis
- intake
- evidence
- preserved tensions

without blocking on full multi-lens review materialization.

## Generation Model

The longform generation path should use a two-stage process:

`synthesis -> outline -> longform writeback`

### Stage 1: Outline Construction

The system should first generate a structured outline from:
- intake controls
- synthesis themes
- selected evidence roles
- preserved tensions

This outline stage is what makes different matrix variants meaningfully diverge.

The outline should decide:
- what the primary question is
- what the article’s argument order is
- which evidence supports which section
- which tensions remain visible

### Stage 2: Longform Rendering

The system should then render the outline into a complete article.

This stage should not invent a new argument.
It should elaborate the outline into readable prose with explicit evidence anchors.

## Longform Structure

The first longform writeback should use a fixed seven-part structure.

### 1. 摘要

Two to four sentences that state:
- what this article is about
- what question it answers
- what conclusion it reaches at a high level

### 2. 主判断

A direct statement of the main conclusion.

For `integrated` mode, this section is especially important because it sets the single narrative thread for the rest of the article.

### 3. 机制拆解

This section should explain why the observed shift is not a surface-level feature accumulation.

It should connect:
- harness engineering
- orchestration logic
- governance structure

into one mechanism-level interpretation.

### 4. 能力边界与工作流变化

This section should explain what product and collaboration boundaries actually change.

It should answer questions such as:
- what work the agent system can now coordinate
- what control layers become first-class product structure
- what team workflows become possible or necessary

### 5. 针对本次追问的回答

This section must explicitly answer the intake-driven extra question.

For the pilot article, that means:
- is this a real paradigm shift from single-agent tool use to agent team structure
- or is it merely stronger workflow packaging

This section is where the writeback must visibly differ from another version with a different extra-question theme.

### 6. 证据锚点

This section must list real evidence anchors.

It should reference:
- episode summaries
- highlights with timestamps where available
- transcript positions when used for contextual recovery

### 7. 保留分歧

This section must explicitly preserve unresolved tensions.

The first pilot should preserve at least:
- whether multi-agent is already a stable product paradigm
- whether harness engineering has crossed from engineering practice into product core

## Mode, Audience, and Extra-Question Effects

These variables must change the article materially, not cosmetically.

### Collaboration Mode

`integrated`
- one strong narrative thread
- disagreements embedded inside a single analytical flow

`sectioned`
- more visibly separated analytical blocks
- easier to surface multiple lenses or sub-questions as distinct sections

`appendix`
- shorter and cleaner main body
- more support material and disagreement moved later

The first pilot uses `integrated`, so the article should feel like one argument, not a stitched bundle of notes.

### Target Audience

`team`
- should emphasize shared understanding
- should foreground workflow implications
- should surface coordination questions and tensions worth discussing

The pilot should therefore avoid sounding like:
- a private research memo
- an executive summary
- a purely archival record

### Extra Question

`multiagent paradigm shift`
- should force the article to answer whether the evidence really supports a structural migration
- should foreground changes in coordination logic, capability boundaries, and stable system structure
- should not degrade into a general “AI is getting more complex” narrative

## Evidence Rules

The first longform pilot should satisfy all of these rules:

1. All five episodes must appear somewhere in the article.
2. Each episode must contribute at least one role-specific evidence point.
3. Evidence should be cited by artifact and position whenever possible.
4. Transcript usage should be contextual, not dominant.
5. The article must not rely on synthesis claims that cannot be traced back to the episode evidence set.

## Output Rules

The longform output must:
- be fully Chinese
- contain no placeholder language
- contain no sections that say “待补充” or similar
- read as an actual product analysis article

The target length for the pilot is:
- approximately `1200-2200` Chinese characters of real analytical prose

The article does not need to be maximally long.
It needs to be materially more developed than the placeholder outputs and clearly shaped by the intake.

## Success Criteria

The pilot succeeds if:
- it reads like a real product-analysis writeback
- it is recognizably `integrated`
- it is recognizably written for `team`
- it visibly answers the `multiagent paradigm shift` question
- it includes real evidence anchors
- it preserves genuine tensions instead of flattening them
- it contains no placeholder language

## Failure Modes

The pilot fails if:
- it still feels like a template shell with longer sentences
- it could be swapped with another matrix variant without meaningful change
- it mentions evidence generically without anchors
- it collapses all tensions into a confident single answer
- it reads like a transcript digest rather than a product analysis

## Implementation Direction

The first implementation should add a new command:

`python3 scripts/writeback_generate.py render-longform --intake-file ... --synthesis-file ... --output ...`

The existing `render` command should stay unchanged for matrix plumbing.

Only after the pilot longform article is successful should the system decide whether to:
- promote `render-longform` into the matrix workflow
- or keep placeholder and longform generation as separate lanes

## Rollout Sequence

1. Add `render-longform`
2. Generate one high-quality pilot for `integrated-team-paradigm`
3. Verify it against the success criteria
4. Compare it to the placeholder version
5. Only then plan expansion to the remaining eleven matrix variants
