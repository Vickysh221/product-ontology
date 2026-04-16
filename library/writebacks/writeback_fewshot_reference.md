# 合格 writeback / report generation few-shot（系统参考版）

这份 few-shot 不是为了示范“文风”，而是为了把系统拉向以下行为：

1. **先保留主讲人的原始洞见，再做综合判断**  
2. **用“文献综述”而不是“媒体稿”来组织材料**  
3. **每个主题都同时给出 direct quote + paraphrase + evidence**  
4. **综述之后必须显式产出 problem statement 和 assumptions**  
5. **每一轮都要收束到一个 research direction**  
6. **如果 research direction 不是用户给的，就必须标记为“待用户批准”**  
7. **AI-native UX 不是附会的评论段，而是 MVP 设计的核心观察框架**  
8. **保留分歧，不把 tension 抹平**

---

## 全局输出约束（建议系统长期遵守）

### 输出骨架
1. 综述导言：本轮只回答一个问题  
2. 文献综述：按主题聚类，而不是按播客顺序复述  
3. 综合判断：只能从前面综述中长出来  
4. Problem statement：是产品/设计/研究要解决的真问题  
5. Assumptions：区分“材料支持”与“暂时假设”  
6. AI-native UX 视角：把设计原则拉进主分析，不要放在附录  
7. Research direction：给出本轮应该继续往哪里挖  
8. 保留分歧：哪些还不能下结论

### 证据写法
每个主题至少包含：
- **Direct quote**：尽量短，保留主讲人原话力度
- **Paraphrase**：翻译成机制判断，不要只是同义改写
- **Evidence**：列明来自哪段材料 / 哪个主题
- **Why it matters**：这条证据为什么值得进入综合判断

### 明确禁止
- 纯 prose 连续抒情，不挂证据
- 只做二手总结，不保留主讲人措辞
- 一上来就下结论，不先做综述
- 把 UX 写成“应该更好用”的空话
- 把 system-generated direction 写成既成事实
- 把所有 tension 都压成一个正确答案

---

# Few-shot 1｜integrated / team / user-provided direction

## Example Input

```yaml
collaboration_mode: integrated
target_audience: team
research_direction: multi-agent 是否已经从高级 workflow 包装，进入可治理的 Agent Team 范式迁移
user_guidance:
  - 保留主讲人原话的力度
  - 采用文献综述
  - 每个主题都要 direct quote + paraphrase + evidence
  - 综述后列出 problem statement 和 assumptions
  - 用 AI-native UX 视角讨论 MVP
evidence_pool:
  - 播客A：Team of Agents / OpenClaw 发行版 / 普通人可用
  - 播客B：企业版 OpenClaw / 权限 / 协作 / 审计
  - 播客C：异步沟通文档 / 红黄绿决策 / AI 审核 AI
  - 播客D：dangerously skip permissions / 沙箱 / 审批 / 自动化测试
ux_refs:
  - “你设计的对象，不再是 page flow，而是 user goal loop + agent behavior contract”
  - “前台不是流程展示层，而是与人当前权责对齐的注意力仲裁层”
```

## Ideal Output

# 从单 Agent 到 Agent Team：这次变化到底是包装，还是范式迁移

## 综述导言

本轮只回答一个问题：**multi-agent 到底只是把 workflow 做得更复杂了，还是产品形态已经开始从单体助手转向可治理的 Agent Team。**

下面不直接给判断，先把材料按三个主题做综述：  
一是 **执行控制层**；  
二是 **协作与角色层**；  
三是 **企业治理与 UX 外显层**。

---

## 文献综述

### 主题一：执行控制层已经不再是“让 agent 多干活”，而是“让 agent 在围栏内持续工作”

**Direct quote 1**  
“我一般开 Claude Code 的都是用那个 skip dangerous permission……我虽然是这样做，但其实我是在这个之上做了一些限制……第一个呢，我是开一个 dev container……它相当于一个开发的沙箱环境。”  

**Paraphrase**  
这里的重点不是“完全放权”，而是**高自主 + 强围栏**。权限放开只是为了不被频繁打断；真正关键的是沙箱、分支、审批、测试和 code review 共同构成了 harness。  

