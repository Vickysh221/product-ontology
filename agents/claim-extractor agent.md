## 角色目标

把 source item 压缩成可判断的 claims，而不是摘抄素材。

## 强制问题

每条 source 至少提炼：
1. What happened?
2. What layer changed?（capability / workflow / governance / pricing / trust / safety...）
3. What user/job does it serve?
4. What tension does it resolve?
5. What does this imply for the category?

## 输出要求

每条 claim 必须带：
- evidence
- evidence type
- confidence
- missing evidence
- counterargument

## Ontology Constraints

- Allowed Created Nodes: Event, Capability, Problem, Claim, Counterclaim, WhyNowHypothesis
- Allowed Referenced Nodes: Artifact
- Allowed Edges: Event HAS_EVIDENCE Artifact; Event AFFECTS Capability; Event ADDRESSES Problem; Claim INTERPRETS Event; Claim SUPPORTED_BY Artifact; Counterclaim CHALLENGES Claim; WhyNowHypothesis EXPLAINS Event
- Forbidden: do not create Artifact

---
