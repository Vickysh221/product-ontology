# Research-Direction Writeback Design

## Goal

Redesign writeback generation so that it produces research-grade product analysis rather than summary-style longform prose.

The new default should preserve more of the speakers' original insights, organize evidence as a literature review, and only then grow toward synthesis, product framing, assumptions, and AI-native UX analysis.

## Core Position

The current longform writeback path still starts too close to "analysis output."

Even after the recent longform upgrade, the system still tends to:
- summarize too early
- flatten multiple speakers into one system voice
- paraphrase without keeping enough original quote force
- arrive at product conclusions before a proper review pack exists

That makes the result more like an expanded analytical memo than a qualified research-oriented product writeback.

The new writeback system should therefore be reorganized around a first-class `research direction`.

The main chain becomes:

`research direction -> evidence review pack -> writeback`

instead of:

`source bundle -> synthesis -> writeback`

## Why Research Direction Must Be First-Class

The few-shot reference makes the intended behavior explicit:

- each round answers one question
- materials are grouped by theme, not by source order
- direct quote and paraphrase both matter
- problem statement and assumptions must be explicit
- the report must end in a next-step research direction
- if the direction is system-generated, it must require user approval

This means the writeback is not fundamentally organized around a batch of sources.
It is organized around a question that determines:
- what evidence is relevant
- what themes are worth clustering
- what should count as a meaningful quote
- what tensions should remain visible

## Scope

This design covers:
- the new research-direction-first writeback model
- the structure of a `Research Review Pack`
- the structure of the final writeback
- how user guidance and system-suggested directions should work
- how AI-native UX enters the body as the MVP lens

This design does not yet cover:
- full multi-lens review rendering
- automatic recommendation ranking across many candidate directions
- UI for direction selection
- expansion to all matrix outputs in the same implementation pass

## New Primary Objects

### 1. Research Direction

`Research Direction` becomes the first-class entry object for a writeback run.

It defines:
- what question this round is trying to answer
- what evidence is relevant
- what kind of synthesis is allowed
- what should count as a next-step research problem

It may originate from either:
- the user
- the system

If it originates from the system, it must be marked:
- `待用户批准`

The system must not present a system-generated direction as already authorized.

### 2. Research Review Pack

The `Research Review Pack` is an intermediate object between raw evidence and final writeback.

It exists to prevent the final report from jumping directly from sources to conclusions.

Its job is to:
- cluster evidence by topic
- preserve direct quotes
- translate them into mechanism-level paraphrases
- keep evidence visible
- preserve counter-signals and tensions
- produce draft problem statements and assumptions

It is not a polished report.
It is a structured review object that later constrains report generation.

### 3. Final Writeback

The final writeback should no longer behave like a summary-driven narrative.

It should behave like:
- a question-driven literature review
- followed by a bounded analytical closure

The writeback remains human-readable, but it should be traceable back to the review pack rather than behaving like a freeform synthesis essay.

## Human-in-the-Loop Control

The previous `writeback intake` design still applies, but it now gains a more important responsibility.

It no longer controls only:
- collaboration mode
- audience
- emphasis

It must also control:
- whether the `research direction` is already approved
- or whether the system is proposing a candidate direction for user approval

This means the human-in-the-loop sequence becomes:

1. user provides a direction
2. or system proposes a direction
3. user approves / revises / rejects
4. review pack is generated
5. final writeback is generated

The system must not skip the approval boundary when the direction is system-generated.

## Review Pack Structure

The `Research Review Pack` should contain these sections.

### 1. Research Question

This section states the single question the round is trying to answer.

It must also record the source of the question:
- `用户给定`
- `系统建议，待用户批准`
- `系统建议，已批准`

### 2. Review Introduction

This section explains:
- why the selected themes matter
- how the evidence is being grouped
- that the review proceeds by theme rather than by source order

It must not give a final judgment yet.

### 3. Thematic Literature Review

This is the core of the review pack.

Each theme cluster must contain:
- `Direct quote`
- `Paraphrase`
- `Evidence`
- `Why it matters`

Each theme is allowed to include multiple quotes and multiple evidence items.

The purpose is not to preserve every sentence.
The purpose is to preserve the lines with the strongest explanatory or structural force.

### 4. Counter-Signals And Tensions

The review pack must preserve:
- contrary evidence
- ambiguous evidence
- over-interpretation risks
- tensions that should remain unresolved

This section prevents the review pack from acting like a one-way support brief.

### 5. Draft Problem Statement

This is not yet the final report problem statement.

It is a structured draft that states:
- what product / design / organizational problem appears to be real
- based on the reviewed evidence

### 6. Draft Assumptions

This section must separate:
- assumptions that are materially supported by the reviewed evidence
- assumptions that remain directional or weakly supported

## Final Writeback Structure

The final writeback should use the following default body structure.

### 1. 研究问题

State the single research question for the round.

Also state whether it is:
- user-provided
- or system-proposed and approved

### 2. 综述导言

Explain how the evidence is clustered and what the review is about to do.

It must make clear that the writeback does not jump straight into a conclusion.

### 3. 文献综述

