# Event-Centered Product Ontology Design

## Scope

This spec defines the ontology backbone for an ontology-based product analysis library with:
- `Product` as anchor
- `Event` as the primary ingestion object
- `Artifact` as the evidence carrier
- `Claim / Pattern / Thesis` as judgment layers
- `Review / Verdict` as the critical update mechanism

The goal is not to generate narrative reports. The goal is to store durable nodes and edges with strict layer separation, so every long-term judgment remains traceable to evidence.

## Design Goal

The library should be defined as:

> an event-centered, evidence-constrained, review-updated ontology-based product analysis library

Its operating rule is:

> build the library along `entity -> event -> evidence -> judgment`, with multi-agent review acting as the promotion and downgrade mechanism

This design exists to prevent three common failure modes:
- source statements being mistaken for facts
- product positioning being mistaken for structural change
- trend interpretation being written into the same layer as observable events

## Core Choice

Three possible modeling centers were considered:

1. `Product`-centered
2. `Event`-centered
3. `Claim`-centered

This design chooses `Event`-centered modeling.

Why:
- product analysis is fundamentally about change, not only static product description
- `Event` is the cleanest boundary between observation and interpretation
- evidence can be attached to `Event` before judgment is attached to `Claim`
- multi-agent review becomes a controlled promotion path rather than free-form commentary

`Product` remains the anchor object, but not the ingestion entrypoint.

## Ontology Layers

The ontology is divided into four layers.

### 1. Fact Layer

Only observable or directly referenceable objects belong here:
- `Product`
- `Event`
- `Source`
- `Artifact`
- `Capability`
- `Problem`

### 2. Interpretation Layer

Only interpretation objects belong here:
- `Claim`
- `Counterclaim`
- `WhyNowHypothesis`

### 3. Pattern Layer

Only cross-event or cross-product structural judgments belong here:
- `Pattern`
- `Thesis`

### 4. Review Layer

Only critical review traces belong here:
- `Review`
- `Verdict`

For the first version, `Confidence` and `Vulnerability` should be fields on `Verdict`, not standalone nodes.

## Core Entity Backbone

The practical MVP node set is:
- `Product`
- `Event`
- `Source`
- `Artifact`
- `Capability`
- `Problem`
- `Claim`
- `Counterclaim`
- `WhyNowHypothesis`
- `Pattern`
- `Thesis`
- `Review`
- `Verdict`

The main chain is:

```text
Product
  -> Event
    -> Artifact
      -> Source

Event
  -> Claim
  -> Counterclaim
  -> WhyNowHypothesis

Claim
  -> Pattern
    -> Thesis

Claim / Pattern / Thesis
  -> Review
    -> Verdict
```

This is not a containment hierarchy. It is a constrained dependency chain.

## Core Relations

The ontology should start with a narrow edge vocabulary.

### Fact Layer Relations

- `Product HAS_EVENT Event`
- `Event HAS_EVIDENCE Artifact`
- `Artifact DERIVED_FROM Source`
- `Event AFFECTS Capability`
- `Event ADDRESSES Problem`
- `Artifact MENTIONS Product`
- `Artifact MENTIONS Capability`
- `Artifact MENTIONS Problem`
- `Artifact SUGGESTS Event`

### Interpretation Layer Relations

- `Claim INTERPRETS Event`
- `Counterclaim CHALLENGES Claim`
- `WhyNowHypothesis EXPLAINS Event`
- `Claim SUPPORTED_BY Artifact`
- `Claim REFUTED_BY Artifact`

### Pattern Layer Relations

- `Pattern ABSTRACTS_FROM Event`
- `Pattern ABSTRACTS_FROM Claim`
- `Thesis COMPOSED_OF Pattern`

### Review Layer Relations

- `Review TARGETS Claim`
- `Review TARGETS Pattern`
- `Review TARGETS Thesis`
- `Review PRODUCES Verdict`
- `Verdict UPGRADES Claim_TO Pattern`
- `Verdict DOWNGRADES Claim_TO WhyNowHypothesis`
- `Verdict MODULATES Thesis`

