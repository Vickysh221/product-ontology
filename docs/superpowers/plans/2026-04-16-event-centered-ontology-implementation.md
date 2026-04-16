# Event-Centered Ontology Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the repository into an event-centered, evidence-constrained, review-updated product ontology library with explicit layer separation, new schema coverage, review lens rubrics, and node-edge oriented agent contracts.

**Architecture:** Keep the repository as a Markdown-plus-JSON-schema knowledge system, but change the ontology backbone from product-centered documentation to event-centered modeling. The implementation updates ontology source docs first, then aligns directory structure, schemas, templates, and agent contracts so every durable judgment can trace back through `Claim -> Event -> Artifact -> Source`.

**Tech Stack:** Markdown, JSON Schema, git, shell validation with `python3 -m json.tool` and `find`/`rg`

---

## File Structure

### Create

- `library/artifacts/.gitkeep`
- `library/counterclaims/.gitkeep`
- `library/theses/.gitkeep`
- `library/verdicts/.gitkeep`
- `ontology/review-lenses/product-lens.md`
- `ontology/review-lenses/ux-collaboration-lens.md`
- `ontology/review-lenses/tech-lens.md`
- `ontology/review-lenses/user-reality-lens.md`
- `ontology/review-lenses/business-lens.md`
- `ontology/review-lenses/brand-lens.md`
- `ontology/review-lenses/contrarian-lens.md`
- `ontology/review-lenses/governance-lens.md`
- `schemas/event.schema.json`
- `schemas/source.schema.json`
- `schemas/artifact.schema.json`
- `schemas/review.schema.json`
- `schemas/pattern.schema.json`
- `templates/artifact-record.md`
- `templates/review-record.md`
- `templates/thesis-record.md`

### Modify

- `README.md`
- `ontology/cognition-ontology.md`
- `ontology/product-intelligence-ontology.md`
- `ontology/jury-review-ontology.md`
- `agents/source-scout agent.md`
- `agents/claim-extractor agent.md`
- `agents/jury-synthesizer agent.md`
- `agents/collaboration-trace-synthesizer agent.md`
- `agents/collaboration-trace-synthesizer output contract.md`
- `schemas/ontology-manifest.json`
- `schemas/claim-record.schema.json`
- `schemas/product-record.schema.json`
- `schemas/session-progress-record.schema.json`
- `templates/product-event-card.md`
- `templates/claim-record.md`
- `templates/pattern-card.md`
- `templates/jury-review-record.md`
- `library/_operating-notes.md`

### Keep Unchanged

- `PRD Session Summary.md`
- `seed/watchlist.md`
- `seed/initial-questions.md`
- `seed/first-tracking-theses.md`

## Task 1: Refactor Repository Entry Docs Around Event-Centered Ontology

**Files:**
- Modify: `README.md`
- Modify: `ontology/cognition-ontology.md`
- Modify: `ontology/product-intelligence-ontology.md`
- Modify: `ontology/jury-review-ontology.md`
- Test: repository grep checks via `rg`

- [ ] **Step 1: Write the failing structure check**

Create a checklist in your terminal notes for required phrases that are currently missing or under-specified:

```text
README.md must mention:
- Product as anchor
- Event as entrypoint
- Artifact as evidence carrier
- Review / Verdict as update mechanism

ontology/product-intelligence-ontology.md must define:
- Source vs Artifact separation
- Event minimum fields
- Claim/Pattern/Thesis promotion path
```

- [ ] **Step 2: Run grep checks to verify the current docs fail the target design**

Run:

```bash
rg -n "Artifact as evidence carrier|Event as the primary ingestion object|review-updated" README.md ontology/product-intelligence-ontology.md ontology/jury-review-ontology.md
```

Expected:
- no full match for the new wording
- at least one missing target concept, proving the docs still reflect the old structure

- [ ] **Step 3: Rewrite `README.md` summary and repository structure copy**

