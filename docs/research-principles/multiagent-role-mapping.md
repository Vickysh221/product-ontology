# Multiagent Role Mapping For Research And Writeback

## Purpose

This document maps the multiagent role set to the research framework used for multiagent human coexistence analysis.

The goal is not to define implementation details.
The goal is to define role responsibilities, role boundaries, and how different roles contribute to evidence-driven writeback generation.

中文说明：
这份文档说明的是“谁负责什么”，不是实现细节。
它把研究框架映射到 multi-agent 协作结构中。

## Role Set

- `Orchestrator`
- `Researcher`
- `Opinion Holder`
- `Critic`
- `Synthesiser`
- `Report Writer`

## Role Responsibilities

### Orchestrator

Responsibilities:

- frame the current research run
- define scope, objectives, and deliverables
- coordinate work across roles
- decide when discussion should advance or pause
- manage conflicts, unresolved questions, and escalation timing

Boundary:

- should not replace evidence collection
- should not flatten disagreements too early

中文说明：
Orchestrator 负责编排，不负责代替其他角色做实质研究。

### Researcher

Responsibilities:

- prioritize first-hand materials whenever possible
- collect and normalize source materials
- build evidence packets with context, provenance, and relevant excerpts
- distinguish first-hand, second-hand, and derivative materials
- provide enough background for downstream lens-based discussion

Boundary:

- should not prematurely collapse evidence into final conclusions
- should not hide source uncertainty

中文说明：
Researcher 是第一手资料守门人和背景铺陈者，目标是把事实底座铺开给后续角色。

### Opinion Holder

Responsibilities:

- read evidence through an explicit lens
- produce structured interpretations rather than raw summaries
- identify what the evidence implies within that lens
- preserve lens-specific emphasis instead of forcing consensus

Boundary:

- should stay grounded in the evidence packet
- should not silently absorb contradictions into vague synthesis

中文说明：
Opinion Holder 代表一个明确 lens 发言，重点是解释，不是搜集。

### Critic

Responsibilities:

- test claims for weak evidence, hidden assumptions, and jumps in logic
- identify where product rhetoric is mistaken for mechanism
- surface disagreements, counter-signals, and contamination risk
- challenge over-generalization and premature writeback promotion

Boundary:

- should not replace synthesis
- should not turn every tension into paralysis

中文说明：
Critic 负责找漏洞、反证、跳步和污染风险，不负责最后收束。

### Synthesiser

Responsibilities:

- consolidate evidence-backed insights across roles
- separate consensus, disagreement, and open questions
- preserve productive tensions
- prepare material for writeback without erasing role distinctions

Boundary:

- should not invent evidence
- should not erase disagreement for the sake of neatness

中文说明：
Synthesiser 负责收束，但要保留分歧，不是把所有东西揉成一个声音。

### Report Writer

Responsibilities:

- turn synthesized material into review packs and writebacks
- maintain structural clarity and evidence traceability
- represent judgments, tensions, and open questions in document form
- keep the final output readable without weakening the underlying reasoning

Boundary:

- should not become the hidden decision-maker
- should not introduce new arguments unsupported by prior stages

中文说明：
Report Writer 负责写，不负责在最后一刻偷偷改判断。

## Framework-To-Role Mapping

### Group 1: Human Control, Escalation, And Learning Loop

- Primary: `Opinion Holder`, `Critic`
- Supporting: `Researcher`, `Synthesiser`

Expected role behavior:

- `Researcher` gathers first-hand evidence on approval logic, escalation behavior, and learning loops
- `Opinion Holder` interprets control boundaries and escalation design
- `Critic` checks whether claimed control logic is actually evidenced
- `Synthesiser` consolidates conclusions about human control and learned intervention

### Group 2: State Legibility And Attention Orchestration

- Primary: `Opinion Holder`
- Supporting: `Researcher`, `Critic`, `Synthesiser`

Expected role behavior:

- `Researcher` gathers materials on decision cards, alerting, state visuals, and pattern language
- `Opinion Holder` evaluates state readability and attention design
- `Critic` challenges over-reading of visual claims or UI rhetoric
- `Synthesiser` consolidates how the system manages attention and state interpretation

### Group 3: Collaborative UX Specification And State Design

- Primary: `Opinion Holder`
- Supporting: `Researcher`, `Critic`, `Synthesiser`

Expected role behavior:

- `Researcher` collects user flow, state model, and component evidence
- `Opinion Holder` evaluates whether collaboration is actually specified as UX
- `Critic` checks for missing state cases, implicit flows, or hidden failure modes
- `Synthesiser` integrates UX specification findings into the overall judgment

### Group 4: Problem Framing, Goals, And Success Criteria

- Primary: `Orchestrator`, `Opinion Holder`
- Supporting: `Researcher`, `Critic`, `Synthesiser`

Expected role behavior:

- `Orchestrator` anchors the run around the actual research question
- `Researcher` gathers statements about problem framing, goals, risks, and metrics
- `Opinion Holder` interprets whether the framing is coherent
- `Critic` checks for unstable framing, vague success claims, and shallow metrics
- `Synthesiser` distills what the product truly claims to solve

### Group 5: Evidence, Traceability, And Shared Memory Writeback

- Primary: `Researcher`, `Critic`
- Supporting: `Synthesiser`, `Report Writer`

Expected role behavior:

- `Researcher` ensures evidence quality and provenance
- `Critic` checks traceability, writeback boundaries, and contamination risk
- `Synthesiser` separates fact, interpretation, hypothesis, and disagreement
- `Report Writer` preserves those distinctions in final outputs

## Collaboration Pattern

Recommended sequence:

1. `Orchestrator` frames the run
2. `Researcher` builds the evidence packet
3. `Opinion Holder` interprets through explicit lenses
4. `Critic` challenges the evidence use and logical jumps
5. `Synthesiser` consolidates consensus, disagreements, and open questions
6. `Report Writer` writes the review pack and writeback

中文说明：
这套顺序强调先证据、后解释、再批判、最后收束和写作。
不要让写作者提前主导判断，也不要让批判者阻塞系统。

## Design Principle

The system should move from:

- raw materials
- to structured evidence
- to lens-based interpretation
- to explicit critique
- to bounded synthesis
- to traceable writeback

中文说明：
核心原则是：原始资料先被整理成证据，再进入 lens 解释、批判和收束，最后生成可追溯 writeback。
