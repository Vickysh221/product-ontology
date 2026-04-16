# Pilot Writeback Quality Upgrade Design

## Goal

Upgrade the current `integrated-team-paradigm` pilot so it behaves like a qualified research-oriented product analysis, not just a structurally correct research-direction writeback.

This pass is explicitly about quality, not breadth.

## Scope

This design covers:
- one pilot-specific quality upgrade for the research review pack
- one pilot-specific quality upgrade for the final writeback
- stronger quality regressions for the pilot

This design does not cover:
- expanding the new behavior to all 12 matrix variants
- redesigning the intake model again
- adding multi-lens review rendering
- building a general recommendation engine for research directions
- indexing the whole `Principles` directory

## Core Position

The current pilot is structurally better than the earlier longform version, but it still fails an important standard:

it reads like a research workflow artifact that has been cleaned up, not like a strong product-analysis writeback that preserves speaker insight and then grows real analytical closure from it.

The main problem is not only wording.
It is the current organization strategy.

The pilot still stays too close to:
- source-by-source review entries
- uniform quote distribution
- repeated paraphrase logic
- thin UX interpretation

The next upgrade must therefore improve the generation mechanism for this pilot, not just patch a few sentences by hand.

## Main Design Decision

Keep the current research-direction-first pipeline:

`research direction -> review pack -> writeback`

But upgrade both intermediate and final outputs so they are organized around three thematic clusters rather than one section per source.

This is the key change.

## Why A Pilot-Specific Upgrade Is Correct

The system has already changed generation behavior significantly in this rollout.

At this point, the correct next move is not to expand the pattern across the matrix.
The correct move is to make one pilot genuinely good enough to serve as the quality reference.

That means this pass should accept some pilot-specific logic if it materially improves analytical quality and keeps the implementation narrow.

## The Three Theme Clusters

The upgraded review pack and final writeback should group evidence into these three clusters.

### 1. 执行控制层

This cluster covers:
- harness engineering
- sandbox / container
- permissions
- tests / review / approval
- the practical conditions under which agents can work for extended periods without collapsing into random trial-and-error

The point of this cluster is to show that sustained agent execution is not a raw model property.
It is a controlled execution design.

### 2. 协作与角色层

This cluster covers:
- Team of Agents
- role assignment
- asynchronous documents
- human escalation paths
- waiting, handoff, and decision routing

The point of this cluster is to show that the minimal unit of interaction is no longer “one user with one assistant.”
It is becoming a managed collaboration network.

### 3. 治理与前台 UX 外显层

This cluster covers:
- permissions
- auditability
- responsibility boundaries
- enterprise coordination
- how governance becomes visible or invisible in the front stage

The point of this cluster is to connect product structure to AI-native UX.
This is where responsibility surface, attention arbitration, and escalation timing should enter the report.

## Review Pack Upgrade

The current review pack should be upgraded from five source-tied theme entries into three cluster-based literature-review sections.

Each cluster must contain:
- at least two `Direct quote` items
- one synthesized `Paraphrase`
- one `Evidence` list
- one `Why it matters` explanation

The cluster should not simply repeat the same sentence shape five times.

Instead, it should behave like a mini literature review:
- collect related evidence
- show two or more representative quotes
- explain the mechanism-level meaning of the cluster

## Final Writeback Upgrade

The final writeback should remain distinct from the review pack, but it should now be upgraded in parallel with it.

The final writeback should keep the same major section set introduced in the research-direction rollout:
- `研究问题`
- `综述导言`
- `文献综述`
- `综合判断`
- `Problem Statement`
- `Assumptions`
- `AI-native UX 视角下的 MVP 设计命题`
- `本轮 Research Direction`
- `保留分歧`

However, the quality standard of those sections must rise.

## Literature Review Expectations

The `文献综述` section in the final writeback should now mirror the three cluster structure.

Each cluster should include:
- multiple representative quotes
- explicit evidence references
- a more compact paraphrase than the review-pack version
- a clearer explanation of why the cluster matters to the research question

The final writeback should still preserve source traceability, but it should no longer feel like a dressed-up review dossier.

## Problem Statement Expectations

The current problem statement is directionally correct, but still too close to a generic summary of the topic.

The upgraded version should make explicit that the real product problem is not:
- “how do we make agents stronger”

It is:
- how to turn agents into a governable execution network
- without pulling the human back into constant supervision
- while still preserving accountability, escalation, and coordination structure

This should read like a real design/research problem, not like a report conclusion paraphrased as a question.

## Assumptions Expectations

The upgraded assumptions should:
- be fewer
- be sharper
- be more obviously derived from the clustered review

The split should remain:
- `被材料支持的 assumptions`
- `仍需验证的 assumptions`

But the content should now reflect the three-cluster structure instead of sounding like generic high-level takeaways.

## AI-Native UX Upgrade

The current AI-native UX section is still too close to a keyword list.

The upgraded version should become a set of MVP design propositions.

It should not merely say:
- responsibility
- handoff
- rollback

It should explicitly propose front-stage design objects such as:
- responsibility state cards
- decision-tier cards
- asynchronous coordination panels
- audit / evidence drawers

This is the most important analytical upgrade in the final writeback.

The section should show how UX becomes the surface where:
- responsibility is displayed
- escalation timing is negotiated
- attention is allocated
- agent behavior contracts become legible

## What A Qualified Product Analysis Must Demonstrate In This Pilot

This pilot should now explicitly demonstrate these properties:

### 1. It Preserves Original Insight Before Synthesis

The report should not rush to synthesis.
The quotes must feel like meaningful retained speaker insight, not just decorative evidence snippets.

### 2. It Organizes By Research Question

The structure should make it obvious that the report is answering one question, not merely summarizing five podcast episodes.

### 3. It Distinguishes Layers

The report should clearly distinguish:
- direct evidence
- paraphrase
- analytical judgment

### 4. It Produces A Real Product Problem

The problem statement should be actionable as a design or research object.

### 5. It Produces Real MVP Design Implications

The AI-native UX section should not be a philosophy note.
It should produce concrete design implications.

## Implementation Boundaries

This pass should only modify:
- `scripts/writeback_generate.py`
- `library/review-packs/podcasts/review-pack-agent-team-paradigm.md`
- `library/writebacks/podcasts/matrix/integrated-team-paradigm.md`
- `tests/test_writeback_generate.py`

It should not modify:
- `scripts/writeback_intake.py`
- matrix-wide output generation
- ontology schemas
- multi-lens review infrastructure

## Testing Strategy

The updated tests should assert quality signals that are strong enough to prevent regression into the current weak pattern.

At minimum, the pilot tests should check:

1. the review pack uses three cluster sections rather than five source-by-source entries
2. each cluster includes multiple quotes
3. the final writeback is not a direct restatement of the review-pack scaffolding
4. the AI-native UX section contains explicit MVP design objects, not only keyword bullets
5. the pilot remains reproducible from the generator

## Success Criteria

This pass succeeds if:
- the review pack becomes a real clustered literature review
- the final writeback reads like a stronger product analysis than the current pilot
- the report preserves more original speaker force
- the problem statement and assumptions become more precise
- the AI-native UX section becomes concretely design-oriented
- the upgraded pilot remains reproducible by the generator

## Failure Modes

This pass fails if:
- the pilot still reads like one source per section
- the quotes are still evenly distributed but analytically weak
- the final writeback still feels like a relabeled review pack
- the UX section remains mostly a keyword list
- the implementation grows beyond the single-pilot scope
