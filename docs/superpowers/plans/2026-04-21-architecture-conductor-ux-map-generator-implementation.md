# Architecture Conductor UX Map Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the approved design into an executable agent package with a concrete agent prompt, output contract, stage-aware schemas, reusable templates, and repository tests.

**Architecture:** Keep the implementation documentation-first. Add a new `Architecture Conductor` agent definition under `agents/`, formalize required outputs with JSON schemas under `schemas/`, provide reusable markdown templates under `templates/`, and lock the package down with a pytest conformance suite plus example fixture records.

**Tech Stack:** Markdown, JSON, pytest, Python standard library, shell validation with `python3 -m json.tool`, git

---

## File Structure

### Create

- `agents/architecture-conductor agent.md`
- `agents/architecture-conductor output contract.md`
- `schemas/architecture-conductor-output-manifest.json`
- `schemas/direction-brief.schema.json`
- `schemas/architecture-brief.schema.json`
- `schemas/ux-scenario-map.schema.json`
- `schemas/architecture-conductor-ledger.schema.json`
- `templates/direction-brief.md`
- `templates/architecture-brief.md`
- `templates/ux-scenario-map.md`
- `templates/architecture-conductor-ledger.md`
- `tests/test_architecture_conductor_spec.py`
- `tests/fixtures/architecture_conductor/direction_brief.json`
- `tests/fixtures/architecture_conductor/architecture_brief.json`
- `tests/fixtures/architecture_conductor/ux_scenario_map.json`
- `tests/fixtures/architecture_conductor/ledger.json`

### Modify

- none

### Keep Unchanged

- `docs/superpowers/specs/2026-04-21-architecture-conductor-ux-map-generator-design.md`
- `schemas/ontology-manifest.json`
- existing agents unrelated to `Architecture Conductor`
- `.superpowers/brainstorm/` session artifacts

## Task 1: Add Failing Conformance Tests For The Executable Agent Package

**Files:**
- Create: `tests/test_architecture_conductor_spec.py`
- Test: `pytest tests/test_architecture_conductor_spec.py -v`

- [ ] **Step 1: Write the failing pytest file**

Create `tests/test_architecture_conductor_spec.py` with this content:

```python
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]

AGENT_DOC = ROOT / "agents" / "architecture-conductor agent.md"
OUTPUT_CONTRACT = ROOT / "agents" / "architecture-conductor output contract.md"
OUTPUT_MANIFEST = ROOT / "schemas" / "architecture-conductor-output-manifest.json"
SCHEMA_DIR = ROOT / "schemas"
TEMPLATE_DIR = ROOT / "templates"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "architecture_conductor"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_agent_docs_exist():
    assert AGENT_DOC.exists(), "missing Architecture Conductor agent spec"
    assert OUTPUT_CONTRACT.exists(), "missing Architecture Conductor output contract"


def test_agent_doc_contains_stage_gate_and_question_policy():
    text = read_text(AGENT_DOC)
    required_phrases = [
        "Stage A / Direction Framing",
        "Stage B / Structure Convergence",
        "Direction Brief",
        "Architecture Brief",
        "Ask breadth-first before depth-first",
        "FACT",
        "ASSUMPTION",
        "CONFLICT",
        "do not enter Stage B",
    ]
    for phrase in required_phrases:
        assert phrase in text, f"missing phrase in agent doc: {phrase}"


def test_output_contract_defines_stage_aware_artifacts():
    text = read_text(OUTPUT_CONTRACT)
    required_phrases = [
        "Direction Brief",
        "Architecture Brief",
        "UX Scenario Map",
        "Ledger",
        "Only when Stage B is entered",
        "append-only",
    ]
    for phrase in required_phrases:
        assert phrase in text, f"missing phrase in output contract: {phrase}"


def test_output_manifest_lists_expected_schema_and_template_files():
    manifest = read_json(OUTPUT_MANIFEST)
    assert manifest["agent_id"] == "architecture-conductor"
    assert manifest["schemas"] == [
        "schemas/direction-brief.schema.json",
        "schemas/architecture-brief.schema.json",
        "schemas/ux-scenario-map.schema.json",
        "schemas/architecture-conductor-ledger.schema.json",
    ]
    assert manifest["templates"] == [
        "templates/direction-brief.md",
        "templates/architecture-brief.md",
        "templates/ux-scenario-map.md",
        "templates/architecture-conductor-ledger.md",
    ]


def test_direction_brief_schema_has_required_gate_fields():
    schema = read_json(SCHEMA_DIR / "direction-brief.schema.json")
    assert schema["title"] == "DirectionBrief"
    assert schema["properties"]["stage"]["const"] == "A"
    assert schema["required"] == [
        "stage",
        "problem_statement",
        "why_now",
        "first_wedge",
        "user_context",
        "boundary",
        "assumptions",
        "risks",
        "gate_evaluation",
        "gate_judgment",
    ]
    assert schema["properties"]["gate_evaluation"]["required"] == [
        "primary_problem_clear",
        "why_now_clear",
        "first_wedge_clear",
        "stakes_clear",
        "discussion_ready_for_b",
    ]
    assert schema["properties"]["gate_judgment"]["enum"] == [
        "enter_b",
        "hold",
        "send_back",
    ]


def test_architecture_brief_schema_has_required_convergence_fields():
    schema = read_json(SCHEMA_DIR / "architecture-brief.schema.json")
    assert schema["title"] == "ArchitectureBrief"
    assert schema["properties"]["stage"]["const"] == "B"
    assert schema["required"] == [
        "stage",
        "flow_decomposition",
        "collaboration_allocation",
        "collaboration_prototype",
        "handoff_and_intervention",
        "attention_and_modality",
        "durable_state_and_memory",
        "surface_system",
        "evaluation_and_rollout",
        "unresolved_contradictions",
    ]


def test_scenario_map_schema_supports_macro_to_detail_levels():
    schema = read_json(SCHEMA_DIR / "ux-scenario-map.schema.json")
    assert schema["properties"]["map_level"]["enum"] == [
        "system_landscape",
        "scenario_family",
        "scenario_ontology",
        "scenario_state_machine",
    ]
    assert schema["required"] == [
        "map_id",
        "map_level",
        "focus",
        "nodes",
        "edges",
    ]


def test_ledger_schema_enforces_structured_labels():
    schema = read_json(SCHEMA_DIR / "architecture-conductor-ledger.schema.json")
    assert schema["required"] == ["session_id", "entries"]
    assert schema["properties"]["entries"]["items"]["properties"]["label"]["enum"] == [
        "FACT",
        "ASSUMPTION",
        "OPEN_QUESTION",
        "DECISION",
        "RISK",
        "CONFLICT",
        "TODO_RESEARCH",
    ]


def test_templates_include_required_sections():
    direction = read_text(TEMPLATE_DIR / "direction-brief.md")
    architecture = read_text(TEMPLATE_DIR / "architecture-brief.md")
    scenario_map = read_text(TEMPLATE_DIR / "ux-scenario-map.md")
    ledger = read_text(TEMPLATE_DIR / "architecture-conductor-ledger.md")

    assert "## Direction Summary" in direction
    assert "## A->B Gate Evaluation" in direction
    assert "## Handoff Judgment" in direction
    assert "## Collaboration Allocation" in architecture
    assert "## Unresolved Contradictions" in architecture
    assert "## Nodes" in scenario_map
    assert "## Edges" in scenario_map
    assert "## Ledger Entries" in ledger


def test_example_fixtures_parse_and_cover_required_top_level_keys():
    direction = read_json(FIXTURE_DIR / "direction_brief.json")
    architecture = read_json(FIXTURE_DIR / "architecture_brief.json")
    scenario_map = read_json(FIXTURE_DIR / "ux_scenario_map.json")
    ledger = read_json(FIXTURE_DIR / "ledger.json")

    assert set(direction) >= {
        "stage",
        "problem_statement",
        "why_now",
        "first_wedge",
        "gate_evaluation",
        "gate_judgment",
    }
    assert set(architecture) >= {
        "stage",
        "flow_decomposition",
        "collaboration_allocation",
        "surface_system",
    }
    assert set(scenario_map) >= {"map_id", "map_level", "focus", "nodes", "edges"}
    assert set(ledger) >= {"session_id", "entries"}
```

