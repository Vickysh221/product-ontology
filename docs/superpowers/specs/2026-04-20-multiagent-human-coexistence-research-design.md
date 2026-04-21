# Multiagent Human Coexistence Research Design

## Goal

Define a research structure for analyzing multiagent human coexistence and collaboration systems.

The structure should distinguish:

- stable system workflow roles
- reusable research preference lenses
- per-run user topic input
- writeback-oriented evidence questions

This document is not an implementation plan.
It is a design draft for the research framing layer that sits above collection and writeback generation.

## Confirmed Group 1

### Human Control, Escalation, And Learning Loop

This group does not ask whether a system is automated.
It asks where automation must stop, how agents should escalate to people, and whether human intervention can become future system capability.

#### 1. When Humans Must Intervene

Research should examine whether the product explicitly defines stable human control points rather than treating human review as an ad hoc fallback.

The core evidence questions are:

- Which nodes require human confirmation?
- Which actions are treated as high-risk, irreversible, or approval-gated?
- Which decisions remain human-owned, including goal definition and standard setting?
- Whether uncertainty, conflict, or shared-memory writeback force escalation to a person

Compressed research question:

`Which critical nodes are reserved for human judgment, and how does the product prevent automated flows from crossing those boundaries?`

#### 2. When Agents Must Escalate To Humans

Research should examine how a product turns uncertainty, conflict, missing permissions, or missing context into requests that a person can actually decide on.

The core evidence questions are:

- Under what conditions does the system expose uncertainty, disagreement, lack of authority, or lack of information?
- Does it interrupt humans per action, or does it compress issues into decision-sized units?
- Does the escalation packet explain what has been done, what is missing, what is recommended, and what the options imply?

Compressed research question:

`How does the product escalate uncertainty, conflict, and authority gaps into requests that are legible and actionable for humans?`

#### 3. Whether Human Intervention Can Be Learned

Research should examine whether a human decision is treated as a one-off patch or as an input that can update future system behavior.

The core evidence questions are:

- Does the system remember the outcome of this intervention?
- Does it affect future handling of similar tasks?
- Is the learning local, persistent, shared, or policy-like?
- Does the product distinguish between a one-off exception, a reusable pattern, and a stable rule?
- What prevents a single human judgment from being over-generalized?

Compressed research question:

`Does the product convert this human intervention into reusable system experience, and can it judge whether similar future situations still require human involvement?`

#### Group-Level Summary

Taken together, this group asks:

`How does the product design control boundaries, escalation behavior, and the learning loop between humans and agents?`

## Confirmed Group 2

### State Legibility And Attention Orchestration

This group asks how system information becomes human-readable under time pressure, cognitive limits, and decision burden.

It does not treat transparency as equivalent to dumping logs onto the interface.
It asks how a product packages, grades, and renders system state so that people can judge what is happening and what they must do next.

#### 1. What Unit Of Information Reaches The Human

Research should examine whether the product exposes raw event streams or compresses many agent actions into decision-sized units.

The core evidence questions are:

- Does the system report agent work action by action, or by issue and decision unit?
- Are multiple agent states, requests, or conflicts compressed into one decision object?
- Does the user first see a decision card, with deeper logs available only as supporting evidence?
- Is system transparency structured as layered disclosure rather than full default expansion?

Compressed research question:

`What information unit does the product present to humans: a stream of events, or a decision-sized issue card?`

#### 2. What Attention Level The Product Assigns To Information

Research should examine how the system decides whether something should interrupt the user, wait for batch review, or remain silent in logs.

The core evidence questions are:

- How does the product distinguish interrupt-worthy items from items that can be deferred?
- Is notification intensity designed by event severity alone, or by human attention budget?
- Which classes of information remain available for audit without demanding immediate attention?
- Does the product explicitly separate interruptive, batched, and silent channels?

Compressed research question:

`How does the product decide whether system information should interrupt, batch, or remain silent, and how is that tied to human attention budget?`

#### 3. Whether System State Is Instantly Legible

Research should examine whether people can identify state, urgency, and required action almost immediately through pattern, color, shape, wording, and visual hierarchy.

This is especially important in embodied systems such as assisted driving, where users may need to recognize required takeover or system state within one second.

The core evidence questions are:

- Can users identify the current state quickly without reading long explanations?
- Does the system use stable visual patterns such as large cards, color systems, line types, shapes, and iconography to signal urgency and role boundaries?
- Are critical conditions rendered in a way that supports immediate action rather than reflective interpretation?
- In spatial or 3D representations, can users infer current driving state, system state, and control responsibility from the rendered environment?
- Does the visual system support one-glance interpretation of handoff, risk, or mode change?

Compressed research question:

`Does the product render system state in a pattern language that enables one-glance human judgment under urgency and cognitive pressure?`

#### Group-Level Summary

Taken together, this group asks:

`How does the product package, prioritize, and render system information so that humans can quickly understand state, urgency, and required action without being overloaded by raw process detail?`

## Confirmed Group 3

### Collaborative UX Specification And State Design

This group asks whether a multiagent human collaboration system has been turned into an explicit UX specification rather than left as an implicit collection of agent capabilities.

It focuses on user flow clarity, state completeness, component behavior, and whether AI-specific conditions are made frontstage.

#### 1. Whether The Collaborative User Flow Is Explicit

Research should examine whether the system clearly specifies how humans and agents move through a shared flow from goal definition to task completion, review, correction, and handoff.

The core evidence questions are:

- Does the product define an explicit collaborative flow from task start to completion?
- Are handoff points between human and agent clearly specified?
- Are review, escalation, approval, correction, and takeover treated as formal flow nodes?
- Is collaboration continuous, or does the user repeatedly have to reconstruct context across broken steps?

Compressed research question:

`Does the product specify a clear collaborative user flow, including handoff, review, correction, and takeover points between humans and agents?`

#### 2. Whether The State Matrix Covers AI Collaboration Reality

Research should examine whether the product defines a complete state model not only for standard UI states but also for AI-specific collaborative states.

The core evidence questions are:

- Does the system define a clear state matrix beyond default, loading, empty, error, and success?
- Are AI-specific states such as low confidence, pending confirmation, takeover required, conflicting agent outputs, memory write pending, insufficient permission, tool failure, and partial completion made explicit?
- Can users understand the system state without inferring it from logs or side effects?
- Are state transitions legible and predictable?

Compressed research question:

`Does the product define an explicit state matrix for human-agent collaboration, including AI-specific uncertainty, conflict, takeover, and pending-writeback states?`

#### 3. Whether Key Collaborative Components Have Clear Behavior

Research should examine whether the product gives formal behavioral definitions to the components that carry collaboration, escalation, and traceability.

The core evidence questions are:

- What are the key collaboration components, such as decision cards, takeover cards, approval cards, memory writeback cards, evidence drawers, and action logs?
- Under what conditions does each component appear?
- What is shown by default, and what is available only after expansion?
- What actions can the user take from each component?
- How does the system state change after the user acts?

Compressed research question:

`Does the product define clear trigger conditions, visibility rules, and user actions for the components that carry collaboration, escalation, and traceability?`

#### 4. Whether AI-Specific Information Is Frontstage

Research should examine whether the system brings AI-specific realities into the frontstage UX rather than hiding them behind documentation, logs, or fallback error states.

The core evidence questions are:

- Does the product make capability boundaries explicit?
- Is uncertainty exposed in the interface rather than hidden?
- Does the system offer a clear correction path when the agent is wrong?
- Does the user know when human takeover is required?
- Are correction and takeover low-friction actions, or are they technically possible but experientially neglected?

Compressed research question:

`Does the product make capability boundaries, uncertainty, correction paths, and human takeover requirements explicit in the frontstage UX?`

#### Group-Level Summary

Taken together, this group asks:

`Has the system turned human-agent collaboration into an explicit UX specification, with defined flows, states, components, and frontstage handling of AI-specific conditions?`

## Confirmed Group 4

### Problem Framing, Goals, And Success Criteria

This group asks whether the product has clearly defined the problem it is solving, the goals it is pursuing, the boundaries it accepts, the risks it depends on, and the metrics by which success will be judged.

It is not enough for a system to have collaborative flows and good state design.
It must also know what problem it is solving, what counts as success, and what tradeoffs it is making.

#### 1. Whether The Problem Is Correctly Framed

Research should examine whether the product clearly defines the problem it is addressing for both users and the business, and whether that framing remains stable across materials.

The core evidence questions are:

