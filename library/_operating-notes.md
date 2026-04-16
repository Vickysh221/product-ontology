## 第一版实际运行建议

### 每天自动跑三件事
1. 拉源
2. 去重 + 打标签
3. 生成 Today Brief + Write-to-Library Candidates

### 每周人工做两件事
1. 审核候选 writeback
2. 更新 patterns / methods / theses（对应当前 library 结构）

### Writeback Chain

`Source -> Artifact -> Candidate -> Review/Verdict -> Writeback Intake -> Writeback`

- writeback generation always passes through intake
- the user may leave intake fields empty
- default report rules are applied when no extra guidance is provided

### 每月做一件事
- 更新长期 thesis，并显式标注哪些判断被强化、削弱或推翻

## 最小成功标准

这个系统不是为了让你“看更多”。
而是为了让你能更稳定地回答：
- 这个产品到底变了什么
- 这次变化属于哪一层
- 它背后的核心诉求是什么
- 用户现实是否支持官方叙事
- 哪些东西值得进入你的长期方法论

## 最后一句

不要把它做成抓新闻机器。
把它做成一个：

**证据先行、分歧保留、强制反诘、可持续 writeback 的产品学习系统。**

## Object Storage Rules

- `sources/` stores source containers and metadata.
- `artifacts/` stores evidence slices extracted from sources.
- `events/` stores durable change units.
- `claims/` stores affirmative interpretation records.
- `counterclaims/` stores opposing or limiting interpretation records.
- `patterns/` stores reviewed structural patterns and recurring observations.
- `theses/` stores reviewed long-horizon judgments and durable positions.
- `reviews/` stores critique traces and review notes.
- `verdicts/` stores final review outcomes and disposition records.
- `methods/` remains part of the current library model for process-level guidance.