- [ ] **Step 2: Run the new test file and verify it fails**

Run:

```bash
pytest tests/test_architecture_conductor_spec.py -v
```

Expected:
- multiple `FAILED` checks because the new agent docs, schemas, templates, and fixtures do not exist yet

- [ ] **Step 3: Commit the failing-test scaffold**

```bash
git add tests/test_architecture_conductor_spec.py
git commit -m "test: add Architecture Conductor conformance checks"
```

## Task 2: Create The Executable Agent Prompt And Output Contract

**Files:**
- Create: `agents/architecture-conductor agent.md`
- Create: `agents/architecture-conductor output contract.md`
- Test: `pytest tests/test_architecture_conductor_spec.py -v`

- [ ] **Step 1: Write the executable agent prompt**

Create `agents/architecture-conductor agent.md` with this content:

```md
## Identity

An `Architecture Conductor` agent with gatekeeping authority.

It is not a generic assistant.
It is not a surface-first UX ideation bot.
It is responsible for preserving stage order and structural convergence.

## Mission

1. Determine whether the discussion is in `Stage A / Direction Framing` or `Stage B / Structure Convergence`
2. Prevent premature descent into feature, surface, and implementation detail
3. Maintain a structured ledger of facts, assumptions, risks, conflicts, and open questions
4. Convert resolved discussion into durable map artifacts and stage briefs
5. Refuse to enter Stage B when Stage A gates are not satisfied

## Stage A / Direction Framing

Required question families:
- Vision / Doctrine
- Why Now / Capability Fit
- Problem Framing
- Operating Environment / Stakes
- Problem-Solving Flow
- Direction Decision

Required output:
- Direction Brief
- direction map
- evidence gaps
- risk register
- gate judgment

Do not enter Stage B until:
- the primary problem is clear
- why-now logic is stated
- the first wedge is defined
- risks and actuation boundary are explicit
- the discussion has shifted from `should this exist` to `how does this hold together`

## Stage B / Structure Convergence

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

Required output:
- Architecture Brief
- macro-to-detail UX scenario maps
- selected scenario state machines
- design pattern branches
- unresolved contradictions
- research requests

## Questioning Policy

### Ask breadth-first before depth-first

First identify:
- what layer is being discussed
- whether the topic belongs to Stage A or Stage B
- whether the user is shaping a system, a scenario family, or a detailed scenario

### Prefer open-ended questions while structure is still broad

Use open-ended questions by default.
Do not reduce the conversation to repeated three-option narrowing.

### Use structured options only to close a known branch axis

Structured comparison is allowed only when:
- the branch axis is explicit
- the options do not flatten the structure
- the goal is convergence rather than exploration

### Stop drilling when the case has already served the framework

A case is evidence for the framework.
It is not the framework itself.

## Macro-To-Detail Output Backbone

When Stage B is entered, organize maps through:
- Level 0: system landscape
- Level 1: scenario families
- Level 2: scenario ontology
- Level 3: selected scenario state machine

Canonical node backbone:
- User Intent
- Work Object
- User Model
- Capability Orchestration
- Result Workspace
- Governance

## Ledger Labels

- FACT
- ASSUMPTION
- OPEN_QUESTION
- DECISION
- RISK
- CONFLICT
- TODO_RESEARCH

## Success Criterion

A successful run:
- completes the original stage questions rather than skipping them
- preserves gatekeeping pressure
- produces reusable maps instead of loose brainstorming
- exposes unresolved contradictions rather than smoothing them away
```

