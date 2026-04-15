## 项目定义

这不是一个新闻抓取器，也不是一个普通竞品分析库。

它是一个 **Product Learning Library**，用于持续吸收来自：
- 官网文档
- changelog / release notes
- engineering blog
- GitHub issues / discussions / releases
- 播客
- YouTube / Bilibili / livestream
- 用户评测视频 / 图文 / 社区反馈
- 监管 / 信任 / 市场信号

并把这些异构来源统一沉淀为：
- 产品记录
- 事件记录
- source item
- claim / hypothesis / decision
- pattern / method
- jury review
- session trace
- writeback proposal

## 核心原则

1. **对象中心，不是文档中心**
   库的中心不是“看过哪些文章”，而是“围绕哪些对象，理解如何持续演化”。

2. **session 与 object 分层**
   session 保存本轮认知推进；object 保存长期稳定连续性。

3. **facts / inference / hypothesis / recommendation 分离**
   不把所有笔记压平到一个桶里。

4. **source 异构统一化**
   播客、B站、YouTube、官网、issue、用户反馈都归一到同一种知识对象模型。

5. **jury review 重于单人结论**
   多视角先独立初审，再交叉质询，再保留分歧，最后谨慎收束。

6. **writeback 是选择性的**
   只有 confirmed / reusable / stable / worth preserving 的内容才写回长期对象层。

7. **目标是稳定判断，不是信息丰富**
   系统必须强制回答：
   - 发生了什么
   - 哪一层变了
   - 为什么现在做
   - 解决什么张力
   - 用户真实买不买账

## 建议目录

```text
product-learning-library/
  README.md
  ontology/
    cognition-ontology.md
    product-intelligence-ontology.md
    jury-review-ontology.md
  agents/
    协作推进记录 agent.md
    collaboration-trace-synthesizer agent.md
    collaboration-trace-synthesizer output contract.md
    source-scout agent.md
    claim-extractor agent.md
    jury-synthesizer agent.md
  schemas/
    ontology-manifest.json
    claim-record.schema.json
    session-progress-record.schema.json
    product-record.schema.json
  templates/
    source-item.md
    product-record.md
    product-event-card.md
    claim-record.md
    method-card.md
    pattern-card.md
    jury-review-record.md
    session-progress-record.md
    writeback-proposal.md
    today-brief.md
    weekly-pattern-review.md
    monthly-thesis-update.md
  library/
    sources/
    events/
    products/
    claims/
    hypotheses/
    patterns/
    methods/
    reviews/
    sessions/
    questions/
    writebacks/
  seed/
    watchlist.md
    initial-questions.md
    first-tracking-theses.md
```

## 第一版推荐监控主线

### 主线 A｜AI coding / agent workflow
重点看：
- harness / orchestration / runtime / workspace
- reviewer / critic / steering / governance
- long-running tasks / subagent / parallel agents
- 插件、环境、token、Windows、model config 等真实摩擦

### 主线 B｜multi-agent collaboration / memory / workspace
重点看：
- persistent identity
- long-term memory
- object continuity
- workspace ownership
- role-based vs object-based collaboration
- writeback / approval / control boundary

### 主线 C｜assisted driving / trust framing / vehicle AI
重点看：
- 能力展示如何被产品化
- HMI / trust / safety communication
- 监管互动与 narrative
- 车内 AI companion 和 driving stack 的分层
- 用户的边界感、可解释性、信任断裂点

## 输出层级

### 日报｜Today Brief
只保留 3–5 个高信号变化：
- 发生了什么
- 为什么值得看
- 和我长期问题的关系

### 周报｜Weekly Pattern Review
不是列新闻，而是回答：
- 本周哪些公司在向同一层收敛
- 哪些是表层 feature，哪些是结构变化
- 用户抱怨集中在哪里

### 月报｜Monthly Thesis Update
更新你的长期判断：
- AI coding 的竞争中心正在往哪迁移
- multi-agent 的责任分配如何变化
- 辅助驾驶产品叙事中 trust framing 的位置如何变化
- 哪些旧判断被新证据推翻

---