Update `README.md` so its top sections explicitly describe:

```md
# Product Learning Library

This repository is an event-centered, evidence-constrained, review-updated ontology-based product analysis library.

Core operating chain:

`Source -> Artifact -> Event -> Claim -> Pattern -> Thesis`

Review and verdict records act as the promotion and downgrade mechanism for long-term judgments.
```

Also update the repository structure section to include:

```text
library/
  artifacts/
  counterclaims/
  theses/
  verdicts/
ontology/
  review-lenses/
schemas/
  event.schema.json
  source.schema.json
  artifact.schema.json
  review.schema.json
  pattern.schema.json
```

- [ ] **Step 4: Rewrite `ontology/cognition-ontology.md` to preserve layer boundaries**

Replace or extend the design-stance sections with text equivalent to:

```md
## Core Claim

This system stores cognitive progression only when it remains traceable through explicit objects.

Long-term writeback must never skip evidence layers.

Required traceability chain:

`Pattern -> Claim -> Event -> Artifact -> Source`
```

Add a section named `Layer Separation Rules` that states:

```md
- facts cannot contain `why_now`
- interpretation cannot masquerade as observation
- patterns cannot be written from a single source mention
- review cannot introduce new fact nodes
```

- [ ] **Step 5: Rewrite `ontology/product-intelligence-ontology.md` around the new backbone**

Insert the new primary object families and relation language:

```md
### Product
Anchor object, not ingestion entrypoint.

### Event
Primary ingestion object and smallest durable change unit.

### Source
Source container with perspective metadata.

### Artifact
Evidence slice used to anchor interpretation.
```

Also add the minimum `Event` fields exactly as:

```md
- event_id
- product_id
- title
- event_type
- date_detected
- time_window
- what_changed
- change_layer
- affected_capabilities
- target_problems
- evidence_refs
- status
```

- [ ] **Step 6: Rewrite `ontology/jury-review-ontology.md` so review acts on claims and patterns instead of raw sources**

Add or revise sections to state:

```md
- Review targets are `Claim`, `Pattern`, and `Thesis`
- Reviewers cannot add facts
- Verdicts can support, weaken, refute, or request more evidence
- Judge is the only role allowed to promote `Claim -> Pattern` or downgrade `Claim -> WhyNowHypothesis`
```

- [ ] **Step 7: Run grep validation on the ontology docs**

Run:

```bash
rg -n "Event.*primary ingestion|Artifact.*evidence|Pattern -> Claim -> Event -> Artifact -> Source|cannot introduce new fact nodes|Claim -> Pattern" README.md ontology/cognition-ontology.md ontology/product-intelligence-ontology.md ontology/jury-review-ontology.md
```

Expected:
- all target concepts present
- exit code `0`

- [ ] **Step 8: Commit the doc refactor**

```bash
git add README.md ontology/cognition-ontology.md ontology/product-intelligence-ontology.md ontology/jury-review-ontology.md
git commit -m "refactor: redefine ontology backbone around events"
```

## Task 2: Create the Missing Event-Centered Library Directories

**Files:**
- Create: `library/artifacts/.gitkeep`
- Create: `library/counterclaims/.gitkeep`
- Create: `library/theses/.gitkeep`
- Create: `library/verdicts/.gitkeep`
- Modify: `library/_operating-notes.md`
- Test: directory existence checks via `find`

- [ ] **Step 1: Write the failing structure check**

Use this expected tree as the target:

```text
library/
  products/
  events/
  sources/
  artifacts/
  capabilities/
  problems/
  claims/
  counterclaims/
  hypotheses/
  patterns/
  theses/
  reviews/
  verdicts/
  sessions/
  writebacks/
```

- [ ] **Step 2: Run a directory check to verify the new directories do not exist yet**

Run:

```bash
find library -maxdepth 1 -type d | sort
```

Expected:
- missing `library/artifacts`
- missing `library/counterclaims`
- missing `library/theses`
- missing `library/verdicts`