## Hard Modeling Rules

These are design constraints, not suggestions.

### Rule 1

`Source` never directly supports a `Claim`.

Only `Artifact` can support or refute a `Claim`. `Source` is a source container with perspective metadata. `Artifact` is the actual evidence slice.

### Rule 2

`Pattern` never abstracts directly from `Source`.

A `Pattern` can only abstract from `Event` or `Claim`.

### Rule 3

`Claim` must always point to at least one `Event` and one `Artifact`.

If either is missing, the record stays in session notes and does not enter the long-term library.

### Rule 4

`WhyNowHypothesis` is not a fact object.

It exists specifically to keep causal explanation out of `Event`.

## Layer Separation Rules

The layer split must be enforced through negative rules.

### Fact Layer Forbidden

Do not write:
- `why_now`
- strategic meaning
- trend language
- category-shift claims
- evaluative narrative like "this matters because"

### Interpretation Layer Forbidden

Do not:
- disguise interpretation as observation
- create unsupported `Claim` records without `Artifact`
- promote `Claim` to `Pattern` without review

### Pattern Layer Forbidden

Do not:
- derive `Thesis` from a single `Event`
- derive `Pattern` from unreviewed claim clusters
- use media repetition as pattern evidence by itself

### Review Layer Forbidden

Do not:
- add new fact nodes
- rewrite `Event`
- silently delete `Claim`
- merge conflicts away without leaving a verdict trace

## Event Schema Design

`Event` is the ingestion entrypoint. Its minimum fields should remain strictly observable.

Required minimum fields:
- `event_id`
- `product_id`
- `title`
- `event_type`
- `date_detected`
- `time_window`
- `what_changed`
- `change_layer`
- `affected_capabilities`
- `target_problems`
- `evidence_refs`
- `status`

Field guidance:

- `event_type`
  Suggested values:
  `launch`, `update`, `repositioning`, `pricing_change`, `policy_change`, `ux_change`, `capability_change`, `workflow_change`, `trust_signal`, `market_signal`

- `change_layer`
  Suggested values:
  `interface`, `capability`, `workflow`, `coordination`, `governance`, `trust`, `business_model`, `distribution`

- `status`
  Suggested values:
  `candidate`, `validated`, `contested`, `merged`, `rejected`

Explicit exclusion:
- `why_now` is not part of the `Event` minimum schema

## Source and Artifact Design

`Source` and `Artifact` must be separate object types.

### Source

`Source` represents the container and perspective context.

Minimum fields:
- `source_id`
- `source_type`
- `platform`
- `publisher`
- `author_or_speaker`
- `publish_time`
- `url_or_ref`
- `viewpoint`
- `stance`
- `audience_position`
- `evidence_quality`
- `reliability_notes`

Critical metadata fields:

- `viewpoint`
  Suggested values:
  `official_product`, `official_engineering`, `founder_exec`, `developer`, `power_user`, `new_user`, `critic`, `media`, `researcher`, `regulator`

- `stance`
  Suggested values:
  `promotional`, `explanatory`, `evaluative_positive`, `evaluative_negative`, `mixed`, `neutral`

- `audience_position`
  Suggested values:
  `investor`, `developer`, `end_user`, `buyer`, `partner`, `public`

- `evidence_quality`
  Suggested values:
  `first_hand_official`, `first_hand_operational`, `first_hand_user_signal`, `second_hand_interpretation`, `aggregated_commentary`

### Artifact

`Artifact` represents the actual evidence slice used for reference.

Minimum fields:
- `artifact_id`
- `source_id`
- `artifact_type`
- `locator`
- `content_excerpt`
- `mentions`
- `event_candidates`
- `signal_strength`

Examples of `locator`:
- transcript timestamp
- release note section
- issue comment id
- screenshot path
- transcript paragraph id

## Extraction Intermediate Factors

Before creating `Event` and `Claim`, the extraction step should normalize six factor groups from each artifact:
- `observable_change`
- `mentioned_capability`
- `mentioned_problem`
- `actor`
- `user_reaction`
- `constraint_or_risk`

