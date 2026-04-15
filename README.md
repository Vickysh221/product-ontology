# Product Learning Library

This repository is an event-centered, evidence-constrained, review-updated ontology-based product analysis library.

The operating model is deliberately narrow:
- Product is the anchor object.
- Event is the entrypoint for durable change.
- Artifact is the evidence carrier.
- Review and verdict records are the promotion and downgrade mechanism for long-term judgments.
- The core operating chain is `Source -> Artifact -> Event -> Claim -> Pattern -> Thesis`.

## Why This Exists

This is not a news scraper and not a generic competitor notes repo. It exists to keep product understanding traceable across evidence layers, so long-term judgments can be updated without losing provenance.

The repository is built to answer:
- What changed
- What evidence supports the change
- Which layer changed
- What should be promoted into a stable judgment
- What should be downgraded, reopened, or weakened by review

## Operating Principles

1. Object-centered, not document-centered.
2. Event-centered, not summary-centered.
3. Evidence-first, with explicit Artifact layers.
4. Review-updated, so long-term judgments can move up or down over time.
5. No skipped layers on writeback.
6. Traceability is mandatory from thesis-level judgment back to source.

## Repository Structure

```text
product-ontology/
  README.md
  ontology/
    cognition-ontology.md
    product-intelligence-ontology.md
    jury-review-ontology.md
  schemas/
    ontology-manifest.json
    session-progress-record.schema.json
    claim-record.schema.json
    product-record.schema.json
  library/
    sources/
    events/
    products/
    claims/
    hypotheses/
    patterns/
    methods/
    reviews/
    sessions/
    questions/
    writebacks/
    _operating-notes.md
  templates/
    source-item.md
    product-record.md
    product-event-card.md
    claim-record.md
    method-card.md
    pattern-card.md
    jury-review-record.md
    session-progress-record.md
    writeback-proposal.md
    today-brief.md
    weekly-pattern-review.md
    monthly-thesis-update.md
  seed/
    watchlist.md
    initial-questions.md
    first-tracking-theses.md
  PRD Session Summary.md
```

Directory responsibilities:
- Current `library/` directories store sources, events, products, claims, hypotheses, patterns, methods, reviews, sessions, questions, and writebacks.
- Current `schemas/` files cover the manifest, product records, claim records, and session progress records.
- Upcoming workstreams include artifact, counterclaim, thesis, verdict, and review-lens layers once those files are added to the tree.

## Getting Started

1. Read [`ontology/cognition-ontology.md`](./ontology/cognition-ontology.md) and [`ontology/product-intelligence-ontology.md`](./ontology/product-intelligence-ontology.md) first.
2. Then inspect the current templates for `source-item`, `product-record`, `product-event-card`, `claim-record`, `pattern-card`, `jury-review-record`, `session-progress-record`, and `writeback-proposal`.
3. Start with `seed/watchlist.md` to choose products and their first event streams.
4. Capture evidence in source notes and event cards before forming claims.
5. Use review records to adjust the status of claims, patterns, and theses rather than rewriting history.
6. Treat artifact, counterclaim, thesis, and verdict layers as upcoming repository additions until those files exist in the tree.

## Main Tracking Lines

### AI Coding / Agent Workflow

Focus on harness, orchestration, runtime, workspace, reviewer loops, long-running tasks, and real friction in environment, cost, and stability.

### Multi-Agent Collaboration / Memory / Workspace

Focus on persistent identity, object continuity, long-term memory, writeback, approval boundaries, and role-based collaboration.

### Assisted Driving / Trust Framing / Vehicle AI

Focus on capability packaging, HMI, trust, safety communication, regulation, and the gap between demo and durable product behavior.

## Output Layers

### Daily Brief

Keep only high-signal changes:
- what changed
- why it matters
- how it affects the long-term chain

### Weekly Pattern Review

Answer which changes are repeating across events and which ones are still isolated.

### Monthly Thesis Update

Update the long-term judgment set with explicit promotion, weakening, or downgrade decisions.