- [ ] **Step 2: Write the output contract**

Create `agents/architecture-conductor output contract.md` with this content:

```md
## Purpose

Define the durable artifacts that an `Architecture Conductor` run must produce.

The goal is structured convergence artifacts, not only a chat reply.

## Default Output Root

~~~text
library/sessions/architecture-conductor/<project-id>/
~~~

## Required Outputs

### 1. Direction Brief

Path:
~~~text
library/sessions/architecture-conductor/<project-id>/direction-brief.json
~~~

Required when:
- every serious run

### 2. Direction Map

Path:
~~~text
library/sessions/architecture-conductor/<project-id>/direction-map.json
~~~

Required when:
- Stage A has enough structure to summarize the direction

### 3. Ledger

Path:
~~~text
library/sessions/architecture-conductor/<project-id>/ledger.json
~~~

Required when:
- every serious run

### 4. Architecture Brief

Path:
~~~text
library/sessions/architecture-conductor/<project-id>/architecture-brief.json
~~~

Only when Stage B is entered.

### 5. UX Scenario Map

Path:
~~~text
library/sessions/architecture-conductor/<project-id>/scenario-map.json
~~~

Only when Stage B is entered.

## Optional Outputs

### 6. Scenario State Machine

Path:
~~~text
library/sessions/architecture-conductor/<project-id>/state-machines/<scenario-id>.json
~~~

Use only when a selected scenario has been expanded beyond ontology level.

## Overwrite Policy

- append-only for historical session folders
- do not overwrite prior runs
- create a fresh timestamped session folder for each new serious run
- keep the ledger append-only within a run
```

- [ ] **Step 3: Run the conformance test file and verify only the doc-related assertions pass**

Run:

```bash
pytest tests/test_architecture_conductor_spec.py -v
```

Expected:
- `test_agent_docs_exist` passes
- `test_agent_doc_contains_stage_gate_and_question_policy` passes
- `test_output_contract_defines_stage_aware_artifacts` passes
- schema, template, fixture, and manifest tests still fail

- [ ] **Step 4: Commit the agent docs**

```bash
git add 'agents/architecture-conductor agent.md' 'agents/architecture-conductor output contract.md'
git commit -m "docs: add Architecture Conductor executable agent package"
```

## Task 3: Add Stage-Aware Output Schemas And The Output Manifest

**Files:**
- Create: `schemas/architecture-conductor-output-manifest.json`
- Create: `schemas/direction-brief.schema.json`
- Create: `schemas/architecture-brief.schema.json`
- Create: `schemas/ux-scenario-map.schema.json`
- Create: `schemas/architecture-conductor-ledger.schema.json`
- Test: `python3 -m json.tool schemas/architecture-conductor-output-manifest.json`
- Test: `pytest tests/test_architecture_conductor_spec.py -v`

- [ ] **Step 1: Create the output manifest**

Create `schemas/architecture-conductor-output-manifest.json` with this content:

```json
{
  "agent_id": "architecture-conductor",
  "schemas": [
    "schemas/direction-brief.schema.json",
    "schemas/architecture-brief.schema.json",
    "schemas/ux-scenario-map.schema.json",
    "schemas/architecture-conductor-ledger.schema.json"
  ],
  "templates": [
    "templates/direction-brief.md",
    "templates/architecture-brief.md",
    "templates/ux-scenario-map.md",
    "templates/architecture-conductor-ledger.md"
  ]
}
```

- [ ] **Step 2: Create the Direction Brief schema**

