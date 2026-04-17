# Generation Mechanism Upgrade Design

## Goal

Upgrade the current pilot writeback generator from pilot-specific quality patching into a reusable question-driven generation mechanism.

The target is not just to keep `integrated-team-paradigm` readable.
The target is to make the generator produce higher-quality review packs and final writebacks because its intermediate reasoning objects are stronger.

## Core Position

The current pilot quality upgrade improved output shape, but it did not yet fully upgrade the generation mechanism.

The main remaining weakness is that too much of the good result is still encoded as fixed pilot content inside `scripts/writeback_generate.py`.

That means the system currently behaves more like:

`question -> pilot-specific cluster constants -> rendered output`

than like:

`question -> evidence selection -> evidence roles -> thematic clustering -> bounded synthesis -> rendered output`

The next pass must therefore move quality from hardcoded output text into explicit intermediate generation objects.

## Why The Current Pilot Is Still Not Enough

The current pilot already fixed several important issues:
- it no longer reads like a plain source-order memo
- it now groups material into three thematic clusters
- it produces clearer AI-native UX design objects

But it still has four mechanism-level weaknesses:

### 1. Cluster content is still largely hardcoded

`PILOT_REVIEW_PACK_THEME_CLUSTERS` currently stores:
- cluster titles
- quotes
- summaries
- paraphrases
- evidence lists
- why-it-matters text

That makes the pilot look better, but it does not prove the generator can derive those outputs from evidence.

### 2. Evidence does not yet have explicit analytical roles

The generator currently selects evidence lines, but it does not distinguish whether a line functions as:
- speaker-force quote
- mechanism explanation
- governance signal
- UX surface signal
- counter-signal

Without those roles, clustering remains shallow and final synthesis easily becomes repetitive.

### 3. Final writeback sections are still too template-driven

The current final writeback does not yet derive each section from a distinct intermediate object.

As a result:
- `综合判断` can still sound like a polished restatement of review-pack paraphrases
- `Problem Statement` can drift into generic summary
- `Assumptions` can become generic takeaways
- `AI-native UX` can still feel partly appended rather than fully review-derived

### 4. Current tests mostly validate structure, not mechanism quality

The current tests successfully guard against obvious regression, but they do not yet prove:
- that each cluster is evidence-composed rather than prewritten
- that tensions are actually preserved from counter-signals
- that UX design propositions are traceable back to reviewed evidence
- that final synthesis is not just repeating review-pack prose

## Design Scope

This design covers:
- a new intermediate evidence-role layer for writeback generation
- cluster composition rules for the pilot
- stronger separation between review-pack objects and final writeback objects
- stronger quality tests for mechanism-derived output

This design does not cover:
- expanding the mechanism to all matrix variants in the same pass
- redesigning writeback intake again
- adding UI for direction approval
- full recommendation ranking across many research directions
- replacing the current Markdown artifact model

## Main Design Decision

Keep the current top-level pipeline:

`research direction -> review pack -> writeback`

But replace the current pilot-specific cluster rendering with a reusable composition model:

`research direction -> candidate evidence -> evidence roles -> theme clusters -> review object -> final writeback object`

This is the key upgrade.

## New Intermediate Objects

### 1. Evidence Candidate

An `Evidence Candidate` is a normalized candidate line or snippet collected from:
- synthesis evidence summary
- episode summary
- episode highlights
- transcript only when needed for context recovery

Each candidate should retain:
- source slug
- source type
- raw text
- optional timestamp

This object should remain close to source language.

### 2. Evidence Role

Each `Evidence Candidate` should be assigned one or more explicit analytical roles.

The MVP role set should be:
- `speaker_force_quote`
- `mechanism_signal`
- `governance_signal`
- `ux_surface_signal`
- `counter_signal`

These roles are not stylistic tags.
They determine how a piece of evidence may be used.

For example:
- `speaker_force_quote` is preferred when preserving original speaker insight
- `mechanism_signal` supports paraphrase and synthesis
- `governance_signal` helps build problem statements and assumptions
- `ux_surface_signal` constrains AI-native UX design propositions
- `counter_signal` must remain visible in tension handling

### 3. Theme Cluster

A `Theme Cluster` should no longer be a hardcoded prose block.
It should be a composed object with:
- `title`
- `research_question_role`
- `evidence_candidates`
- `selected_quotes`
- `cluster_paraphrase`
- `why_it_matters`
- `counter_signals`