- What user problem does the product claim to solve?
- What business or organizational problem does it claim to solve?
- Why is this problem urgent now?
- Is the product addressing efficiency, risk, coordination, trust, or another category of problem?
- Does the problem framing remain stable, or does it shift across different materials?

Compressed research question:

`Does the product clearly and consistently define the user and business problem it is trying to solve?`

#### 2. Whether Goals Are Properly Decomposed

Research should examine whether the product distinguishes among business goals, user goals, delivery goals, and explicit non-goals.

The core evidence questions are:

- Does the product distinguish between business outcomes and user value?
- Are delivery goals and staged rollout goals made explicit?
- Does it state what is out of scope or intentionally deferred?
- Is the product optimizing speed, reduced cognitive load, trust, control, coordination quality, or some other primary objective?

Compressed research question:

`Does the product clearly decompose business goals, user goals, delivery goals, and non-goals?`

#### 3. Whether Boundaries And Success Criteria Are Explicit

Research should examine whether the product defines clear MVP boundaries and testable success conditions rather than relying on abstract promises.

The core evidence questions are:

- What does the current version explicitly do?
- What does it explicitly not do?
- What conditions count as success beyond vague claims of better experience?
- For AI or agent systems, are there explicit conditions for escalation, visibility, reliability, and capability limits?
- Does the product define what failure or unacceptable performance looks like?

Compressed research question:

`Does the product define clear scope boundaries and testable success criteria rather than relying on abstract capability claims?`

#### 4. Whether Risks, Dependencies, And Decision Rationale Are Structured

Research should examine whether the product makes its dependencies, constraints, and decision logic explicit.

The core evidence questions are:

- What technical, data, workflow, or organizational dependencies does the product rely on?
- Are these dependencies exposed honestly, or hidden behind polished narratives?
- Does the system document key tradeoffs and decision rationale?
- Is there evidence of why one design path was chosen instead of another?
- Are risk-bearing choices acknowledged, especially around automation, escalation, and writeback?

Compressed research question:

`Does the product make its dependencies, risks, and design rationale explicit enough to explain why this path was chosen?`

#### 5. Whether Metrics Reflect The Real Collaboration Goal

Research should examine whether the product defines a metric system that matches the actual collaboration problem instead of relying on superficial proxy numbers.

The core evidence questions are:

- How does the product define success after launch?
- Are the metrics tied to the real collaboration goal, such as reduced interruption cost, improved takeover timing, better decision quality, lower rework, or stronger trust?
- Does the metric system distinguish output volume from collaboration quality?
- Are there metrics for human burden, escalation quality, correction success, or memory contamination risk?
- Do the metrics reward the right behavior, or do they encourage over-automation and false confidence?

Compressed research question:

`Does the product define a metric system that measures collaboration quality, human burden, and decision quality rather than just output volume or automation rate?`

#### Group-Level Summary

Taken together, this group asks:

`Does the product clearly define the problem, goals, boundaries, risks, and metrics needed to judge whether the system is actually succeeding?`

## Proposed Group 5

### Evidence, Traceability, And Shared Memory Writeback

This group asks how the system ensures that judgments are grounded in traceable evidence and how only stable enough conclusions are written into shared memory.

It extends beyond evidence collection.
It also asks what is promotable, what must remain provisional, and how the system avoids polluting future reasoning with unstable writeback.

#### 1. Whether Evidence Is Strong Enough To Support Judgment

Research should examine whether judgments are grounded in strong enough evidence rather than weak summaries, vague impressions, or prematurely generalized product rhetoric.

The core evidence questions are:

- Is the judgment grounded in first-hand or otherwise sufficiently strong material?
- Are source strength and source type clearly distinguished?
- Are quotes, excerpts, and context complete enough to support interpretation?
- Has marketing language been mistaken for mechanism?

Compressed research question:

`Is the judgment grounded in strong enough evidence to justify promotion beyond an early reading?`

#### 2. Whether The Inference Chain Is Traceable

Research should examine whether important conclusions can be traced through the chain from source to artifact to interpretation to writeback.

The core evidence questions are:

- Can important conclusions be traced back to specific materials and segments?
- Are facts, interpretations, hypotheses, and disagreements separated clearly?
- Does the writeback preserve the reasoning chain instead of only the final conclusion?
- Are there jumps in interpretation that are not supported by the evidence trail?

