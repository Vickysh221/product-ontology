# Writeback Intake Matrix Test Design

## Goal

Design a controlled writeback-generation test that verifies whether `Writeback Intake` meaningfully changes report output.

The test should use one shared evidence pool and one shared judgment base, then vary:
- collaboration mode
- target audience
- extra question focus

The purpose is not to test different source materials. The purpose is to test whether intake choices genuinely shape writeback structure, emphasis, and argumentation.

## Test Scope

This test covers:
- one shared five-episode podcast evidence pool
- one shared synthesized judgment base
- twelve writeback variants
- all-Chinese output

This test does not cover:
- UI
- automatic personalization from historical user choices
- generation across different source channels in the same batch
- 36-way combinatorial expansion

## Shared Evidence Pool

All twelve writebacks should be generated from the same five Podwise episodes:

- `https://podwise.ai/dashboard/episodes/7758431`
- `https://podwise.ai/dashboard/episodes/7718625`
- `https://podwise.ai/dashboard/episodes/7635732`
- `https://podwise.ai/dashboard/episodes/7504915`
- `https://podwise.ai/dashboard/episodes/7368984`

These episodes collectively emphasize:
- harness engineering
- agent orchestration
- team-of-agents workflows
- enterprise multi-agent collaboration
- safety, permission, and controlled execution

## Shared Judgment Base

All twelve writebacks should share one synthesized parent judgment:

`从单 Agent 工具走向可治理的 Agent Team：harness engineering、multi-agent 协作和企业级多人多agent管理，正在收束为同一条产品演化线。`

This parent judgment should remain stable across all twelve writebacks.

The writebacks may vary in:
- what they emphasize
- how they organize the narrative
- which tensions they foreground

They should not vary in the underlying evidence pool or the base claim set.

## Controlled Variables

The matrix has three controlled variables.

### 1. Collaboration Mode

- `integrated`
- `sectioned`
- `appendix`

### 2. Target Audience

- `self`
- `team`
- `exec`
- `research_archive`

### 3. Extra Question Theme

- `harness engineering`
- `multiagent paradigm shift`
- `多人多agent的企业管理`

The first two variables define the 12-writeback matrix.

The third variable is distributed across the 12 writebacks in a rotating pattern rather than multiplied into a 36-writeback matrix.

## Why This Matrix

The goal is to hold the evidence constant while varying presentation control.

This allows the system to test whether:
- collaboration mode changes report structure
- target audience changes report density and emphasis
- extra question focus changes argument direction

without introducing evidence drift.

## Twelve-Writeback Matrix

### Integrated

1. `integrated + self` -> `harness engineering`
2. `integrated + team` -> `multiagent paradigm shift`
3. `integrated + exec` -> `多人多agent的企业管理`
4. `integrated + research_archive` -> `harness engineering`

### Sectioned

5. `sectioned + self` -> `multiagent paradigm shift`
6. `sectioned + team` -> `多人多agent的企业管理`
7. `sectioned + exec` -> `harness engineering`
8. `sectioned + research_archive` -> `multiagent paradigm shift`

### Appendix

9. `appendix + self` -> `多人多agent的企业管理`
10. `appendix + team` -> `harness engineering`
11. `appendix + exec` -> `multiagent paradigm shift`
12. `appendix + research_archive` -> `多人多agent的企业管理`

## Stable Mode Differences

### Integrated

`integrated` mode should produce a single unified narrative.

Expected characteristics:
- strongest single argument thread
- least visual separation between review voices
- best for testing whether the system can synthesize one coherent report without flattening disagreement

### Sectioned

`sectioned` mode should make structural differences visible.

Expected characteristics:
- clearer separation of themes or review angles
- best for testing whether writeback structure changes meaningfully under mode selection
- easiest mode for exposing multi-lens review logic in the main body

### Appendix

`appendix` mode should keep the primary narrative compact and move more tension/review material out of the main flow.

