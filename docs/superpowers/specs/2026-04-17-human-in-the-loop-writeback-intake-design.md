# Human-in-the-Loop Writeback Intake Design

## Goal

Add a required human-in-the-loop intake step before writeback generation so reports are shaped by explicit user intent rather than only by evidence and agent judgment.

This mechanism should ensure that:
- report generation is not fully autonomous
- the user can state what kind of report they want before generation starts
- the user can add priorities or concerns outside the default ontology frame
- the system records those choices as part of the long-term knowledge workflow

## Core Position

`Writeback Intake` is a user control layer between `Review/Verdict` and `Writeback`.

It is not part of:
- the fact layer
- the interpretation layer
- the pattern layer

It should be treated as a report-generation control object that captures how the next writeback should be produced for this specific run.

The updated pipeline becomes:

`Source -> Artifact -> Candidate -> Review/Verdict -> Writeback Intake -> Writeback`

## Why This Exists

The current system can generate a readable writeback from evidence, promoted claims, and review logic, but it still assumes too much about what the user wants.

That is a problem because:
- the same evidence may need different presentations for different users or tasks
- users often have priorities that sit outside the default ontology framing
- report format is not the only variable; emphasis, skepticism, and required questions also matter
- future collaboration should preserve the user’s intent as part of the reasoning trail

This design makes report generation explicitly human-in-the-loop instead of implicitly agent-directed.

## Scope

This design covers:
- the `writeback intake` concept
- the minimum question set agents must ask before generating a writeback
- the structure of the intake record
- how intake choices influence writeback output
- how this should be reflected in product docs and templates

This design does not yet cover:
- UI implementation
- automatic personalization based on historical intake behavior
- automatic inference of user preferences without asking

## Design Principles

1. The user must be asked before report generation.
2. The intake should be short and structured, not a free-form interview.
3. Users must still be able to add open-ended instructions outside the default frame.
4. The intake result must be recorded as an explicit object, not left implicit in chat history.
5. The final writeback must visibly reflect intake choices.

## Writeback Intake Object

`Writeback Intake` should be a first-class record associated with a specific writeback run.

It captures:
- how the user wants the report structured
- what the report should emphasize
- what extra questions the report must answer
- what tensions or doubts should remain visible

## Intake Fields

`Writeback Intake` should support both:
- explicit user-provided guidance
- empty or minimal user input

The system must allow the user to provide nothing beyond a confirmation to proceed.
In that case, report generation should fall back to the default writeback rules already defined by the product.

This means:
- intake is still a required step in the workflow
- full field population is not required
- only `intake_id` must always exist as a record key
- all other fields may be user-specified, defaulted, or left empty

### Always-Present Field

- `intake_id`

### Optional Structured Fields

- `collaboration_mode`
- `focus_priority`
- `target_audience`
- `decision_intent`
- `evidence_posture`

### Field Definitions

`collaboration_mode`
- Controls the report presentation style.
- Allowed values:
  - `integrated`
  - `sectioned`
  - `appendix`

`focus_priority`
- Ordered list of what this report should emphasize.
- Suggested values:
  - `mechanism`
  - `capability_boundary`
  - `user_trust`
  - `workflow_change`
  - `industry_implication`

`target_audience`
- Who the report is for.
- Suggested values:
  - `self`
  - `team`
  - `exec`
  - `research_archive`

`decision_intent`
- Why this report is being generated.
- Suggested values:
  - `understand`
  - `compare`
  - `decide`
  - `archive`

`evidence_posture`
- How conservative the report should be when drawing conclusions.
- Suggested values:
  - `strict`
  - `balanced`
  - `exploratory`

## Open Intake Fields

These fields allow the user to steer the report beyond the standard frame.

- `special_attention`
- `extra_questions`
- `avoidances`
- `preserve_tensions`

### Open Field Definitions

`special_attention`
- Extra thematic emphasis for this report.
- Example:
  - “focus on long-term memory and state continuity”
  - “look especially at approval boundaries”

`extra_questions`
- Explicit questions the report must answer.
- Example:
  - “does this really change capability boundaries or is it mostly packaging?”

`avoidances`
- Things the report should avoid over-emphasizing.
- Example:
  - “do not turn this into a macro industry trend piece”