The pilot may still use a pilot-specific cluster schema for the three target clusters:
- `执行控制层`
- `协作与角色层`
- `治理与前台 UX 外显层`

But the content inside those clusters should be composed from evidence roles rather than prewritten.

### 4. Review Object

The review pack should be generated from structured cluster objects rather than direct template prose.

The `Review Object` should minimally include:
- research question
- question source
- review introduction
- ordered theme clusters
- counter-signals and tensions
- draft problem statement
- draft assumptions

This object is the constraint boundary for final writeback generation.

### 5. Final Writeback Object

The final writeback should be generated from the review object through a second bounded transformation.

The `Final Writeback Object` should minimally include:
- research question section
- clustered literature review section
- synthesis judgment section
- product problem section
- assumptions section
- AI-native UX proposition section
- research direction section
- preserved tension section

Each section should have its own derivation rules rather than being rendered from one shared prose template.

## Cluster Composition Rules

The pilot should keep the current three-cluster structure, but with composition rules.

Each cluster must contain:
- at least two evidence items
- at least one `speaker_force_quote`
- at least one non-quote support signal
- a paraphrase that describes mechanism rather than repeating quote wording
- a `why it matters` line tied to the research question

At least one cluster in the review pack must also surface a `counter_signal`.

The same quote should not dominate multiple clusters unless there is a strong reason and that reuse is explicitly bounded.

## Final Writeback Derivation Rules

### Literature Review

The final `文献综述` should be rendered from cluster objects and stay visibly traceable to the review pack.

It should preserve:
- representative quotes
- paraphrase
- evidence references
- why-it-matters logic

But it should become more compact and more question-oriented than the review-pack version.

### 综合判断

`综合判断` should be derived from:
- cluster-level mechanism signals
- recurring governance and collaboration patterns
- visible tensions

It should not repeat the exact wording of review-pack paraphrases.

### Problem Statement

`Problem Statement` should be derived mainly from:
- governance signals
- collaboration-role signals
- execution-boundary signals

It should describe the real product or organizational problem implied by the review, not just summarize the topic.

### Assumptions

`Assumptions` should be derived from review evidence and split into:
- materially supported assumptions
- still-open assumptions

Counter-signals should directly affect which assumptions remain open.

### AI-native UX Propositions

The AI-native UX section should no longer be generated as a mostly standalone lens pack expansion.

Each MVP design proposition should be traceable to one or more review clusters.

For the pilot, design objects such as:
- `责任状态卡`
- `分级决策卡`
- `异步沟通面板`
- `审计与证据抽屉`

may still remain the output form, but each one must derive from reviewed evidence rather than being inserted as a fixed list.

## Testing Strategy Upgrade

The next pass should upgrade tests from shape validation to mechanism validation.

At minimum, tests should verify:

1. each pilot cluster is composed from real evidence candidates rather than only fixed cluster prose
2. each cluster includes different evidence roles rather than two equivalent quote slots
3. at least one counter-signal is preserved in both review pack and final writeback
4. the final `综合判断` is not a direct restatement of review-pack paraphrases
5. each AI-native UX proposition can be mapped back to reviewed cluster evidence
6. regenerated pilot artifacts remain reproducible from the generator

## Implementation Boundaries

This pass should modify only:
- `scripts/writeback_generate.py`
- `tests/test_writeback_generate.py`
- `library/review-packs/podcasts/review-pack-agent-team-paradigm.md`
- `library/writebacks/podcasts/matrix/integrated-team-paradigm.md`

It should not modify:
- `scripts/writeback_intake.py`
- matrix-wide generation rules
- ontology schemas
- unrelated writeback artifacts

## Success Criteria

This pass succeeds if:
- the pilot review pack is composed from evidence-role logic rather than mostly hardcoded cluster prose
- the final writeback sections derive from distinct intermediate objects
- preserved tensions come from actual counter-signals
- AI-native UX propositions become review-traceable rather than appended recommendations
- the pilot remains reproducible and clearly closer to `writeback_fewshot_reference.md`

## Failure Modes To Avoid

This pass fails if:
- the pilot still depends on large prewritten cluster bodies
- evidence role assignment is introduced but not used in rendering
- the final writeback still reads like a relabeled review pack
- tests only check headings and keyword presence
- the implementation grows into matrix-wide generalization before the pilot mechanism is proven