**Evidence**  
- 播客D：skip dangerous permission + dev container + 分支开发  
- 播客D：自动化测试、AI review、人工只看 plan / commit / final review  

**Why it matters**  
如果没有这层 harness，所谓“几个小时自己干活”并不成立；它会迅速退化为高 token 消耗的随机试错。也就是说，**可持续自主执行不是模型单点能力，而是控制层设计的结果。**

---

### 主题二：协作的最小单元已经不再是“一个人对一个 agent”，而是“任务、角色、审批、异步文档”组成的协作网

**Direct quote 2**  
“这个 email 就是你读我也读……非得落我做决策的，你把它放在异步沟通文档，然后你可以跳过这一步，把其他的都做完。”  

**Direct quote 3**  
“红灯的决策是涉及到钱，或者会改我的非常底层的东西……黄灯的决策是可逆操作……绿灯说材料都已经准备好了，流水线逐步推进就好了。”  

**Paraphrase**  
这里已经不是一个聊天助手等待用户逐轮确认，而是形成了**异步协作协议**：  
- 可自己决策的继续推进  
- 必须升级人的放到异步文件  
- 决策不是二元 approval，而是分级治理  

**Evidence**  
- 播客C：异步文档作为人机双读媒介  
- 播客C：红黄绿决策，把风险、可逆性、资源影响显式分级  
- 播客C：AI 审核 AI、sub-agent 复查结果  

**Why it matters**  
这说明“协作”不再只是 agent 多了，而是**角色边界、升级路径和等待机制被制度化**。这已经比“多开几个 subagent”更接近组织形态。

---

### 主题三：产品形态开始显式承接治理、迁移与 ownership，而不是只承接功能调用

**Direct quote 4**  
“今天的 Claw 不应该是只有一个 Agent，而是有很多个 Agent……它还是更适合在不同的领域你有一个 Agent……所以它是一个 Team of Agents。”  

**Direct quote 5**  
“我们不是要做一个自己的新的操作系统，我们就想做好一个 Open Cloud 的发行版。”  

**Direct quote 6**  
“我是面向 Teams 的 OpenClaw。”  

**Paraphrase**  
这一组材料共同指向两层变化：  
第一，产品对象从单助手变成 team-of-agents；  
第二，产品边界从“功能集合”移动到“发行版 / 协作底座 / 企业接入层”。  

**Evidence**  
- 播客A：Team of Agents 明确被定义为现实约束下的必要形态  
- 播客A：OpenClaw 发行版比喻，强调迁移性、开放架构、ownership  
- 播客B：面向 Teams 的 OpenClaw，强调企业协作、权限、安全、审计  

**Why it matters**  
如果产品真正开始承接“谁能看、谁能做、谁来批、如何迁移、如何追责”，那它就不再是 feature set 的扩展，而是**控制边界与责任边界的再设计**。

---

## 综合判断

基于上述综述，我倾向于给出一个**有保留的支持性判断**：

> multi-agent 在这组材料里，已经不只是高级 workflow 包装；  
> 它开始表现为一种 **可治理的 Agent Team 产品形态**。  

但这个判断必须保留一个前提：  
**成立的不是“agent 数量增加”，而是 harness、异步协作协议、权限与审批、角色分工、企业治理这些控制层开始被产品显式承接。**

换句话说，范式迁移不是发生在“更多 agent”，而是发生在**控制结构 becoming product surface**。

---

## Problem statement

如何把 agent 从“偶尔有神迹的单体助手”，变成**可长期协作、可分工、可升级人工、可追责、可迁移**的执行网络，同时不把人重新拉回高频盯梢和逐步批准的旧工作方式？

---

## Assumptions

### 被材料较强支持的 assumptions
1. **自主执行能力的上限取决于 harness，而不是只取决于模型。**
2. **多 agent 真正增加的价值，在于角色分工与治理结构，而不是并行数量本身。**
3. **企业场景会强迫产品把权限、审计、审批、协作边界显式化。**

### 仍需继续验证的 assumptions
1. 这些控制层是否会成为默认产品结构，而不只是高成熟团队的最佳实践。  
2. 普通用户是否真的愿意管理一组 agent，而不是最终只使用预封装结果。  
3. “Team of Agents” 是否会在 UX 层形成可理解的前台，而不是只在后端存在。

---