- [ ] **Step 3: Create tracked placeholder files for the missing directories**

Create the files as empty placeholders:

```text
library/artifacts/.gitkeep
library/counterclaims/.gitkeep
library/theses/.gitkeep
library/verdicts/.gitkeep
```

- [ ] **Step 4: Update `library/_operating-notes.md` to reflect the new object layout**

Add a section like:

```md
## Object Storage Rules

- `sources/` stores source containers and metadata
- `artifacts/` stores evidence slices extracted from sources
- `events/` stores durable change units
- `claims/` and `counterclaims/` store interpretation records
- `patterns/` and `theses/` store reviewed structural judgments
- `reviews/` and `verdicts/` store critique traces only
```

- [ ] **Step 5: Run directory validation**

Run:

```bash
find library -maxdepth 2 \( -type d -o -name ".gitkeep" \) | sort
```

Expected:
- each new directory appears
- each contains `.gitkeep`

- [ ] **Step 6: Commit the directory expansion**

```bash
git add library/artifacts/.gitkeep library/counterclaims/.gitkeep library/theses/.gitkeep library/verdicts/.gitkeep library/_operating-notes.md
git commit -m "chore: add event-centered library directories"
```

## Task 3: Add First-Pass JSON Schemas for Event, Source, Artifact, Review, and Pattern

**Files:**
- Create: `schemas/event.schema.json`
- Create: `schemas/source.schema.json`
- Create: `schemas/artifact.schema.json`
- Create: `schemas/review.schema.json`
- Create: `schemas/pattern.schema.json`
- Modify: `schemas/ontology-manifest.json`
- Modify: `schemas/claim-record.schema.json`
- Test: JSON validation via `python3 -m json.tool`

- [ ] **Step 1: Write the failing validation command**

The new schema set should validate with:

```bash
python3 -m json.tool schemas/event.schema.json >/dev/null
python3 -m json.tool schemas/source.schema.json >/dev/null
python3 -m json.tool schemas/artifact.schema.json >/dev/null
python3 -m json.tool schemas/review.schema.json >/dev/null
python3 -m json.tool schemas/pattern.schema.json >/dev/null
```

- [ ] **Step 2: Verify the new schema files are missing**

Run:

```bash
ls schemas/event.schema.json schemas/source.schema.json schemas/artifact.schema.json schemas/review.schema.json schemas/pattern.schema.json
```

Expected:
- `No such file or directory` for each file

- [ ] **Step 3: Create `schemas/event.schema.json`**

