---
name: architecture-conductor
description: Use when structuring a new product, agent, agent OS, or human-machine collaboration concept that risks drifting into slogans, premature UX detail, or repeated forced narrowing before direction and structural gates are clear.
---

# Architecture Conductor

## Overview

Use this skill to turn early product discussion into a gated, map-first structuring process.

Core rule:

`Respect the original framing order first. Generate maps second.`

This skill is for:
- agent products
- agent OS
- human-machine collaboration systems
- semi-automated workbenches
- recommendation or triage systems

This skill is not for:
- implementation work
- surface polish
- free-form ideation without gatekeeping

## Failure Pattern This Skill Prevents

Without this skill, agents tend to:
- accept solution slogans as problem definitions
- jump from vague direction to UX detail
- overuse repeated `3 options, pick one` narrowing
- over-drill one case until the framework disappears
- generate tidy structure that skipped the original gate questions

## Stage Model

Always classify the discussion first.

### Stage A / Direction Framing

Use when the direction is still not proven.

Required question families:
- Vision / Doctrine
- Why Now / Capability Fit
- Problem Framing
- Operating Environment / Stakes
- Problem-Solving Flow
- Direction Decision

Required outputs:
- `Direction Brief`
- `direction map`
- `evidence gaps`
- `risk register`
- `gate judgment`

Do not enter Stage B until all five are clear:
- primary problem
- why now
- first wedge
- risks / attention / actuation boundary
- discussion has shifted from `should this exist` to `how does it hold together`

### Stage B / Structure Convergence

Only enter after Stage A gate passes.

Required convergence areas:
- Flow Decomposition
- Human-Machine Collaboration Allocation
- Collaboration Prototype & Unit
- Interaction Prototypes
- Handoff & Human Intervention
- Attention Budget & Modality
- Durable State & Memory
- Surface System
- Evaluation & Rollout

Required outputs:
- `Architecture Brief`
- `macro-to-detail UX scenario map`
- `selected scenario ontology maps`
- `selected scenario state machines`
- `design pattern branches`
- `unresolved contradictions`
- `research requests`

## Questioning Policy

### Ask Breadth-First Before Depth-First

Start by locating:
- current stage
- current layer
- whether the user is shaping the system, a scenario family, or a specific scenario

### Prefer Open Questions Early

Default to open questions when the structure is still broad.

Good:
- "What is the real user problem here, not the proposed solution?"
- "Which scenario families make up this system?"
- "What makes this phone case meaningfully different from a workflow tool?"

Bad:
- repeated forced narrow choices before the branch structure is visible

### Use Options Only To Close A Known Branch Axis

Only offer constrained options when:
- the branch axis is already explicit
- comparison helps convergence
- the options do not flatten important structure

## Map-First Output Strategy

The default output is not just prose.

Build from macro to detail:

### Level 0: System Landscape
- product branch
- form factor
- stakes profile
- collaboration thesis
- scenario families

### Level 1: Scenario Family Structure
- triage
- clarification
- co-creation
- orchestration
- supervision
- recommendation workspace
- memory governance

### Level 2: Scenario Ontology

Use this backbone:

`User Intent -> Work Object -> User Model -> Capability Orchestration -> Result Workspace -> Governance`

### Level 3: Selected Scenario Expansion

Only when needed:
- scenario state machine
- handoff matrix
- attention policy
- pattern branch map

## Case Handling Rule

A case is evidence for the framework.
It is not the framework itself.

Once a case has exposed:
- user intent
- work object
- user model variables
- workspace form
- governance tension

return to the system map.
Do not keep drilling the case unless the user explicitly wants that scenario expanded.

## Ledger

Maintain explicit labels during the run:
- `FACT`
- `ASSUMPTION`
- `OPEN_QUESTION`
- `DECISION`
- `RISK`
- `CONFLICT`
- `TODO_RESEARCH`

Never smooth these away in the final map.

## Gatekeeping Language

Use direct gatekeeping when needed:
- "This is still a solution slogan, not a problem definition."
- "We should not enter Stage B yet."
- "This case has already served the framework; return to the map."
- "The issue is not UI yet; the work object is still unstable."
- "This branch should remain open instead of being forced into one answer."

## Output Shape

A strong run usually ends with:
1. `Direction Brief`
2. `System Map`
3. `Scenario Family Map`
4. `Selected Scenario Expansion`
5. `Contradictions / Gaps / Research Needed`

## Success Criterion

This skill is working if the final result:
- respects original framing order
- preserves gatekeeping pressure
- produces reusable system maps
- avoids premature wedge collapse
- keeps unresolved contradictions visible
