# Research Review Pack

## Research Question

multi-agent 是否已经从高级 workflow 包装，进入可治理的 Agent Team 范式迁移

问题来源：用户给定

## Review Introduction

本轮先按主题聚类做综述，不按播客顺序复述，也不先给最终判断。 当前可补充的 AI-native UX 观察维度包括：责任, 注意力仲裁, handoff, user goal loop, agent behavior contract, rollback。

## Thematic Literature Review

### 主题：执行控制层

这一组材料先把控制层讲清楚：代码审核、自动化测试和权限边界不是附属工具，而是 agent 能否稳定执行的前提。

**Direct quote**  
[43:02] 写代码的本质不在于快速产出，而在于管理复杂度。随着项目规模增长，代码是否依然可控，才是软件工程的核心挑战。

**Direct quote**  
[11:28] - 徐文浩: 自动化的测试，第二个，你所有的提交都会触发 AI 给你做代码审核，

**Paraphrase**  
执行控制层的关键不是让 agent 更快做事，而是先把每一步动作都放进可测试、可审核、可回退的执行框架里。

**Evidence**  
- `podwise-ai-7758431-2cd3ef48`
- `podwise-ai-7368984-f9a0fefa`

**Why it matters**  
这说明 multi-agent 的关键约束不是模型本身，而是 harness、测试和审核是否已经变成默认产品能力。

### 主题：协作与角色层

这一组材料讨论的是人和 agent 如何分工：谁来提问、谁来调度、谁来承担协作中的角色边界。

**Direct quote**  
[11:38] - 李可佳: 是不是我反而成为了未来人机协作最大的一个瓶颈。

**Direct quote**  
[18:56] - 覃睿: 和你把一个人当一个员工时，你就直接这么去想，你发现他就完全不一样。

**Paraphrase**  
协作与角色层讲的是：一旦任务被交给 agent，人就不再只是使用者，而会变成提示、约束、审核和分工的一部分。

**Evidence**  
- `podwise-ai-7718625-7d0dc7d1`
- `podwise-ai-7635732-bdfba3f3`

**Why it matters**  
这条线索把“更聪明的工具”推进成“可协作的团队结构”，也解释了为什么角色定义会先于功能堆叠变成核心问题。

### 主题：治理与前台 UX 外显层

这一组材料把治理从后台规则推到前台体验：工作环境、权限和组织方式开始被显式地描述出来。

**Direct quote**  
[01:16:57] - 任鑫: 我认为我这个人是一个一百人的公司。

**Direct quote**  
[01:04:46] - 徐文浩: 你不应该干活嘛，你应该给 AI 塑造一个良好的工作环境嘛。

**Paraphrase**  
治理与前台 UX 外显层的重点，是把权限、环境和组织结构做成用户可感知的产品体验，而不是只放在后台约束里。

**Evidence**  
- `podwise-ai-7504915-91b52a0e`
- `podwise-ai-7368984-f9a0fefa`

**Why it matters**  
当治理被前台化，用户看到的就不只是一个会做事的 agent，而是一个可以被组织、被约束、也能被持续协作的工作环境。

## Counter-Signals And Tensions

- `harness engineering` 到底是工程方法，还是已经进入产品主能力层。
- `multi-agent` 到底是稳定范式迁移，还是当前阶段的高级 workflow 包装。
- 企业级多人多agent管理里的治理结构，哪些是安全/合规必要，哪些是效率放大器。

## Draft Problem Statement

这里先提出一个 draft problem statement：如何把 agent 从偶发可用工具，变成可长期协作、可分工、可升级人工、可追责的执行网络？

## Draft Assumptions

### 被材料支持的 assumptions
1. 自主执行能力的上限取决于 harness，而不只是模型本身。

### 仍需验证的 assumptions
1. 这些控制层是否会成为默认产品结构，而不只是高成熟团队的最佳实践。
