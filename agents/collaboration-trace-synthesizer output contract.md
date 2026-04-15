## Purpose

Define what files must be produced when structured mode is invoked.
The goal is durable artifacts, not just a chat reply.

## Default Output Root

```text
library/sessions/<object-id>/
```

## Required Outputs

### 1. Session Markdown Record

Path:
```text
library/sessions/<object-id>/YYYY-MM-DD-<slug>.md
```

Must contain:
- session metadata
- focus object
- intent frame
- current problem definition
- key cognitive moves
- decisions
- open questions
- action items
- next entry point
- writeback recommendation

### 2. Session JSON Record

Path:
```text
library/sessions/<object-id>/YYYY-MM-DD-<slug>.json
```

Minimum fields:
```json
{
  "session_type": "human-agent | agent-agent | reflection | strategy",
  "intent_frame": {},
  "focus_objects": [],
  "start_state": "",
  "cognitive_moves": [],
  "claims": [],
  "hypotheses": [],
  "decisions": [],
  "open_questions": [],
  "action_items": [],
  "memory_candidates": [],
  "next_entry_point": "",
  "writeback_recommended": true
}
```

### 3. Object Writeback Proposal

Path:
```text
library/writebacks/<object-id>/YYYY-MM-DD-<slug>-writeback.md
```

When to create:
Only when the session produced a change that is:
- confirmed
- reusable
- stable
- worth preserving beyond the session

Must contain:
- linked object id
- what changed
- why it now qualifies for object-level continuity
- target fields / sections to update
- confidence / confirmation status

## Optional Outputs

### 4. Handoff Contract

Path:
```text
library/sessions/<object-id>/handoffs/YYYY-MM-DD-<slug>-handoff.md
```

Used when:
- agent-agent handoff
- downstream clean delegation

Must contain:
- input contract
- expected output
- blockers
- escalation path

## Overwrite Policy

- never overwrite existing session records
- append-only for sessions and writebacks
- actual object updates must happen through separate confirmed writeback step

## Quality Bar

A valid output must preserve:
- the object
- the move
- the state change
- the ownership boundary
- the continuation entry point

If these are missing, the output is not compliant.

---
