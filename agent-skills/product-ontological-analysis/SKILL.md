---
name: product-ontological-analysis
description: Use when a research workflow must preserve provenance across source, artifact, intake, review, and final writeback layers.
---

# Product Ontological Analysis

## Overview

Use this skill when the output must stay evidence-constrained instead of becoming a loose summary.

Core rule:

`No writeback without normalized artifacts, an explicit direction, and preserved tensions.`

## When To Use

Use this skill when:
- approved links, transcripts, notes, or imported sources must become a review pack and final writeback
- the workspace separates source, artifact, interpretation, and durable judgment
- the user cares about provenance, approval boundaries, or memory contamination
- disagreement or counter-signal must remain visible instead of being polished away

Do not use this skill for:
- generic summarization
- one-off note cleanup
- opinion writing without evidence refs
- workflows where intermediate layers can be skipped safely

## Core Flow

1. Frame the run.
   - State the research direction, or produce one for explicit approval.
   - Block final writeback if the direction is still pending.
2. Normalize materials.
   - Convert approved sources into stable source and artifact records.
   - Never fabricate missing content for unsupported channels.
3. Build evidence from artifacts.
   - Prefer first-hand or strongest available artifact slices.
   - Tag support, tension, counter-signal, and open questions explicitly.
4. Cluster before concluding.
   - Group evidence by mechanism or theme.
   - Keep evidence refs attached to each cluster.
5. Capture writeback intent.
   - Record audience, mode, focus, and tension-preservation rules in intake.
6. Write the review pack first.
   - Keep `Direct quote`, `Paraphrase`, `Evidence`, and `Why it matters` visible.
7. Derive the writeback from reviewed evidence.
   - Final sections should be traceable to clusters or review objects, not free-floating prose.
8. Verify before closing.
   - Check for placeholders, missing artifacts, broken refs, and collapsed tensions.

## Repo Profiles

If the workspace has a repo-specific profile for this workflow, read it before execution.

Portable packages can keep example profiles under `profiles/`. Target repositories can also store the profile next to their own operating docs.

## Success Check

A good run leaves:
- normalized source and artifact records
- an explicit direction and intake boundary
- a review pack with evidence shape intact
- a writeback whose claims can be traced backward
- tensions that remain visible for later rounds

## Common Mistakes

- Starting from a preferred conclusion instead of an approved direction
- Writing the final report directly from source metadata
- Using artifacts as decoration instead of as the basis for section-level claims
- Treating counter-signals as noise to be removed
- Calling a workflow first-hand when the workspace never normalized the material