This layer exists to reduce direct jumps from long text into event and judgment objects.

Recommended extraction sequence:
1. detect change verbs and release/update signals
2. identify mentioned capabilities
3. identify user jobs or pains
4. identify actors and affected parties
5. identify user reaction or adoption friction
6. identify constraints, approval boundaries, risks, or failure conditions

## Agent Contracts

Agents should write nodes and edges, not free-form long reports.

### Scout

Responsibilities:
- discover `Source`
- cut `Artifact`
- mark `mentions`
- propose weak `Event` candidates

Allowed nodes:
- `Source`
- `Artifact`

Allowed edges:
- `Artifact DERIVED_FROM Source`
- `Artifact MENTIONS Product | Capability | Problem`
- `Artifact SUGGESTS Event`

Output contract:

```yaml
scout_output:
  sources: []
  artifacts: []
  edges:
    - type: derived_from
    - type: mentions
    - type: suggests_event
```

Forbidden:
- writing `Claim`
- writing `Pattern`
- writing `Thesis`

### Extractor

Responsibilities:
- normalize factors
- create `Event`
- identify `Capability` and `Problem`
- create `Claim`, `Counterclaim`, and `WhyNowHypothesis`

Allowed nodes:
- `Event`
- `Capability`
- `Problem`
- `Claim`
- `Counterclaim`
- `WhyNowHypothesis`

Allowed edges:
- `Event HAS_EVIDENCE Artifact`
- `Event AFFECTS Capability`
- `Event ADDRESSES Problem`
- `Claim INTERPRETS Event`
- `Claim SUPPORTED_BY Artifact`
- `Counterclaim CHALLENGES Claim`
- `WhyNowHypothesis EXPLAINS Event`

Output contract:

```yaml
extractor_output:
  factors:
    observable_change: []
    mentioned_capability: []
    mentioned_problem: []
    actor: []
    user_reaction: []
    constraint_or_risk: []
  nodes:
    events: []
    capabilities: []
    problems: []
    claims: []
    counterclaims: []
    why_now_hypotheses: []
  edges:
    - type: has_evidence
    - type: affects
    - type: addresses
    - type: interprets
    - type: supported_by
    - type: challenges
    - type: explains
```

### Jury Lens Agents

Responsibilities:
- evaluate `Claim`, `Pattern`, or `Thesis`
- produce critical review traces
- do not introduce new facts

Allowed nodes:
- `Review`
- `Verdict`

Allowed edges:
- `Review TARGETS Claim | Pattern | Thesis`
- `Review PRODUCES Verdict`

Review structure:

```yaml
review:
  review_id:
  lens:
  target_type:
  target_id:
  verdict: [support, weaken, refute, needs_more_evidence]
  confidence: [low, medium, high]
  vulnerability:
  counterargument:
  required_evidence:
  upgrade_recommendation: [none, to_pattern, to_thesis, downgrade_to_hypothesis]
```

### Judge

Responsibilities:
- update `Thesis`
- mark which `Claim` is promoted to `Pattern`
- mark which `Claim` is downgraded to `WhyNowHypothesis`
- optionally cluster duplicate claims

Allowed nodes:
- `Pattern`
- `Thesis`

Allowed edges:
- `Pattern ABSTRACTS_FROM Claim | Event`
- `Thesis COMPOSED_OF Pattern`
- `Verdict UPGRADES Claim_TO Pattern`
- `Verdict DOWNGRADES Claim_TO WhyNowHypothesis`

## Promotion Rules

### Claim to Pattern

Minimum promotion conditions:
- linked to at least `2-3` distinct `Event` records
- backed by at least `2` distinct `Source viewpoint` categories
- reviewed by at least `2` different lenses
- no high-confidence `refute`
- vulnerability is explicitly recorded

### Pattern to Thesis

Minimum promotion conditions:
- at least `2` patterns point to the same structural judgment
- spans multiple products or multiple time windows
- the update path can be stated through new `Event` and `Verdict` links

