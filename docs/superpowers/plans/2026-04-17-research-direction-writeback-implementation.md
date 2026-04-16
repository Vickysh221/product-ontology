# Research-Direction Writeback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current pilot longform writeback flow with a research-direction-first pipeline that produces one `Research Review Pack` and one final research-grade writeback.

**Architecture:** Keep the scope to one approved research direction and one pilot output. Add a new intermediate `review pack` artifact between evidence and final writeback, then update generation so the final writeback is rendered from that pack rather than jumping directly from synthesis into prose. Use AI-native UX as the only MVP interpretive lens and explicitly distinguish user-approved directions from system-suggested ones.

**Tech Stack:** Python 3, argparse, pathlib, regex parsing, pytest, existing Markdown records in `library/`, `templates/`, `seed/`, and external UX reference files under `/Users/vickyshou/.openclaw/workspace/shared/Principles`

---

## File Structure

### Existing files to modify

- `scripts/writeback_generate.py`
  - Add research-direction-first generation path
  - Generate `Research Review Pack`
  - Render final writeback from the review pack
- `scripts/writeback_intake.py`
  - Extend intake structure to record `research_direction` and `direction_status`
- `tests/test_writeback_generate.py`
  - Add review-pack and research-grade writeback tests
- `tests/test_writeback_intake.py`
  - Add intake coverage for research direction metadata
- `README.md`
  - Document the review-pack and final writeback commands

### Existing content files to read from

- `library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md`
  - Current pilot intake, to be upgraded or superseded with research-direction fields
- `library/syntheses/podcasts/agent-team-governability-2026-04.md`
  - Shared evidence synthesis for the pilot evidence pool
- `library/writebacks/writeback_fewshot_reference.md`
  - Behavioral target for review-pack and final writeback shape
- `library/artifacts/podcasts/podwise-ai-7758431-2cd3ef48/summary.md`
- `library/artifacts/podcasts/podwise-ai-7758431-2cd3ef48/highlights.md`
- `library/artifacts/podcasts/podwise-ai-7718625-7d0dc7d1/summary.md`
- `library/artifacts/podcasts/podwise-ai-7718625-7d0dc7d1/highlights.md`
- `library/artifacts/podcasts/podwise-ai-7635732-bdfba3f3/summary.md`
- `library/artifacts/podcasts/podwise-ai-7635732-bdfba3f3/highlights.md`
- `library/artifacts/podcasts/podwise-ai-7504915-91b52a0e/summary.md`
- `library/artifacts/podcasts/podwise-ai-7504915-91b52a0e/highlights.md`
- `library/artifacts/podcasts/podwise-ai-7368984-f9a0fefa/summary.md`
- `library/artifacts/podcasts/podwise-ai-7368984-f9a0fefa/highlights.md`

### External reference files to distill into an MVP AI-native UX lens pack

- `/Users/vickyshou/.openclaw/workspace/shared/Principles/UX for human、UX of agent、以及 UX of collaboration.md`
- `/Users/vickyshou/.openclaw/workspace/shared/Principles/UX_PRINCIPLES_ATTENTION_ARBITRATION.md`
- `/Users/vickyshou/.openclaw/workspace/shared/Principles/一个合格的 AI native agentic UX designer 要具备的核心能力.md`
- `/Users/vickyshou/.openclaw/workspace/shared/Principles/当今 agent 在人机交互中的主要探索.md`
- selected Context Engineering references only if they directly shape the UX lens pack

### New files to create

- `library/review-packs/podcasts/review-pack-agent-team-paradigm.md`
  - Structured review object for the pilot research direction

### Existing outputs to regenerate

- `library/writebacks/podcasts/matrix/integrated-team-paradigm.md`
  - Replace current longform pilot with research-direction-based writeback

### Scope lock

Do not expand to 12 matrix outputs in this plan.
This implementation produces:
- one upgraded intake
- one review pack
- one final writeback

---

### Task 1: Extend intake to record research direction approval state

**Files:**
- Modify: `scripts/writeback_intake.py`
- Modify: `tests/test_writeback_intake.py`

- [ ] **Step 1: Write the failing intake test for research direction metadata**

Add this test to `tests/test_writeback_intake.py`:

```python
def test_writeback_intake_cli_records_research_direction_and_status(tmp_path):
    target = tmp_path / "intake.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_intake.py",
            "create",
            "--intake-id",
            "intake-research-demo",
            "--output",
            str(target),
            "--collaboration-mode",
            "integrated",
            "--target-audience",
            "team",
            "--research-direction",
            "multi-agent 是否已经从高级 workflow 包装进入可治理的 Agent Team 范式迁移",
            "--direction-status",
            "user_provided",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- research_direction: `multi-agent 是否已经从高级 workflow 包装进入可治理的 Agent Team 范式迁移`" in text
    assert "- direction_status: `user_provided`" in text
```

- [ ] **Step 2: Run the targeted intake test and confirm it fails**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_intake.py -k research_direction -v
```

Expected:
- FAIL because the CLI does not yet accept `--research-direction` / `--direction-status`

- [ ] **Step 3: Add the minimal intake implementation**

Update `scripts/writeback_intake.py`:

```python
    create.add_argument("--research-direction")
    create.add_argument(
        "--direction-status",
        choices=["user_provided", "system_suggested_pending", "system_suggested_approved"],
    )
```

And add these lines inside `build_markdown(args)` after `target_audience`:

```python
    research_direction = normalize_text(args.research_direction)
    direction_status = normalize_text(args.direction_status)
```

And add these output lines:

```python
- research_direction: `{research_direction}`
- direction_status: `{direction_status}`
```

- [ ] **Step 4: Run the targeted intake test and confirm it passes**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_intake.py -k research_direction -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/writeback_intake.py tests/test_writeback_intake.py
git commit -m "feat: record research direction in writeback intake"
```

### Task 2: Add review-pack generation tests

**Files:**
- Modify: `tests/test_writeback_generate.py`
- Read: `library/writebacks/writeback_fewshot_reference.md`

- [ ] **Step 1: Write the failing test for review-pack structure**

Add this test to `tests/test_writeback_generate.py`:

```python
def test_writeback_generate_render_review_pack_creates_research_sections(tmp_path):
    target = tmp_path / "review-pack.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_generate.py",
            "render-review-pack",
            "--intake-file",
            "library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md",
            "--synthesis-file",
            "library/syntheses/podcasts/agent-team-governability-2026-04.md",
            "--output",
            str(target),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "## Research Question" in text
    assert "## Review Introduction" in text
    assert "## Thematic Literature Review" in text
    assert "## Counter-Signals And Tensions" in text
    assert "## Draft Problem Statement" in text
    assert "## Draft Assumptions" in text
```

- [ ] **Step 2: Write the failing test for quote-preserving review-pack content**

Add this test to `tests/test_writeback_generate.py`:

```python
def test_review_pack_preserves_quote_paraphrase_evidence_shape(tmp_path):
    target = tmp_path / "review-pack.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_generate.py",
            "render-review-pack",
            "--intake-file",
            "library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md",
            "--synthesis-file",
            "library/syntheses/podcasts/agent-team-governability-2026-04.md",
            "--output",
            str(target),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "Direct quote" in text
    assert "Paraphrase" in text
    assert "Evidence" in text
    assert "Why it matters" in text
```

- [ ] **Step 3: Run the targeted tests to confirm failure**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k review_pack -v
```

Expected:
- FAIL because `render-review-pack` does not exist yet

- [ ] **Step 4: Commit**

```bash
git add tests/test_writeback_generate.py
git commit -m "test: add failing review pack generation checks"
```

### Task 3: Build the AI-native UX lens pack and review-pack helpers

**Files:**
- Modify: `scripts/writeback_generate.py`
- Read: `/Users/vickyshou/.openclaw/workspace/shared/Principles/UX for human、UX of agent、以及 UX of collaboration.md`
- Read: `/Users/vickyshou/.openclaw/workspace/shared/Principles/UX_PRINCIPLES_ATTENTION_ARBITRATION.md`
- Read: `/Users/vickyshou/.openclaw/workspace/shared/Principles/一个合格的 AI native agentic UX designer 要具备的核心能力.md`
- Read: `/Users/vickyshou/.openclaw/workspace/shared/Principles/当今 agent 在人机交互中的主要探索.md`

- [ ] **Step 1: Add a minimal UX lens pack helper**

Add this helper to `scripts/writeback_generate.py`:

```python
UX_LENS_REFS = [
    Path("/Users/vickyshou/.openclaw/workspace/shared/Principles/UX for human、UX of agent、以及 UX of collaboration.md"),
    Path("/Users/vickyshou/.openclaw/workspace/shared/Principles/UX_PRINCIPLES_ATTENTION_ARBITRATION.md"),
    Path("/Users/vickyshou/.openclaw/workspace/shared/Principles/一个合格的 AI native agentic UX designer 要具备的核心能力.md"),
    Path("/Users/vickyshou/.openclaw/workspace/shared/Principles/当今 agent 在人机交互中的主要探索.md"),
]