Use this complete JSON:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "EventRecord",
  "type": "object",
  "required": [
    "event_id",
    "product_id",
    "title",
    "event_type",
    "date_detected",
    "time_window",
    "what_changed",
    "change_layer",
    "affected_capabilities",
    "target_problems",
    "evidence_refs",
    "status"
  ],
  "properties": {
    "event_id": { "type": "string" },
    "product_id": { "type": "string" },
    "title": { "type": "string" },
    "event_type": {
      "type": "string",
      "enum": [
        "launch",
        "update",
        "repositioning",
        "pricing_change",
        "policy_change",
        "ux_change",
        "capability_change",
        "workflow_change",
        "trust_signal",
        "market_signal"
      ]
    },
    "date_detected": { "type": "string" },
    "time_window": { "type": "string" },
    "what_changed": { "type": "string" },
    "change_layer": {
      "type": "string",
      "enum": [
        "interface",
        "capability",
        "workflow",
        "coordination",
        "governance",
        "trust",
        "business_model",
        "distribution"
      ]
    },
    "affected_capabilities": { "type": "array", "items": { "type": "string" } },
    "target_problems": { "type": "array", "items": { "type": "string" } },
    "evidence_refs": { "type": "array", "items": { "type": "string" } },
    "status": {
      "type": "string",
      "enum": ["candidate", "validated", "contested", "merged", "rejected"]
    }
  }
}
```

- [ ] **Step 4: Create `schemas/source.schema.json`**

Use this complete JSON:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SourceRecord",
  "type": "object",
  "required": [
    "source_id",
    "source_type",
    "platform",
    "publish_time",
    "url_or_ref",
    "viewpoint",
    "stance",
    "audience_position",
    "evidence_quality"
  ],
  "properties": {
    "source_id": { "type": "string" },
    "source_type": { "type": "string" },
    "platform": { "type": "string" },
    "publisher": { "type": "string" },
    "author_or_speaker": { "type": "string" },
    "publish_time": { "type": "string" },
    "url_or_ref": { "type": "string" },
    "viewpoint": {
      "type": "string",
      "enum": [
        "official_product",
        "official_engineering",
        "founder_exec",
        "developer",
        "power_user",
        "new_user",
        "critic",
        "media",
        "researcher",
        "regulator"
      ]
    },
    "stance": {
      "type": "string",
      "enum": [
        "promotional",
        "explanatory",
        "evaluative_positive",
        "evaluative_negative",
        "mixed",
        "neutral"
      ]
    },
    "audience_position": {
      "type": "string",
      "enum": ["investor", "developer", "end_user", "buyer", "partner", "public"]
    },
    "evidence_quality": {
      "type": "string",
      "enum": [
        "first_hand_official",
        "first_hand_operational",
        "first_hand_user_signal",
        "second_hand_interpretation",
        "aggregated_commentary"
      ]
    },
    "reliability_notes": { "type": "string" }
  }
}
```

- [ ] **Step 5: Create `schemas/artifact.schema.json`**

Use this complete JSON:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ArtifactRecord",
  "type": "object",
  "required": [
    "artifact_id",
    "source_id",
    "artifact_type",
    "locator",
    "content_excerpt",
    "mentions",
    "event_candidates",
    "signal_strength"
  ],
  "properties": {
    "artifact_id": { "type": "string" },
    "source_id": { "type": "string" },
    "artifact_type": { "type": "string" },
    "locator": { "type": "string" },
    "content_excerpt": { "type": "string" },
    "mentions": { "type": "array", "items": { "type": "string" } },
    "event_candidates": { "type": "array", "items": { "type": "string" } },
    "signal_strength": {
      "type": "string",
      "enum": ["weak", "medium", "strong"]
    }
  }
}
```

- [ ] **Step 6: Create `schemas/review.schema.json`**

Use this complete JSON:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ReviewRecord",
  "type": "object",
  "required": [
    "review_id",
    "lens",
    "target_type",
    "target_id",
    "verdict",
    "confidence"
  ],
  "properties": {
    "review_id": { "type": "string" },
    "lens": {
      "type": "string",
      "enum": [
        "product",
        "ux_collaboration",
        "tech",
        "user_reality",
        "business",
        "brand",
        "contrarian",
        "governance"
      ]
    },
    "target_type": {
      "type": "string",
      "enum": ["claim", "pattern", "thesis"]
    },
    "target_id": { "type": "string" },
    "verdict": {
      "type": "string",
      "enum": ["support", "weaken", "refute", "needs_more_evidence"]
    },
    "confidence": {
      "type": "string",
      "enum": ["low", "medium", "high"]
    },
    "vulnerability": { "type": "string" },
    "counterargument": { "type": "string" },
    "required_evidence": { "type": "string" },
    "upgrade_recommendation": {
      "type": "string",
      "enum": ["none", "to_pattern", "to_thesis", "downgrade_to_hypothesis"]
    }
  }
}
```

- [ ] **Step 7: Create `schemas/pattern.schema.json`**

