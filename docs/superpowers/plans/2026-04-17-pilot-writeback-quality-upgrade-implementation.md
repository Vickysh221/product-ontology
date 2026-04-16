# Pilot Writeback Quality Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the single `integrated-team-paradigm` pilot so its review pack and final writeback read like a stronger research-oriented product analysis while staying reproducible from the generator.

**Architecture:** Keep the existing `research direction -> review pack -> writeback` chain, but replace the current source-by-source organization with three pilot-specific theme clusters. Improve the review pack first, then make the final writeback grow from those richer clusters into sharper problem statements, assumptions, and AI-native UX design propositions.

**Tech Stack:** Python 3, argparse, pathlib, regex parsing, pytest, existing Markdown records in `library/`, and current research-direction writeback generation code in `scripts/writeback_generate.py`

---

## File Structure

### Existing files to modify

- `scripts/writeback_generate.py`
  - Upgrade pilot-specific cluster mapping and final report rendering
- `tests/test_writeback_generate.py`
  - Add quality regressions for clustered literature review and stronger UX/design output
- `library/review-packs/podcasts/review-pack-agent-team-paradigm.md`
  - Regenerate upgraded review pack
- `library/writebacks/podcasts/matrix/integrated-team-paradigm.md`
  - Regenerate upgraded final writeback

### Scope lock

Do not modify:
- `scripts/writeback_intake.py`
- `tests/test_writeback_intake.py`
- any matrix-wide generation path
- any schema
- any other writeback or review-pack file

This implementation is only for the one pilot.

---

### Task 1: Add failing quality tests for clustered review-pack output

**Files:**
- Modify: `tests/test_writeback_generate.py`

- [ ] **Step 1: Write the failing test for three-cluster review-pack structure**

Add this test to `tests/test_writeback_generate.py`:

```python
def test_materialized_review_pack_uses_three_theme_clusters():
    text = Path("library/review-packs/podcasts/review-pack-agent-team-paradigm.md").read_text()
    assert "### 主题：执行控制层" in text
    assert "### 主题：协作与角色层" in text
    assert "### 主题：治理与前台 UX 外显层" in text
    assert text.count("### 主题：") == 3
```

- [ ] **Step 2: Write the failing test for multiple quotes per cluster**

Add this test to `tests/test_writeback_generate.py`:

```python
def test_materialized_review_pack_has_multiple_quotes_per_cluster():
    text = Path("library/review-packs/podcasts/review-pack-agent-team-paradigm.md").read_text()
    assert text.count("**Direct quote 1**") >= 3
    assert text.count("**Direct quote 2**") >= 3
```

