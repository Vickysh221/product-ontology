---
name: human-agent-coop-ux-init
description: Use when a human-agent or agent-agent session needs a durable progression record with ownership, decisions, open questions, and next-entry continuity.
---

# Human Agent Coop UX Init

## Overview

Use this skill when collaboration itself is the object that needs to be preserved.

Core rule:

`Record the move, the owner, the state change, and the next entry point.`

## When To Use

Use this skill when:
- a human-agent session needs a durable progression record
- an agent-agent handoff needs a continuation contract instead of a prose summary
- the workflow must preserve who proposed, who decided, and what remains unresolved
- session output may later justify writeback, but should not become writeback by default

Do not use this skill for:
- generic meeting summaries
- source ingestion
- artifact-level evidence extraction
- final review-pack or writeback generation

## Required Output Shape

- focus object
- intent owner
- decision owner
- structuring owner
- execution owner
- current problem definition
- subproblems
- proposals
- decisions made
- open questions
- assumptions
- memory candidates
- next entry point
- writeback eligibility

## Guardrails

- Do not flatten unconfirmed interpretation into final judgment.
- Do not lose who owns a decision.
- Do not replace a progression record with prose-only summary.
- Do not update object-level continuity directly from a session trace.

## Common Mistakes

- Treating a handoff note like a retrospective
- Mixing final decisions with still-open options
- Dropping ownership fields because the participants feel obvious in context
- Promoting tentative framing into durable memory without marking confidence