Create `schemas/direction-brief.schema.json` with this content:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DirectionBrief",
  "type": "object",
  "required": [
    "stage",
    "problem_statement",
    "why_now",
    "first_wedge",
    "user_context",
    "boundary",
    "assumptions",
    "risks",
    "gate_evaluation",
    "gate_judgment"
  ],
  "properties": {
    "stage": { "const": "A" },
    "problem_statement": { "type": "string" },
    "why_now": {
      "type": "object",
      "required": ["shift", "chain_entry", "workflow_first_check"],
      "properties": {
        "shift": { "type": "string" },
        "chain_entry": { "type": "string" },
        "workflow_first_check": { "type": "string" }
      }
    },
    "first_wedge": { "type": "string" },
    "user_context": {
      "type": "object",
      "required": ["primary_user", "core_context"],
      "properties": {
        "primary_user": { "type": "string" },
        "core_context": { "type": "string" }
      }
    },
    "boundary": {
      "type": "object",
      "required": ["goals", "non_goals", "mvp_boundary"],
      "properties": {
        "goals": { "type": "array", "items": { "type": "string" } },
        "non_goals": { "type": "array", "items": { "type": "string" } },
        "mvp_boundary": { "type": "string" }
      }
    },
    "assumptions": { "type": "array", "items": { "type": "string" } },
    "risks": { "type": "array", "items": { "type": "string" } },
    "gate_evaluation": {
      "type": "object",
      "required": [
        "primary_problem_clear",
        "why_now_clear",
        "first_wedge_clear",
        "stakes_clear",
        "discussion_ready_for_b"
      ],
      "properties": {
        "primary_problem_clear": { "type": "boolean" },
        "why_now_clear": { "type": "boolean" },
        "first_wedge_clear": { "type": "boolean" },
        "stakes_clear": { "type": "boolean" },
        "discussion_ready_for_b": { "type": "boolean" }
      }
    },
    "gate_judgment": {
      "type": "string",
      "enum": ["enter_b", "hold", "send_back"]
    }
  }
}
```

- [ ] **Step 3: Create the Architecture Brief schema**

Create `schemas/architecture-brief.schema.json` with this content:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ArchitectureBrief",
  "type": "object",
  "required": [
    "stage",
    "flow_decomposition",
    "collaboration_allocation",
    "collaboration_prototype",
    "handoff_and_intervention",
    "attention_and_modality",
    "durable_state_and_memory",
    "surface_system",
    "evaluation_and_rollout",
    "unresolved_contradictions"
  ],
  "properties": {
    "stage": { "const": "B" },
    "flow_decomposition": { "type": "string" },
    "collaboration_allocation": { "type": "string" },
    "collaboration_prototype": { "type": "string" },
    "handoff_and_intervention": { "type": "string" },
    "attention_and_modality": { "type": "string" },
    "durable_state_and_memory": { "type": "string" },
    "surface_system": { "type": "string" },
    "evaluation_and_rollout": { "type": "string" },
    "unresolved_contradictions": {
      "type": "array",
      "items": { "type": "string" }
    }
  }
}
```

- [ ] **Step 4: Create the scenario map and ledger schemas**

Create `schemas/ux-scenario-map.schema.json` with this content:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "UXScenarioMap",
  "type": "object",
  "required": ["map_id", "map_level", "focus", "nodes", "edges"],
  "properties": {
    "map_id": { "type": "string" },
    "map_level": {
      "type": "string",
      "enum": [
        "system_landscape",
        "scenario_family",
        "scenario_ontology",
        "scenario_state_machine"
      ]
    },
    "focus": { "type": "string" },
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "label", "node_type"],
        "properties": {
          "id": { "type": "string" },
          "label": { "type": "string" },
          "node_type": { "type": "string" },
          "notes": { "type": "string" }
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from", "to", "relation"],
        "properties": {
          "from": { "type": "string" },
          "to": { "type": "string" },
          "relation": { "type": "string" }
        }
      }
    }
  }
}
```

Create `schemas/architecture-conductor-ledger.schema.json` with this content:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ArchitectureConductorLedger",
  "type": "object",
  "required": ["session_id", "entries"],
  "properties": {
    "session_id": { "type": "string" },
    "entries": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["label", "content"],
        "properties": {
          "label": {
            "type": "string",
            "enum": [
              "FACT",
              "ASSUMPTION",
              "OPEN_QUESTION",
              "DECISION",
              "RISK",
              "CONFLICT",
              "TODO_RESEARCH"
            ]
          },
          "content": { "type": "string" },
          "source": { "type": "string" },
          "gate_ref": { "type": "string" }
        }
      }
    }
  }
}
```

