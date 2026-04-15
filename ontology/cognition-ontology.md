## Core Claim

本系统不是 task log，也不是聊天摘要器。
它应被定义为：

**object-centered cognitive progression system**

它要保留的不是“说了什么”，而是：
- 讨论对象是什么
- 对象是如何被 framing 的
- 发生了哪些 cognitive moves
- 哪些理解发生了状态变化
- 哪些变化稳定到足以 write back

## 1. Two-Level Structure

### A. Object Record
长期层。
用于承载稳定定义、长期连续状态、已确认结论、长期 questions、历史关键转向。

### B. Session Progress Record
会话层。
用于承载一次有边界的研究 / 讨论 / 审议过程中，理解如何推进、产生哪些 claim / hypothesis / decision / action item。

## 2. Core Design Stance

- **Object-state continuity is the main record.**
- **Intent continuity is the guardrail.**

意思是：
- 主记录应忠于对象状态如何演化
- 但必须保留 initiator 的原始方向，防止 agent 过度重构而偏航

## 3. Focus Object

focus object 应广于 task。
推荐 object types：
- `product`
- `product_event`
- `source_item`
- `claim`
- `hypothesis`
- `decision`
- `question`
- `pattern`
- `method`
- `jury_review`
- `evidence_artifact`
- `session_trace`
- `strategy`
- `concept`
- `problem`
- `reflection_theme`

## 4. Frame

对象可从不同 frame 被理解，例如：
- product strategy
- user trust
- workflow mechanism
- system architecture
- responsibility allocation
- positioning / narrative
- adoption friction
- safety / regulation

重要的不只是新增信息，很多时候是 **reframing**。
因此每个 session 至少应保留：
- initial frame
- reframing moves
- current dominant frame

## 5. Cognitive Move

最小记录单元不是 sentence，而是 **cognitive move**。
推荐 move types：
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

记录规则：
只记录那些改变了以下任一状态的动作：
- object understanding
- frame
- ownership
- decision status
- direction
- next-step structure

## 6. Cognitive Dimensions

推荐共享维度：
- `goal_understanding`
- `problem_framing`
- `scope_boundary`
- `causal_model`
- `solution_path`
- `priority_logic`
- `risk_assessment`
- `responsibility_model`
- `decision_status`
- `confidence_level`
- `narrative_alignment`
- `user_reality_alignment`

附加维度：
- `self_positioning`
- `identity_tension`
- `emotional_interpretation`
- `meta_pattern`

## 7. Structured Outputs

系统必须显式区分：
- `fact_statement`
- `claim`
- `hypothesis`
- `decision`
- `question`
- `plan`
- `recommendation`

不能压平为 generic note。

## 8. Trigger / Evidence

每个重要认知转变都应保留触发来源：
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

## 9. Ownership

最低 ownership 字段：
- `intent_owner`
- `decision_owner`
- `structuring_owner`
- `execution_owner`
- `writeback_owner`

## 10. Writeback Rule

只有满足若干条件，才允许从 session 写回 object：
- confirmed
- reusable
- stable
- non-ephemeral
- worth preserving beyond the session

---