Use this complete JSON:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PatternRecord",
  "type": "object",
  "required": [
    "pattern_id",
    "pattern_statement",
    "derived_from_event_refs",
    "derived_from_claim_refs",
    "status"
  ],
  "properties": {
    "pattern_id": { "type": "string" },
    "pattern_statement": { "type": "string" },
    "derived_from_event_refs": { "type": "array", "items": { "type": "string" } },
    "derived_from_claim_refs": { "type": "array", "items": { "type": "string" } },
    "scope": { "type": "string" },
    "applicability": { "type": "string" },
    "failure_mode": { "type": "string" },
    "status": {
      "type": "string",
      "enum": ["candidate", "reviewed", "accepted", "rejected"]
    },
    "review_refs": { "type": "array", "items": { "type": "string" } }
  }
}
```

- [ ] **Step 8: Update `schemas/claim-record.schema.json` to support the new event-centered interpretation model**

Change the schema to require:

```json
"required": [
  "id",
  "claim_text",
  "event_refs",
  "artifact_refs",
  "claim_type",
  "status",
  "confidence"
]
```

Add these properties:

```json
"event_refs": { "type": "array", "items": { "type": "string" } },
"artifact_refs": { "type": "array", "items": { "type": "string" } },
"claim_type": {
  "type": "string",
  "enum": [
    "mechanism",
    "positioning",
    "workflow",
    "trust",
    "governance",
    "market_implication"
  ]
},
"counterclaim_refs": { "type": "array", "items": { "type": "string" } },
"review_status": { "type": "string" }
```

- [ ] **Step 9: Update `schemas/ontology-manifest.json` to include the new entities**

Ensure the manifest entity list includes:

```json
"artifact",
"counterclaim",
"thesis",
"review",
"verdict"
```

And ensure the relations list includes:

```json
"Artifact DERIVED_FROM Source",
"Event HAS_EVIDENCE Artifact",
"Claim INTERPRETS Event",
"Review PRODUCES Verdict",
"Verdict UPGRADES Claim_TO Pattern"
```

- [ ] **Step 10: Run JSON validation**

Run:

```bash
python3 -m json.tool schemas/event.schema.json >/dev/null
python3 -m json.tool schemas/source.schema.json >/dev/null
python3 -m json.tool schemas/artifact.schema.json >/dev/null
python3 -m json.tool schemas/review.schema.json >/dev/null
python3 -m json.tool schemas/pattern.schema.json >/dev/null
python3 -m json.tool schemas/claim-record.schema.json >/dev/null
python3 -m json.tool schemas/ontology-manifest.json >/dev/null
echo JSON_OK
```

Expected:
- `JSON_OK`

- [ ] **Step 11: Commit the schema pass**

```bash
git add schemas/event.schema.json schemas/source.schema.json schemas/artifact.schema.json schemas/review.schema.json schemas/pattern.schema.json schemas/claim-record.schema.json schemas/ontology-manifest.json
git commit -m "feat: add event-centered ontology schemas"
```

## Task 4: Add Review Lens Rubrics

**Files:**
- Create: `ontology/review-lenses/product-lens.md`
- Create: `ontology/review-lenses/ux-collaboration-lens.md`
- Create: `ontology/review-lenses/tech-lens.md`
- Create: `ontology/review-lenses/user-reality-lens.md`
- Create: `ontology/review-lenses/business-lens.md`
- Create: `ontology/review-lenses/brand-lens.md`
- Create: `ontology/review-lenses/contrarian-lens.md`
- Create: `ontology/review-lenses/governance-lens.md`
- Test: file presence and grep checks

- [ ] **Step 1: Write the failing lens check**

The target lens set is:

```text
product
ux-collaboration
tech
user-reality
business
brand
contrarian
governance
```

- [ ] **Step 2: Verify the review-lenses directory is missing**

Run:

```bash
find ontology/review-lenses -maxdepth 1 -type f
```

Expected:
- `No such file or directory`

- [ ] **Step 3: Create `ontology/review-lenses/product-lens.md`**

Use this content:

```md
# Product Lens

## Focus

Evaluate whether an event changes the product's structure, not just its surface feature set.

## Questions