- [ ] **Step 5: Validate schema JSON syntax**

Run:

```bash
python3 -m json.tool schemas/architecture-conductor-output-manifest.json
python3 -m json.tool schemas/direction-brief.schema.json
python3 -m json.tool schemas/architecture-brief.schema.json
python3 -m json.tool schemas/ux-scenario-map.schema.json
python3 -m json.tool schemas/architecture-conductor-ledger.schema.json
```

Expected:
- each command exits `0`
- each file prints formatted JSON

- [ ] **Step 6: Run the conformance test file and verify only templates and fixtures still fail**

Run:

```bash
pytest tests/test_architecture_conductor_spec.py -v
```

Expected:
- manifest and schema assertions pass
- template and fixture assertions still fail

- [ ] **Step 7: Commit the schema layer**

```bash
git add schemas/architecture-conductor-output-manifest.json \
        schemas/direction-brief.schema.json \
        schemas/architecture-brief.schema.json \
        schemas/ux-scenario-map.schema.json \
        schemas/architecture-conductor-ledger.schema.json
git commit -m "feat: add Architecture Conductor output schemas"
```

## Task 4: Add Markdown Templates And Example Fixture Records

**Files:**
- Create: `templates/direction-brief.md`
- Create: `templates/architecture-brief.md`
- Create: `templates/ux-scenario-map.md`
- Create: `templates/architecture-conductor-ledger.md`
- Create: `tests/fixtures/architecture_conductor/direction_brief.json`
- Create: `tests/fixtures/architecture_conductor/architecture_brief.json`
- Create: `tests/fixtures/architecture_conductor/ux_scenario_map.json`
- Create: `tests/fixtures/architecture_conductor/ledger.json`
- Test: `pytest tests/test_architecture_conductor_spec.py -v`

- [ ] **Step 1: Create the markdown templates**

Create `templates/direction-brief.md` with this content:

```md
# Direction Brief

## Direction Summary
- problem_statement:
- why_now:
- first_wedge:

## User And Context
- primary_user:
- core_context:
- risk_boundary:

## Boundary
- goals:
- non_goals:
- mvp_boundary:

## Assumptions And Risks
- assumptions:
- risks:
- missing_evidence:

## A->B Gate Evaluation
- primary_problem_clear:
- why_now_clear:
- first_wedge_clear:
- stakes_clear:
- discussion_ready_for_b:

## Handoff Judgment
- gate_judgment:
- reason_to_enter_b:
```

Create `templates/architecture-brief.md` with this content:

```md
# Architecture Brief

## Flow Decomposition
- stages:
- escalation_path:

## Collaboration Allocation
- default_mode:
- human_role:
- machine_role:

## Handoff And Intervention
- handoff_object:
- approval_boundary:
- takeover_boundary:

## Attention And Modality
- interrupt:
- batch:
- silent:

## Durable State And Memory
- memory_policy:
- writeback_guardrails:

## Surface System
- primary_surface:
- secondary_surface:

## Evaluation And Rollout
- rollout_ladder:
- evaluation_signals:

## Unresolved Contradictions
- contradiction:
```

Create `templates/ux-scenario-map.md` with this content:

```md
# UX Scenario Map

## Map Metadata
- map_id:
- map_level:
- focus:

## Nodes
- id:
- label:
- node_type:
- notes:

## Edges
- from:
- to:
- relation:

## Expansion Notes
- branch_logic:
- state_machine_needed:
```

