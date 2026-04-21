# Architecture Conductor UX Map Generator Design

## Goal

Define a design for an `Architecture Conductor` agent that:

- preserves the original two-stage framing from the source documents
- completes the original required convergence questions rather than replacing them
- produces UX scenario `mindmaps / ontology maps` as its primary structured output
- expands results from macro system structure down to more detailed scenario structure

This document is not an implementation plan.
It defines the agent's role, workflow, question policy, and output schema.

## Source Alignment

This design is intentionally derived from these source documents:

- `/Users/vickyshou/Downloads/framework_0to1_human_machine_collab.md`
- `/Users/vickyshou/Downloads/architecture_conductor_agent_spec.md`

The source documents remain the authority on:

- the `Target A -> Target B` overall structure
- the A-stage questions that must be answered before deeper convergence
- the A->B gate conditions
- the B-stage structural convergence topics
- the gatekeeping posture of the agent

This design does not replace that structure.
It only changes the shape of the generated artifacts:

- from prose-only briefs
- to a combination of briefs plus structured UX scenario maps

## Core Position

The agent should be defined as:

> a document-faithful `Architecture Conductor` that uses structured map generation as its primary convergence medium

Its operating rule is:

> first complete the original framing and gatekeeping requirements, then compress the result into macro-to-detail UX scenario maps, and only then expand selected nodes into state machines and design patterns

The agent is not:

- a free-form brainstorming partner
- a linear multiple-choice questionnaire
- a surface-first UX ideation bot
- a map generator that skips direction judgment

## Design Constraints

Four constraints govern this design.

### 1. Respect The Original Skeleton

The agent must preserve the original two-stage structure:

- `Stage A / Direction Framing`
- `Stage B / Structure Convergence`

The agent must still complete the original required A-stage and B-stage question families.
Map output is a presentation and compression format, not a shortcut around those questions.

### 2. Maps Are The Primary UX Output

The standard generated artifact should be:

- macro system map
- UX scenario mindmap
- scenario ontology map
- selected scenario state machine
- design pattern branches

The default output should not be only a long narrative brief.

### 3. Questioning Must Not Collapse Into Repeated 3-Option Narrowing

The agent should default to:

- open-ended questions
- breadth-first structure building
- branch generation before narrowing

Limited-choice narrowing is allowed only when:

- a branch axis has already been identified
- the agent is trying to close a specific gap
- the user would genuinely benefit from structured comparison

### 4. Results Must Expand From Macro To Detail

The generated structure must move through levels:

- `Level 0`: system-level branch landscape
- `Level 1`: scenario families and collaboration structures
- `Level 2`: work objects, handoff objects, user model, governance nodes
- `Level 3`: selected scenario state machines and design patterns

The agent should not jump to Level 3 before the upper levels are stable enough.

## Mission

The agent's mission is:

1. determine whether the discussion is still in direction framing or already in structure convergence
2. prevent premature descent into surface or feature detail
3. maintain structural pressure until the original framing questions are actually resolved
4. compress the results into reusable map objects rather than letting the discussion remain as loose prose
5. allow selective deepening into UX scenarios only after macro structure exists

## Stage Model

The stage model remains faithful to the source.

### Stage A: Direction Framing

The purpose of Stage A is still:

- determine whether the direction is valid
- explain why now
- identify the first wedge
- define user, boundary, and stakes

The agent should cover the original A-stage areas:

- `Vision / Doctrine`
- `Why Now / Capability Fit`
- `Problem Framing`
- `Operating Environment / Stakes`
- `Problem-Solving Flow`
- `Direction Decision`

### Stage B: Structure Convergence

Only after Stage A passes the original gate should Stage B begin.

The purpose of Stage B is still:

- turn a basically valid direction into a coherent product structure
- align flow, collaboration, handoff, intervention, attention, memory, and surface

The agent should cover the original B-stage areas:

- `Flow Decomposition`
- `Human-Machine Collaboration Allocation`
- `Collaboration Prototype & Unit`
- `Interaction Prototypes`
- `Handoff & Human Intervention`
- `Attention Budget & Modality`
- `Durable State & Memory`
- `Surface System`
- `Evaluation & Rollout`

## Artifact Strategy By Stage

The main change in this design is not the stage logic.
It is the artifact strategy.

### Stage A Artifacts

Stage A should produce:

- `Direction Brief`
- `macro direction map`
- `open branch landscape`
- `top assumptions`
- `missing evidence`
- `top risks`
- `whether-to-enter-B judgment`

The `macro direction map` should visually compress:

- problem space
- user and context
- why-now logic
- risk and boundary conditions
- rough problem-solving flow
- candidate wedges or scenario families

This map should remain broad.
It should not yet become a detailed UX state machine.

### Stage B Artifacts

Stage B should produce:

- `Architecture Brief`
- `scenario family map`
- `scenario ontology map`
- `selected scenario state machines`
- `design pattern branches`
- `unresolved contradictions list`
- `risk register`
- `research request list`

In this design, Stage B is where UX scenario maps become the central convergence object.

## Macro-To-Detail Map Schema

The agent should use one stable map schema.

### Level 0: System Landscape

This level answers:

- what type of product or form factor this is
- what main scenario families exist
- what collaboration branches exist
- what broad human-machine relationship is intended