`preserve_tensions`
- Disagreements or uncertainties that should remain visible in the final writeback.
- Example:
  - “preserve the disagreement between product value and actual UX evidence”

## Minimum Agent Question Set

Before generating a writeback, the agent should offer a short intake prompt that gives the user a chance to steer the report.

The intake prompt should cover these areas:

1. collaboration mode
2. focus priority
3. extra themes or required questions
4. doubts, tensions, or boundaries to preserve

These questions should be short and operational. They are not meant to trigger a long conversation.

The user may also decline to specify any of them.
If the user does not provide guidance, the system should proceed with default writeback behavior.

## Relationship To Review Layer

`Writeback Intake` does not replace review.

`Review/Verdict` captures:
- what different seats think about the claim, pattern, or thesis
- where evidence is weak or contested

`Writeback Intake` captures:
- how the user wants those findings presented in this report

The review layer answers:
- “what does the system think?”

The intake layer answers:
- “how should this be written for this user, right now?”

## Relationship To Multi-Lens Review

This design works with the existing multi-lens review model:
- `product`
- `ux_collaboration`
- `tech`
- `user_reality`
- `business`
- `brand`
- `contrarian`
- `governance`

The intake layer does not create new review data.
Instead, it selects how the writeback should present and weight already-existing review traces.

Examples:
- `integrated` mode may summarize lens conflicts inside one narrative
- `sectioned` mode may allocate a section to each active lens
- `appendix` mode may keep the main writeback unified and move review traces to an appendix

## Writeback Requirements

Every future writeback should record:
- `intake_id`
- `collaboration_mode`
- `focus_priority`
- `special_attention`
- `review_refs`
- `verdict_refs`
- `preserved_tensions`

The body of the writeback should visibly reflect intake choices.

If the user provides no intake guidance, the writeback should still record:
- the `intake_id`
- that default report rules were used
- any structured fields that remained unset

Examples:
- if `focus_priority` starts with `user_trust`, trust should move earlier in the report
- if `evidence_posture` is `strict`, speculative implications should be clearly limited
- if `preserve_tensions` includes UX doubt, the report should not resolve that doubt away

## Product Documentation Changes

This mechanism should be written back into product docs in two places.

### 1. Ontology / Operating Rules

Add `Writeback Intake` as a required step between `Review/Verdict` and `Writeback`.

This should explicitly state:
- writebacks are not generated immediately after evidence synthesis
- intake is required before report generation
- the user can steer emphasis and preserve unresolved tensions

### 2. Writeback Template

The writeback template should be expanded to include intake metadata and a visible review-awareness section.

At minimum, future writebacks should expose:
- user-selected collaboration mode
- selected priorities
- special attention items
- preserved tensions
- linked review and verdict references

## Recommended First Implementation

Phase 1 should stay narrow.

Implement:
- a documented `writeback intake` object
- a fixed question set for agents
- template support for intake metadata
- one upgraded sample writeback showing the pattern

Do not implement yet:
- automated preference learning
- dynamic question generation
- user-profile inference
- standalone UI

## Error Handling And Edge Cases

If the user gives no extra guidance:
- the system should still pass through intake
- the agent should allow an empty response
- default writeback rules should be used
- the writeback should record that defaults were applied

If the user gives instructions outside the ontology frame:
- they should be recorded in open fields
- they should not be discarded just because they do not map cleanly to existing lenses

If the user asks for a mode that conflicts with evidence posture:
- the report should preserve that conflict rather than silently smoothing it out

## Testing Expectations

Verification for the first implementation should check:
- a writeback cannot be generated without an intake record
- default-mode writebacks can be generated with no user-specified structured fields
- open-ended user instructions are preserved in the writeback record
- the same evidence can produce different writeback shapes under different collaboration modes
- preserved tensions remain visible in the final output

## Non-Goals

This design does not attempt to:
- turn report generation into a full conversational planning system
- infer the user’s needs without asking
- replace review, verdict, or judge logic

## Final Position

Writeback generation should no longer be treated as a direct consequence of evidence and review alone.

It should be treated as a controlled finalization step that requires explicit user intent, preserves user-specific priorities, and records those priorities as part of the long-term reasoning trail.