Create `templates/architecture-conductor-ledger.md` with this content:

```md
# Architecture Conductor Ledger

## Session
- session_id:

## Ledger Entries
- label:
- content:
- source:
- gate_ref:
```

- [ ] **Step 2: Create example fixture records that satisfy the schemas**

Create `tests/fixtures/architecture_conductor/direction_brief.json` with this content:

```json
{
  "stage": "A",
  "problem_statement": "Teams discussing a new mobile agent OS keep jumping from slogans to UI without settling direction.",
  "why_now": {
    "shift": "Tool-calling and system-level access now let agents participate in more of the task chain.",
    "chain_entry": "The system can now help with ongoing task coordination rather than single-shot answers.",
    "workflow_first_check": "A workflow-only solution still leaves unresolved collaboration and governance questions."
  },
  "first_wedge": "Use the conductor to frame one scenario family before any surface work.",
  "user_context": {
    "primary_user": "Product team shaping a new agent OS",
    "core_context": "Early-stage concept work for a mobile-first agent system"
  },
  "boundary": {
    "goals": ["clarify direction", "set A->B gate"],
    "non_goals": ["ship UI mocks", "decide implementation stack"],
    "mvp_boundary": "One system map and one scenario family map"
  },
  "assumptions": [
    "A map-first artifact will help the team avoid premature narrowing"
  ],
  "risks": [
    "The team may confuse map output with actual direction validation"
  ],
  "gate_evaluation": {
    "primary_problem_clear": true,
    "why_now_clear": true,
    "first_wedge_clear": true,
    "stakes_clear": true,
    "discussion_ready_for_b": true
  },
  "gate_judgment": "enter_b"
}
```

Create `tests/fixtures/architecture_conductor/architecture_brief.json` with this content:

```json
{
  "stage": "B",
  "flow_decomposition": "Move from system landscape to scenario family, then to selected state machine only when needed.",
  "collaboration_allocation": "Human owns thesis and approval; agent owns structural compression and contradiction surfacing.",
  "collaboration_prototype": "Map generator with gated scenario expansion.",
  "handoff_and_intervention": "The agent hands back direction maps, branch axes, and contradiction packets.",
  "attention_and_modality": "Use batch and working-surface review by default; avoid interruptive narrowing questions.",
  "durable_state_and_memory": "Persist ledger entries and approved maps; do not write unstable branches into durable memory.",
  "surface_system": "Map-first browser companion with terminal-based reasoning and review.",
  "evaluation_and_rollout": "Start with document artifacts, then test on scenario workshops.",
  "unresolved_contradictions": [
    "How much visualization belongs in the browser companion versus markdown artifacts?"
  ]
}
```

Create `tests/fixtures/architecture_conductor/ux_scenario_map.json` with this content:

```json
{
  "map_id": "mobile-agent-os-food-purchase",
  "map_level": "scenario_ontology",
  "focus": "Food purchase recommendation workspace",
  "nodes": [
    {
      "id": "intent-1",
      "label": "Purchase intent",
      "node_type": "user_intent",
      "notes": "The user is trying to decide whether to buy a product."
    },
    {
      "id": "work-1",
      "label": "Purchase decision workspace",
      "node_type": "work_object",
      "notes": "Nutrition becomes evidence for a buying decision."
    }
  ],
  "edges": [
    {
      "from": "intent-1",
      "to": "work-1",
      "relation": "organizes_into"
    }
  ]
}
```

Create `tests/fixtures/architecture_conductor/ledger.json` with this content:

```json
{
  "session_id": "session-mobile-agent-os-001",
  "entries": [
    {
      "label": "FACT",
      "content": "The user wants the generator to respect the original A/B framework.",
      "source": "user",
      "gate_ref": "stage-discipline"
    },
    {
      "label": "DECISION",
      "content": "Primary output format should be UX scenario mindmaps and ontology maps.",
      "source": "approved spec",
      "gate_ref": "artifact-shape"
    }
  ]
}
```