def build_ai_native_ux_lens_pack() -> list[str]:
    lens_points: list[str] = []
    for path in UX_LENS_REFS:
        if not path.exists():
            continue
        text = read_file(path)
        for needle in [
            "user goal loop",
            "agent behavior contract",
            "注意力仲裁",
            "handoff",
            "rollback",
            "责任",
        ]:
            if needle in text and needle not in lens_points:
                lens_points.append(needle)
    return lens_points
```

- [ ] **Step 2: Add review-pack builder helpers**

Add these helpers to `scripts/writeback_generate.py`:

```python
def build_research_question(intake_text: str) -> tuple[str, str]:
    return read_field(intake_text, "research_direction"), read_field(intake_text, "direction_status")


def build_review_pack_sections(intake_text: str, synthesis_text: str) -> dict[str, str]:
    research_direction, direction_status = build_research_question(intake_text)
    role_map = build_episode_role_map(synthesis_text)
    episode_slugs = collect_episode_slugs(synthesis_text)
    theme_lines = []
    for slug in episode_slugs:
        evidence = collect_evidence_for_episode(slug)
        quote = strip_number_prefix(evidence["highlights"][0]) if evidence["highlights"] else ""
        theme_lines.append(
            "\n".join(
                [
                    f"### 主题：{role_map.get(slug, slug)}",
                    "",
                    f"**Direct quote**  ",
                    quote,
                    "",
                    f"**Paraphrase**  ",
                    f"这条材料与研究问题“{research_direction}”相关，因为它在强调 {role_map.get(slug, slug)}。",
                    "",
                    f"**Evidence**  ",
                    f"- `{slug}`",
                    "",
                    f"**Why it matters**  ",
                    "这条证据值得进入综合判断，因为它直接触及产品结构、协作边界或治理机制。",
                ]
            )
        )
    intro = "本轮先按主题聚类做综述，不按播客顺序复述，也不先给最终判断。"
    tensions = "\n".join(f"- {item}" for item in parse_bullets(read_section(synthesis_text, '保留张力')))
    assumptions = "\n".join(
        [
            "### 被材料支持的 assumptions",
            "1. 自主执行能力的上限取决于 harness，而不只是模型本身。",
            "",
            "### 仍需验证的 assumptions",
            "1. 这些控制层是否会成为默认产品结构，而不只是高成熟团队的最佳实践。",
        ]
    )
    question_source_map = {
        "user_provided": "用户给定",
        "system_suggested_pending": "系统建议，待用户批准",
        "system_suggested_approved": "系统建议，已批准",
    }
    return {
        "question": f"{research_direction}\n\n问题来源：{question_source_map.get(direction_status, direction_status)}",
        "intro": intro,
        "review": "\n\n".join(theme_lines),
        "tensions": tensions,
        "problem": "这里先提出一个 draft problem statement：如何把 agent 从偶发可用工具，变成可长期协作、可分工、可升级人工、可追责的执行网络？",
        "assumptions": assumptions,
    }
```

- [ ] **Step 3: Run the existing review-pack tests and confirm they still fail at missing command wiring**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k review_pack -v
```

Expected:
- FAIL because command wiring is not added yet

- [ ] **Step 4: Commit**

```bash
git add scripts/writeback_generate.py
git commit -m "feat: add research review pack helpers"
```

### Task 4: Add review-pack rendering command and materialize the pilot review pack

**Files:**
- Modify: `scripts/writeback_generate.py`
- Create: `library/review-packs/podcasts/review-pack-agent-team-paradigm.md`
- Modify: `tests/test_writeback_generate.py`

- [ ] **Step 1: Add the `render-review-pack` subcommand**

Add this argparse setup to `scripts/writeback_generate.py`:

```python
    review_pack = subparsers.add_parser("render-review-pack")
    review_pack.add_argument("--intake-file", required=True)
    review_pack.add_argument("--synthesis-file", required=True)
    review_pack.add_argument("--output", required=True)
```

- [ ] **Step 2: Add the review-pack renderer**

Add this function to `scripts/writeback_generate.py`:

```python
def render_review_pack(args: argparse.Namespace) -> str:
    intake_text = read_file(args.intake_file)
    synthesis_text = read_file(args.synthesis_file)
    sections = build_review_pack_sections(intake_text, synthesis_text)
    return f"""# Research Review Pack

## Research Question

{sections['question']}

## Review Introduction

{sections['intro']}

## Thematic Literature Review

{sections['review']}

## Counter-Signals And Tensions

{sections['tensions']}

## Draft Problem Statement

{sections['problem']}

## Draft Assumptions

{sections['assumptions']}
"""
```

- [ ] **Step 3: Dispatch the command in `main()`**

Update the dispatch:

```python
    if args.command == "render-review-pack":
        output.write_text(render_review_pack(args))
        return 0
```

- [ ] **Step 4: Materialize the pilot review pack**

Run:

```bash
python3 scripts/writeback_generate.py render-review-pack \
  --intake-file library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md \
  --synthesis-file library/syntheses/podcasts/agent-team-governability-2026-04.md \
  --output library/review-packs/podcasts/review-pack-agent-team-paradigm.md
```

- [ ] **Step 5: Run the review-pack tests and make sure they pass**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k review_pack -v
```

Expected:
- PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/writeback_generate.py tests/test_writeback_generate.py library/review-packs/podcasts/review-pack-agent-team-paradigm.md
git commit -m "feat: materialize pilot research review pack"
```

### Task 5: Replace the final writeback body with review-pack-driven research output

**Files:**
- Modify: `scripts/writeback_generate.py`
- Modify: `tests/test_writeback_generate.py`
- Modify: `library/writebacks/podcasts/matrix/integrated-team-paradigm.md`

- [ ] **Step 1: Write the failing test for the new research-grade body**

Add this test to `tests/test_writeback_generate.py`:

```python
def test_research_direction_writeback_contains_review_driven_sections(tmp_path):
    target = tmp_path / "writeback.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_generate.py",
            "render-longform",
            "--writeback-id",
            "writeback-integrated-team-paradigm",
            "--intake-file",
            "library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md",
            "--synthesis-file",
            "library/syntheses/podcasts/agent-team-governability-2026-04.md",
            "--output",
            str(target),
            "--title",
            "从单 Agent 工具到可治理的 Agent Team：五条一线语料中的编排、协作与企业化信号",
            "--subtitle",
            "给团队看的 integrated 版：Multi-Agent 是否已进入范式迁移期",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "## 研究问题" in text
    assert "## 综述导言" in text
    assert "## 文献综述" in text
    assert "Direct quote" in text
    assert "Paraphrase" in text
    assert "Evidence" in text
    assert "Why it matters" in text
    assert "## Problem Statement" in text
    assert "## Assumptions" in text
    assert "## AI-native UX 视角" in text
    assert "## 本轮 Research Direction" in text
```

- [ ] **Step 2: Update `render-longform` to render from the review pack**

Modify `scripts/writeback_generate.py` so that:
- it generates or reads the same review-pack sections first
- the final writeback body becomes:
  - `研究问题`
  - `综述导言`
  - `文献综述`
  - `综合判断`
  - `Problem Statement`
  - `Assumptions`
  - `AI-native UX 视角`
  - `本轮 Research Direction`
  - `保留分歧`

Use this body template:

```python
def render_longform_writeback(args: argparse.Namespace) -> str:
    intake_text = read_file(args.intake_file)
    synthesis_text = read_file(args.synthesis_file)
    intake_id = read_field(intake_text, "intake_id")
    review_sections = build_review_pack_sections(intake_text, synthesis_text)
    ux_lens_points = build_ai_native_ux_lens_pack()
    ux_body = "\n".join(f"- {point}" for point in ux_lens_points) or "- 暂无 AI-native UX lens point"
    research_direction = read_field(intake_text, "research_direction")
    direction_status = read_field(intake_text, "direction_status")
    return f"""# Writeback Proposal

- writeback_id: `{args.writeback_id}`
- intake_id: `{intake_id}`
- collaboration_mode: `{read_field(intake_text, 'collaboration_mode')}`
- used_default_rules: `{read_field(intake_text, 'used_default_rules')}`
- focus_priority: {format_list(read_list_field(intake_text, 'focus_priority'))}
- special_attention: {format_list(read_list_field(intake_text, 'special_attention'))}
- target_audience: `{read_field(intake_text, 'target_audience')}`
- research_direction: `{research_direction}`
- direction_status: `{direction_status}`
- synthesis_ref: `{read_field(synthesis_text, 'synthesis_id')}`

## 标题

{args.title}

## 副标题

{args.subtitle}

## 研究问题

{review_sections['question']}

## 综述导言

{review_sections['intro']}

## 文献综述

{review_sections['review']}

## 综合判断

{read_section(synthesis_text, '核心综合判断')}

## Problem Statement

{review_sections['problem']}

## Assumptions

{review_sections['assumptions']}

## AI-native UX 视角

{ux_body}

## 本轮 Research Direction

{research_direction}

## 保留分歧

{review_sections['tensions']}
"""
```

- [ ] **Step 3: Regenerate the pilot final writeback**

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

- [ ] **Step 4: Run the targeted tests and make sure they pass**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k \"review_pack or research_direction_writeback\" -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/writeback_generate.py tests/test_writeback_generate.py library/writebacks/podcasts/matrix/integrated-team-paradigm.md
git commit -m "feat: render pilot writeback from research review pack"
```

### Task 6: Document and verify the single-pilot research-direction flow

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-04-17-research-direction-writeback-implementation.md`

- [ ] **Step 1: Document the two-step flow in README**

Add this section to `README.md`:

```md
### 生成 research-direction writeback

先生成 review pack：

```bash
python3 scripts/writeback_generate.py render-review-pack \
  --intake-file library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md \
  --synthesis-file library/syntheses/podcasts/agent-team-governability-2026-04.md \
  --output library/review-packs/podcasts/review-pack-agent-team-paradigm.md
```

再生成最终 writeback：

```bash
python3 scripts/writeback_generate.py render-longform \
  --writeback-id writeback-integrated-team-paradigm \
  --intake-file library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md \
  --synthesis-file library/syntheses/podcasts/agent-team-governability-2026-04.md \
  --output library/writebacks/podcasts/matrix/integrated-team-paradigm.md \
  --title "从单 Agent 工具到可治理的 Agent Team：五条一线语料中的编排、协作与企业化信号" \
  --subtitle "给团队看的 integrated 版：Multi-Agent 是否已进入范式迁移期"
```
```

- [ ] **Step 2: Run the full relevant test set**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_intake.py tests/test_writeback_generate.py tests/test_writeback_matrix.py -v
```

Expected:
- PASS

- [x] **Step 3: Add implementation notes to this plan**

Append:

```md
## Implementation Notes

- this rollout intentionally upgrades only one pilot writeback
- matrix-wide regeneration is explicitly out of scope
- the new default chain is `research direction -> review pack -> writeback`
- AI-native UX is the only MVP interpretive lens in this pass
```

- [x] **Step 4: Commit**

```bash
git add README.md docs/superpowers/plans/2026-04-17-research-direction-writeback-implementation.md
git commit -m "docs: record research-direction writeback rollout"
```

## Self-Review

Spec coverage check:
- research direction as first-class object: Task 1 and Task 5
- review pack intermediate object: Tasks 2-4
- research-oriented writeback body: Task 5
- AI-native UX as MVP lens: Tasks 3 and 5
- single-pilot scope only: enforced in file structure and tasks

Placeholder scan:
- no `TODO`, `TBD`, or deferred-placeholder task steps remain
- all code-changing steps include concrete code blocks
- all verification steps include exact commands

Type consistency:
- `research_direction` and `direction_status` are used consistently
- command names are consistently `render-review-pack` and `render-longform`
- the pilot paths are consistent across all tasks

## Implementation Notes

- this rollout intentionally upgrades only one pilot writeback
- matrix-wide regeneration is explicitly out of scope
- the new default chain is `research direction -> review pack -> writeback`
- AI-native UX is the only MVP interpretive lens in this pass