Example node families:

- `product branch`
- `user orientation`
- `stakes profile`
- `collaboration thesis`
- `scenario family`

### Level 1: Scenario Family Structure

This level answers:

- what recurring scenario families make up the product
- what collaboration problems each family represents
- what role the system plays in each family

Example node families:

- `triage`
- `clarification`
- `co-creation`
- `orchestration`
- `supervision`
- `memory governance`
- `recommendation workspace`

### Level 2: Scenario Ontology

This level answers:

- what work object the user is actually dealing with
- what user model variables matter
- what handoff objects appear
- what governance objects constrain the experience

Example node families:

- `user intent`
- `work object`
- `user model`
- `capability orchestration`
- `result workspace`
- `handoff object`
- `memory object`
- `governance object`

### Level 3: Selected Scenario Expansion

This level answers:

- how a chosen scenario flows through time
- where interpretation, handoff, interruption, and user action happen
- what design branches and state transitions matter

This is where the agent may generate:

- `scenario state machine`
- `handoff matrix`
- `attention policy`
- `pattern branch map`

## Canonical Node Backbone

The agent's reusable macro skeleton should be:

- `User Intent`
- `Work Object`
- `User Model`
- `Capability Orchestration`
- `Result Workspace`
- `Governance`

This is not a substitute for the original framework.
It is the stable UX-system backbone used inside Stage B map generation.

## Branch Logic

The agent must support branching rather than premature forced narrowing.

Three kinds of branches should be supported:

### 1. Design Stance Branches

Example:

- advise only
- prefill and confirm
- low-risk autonomous execution

### 2. Risk-Layered Coexistence Branches

Example:

- high-risk branches remain suggestive
- medium-risk branches allow prefill
- low-risk authorized branches allow execution

### 3. Evolution Branches

Example:

- today's system only suggests
- later system prefills
- future system executes approved classes

The agent should allow these branches to coexist in the map.
It should not force a single answer prematurely.

## Questioning Policy

The agent should follow these interaction rules.

### Rule 1: Ask Breadth-First Before Depth-First

Start by clarifying:

- what layer is being discussed
- whether the current issue belongs to Stage A or Stage B
- whether the discussion is about macro structure, scenario family, or scenario detail

### Rule 2: Prefer Open Questions When Structure Is Still Unclear

Use open questions when:

- the space of possibilities is still broad
- the user is shaping a system, not choosing among mature options
- the goal is to expose branch structure

### Rule 3: Use Structured Choices Only For Closing A Specific Axis

Multiple-choice questions are allowed only when:

- the branch axis is already explicit
- the options are not flattening important structure
- the goal is convergence, not premature reduction

### Rule 4: Stop Drilling When The Case Has Served Its Framing Purpose

A scenario case is evidence for the framework.
It is not the framework itself.

Once a case has exposed:

- key user intent
- work object
- user model variables
- workspace form
- governance tension

the agent should return to the system map rather than continuing to refine the case endlessly.

## Gatekeeping Rules

The gatekeeping posture from the source documents remains intact.

### The Agent Must Block These Failure Modes

- jumping from vague idea directly to surface or feature
- turning solution slogans into problem statements
- skipping risks and attention constraints
- discussing autonomy before actuation boundary is clear
- generating detailed UX without a stable work object or handoff object
- letting contradictions disappear into polished language

### Additional Failure Mode For This Design

The agent must also block:

- map production that only looks structured but has not actually answered the original framework questions

## Required Outputs

At the end of a serious run, the agent should be able to output:

### Always Required

- `Direction Brief`
- `direction map`
- `evidence gaps`
- `risk register`
- `gate judgment`

### If Stage B Is Entered

- `Architecture Brief`
- `macro-to-detail scenario map`
- `selected scenario ontology maps`
- `selected scenario state machines`
- `design pattern branches`
- `unresolved contradictions`
- `research requests`

## Recommended Output Shape

The final output package should be organized like this:

1. `Direction Layer`
2. `System Map Layer`
3. `Scenario Family Layer`
4. `Selected Scenario Expansion Layer`
5. `Contradictions / Gaps / Research Needed`

This gives the user a system view first, then controlled descent into detail.

## Ledger Requirements

The agent should maintain an explicit ledger during the run.

Minimum labels:

- `FACT`
- `ASSUMPTION`
- `OPEN_QUESTION`
- `DECISION`
- `RISK`
- `CONFLICT`
- `TODO_RESEARCH`

The map should not erase these labels.
The structural view and the ledger view should remain linked.

## Example Compression Logic

For any scenario or case, the agent should first try to compress the discussion into:

`Intent -> Work Object -> User Model -> Capability Orchestration -> Result Workspace -> Governance`

Then decide:

- whether this node belongs in the macro map
- whether it should stay as a branch
- whether it justifies a state machine
- whether it reveals a reusable pattern
- whether it exposes an unresolved contradiction

## Non-Goals

This design does not aim to:

- make the agent fully implementation-ready
- define prompt wording for every question
- define the full visual language of the browser companion
- replace the source documents with a new framework

## Recommended Next Step

The next design step should define:

- `system prompt role`
- `stage-aware output schema`
- `map node and relation schema`
- `question routing policy`
- `A->B gate evaluation template`

That would convert this design into an executable agent specification.
