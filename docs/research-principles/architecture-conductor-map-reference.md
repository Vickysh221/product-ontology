# Architecture Conductor Map Reference

## Purpose

This document is a repository-local reference for the `architecture-conductor` skill.

It exists to provide:

- longer artifact examples than should live inside `SKILL.md`
- stable schema examples for stage outputs
- example map shapes from macro system structure down to selected scenario detail
- a concrete reminder that map output must not bypass the original A/B gate structure

This document is a reference companion.
It is not the primary skill and not the authoritative source of stage order.

## Operating Rule

Always preserve this sequence:

1. `Stage A / Direction Framing`
2. `A->B gate judgment`
3. `Stage B / Structure Convergence`
4. `macro-to-detail UX scenario maps`
5. selected detailed expansion only when justified

The map is not permission to skip direction work.

## Standard Output Family

For a serious run, the artifact family should look like:

- `Direction Brief`
- `Direction Map`
- `Ledger`
- `Architecture Brief` only if Stage B is entered
- `Scenario Family Map` only if Stage B is entered
- `Scenario Ontology Map` only if Stage B is entered
- `Scenario State Machine` only for selected nodes
- `Unresolved Contradictions`
- `Research Requests`

## A-Stage Direction Brief Shape

Recommended JSON shape:

```json
{
  "stage": "A",
  "problem_statement": "string",
  "why_now": {
    "shift": "string",
    "chain_entry": "string",
    "workflow_first_check": "string"
  },
  "first_wedge": "string",
  "user_context": {
    "primary_user": "string",
    "core_context": "string"
  },
  "boundary": {
    "goals": ["string"],
    "non_goals": ["string"],
    "mvp_boundary": "string"
  },
  "assumptions": ["string"],
  "risks": ["string"],
  "gate_evaluation": {
    "primary_problem_clear": true,
    "why_now_clear": true,
    "first_wedge_clear": true,
    "stakes_clear": true,
    "discussion_ready_for_b": false
  },
  "gate_judgment": "enter_b | hold | send_back"
}
```

## Macro System Map Shape

Use a node-edge structure rather than free-form prose.

Recommended JSON shape:

```json
{
  "map_id": "system-landscape-example",
  "map_level": "system_landscape",
  "focus": "high-level product structure",
  "nodes": [
    {
      "id": "branch-1",
      "label": "In-car Agent OS",
      "node_type": "product_branch",
      "notes": "Low-attention environment with strict mode awareness."
    },
    {
      "id": "scenario-1",
      "label": "Trip Coordination",
      "node_type": "scenario_family",
      "notes": "Coordination between destination, timing, passengers, and interruptions."
    },
    {
      "id": "thesis-1",
      "label": "Shared context without overload",
      "node_type": "collaboration_thesis",
      "notes": "The system should reduce re-coordination while respecting driver attention limits."
    }
  ],
  "edges": [
    {
      "from": "branch-1",
      "to": "scenario-1",
      "relation": "contains"
    },
    {
      "from": "branch-1",
      "to": "thesis-1",
      "relation": "organizes_around"
    }
  ]
}
```

## Scenario Ontology Map Shape

Use this backbone:

`User Intent -> Work Object -> User Model -> Capability Orchestration -> Result Workspace -> Governance`

Example:

```json
{
  "map_id": "trip-coordination-ontology",
  "map_level": "scenario_ontology",
  "focus": "family trip coordination",
  "nodes": [
    {
      "id": "intent-1",
      "label": "Reach destination with minimal re-coordination",
      "node_type": "user_intent",
      "notes": "The goal is not chat. The goal is travel coordination."
    },
    {
      "id": "work-1",
      "label": "Trip state workspace",
      "node_type": "work_object",
      "notes": "A shared object holding route, pickup timing, passengers, and constraints."
    },
    {
      "id": "user-model-1",
      "label": "Driver attention + family preference model",
      "node_type": "user_model",
      "notes": "Includes interruption tolerance, children's needs, and preferred update style."
    },
    {
      "id": "cap-1",
      "label": "Navigation + messaging + timing estimation",
      "node_type": "capability_orchestration",
      "notes": "Capabilities are backstage, not the frontstage UX."
    },
    {
      "id": "workspace-1",
      "label": "Coordination result workspace",
      "node_type": "result_workspace",
      "notes": "The user sees a compact status and options, not raw tool traces."
    },
    {
      "id": "gov-1",
      "label": "Interruption and authority guardrails",
      "node_type": "governance",
      "notes": "The system cannot interrupt or act the same way in all states."
    }
  ],
  "edges": [
    {
      "from": "intent-1",
      "to": "work-1",
      "relation": "organizes_into"
    },
    {
      "from": "user-model-1",
      "to": "workspace-1",
      "relation": "conditions"
    },
    {
      "from": "cap-1",
      "to": "workspace-1",
      "relation": "powers"
    },
    {
      "from": "gov-1",
      "to": "workspace-1",
      "relation": "constrains"
    }
  ]
}
```

## Selected Scenario State Machine Shape

Use state machines only after macro structure is stable.

Recommended markdown shape:

```md
# Scenario State Machine

## Scenario
- trip re-coordination during live driving

## Trigger
- route change
- delayed passenger
- destination update

## State Flow
1. Ongoing trip state
2. New coordination signal detected
3. Safety and attention check
4. Compressed coordination object prepared
5. Handoff moment chosen
6. Driver or passenger response
7. Trip state updated

## Handoff Object
- decision-sized coordination card

## Governance Note
- if driver attention is constrained, shift from interrupt to passenger-facing or batched mode
```

## Ledger Shape

The map must stay linked to an explicit ledger.

Recommended JSON shape:

```json
{
  "session_id": "architecture-conductor-demo-001",
  "entries": [
    {
      "label": "FACT",
      "content": "The form factor is in-car agent OS rather than phone agent OS."
    },
    {
      "label": "ASSUMPTION",
      "content": "Passengers can absorb some non-driving coordination burden."
    },
    {
      "label": "RISK",
      "content": "The system may over-interrupt during navigation-critical moments."
    },
    {
      "label": "CONFLICT",
      "content": "High state transparency and low-attention interaction may conflict."
    },
    {
      "label": "TODO_RESEARCH",
      "content": "Need evidence for acceptable passenger-facing versus driver-facing escalation rules."
    }
  ]
}
```

## Good Expansion Pattern

Good sequence:

1. route the form factor
2. clarify the system-level problem
3. produce a broad direction map
4. judge whether Stage B is allowed
5. map scenario families
6. pick one node for deeper expansion
7. stop drilling once the framework value has been extracted

Bad sequence:

1. receive one case
2. immediately ask repeated forced choices
3. jump into card details or state transitions
4. forget the upper system map

## Example Final Output Package

A strong output package usually has:

1. `Direction Brief`
2. `Direction Map`
3. `Scenario Family Map`
4. `Selected Scenario Ontology Map`
5. `Selected Scenario State Machine`
6. `Unresolved Contradictions`
7. `Research Requests`

## Practical Rule

If a map looks neat but the original gate questions were not actually answered, the run is invalid.