- [ ] **Step 3: Run the targeted tests to confirm failure**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k "three_theme_clusters or multiple_quotes_per_cluster" -v
```

Expected:
- FAIL because the current pilot review pack is still source-oriented and does not have the three-cluster shape

- [ ] **Step 4: Commit**

```bash
git add tests/test_writeback_generate.py
git commit -m "test: add failing pilot review pack quality checks"
```

### Task 2: Upgrade the pilot review-pack generator to use three clusters

**Files:**
- Modify: `scripts/writeback_generate.py`
- Modify: `library/review-packs/podcasts/review-pack-agent-team-paradigm.md`
- Test: `tests/test_writeback_generate.py`

- [ ] **Step 1: Add a pilot-specific cluster map**

Add this mapping to `scripts/writeback_generate.py`:

```python
PILOT_REVIEW_CLUSTERS = [
    {
        "title": "执行控制层",
        "episode_slugs": [
            "podwise-ai-7758431-2cd3ef48",
            "podwise-ai-7368984-f9a0fefa",
        ],
    },
    {
        "title": "协作与角色层",
        "episode_slugs": [
            "podwise-ai-7504915-91b52a0e",
            "podwise-ai-7635732-bdfba3f3",
        ],
    },
    {
        "title": "治理与前台 UX 外显层",
        "episode_slugs": [
            "podwise-ai-7718625-7d0dc7d1",
            "podwise-ai-7635732-bdfba3f3",
            "podwise-ai-7368984-f9a0fefa",
        ],
    },
]
```

- [ ] **Step 2: Add pilot-specific quote selection**

Add this mapping to `scripts/writeback_generate.py`:

```python
PILOT_CLUSTER_QUOTES = {
    "执行控制层": [
        "[43:02] 写代码的本质不在于快速产出，而在于管理复杂度。随着项目规模增长，代码是否依然可控，才是软件工程的核心挑战。",
        "[01:04:46] 你不应该干活嘛，你应该给 AI 塑造一个良好的工作环境嘛。",
    ],
    "协作与角色层": [
        "[01:16:57] 我认为我这个人是一个一百人的公司。",
        "[18:56] 和你把一个人当一个员工时，你就直接这么去想，你发现他就完全不一样。",
    ],
    "治理与前台 UX 外显层": [
        "[11:38] 是不是我反而成为了未来人机协作最大的一个瓶颈。",
        "[18:56] 和你把一个人当一个员工时，你就直接这么去想，你发现他就完全不一样。",
    ],
}
```

- [ ] **Step 3: Rewrite the review-pack section builder for the pilot**

Update `build_review_pack_sections()` so that for the `integrated-team-paradigm` pilot it renders cluster-based sections:

```python
def build_pilot_cluster_review(
    cluster_title: str,
    research_direction: str,
    ux_points: list[str],
) -> str:
    quotes = PILOT_CLUSTER_QUOTES[cluster_title]
    ux_phrase = "、".join(ux_points[:3]) if ux_points else "责任、注意力仲裁与交接边界"
    return "\n".join(
        [
            f"### 主题：{cluster_title}",
            "",
            "**Direct quote 1**  ",
            quotes[0],
            "",
            "**Direct quote 2**  ",
            quotes[1],
            "",
            "**Paraphrase**  ",
            f"围绕“{research_direction}”这个问题，这组材料共同说明 {cluster_title} 已经不只是局部能力描述，而是在逼近 agent 协作结构、控制边界或前台责任分配的产品定义。",
            "",
            "**Evidence**  ",
            f"- 主题簇：{cluster_title}",
            "",
            "**Why it matters**  ",
            f"它之所以重要，是因为它把研究问题推进到 {ux_phrase} 这些真正会改变产品表面的结构层。",
        ]
    )
```

Then inside `build_review_pack_sections()` for this pilot:

```python
    ux_points = build_ai_native_ux_lens_pack()
    theme_lines = [
        build_pilot_cluster_review(cluster["title"], research_direction, ux_points)
        for cluster in PILOT_REVIEW_CLUSTERS
    ]
```

- [ ] **Step 4: Regenerate the pilot review pack**

Run:

```bash
python3 scripts/writeback_generate.py render-review-pack \
  --intake-file library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md \
  --synthesis-file library/syntheses/podcasts/agent-team-governability-2026-04.md \
  --output library/review-packs/podcasts/review-pack-agent-team-paradigm.md
```

- [ ] **Step 5: Run the targeted tests and make sure they pass**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k "three_theme_clusters or multiple_quotes_per_cluster or review_pack" -v
```

Expected:
- PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/writeback_generate.py tests/test_writeback_generate.py library/review-packs/podcasts/review-pack-agent-team-paradigm.md
git commit -m "feat: cluster pilot review pack by research themes"
```

### Task 3: Add failing quality tests for the final writeback

**Files:**
- Modify: `tests/test_writeback_generate.py`

- [ ] **Step 1: Write the failing test for clustered literature review in final writeback**

Add this test to `tests/test_writeback_generate.py`:

```python
def test_materialized_pilot_writeback_uses_three_review_clusters():
    text = Path("library/writebacks/podcasts/matrix/integrated-team-paradigm.md").read_text()
    assert "### 主题一：执行控制层" in text
    assert "### 主题二：协作与角色层" in text
    assert "### 主题三：治理与前台 UX 外显层" in text
```

- [ ] **Step 2: Write the failing test for explicit MVP design propositions**

Add this test to `tests/test_writeback_generate.py`:

```python
def test_materialized_pilot_writeback_ai_native_ux_has_design_objects():
    text = Path("library/writebacks/podcasts/matrix/integrated-team-paradigm.md").read_text()
    assert "责任状态卡" in text
    assert "分级决策卡" in text
    assert "异步沟通面板" in text
    assert "审计与证据抽屉" in text
```

- [ ] **Step 3: Run the targeted tests to confirm failure**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k "three_review_clusters or design_objects" -v
```

Expected:
- FAIL because the current pilot writeback does not yet render those stronger clustered sections and explicit MVP design objects

