# Multiagent Human Coexistence Research Framework

## Purpose

This document defines a reusable research framework for analyzing multiagent human coexistence and collaboration systems.

It is not a product spec, not a feature list, and not an implementation plan.
It is a question framework for:

- collecting source materials
- extracting evidence
- organizing discussion
- generating writebacks

中文说明：
这不是产品方案文档，而是一套研究问题框架。
它的作用是把 0-to-1 设计问题转写成适合资料分析、证据提取和 writeback 生成的问题结构。

## How To Use This Framework

Use this framework when the system under study involves:

- humans and agents sharing work
- escalation, approval, or takeover logic
- collaborative state presentation
- memory writeback or reusable system learning
- decision support under uncertainty

The framework should be applied in this order:

1. collect first-hand sources and supporting materials
2. paraphrase product claims into analyzable research questions
3. evaluate the system through the question groups below
4. separate facts, interpretations, hypotheses, and disagreements
5. produce a review pack and then a writeback

中文说明：
使用顺序应是先收集资料，再按下面的问题组分析，再组织 review pack，最后进入 writeback。
不要直接把营销说法提升为结构判断。

## Core Question Group 1

### Human Control, Escalation, And Learning Loop

This group asks how a system defines human control boundaries, when agents must escalate to people, and whether human intervention becomes future system capability.

Key questions:

- Which critical nodes are reserved for human judgment?
- How does the product prevent automated flows from crossing those boundaries?
- How does the product escalate uncertainty, conflict, and authority gaps into requests that are legible and actionable for humans?
- Does the product convert human intervention into reusable system experience?
- Can the system judge whether similar future situations still require human involvement?

中文说明：
这一组关注三件事：人何时介入，agent 何时主动找人，以及这次人的介入能不能被系统学会。

## Core Question Group 2

### State Legibility And Attention Orchestration

This group asks how system information becomes human-readable under time pressure, cognitive limits, and decision burden.

Key questions:

- What information unit reaches the human: an event stream or a decision-sized issue card?
- How does the product decide whether information should interrupt, batch, or remain silent?
- Is notification intensity designed by event severity alone, or by human attention budget?
- Does the product render system state in a pattern language that supports one-glance judgment?
- Can users quickly identify urgency, mode, risk, and required action?

中文说明：
这一组不只是看“有没有通知”，而是看信息如何被分级、压缩、呈现，以及用户能不能一眼判断自己所处状态。

## Core Question Group 3

### Collaborative UX Specification And State Design

This group asks whether human-agent collaboration has been turned into an explicit UX specification instead of remaining an implicit capability bundle.

Key questions:

- Does the product specify a clear collaborative user flow, including handoff, review, correction, and takeover?
- Does the product define an explicit state matrix for AI collaboration?
- Are key collaboration components defined with clear trigger conditions and user actions?
- Does the product make capability boundaries, uncertainty, correction paths, and human takeover requirements explicit in the frontstage UX?

中文说明：
这一组关注协作 UX 是否真正被规格化，包括用户流、状态矩阵、关键组件行为，以及 AI 特有信息是否进入前台。

## Core Question Group 4

### Problem Framing, Goals, And Success Criteria

This group asks whether the product clearly defines the problem it is solving, the goals it is pursuing, the boundaries it accepts, the risks it depends on, and the metrics by which success will be judged.

Key questions:

- Does the product clearly and consistently define the user and business problem it is trying to solve?
- Does it clearly decompose business goals, user goals, delivery goals, and non-goals?
- Does it define explicit scope boundaries and testable success criteria?
- Does it make dependencies, risks, and design rationale explicit?
- Does it define a metric system that measures collaboration quality, human burden, and decision quality rather than output volume alone?

中文说明：
这一组把“为什么做、做到什么算成功、边界在哪、依赖是什么、怎么衡量”单独拉出来，防止系统只有协作表面而没有问题定义。

## Core Question Group 5

### Evidence, Traceability, And Shared Memory Writeback

This group asks how the system ensures that judgments are grounded in traceable evidence and how only stable enough conclusions are written into shared memory.

Key questions:

- Is the judgment grounded in strong enough evidence?
- Can important conclusions be traced back to concrete source materials and specific segments?
- Does the system distinguish facts, interpretations, hypotheses, and disagreements before writeback?
- What is allowed to enter shared memory?
- How does the system prevent memory contamination, over-generalization, and premature flattening of disagreement?

中文说明：
这一组关注判断生命周期管理，特别是证据强度、可追溯性、写回边界，以及共享记忆污染风险。

## Practical Use In Writeback Work

This framework is not meant to replace direct evidence work.
Its role is to guide how evidence is read and what kinds of structural judgments are worth promoting.

It should help answer:

- what the system is optimizing
- where control remains human
- how collaboration becomes readable
- whether the UX is properly specified
- whether the evidence is strong enough to support durable writeback

中文说明：
这套框架的目的不是代替证据，而是帮助判断什么值得被提升成稳定 writeback 结论。