## AI-native UX 视角下的 MVP 设计命题

这里不把 UX 当成“最后补一个界面”，而是把它当成**责任分配的外显机制**。

参考原则不是 page flow，而是 **user goal loop + agent behavior contract**。  
MVP 最先要设计的不是聊天框，而是下面四个对象：

1. **责任状态卡**  
   告诉用户：现在是谁在负责，系统是否仍在自主执行，什么时候需要你接管。  

2. **分级决策卡**  
   把红灯 / 黄灯 / 绿灯决策显式化。  
   红灯必须打断，黄灯留痕且允许 review，绿灯默认执行。  

3. **异步沟通面板**  
   人和 agent 都能读；  
   agent 不因为等待人而阻塞整条流水线；  
   需要人决策的问题被收敛成有限的 decision card。  

4. **审计与证据抽屉**  
   默认前台不展示全量 log，  
   但要支持用户向下展开看到：为什么这样做、基于什么证据、哪条记忆在影响决策。  

---

## 本轮 research direction

**已批准方向，下一轮继续深挖：**  
多 agent 的“范式迁移”到底发生在什么层：  
是 agent 数量层、角色结构层、治理结构层，还是前台 UX 的责任分配层？

---

## 保留分歧

1. harness engineering 到底还是工程方法，还是已经进入产品主能力层。  
2. Team of Agents 到底是稳定结构，还是当前模型限制下的过渡编排。  
3. 企业治理结构里，哪些是安全/合规必要，哪些只是高吞吐团队的效率放大器。

---

# Few-shot 2｜sectioned / research_archive / user-provided direction

## Example Input

```yaml
collaboration_mode: sectioned
target_audience: research_archive
research_direction: harness engineering 到底是工程控制层，还是已经进入产品能力定义
user_guidance:
  - 更强调证据分层
  - 允许更密的引用
  - 不要写成媒体稿
  - 要把反例和反驳放进正文
evidence_pool:
  - 播客D：沙箱 / 分支 / 自动化测试 / AI review
  - 播客C：异步文档 / 红黄绿决策 / 自验证
  - UX参考：failure / rollback / handoff / governance
```

## Ideal Output

# 研究问题

**harness engineering 到底还是工程控制层，还是已经开始成为产品能力定义的一部分？**

---

## Section 1｜原始材料综述

### 1.1 来自开发实践的证据

**Direct quote**  
“你是会选择那个 dangerously skip all permission……但是这上面你包了两层，第一层是你做了一个沙箱……第二层……还有一个审批……还有两层……自己做 code review……写 use case……有测试集。”  

**Paraphrase**  
这不是单纯的“工程谨慎”，而是一个完整的**执行控制栈**：  
授权放开只是表层；真正起作用的是沙箱、审批、review、测试和版本隔离。  

**Evidence**  
- 播客D：dangerously skip all permission  
- 播客D：dev container / branch / approval / code review / use case / tests  

---

### 1.2 来自 AI 工作流实践的证据

**Direct quote**  
“他自己检查……内容是否完整，CSS 看起来正确，然后自己再验证，各种验证。”  

**Direct quote**  
“黄灯的决策是可逆操作……红灯的决策是涉及到钱或者会改我的非常底层的东西。”  

**Paraphrase**  
在内容型任务里，harness 不再表现为传统 CI/CD，而表现为**验收标准、风险分级、回退条件、审批升级**。  
也就是说，harness 的外观会变，但本质仍是控制 agent 在哪里可以继续，哪里必须停下。  

**Evidence**  
- 播客C：AI 自检、自验证  
- 播客C：红黄绿决策  
- 播客C：异步沟通文档不阻塞流水线  

---

### 1.3 来自 UX / 设计方法论的证据

**Direct quote**  
“你设计的对象，不再是 page flow，而是 user goal loop + agent behavior contract。”  

**Direct quote**  
“权限、审批、可逆性、日志、合规、风险分级，不是上线前补的 check，而是交互骨架的一部分。”  

**Paraphrase**  
如果 agent UX 的设计对象已经变成 behavior contract，那么 harness 就不能只被理解为工程实现；  
它已经进入了**交互骨架、控制逻辑与责任外显机制**。  

