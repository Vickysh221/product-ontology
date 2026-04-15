## Core Claim

The system stores cognitive progression only when it is traceable through explicit objects.
Long-term writeback must never skip evidence layers.
Required traceability chain: `Pattern -> Claim -> Event -> Artifact -> Source`

## Layer Separation Rules

- Facts cannot contain `why_now`.
- Interpretation cannot masquerade as observation.
- Patterns cannot be written from a single source mention.
- Review cannot introduce new fact nodes.

## 1. Two-Level Structure

### A. Object Record
Long-term layer for stable definitions, confirmed judgments, and durable continuity.
Minimum fields:
- `object_type`
- `object_id`
- `title`
- `status`
- `confidence`
- `evidence_refs`
- `updated_at`

### B. Session Progress Record
Session layer for bounded cognitive progression, framing moves, and provisional outputs.
Minimum fields:
- `session_id`
- `focus_object_ids`
- `initial_frame`
- `cognitive_moves`
- `outputs`
- `writeback_candidates`
- `status`

## 2. Core Design Stance

- Object-state continuity is the main record.
- Intent continuity is the guardrail.

## 3. Focus Object

Recommended object types:
- `product`
- `event`
- `artifact`
- `source`
- `claim`
- `hypothesis`
- `decision`
- `question`
- `pattern`
- `thesis`
- `verdict`
- `review`
- `counterclaim`
- `why_now_hypothesis`
- `session_trace`

## 4. Frame

Objects can be understood through different frames such as product strategy, user trust, workflow mechanism, system architecture, responsibility allocation, positioning, adoption friction, and safety.

## 5. Cognitive Move

Recommended move types:
- `propose`
- `clarify`
- `reframe`
- `decompose`
- `compare`
- `challenge`
- `infer`
- `validate`
- `converge`
- `confirm`
- `reject`
- `defer`
- `reflect`
- `escalate`
- `assign`

## 6. Structured Outputs

The system must distinguish:
- `fact_statement`
- `claim`
- `hypothesis`
- `decision`
- `question`
- `plan`
- `recommendation`

## 7. Trigger / Evidence

Each major cognitive shift should keep a trigger source:
- `official_source`
- `engineering_source`
- `user_feedback`
- `podcast_or_video`
- `issue_or_discussion`
- `contradiction`
- `benchmark`
- `regulatory_signal`
- `agent_analysis`
- `memory`

## 8. Ownership

Minimum ownership fields:
- `intent_owner`
- `decision_owner`
- `structuring_owner`
- `execution_owner`
- `writeback_owner`

## 9. Writeback Rule

Only write back from session to object when the result is confirmed, reusable, stable, non-ephemeral, and worth preserving beyond the session.