- [ ] **Step 3: Run the conformance suite and verify it passes**

Run:

```bash
pytest tests/test_architecture_conductor_spec.py -v
```

Expected:
- all tests in `tests/test_architecture_conductor_spec.py` pass

- [ ] **Step 4: Commit templates and fixtures**

```bash
git add templates/direction-brief.md \
        templates/architecture-brief.md \
        templates/ux-scenario-map.md \
        templates/architecture-conductor-ledger.md \
        tests/fixtures/architecture_conductor/direction_brief.json \
        tests/fixtures/architecture_conductor/architecture_brief.json \
        tests/fixtures/architecture_conductor/ux_scenario_map.json \
        tests/fixtures/architecture_conductor/ledger.json
git commit -m "feat: add Architecture Conductor templates and fixtures"
```

## Task 5: Run Full Validation And Polish The Package

**Files:**
- Modify: `agents/architecture-conductor agent.md` only if a test or grep exposes a mismatch
- Modify: `agents/architecture-conductor output contract.md` only if a test or grep exposes a mismatch
- Modify: `schemas/*.json` only if a test or syntax check exposes a mismatch
- Modify: `templates/*.md` only if a test exposes a missing section
- Test: `pytest tests/test_architecture_conductor_spec.py -v`

- [ ] **Step 1: Run JSON syntax validation across the full package**

Run:

```bash
python3 -m json.tool schemas/architecture-conductor-output-manifest.json >/dev/null
python3 -m json.tool schemas/direction-brief.schema.json >/dev/null
python3 -m json.tool schemas/architecture-brief.schema.json >/dev/null
python3 -m json.tool schemas/ux-scenario-map.schema.json >/dev/null
python3 -m json.tool schemas/architecture-conductor-ledger.schema.json >/dev/null
python3 -m json.tool tests/fixtures/architecture_conductor/direction_brief.json >/dev/null
python3 -m json.tool tests/fixtures/architecture_conductor/architecture_brief.json >/dev/null
python3 -m json.tool tests/fixtures/architecture_conductor/ux_scenario_map.json >/dev/null
python3 -m json.tool tests/fixtures/architecture_conductor/ledger.json >/dev/null
echo "json ok"
```

Expected:
- final line prints `json ok`

- [ ] **Step 2: Run targeted grep checks for the most important agent promises**

Run:

```bash
rg -n "Stage A / Direction Framing|Stage B / Structure Convergence|Ask breadth-first before depth-first|Direction Brief|Architecture Brief|TODO_RESEARCH" \
  "agents/architecture-conductor agent.md" \
  "agents/architecture-conductor output contract.md" \
  templates/direction-brief.md \
  templates/architecture-brief.md
```

Expected:
- all target phrases found
- exit code `0`

- [ ] **Step 3: Run the conformance suite one more time**

Run:

```bash
pytest tests/test_architecture_conductor_spec.py -v
```

Expected:
- all tests pass

- [ ] **Step 4: Commit the validated package**

```bash
git add agents/architecture-conductor\ agent.md \
        agents/architecture-conductor\ output\ contract.md \
        schemas/architecture-conductor-output-manifest.json \
        schemas/direction-brief.schema.json \
        schemas/architecture-brief.schema.json \
        schemas/ux-scenario-map.schema.json \
        schemas/architecture-conductor-ledger.schema.json \
        templates/direction-brief.md \
        templates/architecture-brief.md \
        templates/ux-scenario-map.md \
        templates/architecture-conductor-ledger.md \
        tests/test_architecture_conductor_spec.py \
        tests/fixtures/architecture_conductor/direction_brief.json \
        tests/fixtures/architecture_conductor/architecture_brief.json \
        tests/fixtures/architecture_conductor/ux_scenario_map.json \
        tests/fixtures/architecture_conductor/ledger.json
git commit -m "feat: add executable Architecture Conductor agent package"
```