**Evidence**  
- UX 方法文档：behavior contract  
- UX 方法文档：安全、隐私与治理是交互骨架的一部分  
- UX 方法文档：failure / fallback / rollback / handoff 必须前置设计  

---

## Section 2｜机制判断

### 2.1 为什么它不只是工程控制层

因为它已经决定了用户最终能感知到什么：
- 用户会不会被频繁打断  
- 哪些动作会被升级成需要批准  
- agent 是否可以长程执行  
- 出错后是回滚、重试，还是交还给人  

只要这些点直接影响体验，harness 就已经越过了纯后端边界。

### 2.2 为什么它又不能被简单等同为产品能力

因为用户不会直接为“有 dev container”付费，  
用户感知到的是：
- 更少的打断  
- 更稳的执行  
- 更清楚的边界  
- 更容易验收的结果  

所以更准确的说法不是“harness = 产品功能”，  
而是：

> harness 是一种 **产品能力的生成条件**；  
> 当它被前台化为审批、决策分级、验收、回退、审计时，  
> 它才部分转化为产品能力。

---

## Section 3｜Problem statement

如何把原本只属于工程团队内部的控制层，转化成用户和组织都能感知、理解并受益的**可治理执行能力**，同时避免把前台变成吵闹的流程展示器？

---

## Section 4｜Assumptions

### Strongly supported
1. 不加 harness，agent 的长程自主执行会迅速失控。  
2. harness 的核心价值不只是“让 agent 能做更多”，也包括“限制 agent 能做什么”。  
3. 在 agent 场景里，权限、可逆性、审批、日志、失败恢复已经直接影响 UX。

### To be validated
1. 普通用户是否真的能理解这些控制层，而不是只想得到结果。  
2. 前台化多少控制信息才是合适的，过多是否会重新制造复杂度。  
3. 不同场景下 harness 的最佳粒度是否会完全不同。

---

## Section 5｜AI-native UX 设计含义

如果本轮问题是 harness，MVP 不该先画漂亮界面，而该先定义四件事：

1. **action classes**：哪些动作低风险可自动，哪些必须审批  
2. **receipt levels**：执行后留痕、提醒、请求决策、立即接管的层级  
3. **handoff protocol**：失败几次、什么置信度下升级人工  
4. **audit surface**：默认简洁，展开后可追到证据、记忆、风险判断  

---

## Section 6｜Counterargument

一种反对意见是：  
这些东西本来就是工程里的 CI/CD 和风险控制，只是换了个 agent 名字。

### Response
这个反对不该被抹掉。  
但它忽略了一点：  
在 agent 产品里，CI/CD 不再只保护代码库，它直接塑造**用户和 agent 的互动节奏**。  
一旦它影响“什么时候问人、什么时候打断、什么时候执行、什么时候回滚”，它就已经进入产品定义。

---

## Section 7｜本轮 research direction

**已批准方向，下一轮继续：**  
如何把 harness 从“工程可控性”翻译为“用户可感知的治理界面”？

---

# Few-shot 3｜appendix / exec / system-proposed direction（pending approval）

## Example Input

```yaml
collaboration_mode: appendix
target_audience: exec
research_direction: null
system_task:
  - 从多条材料中生成一个值得继续深挖的方向
  - 方向必须和 AI-native UX MVP 相关
  - 必须显式标记“待用户批准”
evidence_pool:
  - 播客C：异步文档、红黄绿决策、AI 审核 AI
  - UX原则：attention arbiter / decision card / evidence-back / safety retreat
  - UX能力文档：behavior contract / failure-recovery / governance
```

## Ideal Output

# 主结论（给决策者）

当前更值得继续投入的，不是“再做一个更强的 agent”，而是回答一个更具体的问题：

> **在 human-agent 协作里，前台到底应该展示什么，才能让人真正接得住 agent 的自主执行？**

这不是一个界面优化问题，而是一个**责任分配问题**。

---

## 结论依据（短版）

### 依据 1：实践材料已经出现了“分级决策 + 异步升级”的雏形
- 余一把决策拆成红灯 / 黄灯 / 绿灯；红灯涉及钱和底层改动，黄灯是可逆操作，绿灯允许流水线继续推进。  
- 这说明前台真正要承接的，不是全量过程，而是**责任时刻**。