This section is theme-based rather than source-order-based.

Each theme must retain:
- `Direct quote`
- `Paraphrase`
- `Evidence`
- `Why it matters`

This is the minimum standard for a qualified writeback.

### 4. 综合判断

The synthesis may only grow from the review material above.

It must not introduce a major conclusion that has not already been grounded in the review.

### 5. Problem Statement

This section states the real product / design / research problem surfaced by the review.

It must not be a loose summary sentence.

It should behave like a real design or strategy problem statement.

### 6. Assumptions

This section should be split into:
- `被材料支持的 assumptions`
- `仍需验证的 assumptions`

This explicit split is important because it prevents the report from disguising interpretation as evidence.

### 7. AI-native UX 视角

For MVP, this becomes the core design lens.

It should not be treated as an appendix or optional reflection.

The writeback should explicitly interpret the reviewed evidence through AI-native UX concerns such as:
- responsibility surface
- user goal loop
- agent behavior contract
- attention arbitration
- handoff / rollback / escalation timing

### 8. 本轮 Research Direction

This section states what the next round should investigate.

If the system proposes the next direction, it must be labeled:
- `待用户批准`

This is not optional.

### 9. 保留分歧

This section explicitly records unresolved tensions that should not be flattened into the final synthesis.

## AI-Native UX As The MVP Lens

In MVP, the writeback should not try to support every analytical lens equally.

The primary interpretive lens should be AI-native UX.

This does not mean generic usability commentary.

It means the writeback should ask:
- how responsibility becomes visible
- how the system exposes or hides its current role
- when the user is expected to intervene
- how attention is allocated between human and agent
- whether the interaction model reflects a user goal loop rather than a page flow

## UX Reference Source

The folder:

`/Users/vickyshou/.openclaw/workspace/shared/Principles`

should become the long-term reference base for the AI-native UX lens.

However, MVP should not inject the entire folder directly into generation.

Instead, MVP should derive a compact `AI-native UX lens pack` from selected files such as:
- `UX for human、UX of agent、以及 UX of collaboration.md`
- `UX_PRINCIPLES_ATTENTION_ARBITRATION.md`
- `一个合格的 AI native agentic UX designer 要具备的核心能力.md`
- `当今 agent 在人机交互中的主要探索.md`
- selected `Context Engineering` references where they directly shape UX reasoning

This lens pack should then influence:
- what counts as a relevant quote
- how the paraphrase is framed
- how the problem statement is shaped
- what the final UX section focuses on

## What A Qualified Product Analysis Must Also Include

Beyond the few-shot structure, the system should treat these as required analytical qualities.

### 1. Object Boundary

The report should make clear what exactly is being analyzed:
- product capability
- workflow structure
- governance layer
- collaboration protocol
- UX responsibility surface

Without this, the report will drift between layers and make unstable claims.

### 2. Counterargument Handling

A qualified analysis should not only accumulate supportive evidence.

It must also state:
- what weakens the current direction
- what contrary reading remains plausible
- what evidence would change the judgment

### 3. Evidence Stratification

The system should distinguish:
- direct quote
- paraphrase
- synthesized conclusion

This is necessary so the reader can tell which layer a given statement belongs to.

### 4. Confidence Shape

The report should not treat all claims as equally strong.

Even if the first MVP does not yet render explicit confidence labels, the structure should support:
- strongly supported judgments
- moderate support
- directional signals
- still speculative assumptions

### 5. Research Continuity

A good analysis should naturally suggest what the next round should study.

This is why `Research Direction` should be an explicit output object rather than a casual closing thought.

## Generation Strategy

The current single-pass writeback generation should be replaced with a two-stage process.

### Stage 1: Generate Research Review Pack

Input:
- approved research direction
- evidence pool
- user guidance
- AI-native UX lens pack

Output:
- topic clusters
- direct quotes
- paraphrases
- evidence references
- why-it-matters notes
- counter-signals
- draft problem statement
- draft assumptions

### Stage 2: Generate Final Writeback

Input:
- review pack
- writeback intake
- collaboration mode
- target audience

Output:
- research-oriented final writeback

The final writeback may not skip the review pack.

## What MVP Should Not Do

To keep the first implementation tractable, MVP should avoid:

1. supporting all analytical lenses equally
2. full multi-agent review synthesis
3. automatic direction ranking across many candidates
4. full ingestion of the entire `Principles` corpus into the prompt
5. expansion to all matrix variants before one research-grade pilot is proven

## Success Criteria

This redesign succeeds if:
- writebacks are organized around one explicit research question
- the system preserves more original speaker insight through quotes
- literature review precedes analytical closure
- the final report includes explicit problem statements and assumptions
- AI-native UX is a real analytical section, not an appendix
- system-generated research directions require user approval
- the output feels like a research-oriented product analysis rather than a long summary memo

## Failure Modes

This redesign fails if:
- the report still reads like a summary-first analysis
- direct quotes are sparse or ornamental
- paraphrases merely restate quotes without mechanism interpretation
- assumptions are mixed into conclusions without being labeled
- UX remains a generic commentary layer
- the system proposes research directions as if already approved
