# Product Learning Library

面向 AI agent、AI coding、辅助驾驶等领域的一手产品学习库。

这不是一个新闻抓取器，也不是一个普通竞品分析库。它是一个基于 ontology 的 **Product Intelligence System**，用于持续吸收异构一手信号，并通过 session trace、jury review、selective writeback，形成稳定的产品判断系统。

## 为什么存在

常见的竞品调研库很容易退化成资料堆：
- 看过很多内容，但无法回答“产品到底变了什么”
- 能摘录信息，但无法区分事实、推断、假设与判断
- 能记录 source，却不能稳定写回长期对象层

这个仓库的目标不是“存更多信息”，而是更稳定地回答：
- 发生了什么
- 哪一层变了
- 为什么现在做
- 解决什么张力
- 用户是否真的买账

## 系统定义

这个库持续吸收来自以下来源的一手信号：
- 官网文档
- changelog / release notes
- engineering blog
- GitHub issues / discussions / releases
- 播客
- YouTube / Bilibili / livestream
- 用户评测视频 / 图文 / 社区反馈
- 监管 / 信任 / 市场信号

并把这些来源统一沉淀为：
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

## 仓库结构

```text
product-ontology/
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
    _operating-notes.md
  seed/
    watchlist.md
    initial-questions.md
    first-tracking-theses.md
  PRD Session Summary.md
```

各目录职责：
- `ontology/`：定义系统的对象、关系、认知推进与评审协议。
- `agents/`：定义不同研究与评审 agent 的职责边界与输出要求。
- `schemas/`：给结构化记录提供 JSON Schema。
- `templates/`：提供日常写作与写回模板。
- `library/`：长期累积的运行数据与对象层内容。
- `seed/`：第一轮 watchlist、问题和 thesis 种子。

## 快速开始

推荐第一次使用按这个顺序开始：

1. 先读 [`ontology/cognition-ontology.md`](./ontology/cognition-ontology.md) 和 [`ontology/product-intelligence-ontology.md`](./ontology/product-intelligence-ontology.md)，理解 object layer / session layer 的边界。
2. 再看 [`templates/source-item.md`](./templates/source-item.md)、[`templates/product-event-card.md`](./templates/product-event-card.md)、[`templates/session-progress-record.md`](./templates/session-progress-record.md)，掌握最小记录单元。
3. 用 [`seed/watchlist.md`](./seed/watchlist.md) 里的对象作为第一批跟踪对象。
4. 每次研究先写 `source item`、再提炼 `claim / hypothesis / question`，最后只把稳定结论写回 `library/` 对应对象层。
5. 参考 [`library/_operating-notes.md`](./library/_operating-notes.md) 建立每天、每周、每月的运行节奏。

如果你想先跑最小系统，可以从以下目录开始填充：
- `library/sources/`
- `library/events/`
- `library/products/`
- `library/questions/`
- `library/sessions/`

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
