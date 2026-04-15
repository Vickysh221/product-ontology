## 本轮目标

把“懒得做竞品调研”重构为：

> 设计一个基于 ontology 的 Product Learning Library，持续吸收一手信号，并通过 session trace、jury review、selective writeback，形成稳定的产品判断系统。

## 本轮稳定结论

1. 这套系统不是竞品文档生成器，而是 Product Intelligence System。
2. 系统中心对象不是文档，而是对象状态与判断状态。
3. 需要显式区分 object layer 与 session layer。
4. 需要显式区分 fact / claim / hypothesis / decision / question。
5. 需要 Source Scout、Claim Extractor、Jury Synthesizer、Collaboration Trace Synthesizer 这类 agent，而不是一个“万能研究 agent”。
6. 需要评审团式 review protocol，而不是多人并行写作。
7. 播客、YouTube、Bilibili、直播、用户评测必须作为正式 source bucket，而不是补充材料。
8. Podwise 适合作为 ingest / normalization 层，不应替代 interpretation 层。

## 建议写回 Object Layer 的内容

- object-centered cognitive progression
- selective writeback rule
- evidence-constrained claim system
- jury review as the core quality-control mechanism
- Product Learning Library 目录结构与对象族

## 当前待定项

- writeback threshold 是否需要更明确量化
- object types 是否允许多标签共存
- session frame 是否要成为 object-level persistent field
- 多对象 session 的挂接策略如何表达
- 不同 review mode 的席位权重如何自动调整

## 下一阶段建议

### Phase 1
先跑最小可用系统：
- `events/`
- `products/`
- `patterns/`
- `questions/`
- `sources/`
- `sessions/`

### Phase 2
接入 automation / skills：
- source watcher
- podcast/video ingest
- claim extractor
- cross-source verifier
- importance scorer
- writeback recommender

### Phase 3
引入 jury review：
- independent first pass
- cross-examination
- preserved conflicts
- structured verdict

---