Expected characteristics:
- cleaner main body
- review traces, preserved disagreements, and deeper support material shifted later
- best for testing whether the main narrative becomes more decision-friendly without deleting nuance

## Stable Audience Differences

### Self

Expected characteristics:
- more exploratory
- more unfinished but useful thinking
- more explicit open questions
- more tolerance for ambiguity

### Team

Expected characteristics:
- more discussion-oriented
- more emphasis on shared alignment, tradeoffs, and next questions
- more explicit preserved disagreements

### Exec

Expected characteristics:
- shorter and more compressed
- stronger emphasis on practical meaning and decision relevance
- less detail unless required by the extra question

### Research Archive

Expected characteristics:
- strongest traceability
- clearer evidence anchoring
- strongest preservation of framing precision
- best archival value

## Extra Question Forms

The extra question layer should not be treated as a keyword boost. It should alter what the writeback must answer.

### A. Harness Engineering

Question form:
- 这到底是工程控制层，还是产品能力层？
- 哪些部分属于让 agent 可控的基础设施，哪些部分已经变成用户可感知的产品机制？
- 如果没有 code review、BDD、container、权限边界，这套 agent workflow 还成立吗？

Expected report effect:
- more emphasis on control boundaries, testability, execution environment, and operational discipline

### B. Multiagent Paradigm Shift

Question form:
- 这里发生的是 feature 组合增强，还是从单 agent 到 agent team 的范式迁移？
- “Team of Agents / subagent / OpenClaw / OpenCore” 背后，真正稳定的结构变化是什么？
- 哪些证据说明这不是包装话术，而是能力边界和工作流真的变了？

Expected report effect:
- more emphasis on category change, structural migration, orchestration logic, and stable architectural pattern

### C. 多人多agent的企业管理

Question form:
- 当多人和多 agent 一起工作时，角色、权限、审计、责任如何分配？
- 企业为什么需要 agent 与人、agent 与 agent 的明确沟通边界？
- 哪些管理结构是为了安全与合规，哪些是为了提高协作吞吐量？

Expected report effect:
- more emphasis on governance, enterprise coordination, permission boundaries, and responsibility structure

## Output Rules

All twelve outputs must be fully Chinese.

This includes:
- titles
- subtitles
- report body
- intake-facing labels in final output
- explanation sections

Internal implementation may still preserve canonical enum values where needed, but rendered output should remain fully Chinese.

## Output Pattern

Each writeback should share one common theme title and one variant subtitle.

Recommended parent title:

`从单 Agent 工具到可治理的 Agent Team：五条一线语料中的编排、协作与企业化信号`

Each writeback should then add a variant subtitle that reflects:
- collaboration mode
- target audience
- extra question focus

Example:
- `给团队看的 integrated 版：Harness Engineering 是工程手段还是产品主能力`
- `给高层看的 appendix 版：Multi-Agent 是否已进入范式迁移期`

## Success Criteria

This test succeeds if:
- the 12 writebacks clearly differ by mode and audience
- the extra question theme produces visible shifts in argument emphasis
- all outputs remain grounded in the same evidence pool and judgment base
- the reports do not collapse into template clones with only shallow wording differences

## Failure Modes

This test fails if:
- the 12 outputs are structurally too similar
- audience changes only alter tone but not information density or emphasis
- extra question themes behave like keyword substitutions rather than argumentative pivots
- evidence usage drifts between variants
- the parent judgment changes across variants

## Recommended First Implementation

Phase 1 should:
- synthesize one shared cross-episode judgment base
- define 12 intake records
- generate 12 writebacks from that shared base
- evaluate whether output differences are meaningful

Phase 1 should not yet:
- expand to 36 writebacks
- mix podcast, xiaohongshu, wechat, and official sources in the same matrix
- optimize style or ranking automatically

## Final Position

This matrix is a controlled test of whether writeback generation is truly shaped by human-in-the-loop intake.

By fixing evidence and judgment while varying collaboration mode, target audience, and extra-question emphasis, the system can observe whether intake is a real control layer or only cosmetic metadata.