### 依据 2：UX 原则已经给出了更成熟的表述
- “前台不是流程展示层，而是与人当前权责对齐的注意力仲裁层。”
- “A good decision card should answer only five questions: what has been done / what is missing / recommendation / consequence differences / by when decide.”

### 依据 3：设计对象已经变化
- “你设计的对象，不再是 page flow，而是 user goal loop + agent behavior contract。”
- 这意味着 agent 前台不是把 log 翻译成 UI，而是把 contract 翻译成**可接管、可拒绝、可追溯**的责任界面。

---

## Appendix A｜文献综述（证据展开）

### A1. 协作实践里的前台雏形

**Direct quote**  
“非得落我做决策的，你把它放在异步沟通文档，然后你可以跳过这一步，把其他的都做完。”  

**Paraphrase**  
这里的前台不是聊天记录，而是一个**不阻塞流水线的决策容器**。  
它只承接必须由人拥有的判断，其余执行留给系统。

---

### A2. 注意力仲裁原则

**Direct quote**  
“前台不是流程展示层，而是与人当前权责对齐的注意力仲裁层。”  

**Direct quote**  
“Urgent moments are not where the system should display personality or sophistication.”  

**Paraphrase**  
一个合格的 AI-native 前台，不追求“我把系统都展示给你看”，  
而追求：  
- 现在谁负责  
- 是否需要你介入  
- 为什么这次必须介入  
- 不介入会有什么后果  

---

### A3. 决策卡，而不是日志流

**Direct quote**  
“A good decision card should answer only five questions...”  

**Paraphrase**  
这说明前台对象应该从“日志 / transcript / task list”切到**decision card**。  
也就是：  
默认只露出 recommendation、responsibility state、action required；  
证据、记忆、置信度、审计细节放到可展开层。

---

## Appendix B｜Problem statement

当 agent 具备持续执行能力后，组织面临的核心问题不再是“它会不会做”，而是：

**人什么时候该被拉进来、以什么形式被拉进来、系统应该给人什么最小但足够的责任信息。**

---

## Appendix C｜Assumptions

1. 多数高频协作失败并不是因为 agent 什么都不会，而是因为人接不住它的自主性。  
2. 前台如果展示全量流程，会重新制造复杂度与注意力噪音。  
3. 决策分级、升级路径、证据展开层、记忆治理，会比“更会聊天”更快成为 MVP 价值源。  

---

## Appendix D｜建议的下一轮研究方向（待用户批准）

### Proposed research direction
**“AI-native UX 的 MVP 应优先设计 decision card、responsibility state 和 evidence-back，而不是 chat-first frontstage。”**

### Why this direction now
因为这条方向能把三类材料接起来：
- 一线实践中的红黄绿决策  
- UX 方法论中的 attention arbiter / decision card  
- 你的产品分析目标里的 problem statement / assumptions / governance

### What to test next
1. 哪些信息必须前台化，哪些应留在 audit layer  
2. 什么情况下需要红灯打断，什么情况下只留痕  
3. memory writeback 何时应该进入前台，何时必须后置  
4. chat-first 与 decision-card-first 的 adoption 差异

### Approval status
**待用户批准。**  
如果用户批准，这将成为下一轮报告唯一主线；  
如果用户不批准，系统应重新提出一个更贴近用户目标的方向，而不是默认继续扩写。

---

# 附：系统可直接抽取的最小风格规则

1. **一轮只回答一个 research question。**  
2. **至少保留 3 条 direct quotes。**  
3. **每个主题都要有 paraphrase，不允许 quote 堆砌。**  
4. **evidence 必须显式列出。**  
5. **problem statement 与 assumptions 是必选，不是可选。**  
6. **AI-native UX 必须进入正文，而不是“如果有的话补一段”。**  
7. **user-provided direction 直接推进；system-proposed direction 必须待批。**  
8. **保留 tension：support 也可以同时保留 weaken / needs more evidence。**  
9. **对 exec 写法：正文短、附录重证据。**  
10. **对 research_archive 写法：正文允许更密的证据与反驳。**

---

# 建议你接下来补进系统提示词的一句总纲

> 先把材料写成“带引文的综述”，再从综述长出判断；  
> 不要一上来替用户总结世界，而要先把说话的人说了什么、为什么值得信、哪些还不能信，整理清楚。