- What layer did this event actually change?
- What problem is being addressed?
- Is this a feature increment or a structural migration?
- Why now?
- Does this change control boundary, responsibility allocation, or adoption logic?
```

- [ ] **Step 4: Create `ontology/review-lenses/ux-collaboration-lens.md`**

Use this content:

```md
# UX Collaboration Lens

## Focus

Evaluate human-agent collaboration quality, capability visibility, intervention timing, and recovery design.

## Questions

- Can the user understand the current system or agent state?
- Is the capability boundary visible?
- When should the system clarify versus act?
- Is there a recovery path?
- Are high-risk actions correctly gated?
- Is trust calibration appropriate?
- Is there a temporary or task-specific interface for complex collaboration?
```

- [ ] **Step 5: Create the remaining six lens files**

Use these exact headings and question blocks:

```md
# Tech Lens
- Is this structural capability or prompt assembly?
- Do context, tools, state retention, latency, and cost support the promise?
- What are the failure modes?
- Is the handoff contract traceable?
```

```md
# User Reality Lens
- Will users actually adopt it?
- Where is the friction?
- Are complaints surface-level or signs of a deeper mental model break?
- Does user language align with official framing?
```

```md
# Business Lens
- Should this enter priority?
- What organizational preconditions are required?
- Does it support durable ROI?
- Does it alter distribution or monetization logic?
```

```md
# Brand Lens
- Does this reinforce who the product is?
- Is narrative aligned with mechanism?
- Is this a category weapon or feature noise?
```

```md
# Contrarian Lens
- Is marketing language being mistaken for mechanism?
- Is a small sample being inflated into a trend?
- Is a feature change being overstated as a paradigm change?
- Where is the evidence chain broken?
- What missing evidence would overturn the current claim?
```

```md
# Governance Lens
- Where is the approval boundary?
- Is the action reversible?
- Is the action auditable?
- Is permission sensitivity modeled correctly?
- When should a human be brought in?
```

- [ ] **Step 6: Run lens validation**

Run:

```bash
find ontology/review-lenses -maxdepth 1 -type f | sort
rg -n "Why now|trust calibration|approval boundary|prompt assembly|category weapon" ontology/review-lenses
```

Expected:
- eight files listed
- grep returns matches from the expected files

- [ ] **Step 7: Commit the lens rubric set**

```bash
git add ontology/review-lenses
git commit -m "feat: add review lens rubrics"
```

## Task 5: Rewrite Agent Contracts to Produce Nodes and Edges Instead of Prose

**Files:**
- Modify: `agents/source-scout agent.md`
- Modify: `agents/claim-extractor agent.md`
- Modify: `agents/jury-synthesizer agent.md`
- Modify: `agents/collaboration-trace-synthesizer agent.md`
- Modify: `agents/collaboration-trace-synthesizer output contract.md`
- Test: grep checks for node-edge output contracts

- [ ] **Step 1: Write the failing contract check**

Target concepts:

```text
source-scout -> Source, Artifact, suggests_event
claim-extractor -> Event, Claim, Counterclaim, WhyNowHypothesis
jury-synthesizer -> Review, Verdict
no long reports as primary output
```

- [ ] **Step 2: Verify current agent docs still skew toward prose summaries**

Run:

```bash
rg -n "summary|summarizer|verdict|Source|Artifact|Counterclaim|WhyNowHypothesis|nodes|edges" agents
```

Expected:
- missing at least some of the new required node-edge language

- [ ] **Step 3: Rewrite `agents/source-scout agent.md`**

Add a section with this exact contract:

```md
## Allowed Nodes

- `Source`
- `Artifact`

## Allowed Edges

- `Artifact DERIVED_FROM Source`
- `Artifact MENTIONS Product | Capability | Problem`
- `Artifact SUGGESTS Event`

## Forbidden

- Do not write `Claim`
- Do not write `Pattern`
- Do not write `Thesis`
```

- [ ] **Step 4: Rewrite `agents/claim-extractor agent.md`**

Add a section with this exact contract:

```md
## Allowed Nodes