## Review Lenses

Review should be rubric-based, not open-ended.

Recommended lens files:
- `ontology/review-lenses/product-lens.md`
- `ontology/review-lenses/ux-collaboration-lens.md`
- `ontology/review-lenses/tech-lens.md`
- `ontology/review-lenses/user-reality-lens.md`
- `ontology/review-lenses/business-lens.md`
- `ontology/review-lenses/brand-lens.md`
- `ontology/review-lenses/contrarian-lens.md`
- `ontology/review-lenses/governance-lens.md`

### Product Lens

Core questions:
- what layer does this event actually change
- what problem is being addressed
- is this feature increment or structural migration
- why now
- does this change control boundary, responsibility allocation, or adoption logic

### UX Collaboration Lens

This lens should capture the AI-native and collaboration-specific UX concerns found in the referenced principles documents.

Core questions:
- can the user understand the current system or agent state
- is the capability boundary visible
- when should the system clarify versus act
- is there a recovery path
- are high-risk actions correctly gated
- is trust calibration appropriate
- is there a temporary or task-specific interface to support complex collaboration

### Tech Lens

Core questions:
- is this structural capability or prompt assembly
- do context, tools, state retention, latency, and cost support the promise
- what are the failure modes
- is the handoff contract traceable

### User Reality Lens

Core questions:
- will users actually adopt it
- where is the friction
- are complaints surface-level or signs of a deeper mental model break
- does user language align with official framing

### Business Lens

Core questions:
- should this enter priority
- what organizational preconditions are required
- does it support durable ROI
- does it alter distribution or monetization logic

### Brand Lens

Core questions:
- does this reinforce who the product is
- is narrative aligned with mechanism
- is this a category weapon or feature noise

### Contrarian Lens

Core questions:
- is marketing language being mistaken for mechanism
- is a small sample being inflated into a trend
- is a feature change being overstated as a paradigm change
- where is the evidence chain broken
- what missing evidence would overturn the current claim

### Governance Lens

This lens is justified by the referenced orchestration principles around handoff, approval, escalation, and responsibility flow.

Core questions:
- where is the approval boundary
- is the action reversible
- is the action auditable
- is permission sensitivity modeled correctly
- when should a human be brought in

## Directory Structure

The library should distinguish object-layer and process-layer records.

Recommended structure:

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

This design intentionally separates `sources/` and `artifacts/`.

## Schema Priorities

The first schema pass should focus on the six objects most likely to distort the library if underspecified:
- `event.schema.json`
- `source.schema.json`
- `artifact.schema.json`
- `claim.schema.json`
- `review.schema.json`
- `pattern.schema.json`

Suggested `claim_type` values:
- `mechanism`
- `positioning`
- `workflow`
- `trust`
- `governance`
- `market_implication`

## Validation and Quality Rules

The long-term library should only accept traceable judgments.

That means:
- every `Pattern` must trace back to `Claim`
- every `Claim` must trace back to `Event`
- every `Event` must trace back to `Artifact`
- every `Artifact` must trace back to `Source`
- every `Thesis` must trace back to `Review` and `Verdict`

If a record cannot be traced across this chain, it should remain in session-level material and should not be written back into the durable ontology.

## Testing and Verification Approach

This is a design-stage change, so verification is document-level.

The design is considered internally consistent when:
- node types are layer-separated
- edge vocabulary is explicit
- `Event` excludes interpretation fields
- `Source` and `Artifact` are separated
- agent outputs are node-edge constrained
- review lenses are rubric-based rather than free-form
- promotion rules are explicit

## Recommended Next Planning Scope

The implementation plan that follows this spec should focus on:
1. updating ontology documents to reflect the new event-centered backbone
2. adding missing directories for `artifacts/`, `counterclaims/`, `theses/`, and `verdicts/`
3. adding first-pass schemas for `Event`, `Source`, `Artifact`, `Review`, and `Pattern`
4. introducing `review-lenses/` rubric documents
5. revising agent contracts so outputs map to nodes and edges rather than prose summaries