Compressed research question:

`Can the system trace important conclusions back through a clear evidence and inference chain?`

#### 3. What Is Allowed To Enter Shared Memory

Research should examine whether the system explicitly distinguishes among stable facts, working hypotheses, unresolved questions, and preserved disagreements before writing to shared memory.

The core evidence questions are:

- What kinds of statements are allowed to enter shared memory?
- Does the system distinguish verified facts from provisional interpretation?
- Are unresolved tensions prevented from being flattened into stable memory?
- Are promotion and demotion rules explicit?

Compressed research question:

`What kinds of conclusions are allowed to enter shared memory, and how are stable judgments distinguished from provisional ones?`

#### 4. How Memory Contamination Is Prevented

Research should examine how the system handles rollback, downgrade, reopening, and scope-limiting of prior writeback.

The core evidence questions are:

- How does the system prevent one weak judgment from contaminating future runs?
- Can wrong or unstable writeback be downgraded, invalidated, or reopened?
- Does the system preserve conflict instead of erasing it too early?
- Are confidence and scope boundaries attached to written memory?

Compressed research question:

`How does the system prevent unstable or incorrect writeback from contaminating future reasoning?`

#### Group-Level Summary

Taken together, this group asks:

`How does the system ensure that judgments are evidence-grounded, traceable, and only written into shared memory at the right level of stability?`

## Proposed Intermediate Artifact Layer

The current repository already contains source, artifact, review-pack, and writeback layers.
To support the confirmed research framework without replacing the existing backbone, one intermediate working layer should be added under `library/sessions/`.

The purpose of this layer is to make multiagent discussion explicit before final review-pack and writeback generation.

### Proposed Working Artifacts

#### 1. Researcher Packet

Suggested path:

- `library/sessions/research-packets/<run-id>/packet.md`

Purpose:

- provide a first-hand-material-first evidence packet
- establish source provenance and context
- prepare a shared factual base for later lens readings

Core contents:

- source inventory
- evidence excerpts
- context notes
- open evidence gaps
- suggested reading angles

#### 2. Lens Reading

Suggested path:

- `library/sessions/lens-readings/<run-id>/<lens-id>.md`

Purpose:

- let an explicit lens interpret the shared packet
- produce structured findings without prematurely collapsing into consensus

Core contents:

- lens purpose
- priority question groups
- key findings
- evidence anchors
- tensions
- unknowns
- provisional judgment

#### 3. Critique Memo

Suggested path:

- `library/sessions/critique-memos/<run-id>/critic.md`

Purpose:

- inspect weak evidence, jumps in logic, rhetoric-vs-mechanism confusion, unresolved conflicts, and memory contamination risks

Core contents:

- evidence weaknesses
- logic gaps
- rhetoric-vs-mechanism warnings
- conflict register
- memory contamination risks
- downgrade or reopen suggestions

#### 4. Synthesis Memo

Suggested path:

- `library/sessions/synthesis-memos/<run-id>/synthesis.md`

Purpose:

- consolidate packet, lens readings, and critique output into a bounded synthesis object
- bridge multiagent discussion into review-pack and writeback generation

Core contents:

- consensus
- preserved disagreements
- open questions
- human decision needed
- promotion candidates
- memory write notes
- writeback seed

### Why This Layer Matters

Without this intermediate layer:

- `Researcher` remains only a collection and import function
- `Opinion Holder` remains hidden inside fixed heuristics and generation defaults
- `Critic` remains a scattered set of downgrade checks
- `Synthesiser` remains fused with final report generation

With this layer:

- evidence packets become explicit
- lens-based interpretation becomes inspectable
- critique becomes separable from synthesis
- synthesis becomes a bridge rather than a hidden step

## Proposed Role-To-Artifact Mapping

This design now recommends the following mapping:

- `Researcher` -> `Researcher Packet`
- `Opinion Holder` -> `Lens Reading`
- `Critic` -> `Critique Memo`
- `Synthesiser` -> `Synthesis Memo`
- `Report Writer` -> `Review Pack` and `Writeback`

`Orchestrator` does not need a separate persistent artifact in the first version.
Its work is to frame the run, coordinate role outputs, and determine when the process should advance, pause, or escalate to human review.