- [ ] **Step 4: Commit**

```bash
git add tests/test_writeback_generate.py
git commit -m "test: add failing pilot writeback quality checks"
```

### Task 4: Upgrade the final writeback rendering quality for the pilot

**Files:**
- Modify: `scripts/writeback_generate.py`
- Modify: `library/writebacks/podcasts/matrix/integrated-team-paradigm.md`
- Test: `tests/test_writeback_generate.py`

- [ ] **Step 1: Replace the final literature review with three clustered sections**

Update `render_longform_writeback()` so the `文献综述` section is built from the three pilot cluster titles and cluster-level content instead of reusing the current flatter pattern.

Add a helper:

```python
def build_pilot_writeback_clusters() -> str:
    return "\n\n".join(
        [
            "\n".join(
                [
                    "### 主题一：执行控制层",
                    "",
                    "代表引文 1： [43:02] 写代码的本质不在于快速产出，而在于管理复杂度。随着项目规模增长，代码是否依然可控，才是软件工程的核心挑战。",
                    "代表引文 2： [01:04:46] 你不应该干活嘛，你应该给 AI 塑造一个良好的工作环境嘛。",
                    "观察：这组材料说明 agent 的持续执行能力不是模型单点能力，而是 harness、测试、权限与环境设计共同塑造的执行控制层。",
                    "证据来源：`podwise-ai-7758431-2cd3ef48`, `podwise-ai-7368984-f9a0fefa`",
                    "为什么重要：如果这层控制结构不能被产品显式承接，所谓 multi-agent 协作最终只会退化成更贵的随机试错。",
                ]
            ),
            "\n".join(
                [
                    "### 主题二：协作与角色层",
                    "",
                    "代表引文 1： [01:16:57] 我认为我这个人是一个一百人的公司。",
                    "代表引文 2： [18:56] 和你把一个人当一个员工时，你就直接这么去想，你发现他就完全不一样。",
                    "观察：这里真正变化的不是 agent 数量，而是任务如何被分工、角色如何被理解、升级与等待如何进入协作结构。",
                    "证据来源：`podwise-ai-7504915-91b52a0e`, `podwise-ai-7635732-bdfba3f3`",
                    "为什么重要：这意味着产品对象开始从单体助手转向一个可被组织、分工和管理的协作网络。",
                ]
            ),
            "\n".join(
                [
                    "### 主题三：治理与前台 UX 外显层",
                    "",
                    "代表引文 1： [11:38] 是不是我反而成为了未来人机协作最大的一个瓶颈。",
                    "代表引文 2： [18:56] 和你把一个人当一个员工时，你就直接这么去想，你发现他就完全不一样。",
                    "观察：当前问题已经不只是 agent 能做什么，而是责任、权限、审计与前台可理解性如何一起进入产品表面。",
                    "证据来源：`podwise-ai-7718625-7d0dc7d1`, `podwise-ai-7635732-bdfba3f3`",
                    "为什么重要：当治理结构必须被用户看见、理解并在关键节点介入时，AI-native UX 就不再是附录，而是产品机制的一部分。",
                ]
            ),
        ]
    )
```

- [ ] **Step 2: Sharpen problem statement and assumptions**

Replace the current `Problem Statement` and `Assumptions` body in `render_longform_writeback()` with:

```python
problem_statement = (
    "真正的问题不是如何让 agent 再多做一点事，而是如何把 agent 组织成一个可治理的执行网络："
    "它既能持续推进工作，又不会把人重新拉回高频批准、盯梢和善后的位置；"
    "同时还要保留责任边界、升级路径和审计能力。"
)

assumptions_body = \"\"\"被材料支持的 assumptions
- agent 的持续执行上限取决于 harness，而不只是模型能力。
- 多 agent 的核心价值在于角色分工与治理结构，而不是并行数量本身。

仍需验证的 assumptions
- 这些控制层是否会成为默认产品结构，而不只是高成熟团队的局部最佳实践。
- 前台 UX 是否能把责任状态、升级节点和证据抽屉讲清，而不把用户重新压回流程管理负担。\"\"\"
```

- [ ] **Step 3: Replace the AI-native UX section with MVP design propositions**

Set the `AI-native UX 视角下的 MVP 设计命题` section body to:

```python
ux_body = \"\"\"这轮材料真正逼出来的不是一个“更好聊天”的界面，而是一个把责任、权限和升级时机前台化的协作界面。MVP 最值得先做的不是聊天框，而是四个对象：

1. 责任状态卡
告诉用户当前是谁在负责、系统是否仍在自主执行、什么时候需要人接管。

2. 分级决策卡
把高风险、可逆、默认推进三类决策显式区分，让升级不是一团模糊的“要不要问人”。

3. 异步沟通面板
把需要人类输入的问题沉淀成可被人和 agent 共读的协调面板，而不是让 agent 每一步都阻塞等待。

4. 审计与证据抽屉
默认前台不展示所有 log，但要允许用户按需下钻：为什么这样做、基于哪条证据、哪一步触发了升级或回滚。\"\"\"
```

- [ ] **Step 4: Regenerate the pilot final writeback**

Run:

```bash
python3 scripts/writeback_generate.py render-longform \
  --writeback-id writeback-integrated-team-paradigm \
  --intake-file library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md \
  --synthesis-file library/syntheses/podcasts/agent-team-governability-2026-04.md \
  --output library/writebacks/podcasts/matrix/integrated-team-paradigm.md \
  --title "从单 Agent 工具到可治理的 Agent Team：五条一线语料中的编排、协作与企业化信号" \
  --subtitle "给团队看的 integrated 版：Multi-Agent 是否已进入范式迁移期"
```

- [ ] **Step 5: Run the targeted tests and make sure they pass**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k "three_review_clusters or design_objects or materialized_pilot_writeback or review_pack" -v
```

Expected:
- PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/writeback_generate.py tests/test_writeback_generate.py library/review-packs/podcasts/review-pack-agent-team-paradigm.md library/writebacks/podcasts/matrix/integrated-team-paradigm.md
git commit -m "feat: upgrade pilot writeback analytical quality"
```

### Task 5: Final verification for the single-pilot quality upgrade

**Files:**
- Modify: `docs/superpowers/plans/2026-04-17-pilot-writeback-quality-upgrade-implementation.md`

- [ ] **Step 1: Run the full relevant test set**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_generate.py tests/test_writeback_matrix.py -v
```

Expected:
- PASS

- [ ] **Step 2: Smoke-check the upgraded pilot outputs**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
review = Path("library/review-packs/podcasts/review-pack-agent-team-paradigm.md").read_text()
writeback = Path("library/writebacks/podcasts/matrix/integrated-team-paradigm.md").read_text()
checks = {
    "review_has_3_clusters": review.count("### 主题：") == 3,
    "review_has_multi_quotes": review.count("**Direct quote 2**") >= 3,
    "writeback_has_3_clusters": "### 主题一：执行控制层" in writeback and "### 主题二：协作与角色层" in writeback and "### 主题三：治理与前台 UX 外显层" in writeback,
    "writeback_has_design_objects": all(
        needle in writeback
        for needle in ["责任状态卡", "分级决策卡", "异步沟通面板", "审计与证据抽屉"]
    ),
}
for name, passed in checks.items():
    print(f"{name}={'PASS' if passed else 'FAIL'}")
PY
```

Expected:
- all checks print `PASS`

- [ ] **Step 3: Add implementation notes to this plan**

Append:

```md
## Implementation Notes

- this pass intentionally improves only the `integrated-team-paradigm` pilot
- the review pack is now clustered by three research themes rather than one source per section
- the final writeback now carries explicit MVP design propositions in the AI-native UX section
- matrix-wide rollout remains a future follow-up once this pilot quality bar is accepted
```

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/plans/2026-04-17-pilot-writeback-quality-upgrade-implementation.md
git commit -m "docs: record pilot writeback quality upgrade verification"
```

## Self-Review

Spec coverage check:
- three theme clusters: Tasks 1, 2, and 4
- multiple quotes per cluster: Tasks 1 and 2
- stronger problem statement and assumptions: Task 4
- AI-native UX as MVP design propositions: Task 4
- single-pilot-only scope: file structure and all tasks

Placeholder scan:
- no `TODO`, `TBD`, or unspecified implementation placeholders remain
- all code-changing steps include concrete code blocks or exact command outputs
- all verification steps include exact commands

Type consistency:
- cluster titles are consistent between tests and implementation
- the pilot file paths are consistent across all tasks
- the final writeback section names are consistent with the spec