- `Event`
- `Capability`
- `Problem`
- `Claim`
- `Counterclaim`
- `WhyNowHypothesis`

## Allowed Edges

- `Event HAS_EVIDENCE Artifact`
- `Event AFFECTS Capability`
- `Event ADDRESSES Problem`
- `Claim INTERPRETS Event`
- `Claim SUPPORTED_BY Artifact`
- `Counterclaim CHALLENGES Claim`
- `WhyNowHypothesis EXPLAINS Event`
```

- [ ] **Step 5: Rewrite `agents/jury-synthesizer agent.md`**

Add this review-only contract:

```md
## Allowed Nodes

- `Review`
- `Verdict`

## Allowed Targets

- `Claim`
- `Pattern`
- `Thesis`

## Forbidden

- Do not add new fact nodes
- Do not rewrite `Event`
- Do not silently resolve conflict without a `Verdict`
```

- [ ] **Step 6: Rewrite collaboration-trace contracts so they no longer imply generic prose summaries**

In `agents/collaboration-trace-synthesizer agent.md`, add:

```md
Primary output is a structured session trace that references durable nodes and edges.

Long-form prose is secondary and must never replace node-edge records.
```

In `agents/collaboration-trace-synthesizer output contract.md`, ensure the required outputs explicitly mention:

```md
- node references
- edge references
- writeback eligibility
- continuation entry point
```

- [ ] **Step 7: Run contract validation**

Run:

```bash
rg -n "Allowed Nodes|Allowed Edges|Forbidden|Do not add new fact nodes|Long-form prose is secondary" agents
```

Expected:
- every target file shows the new contract language

- [ ] **Step 8: Commit the agent contract rewrite**

```bash
git add agents/source-scout\ agent.md agents/claim-extractor\ agent.md agents/jury-synthesizer\ agent.md agents/collaboration-trace-synthesizer\ agent.md agents/collaboration-trace-synthesizer\ output\ contract.md
git commit -m "refactor: constrain agent outputs to nodes and edges"
```

## Task 6: Update Templates to Match the New Object Model

**Files:**
- Create: `templates/artifact-record.md`
- Create: `templates/review-record.md`
- Create: `templates/thesis-record.md`
- Modify: `templates/product-event-card.md`
- Modify: `templates/claim-record.md`
- Modify: `templates/pattern-card.md`
- Modify: `templates/jury-review-record.md`
- Test: grep checks for required headings and fields

- [ ] **Step 1: Write the failing template check**

Required new templates:

```text
artifact-record.md
review-record.md
thesis-record.md
```

Required revised fields:
- event card must include `change_layer` and `evidence_refs`
- claim record must include `event_refs`, `artifact_refs`, `claim_type`
- pattern card must include derived-from references

- [ ] **Step 2: Verify the new templates do not exist yet**

Run:

```bash
ls templates/artifact-record.md templates/review-record.md templates/thesis-record.md
```

Expected:
- `No such file or directory`

- [ ] **Step 3: Create `templates/artifact-record.md`**

Use this content:

```md
# Artifact Record

## Identity
- artifact_id:
- source_id:
- artifact_type:

## Locator
- locator:

## Evidence Slice
- content_excerpt:

## Mentions
- mentions:

## Event Candidates
- event_candidates:

## Signal Strength
- signal_strength:
```

- [ ] **Step 4: Create `templates/review-record.md`**

Use this content:

```md
# Review Record

## Identity
- review_id:
- lens:
- target_type:
- target_id:

## Verdict
- verdict:
- confidence:

## Critique
- vulnerability:
- counterargument:
- required_evidence:
- upgrade_recommendation:
```

- [ ] **Step 5: Create `templates/thesis-record.md`**

Use this content:

```md
# Thesis Record

## Identity
- thesis_id:
- thesis_statement:

## Composed Of
- pattern_refs:

## Scope
- scope:

## Update History
- review_refs:
- event_refs:

## Status
- status:
```

- [ ] **Step 6: Update the existing templates**

Revise `templates/product-event-card.md` to include:

```md
## Change Definition
- event_type:
- change_layer:
- what_changed:

## Evidence
- evidence_refs:
```

Revise `templates/claim-record.md` to include:

```md
## Traceability
- event_refs:
- artifact_refs:

## Classification
- claim_type:
```

Revise `templates/pattern-card.md` to include:

```md
## Derived From
- derived_from_event_refs:
- derived_from_claim_refs:
```

Revise `templates/jury-review-record.md` to reflect the new review fields:

```md
- verdict:
- confidence:
- vulnerability:
- counterargument:
- required_evidence:
- upgrade_recommendation:
```

- [ ] **Step 7: Run template validation**

Run:

```bash
rg -n "event_type|change_layer|evidence_refs|event_refs|artifact_refs|claim_type|derived_from_event_refs|upgrade_recommendation" templates
```

Expected:
- matches from all revised and newly created templates

- [ ] **Step 8: Commit the template alignment**

```bash
git add templates/artifact-record.md templates/review-record.md templates/thesis-record.md templates/product-event-card.md templates/claim-record.md templates/pattern-card.md templates/jury-review-record.md
git commit -m "feat: align templates with event-centered ontology"
```

## Task 7: Final Repository Consistency Validation

**Files:**
- Validate all modified files from Tasks 1-6

- [ ] **Step 1: Run JSON validation**

```bash
python3 -m json.tool schemas/event.schema.json >/dev/null
python3 -m json.tool schemas/source.schema.json >/dev/null
python3 -m json.tool schemas/artifact.schema.json >/dev/null
python3 -m json.tool schemas/review.schema.json >/dev/null
python3 -m json.tool schemas/pattern.schema.json >/dev/null
python3 -m json.tool schemas/claim-record.schema.json >/dev/null
python3 -m json.tool schemas/ontology-manifest.json >/dev/null
echo JSON_OK
```

Expected:
- `JSON_OK`

- [ ] **Step 2: Run repository structure validation**

```bash
find library ontology/review-lenses schemas templates -maxdepth 2 \( -type f -o -type d \) | sort
```

Expected:
- new directories, lens files, schemas, and templates all present

- [ ] **Step 3: Run ontology contract validation**

```bash
rg -n "Artifact DERIVED_FROM Source|Claim INTERPRETS Event|Verdict UPGRADES Claim_TO Pattern|Do not add new fact nodes|trust calibration|approval boundary" README.md ontology agents templates schemas
```

Expected:
- all critical backbone concepts matched

- [ ] **Step 4: Review git status**

Run:

```bash
git status --short
```

Expected:
- no unexpected untracked files
- only the planned modifications appear before the final commit

- [ ] **Step 5: Create the final integration commit**

```bash
git add README.md ontology library schemas templates agents
git commit -m "feat: implement event-centered product ontology"
```

## Self-Review

### Spec coverage

- Event-centered backbone: covered in Task 1 and Task 3
- Four-layer separation rules: covered in Task 1
- Event minimum fields: covered in Task 3
- Source vs Artifact split: covered in Task 2 and Task 3
- Node-edge agent workflow: covered in Task 5
- Review lenses with PM and UX emphasis: covered in Task 4
- Promotion and downgrade path: covered in Task 1, Task 3, and Task 5

### Placeholder scan

No unresolved placeholders, vague "handle later" wording, or cross-task shorthand remains. Every code or content step includes concrete text or complete JSON.

### Type consistency

- `Event`, `Source`, `Artifact`, `Claim`, `Pattern`, `Review`, and `Verdict` names match across tasks
- `ux_collaboration` is used consistently in schema and lens naming
- `upgrade_recommendation` values are identical in schema and template expectations
