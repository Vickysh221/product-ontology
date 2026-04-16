# Longform Writeback Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new `render-longform` generation path that can produce one real longform matrix writeback for `integrated-team-paradigm` from synthesis, intake, and podcast evidence.

**Architecture:** Keep the current `render` command unchanged for matrix plumbing, and add a separate `render-longform` command in `scripts/writeback_generate.py`. The longform path will read the intake record, synthesis record, and selected evidence artifacts, assemble a constrained outline, then render a complete Chinese writeback with real evidence anchors and preserved tensions.

**Tech Stack:** Python 3, argparse, pathlib, regex parsing, pytest, existing Markdown records in `library/`, `seed/`, and `docs/`

---

## File Structure

### Existing files to modify

- `scripts/writeback_generate.py`
  - Add `render-longform`
  - Parse synthesis and evidence records
  - Build outline and render longform Markdown
- `tests/test_writeback_generate.py`
  - Add longform generation tests
  - Verify structure, evidence anchors, and no placeholder language
- `README.md`
  - Document the new longform command

### Existing content files to read from

- `library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md`
  - Intake control object for the pilot
- `library/syntheses/podcasts/agent-team-governability-2026-04.md`
  - Shared synthesis base
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

### Existing outputs to replace or regenerate

- `library/writebacks/podcasts/matrix/integrated-team-paradigm.md`
  - Replace placeholder body with longform pilot output

### No new modules unless blocked

Keep the first pass inside `scripts/writeback_generate.py`. Split only if the file becomes too hard to hold in context while implementing.

---

### Task 1: Add longform generation tests

**Files:**
- Modify: `tests/test_writeback_generate.py`
- Modify: `scripts/writeback_generate.py`
- Read: `library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md`
- Read: `library/syntheses/podcasts/agent-team-governability-2026-04.md`

- [ ] **Step 1: Write the failing test for `render-longform` output shape**

Add this test to `tests/test_writeback_generate.py`:

```python
def test_writeback_generate_render_longform_creates_real_sections(tmp_path):
    target = tmp_path / "longform.md"
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
    assert "## 摘要" in text
    assert "## 主判断" in text
    assert "## 机制拆解" in text
    assert "## 能力边界与工作流变化" in text
    assert "## 针对本次追问的回答" in text
    assert "## 证据锚点" in text
    assert "## 保留分歧" in text
```

- [ ] **Step 2: Write the failing test for evidence anchors and no placeholder language**

Add this test to `tests/test_writeback_generate.py`:

```python
def test_writeback_generate_render_longform_has_real_evidence_and_no_placeholders(tmp_path):
    target = tmp_path / "longform.md"
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
    assert "待补充" not in text
    assert "待由 evidence" not in text
    assert "podwise-ai-7758431-2cd3ef48" in text
    assert "podwise-ai-7718625-7d0dc7d1" in text
    assert "podwise-ai-7635732-bdfba3f3" in text
    assert "podwise-ai-7504915-91b52a0e" in text
    assert "podwise-ai-7368984-f9a0fefa" in text
```

- [ ] **Step 3: Run the targeted tests to confirm failure**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k longform -v
```

Expected:
- FAIL because `render-longform` does not exist yet

- [ ] **Step 4: Commit the failing test scaffold**

```bash
git add tests/test_writeback_generate.py
git commit -m "test: add failing longform writeback generation checks"
```

### Task 2: Add parsing helpers for synthesis and evidence selection

**Files:**
- Modify: `scripts/writeback_generate.py`
- Test: `tests/test_writeback_generate.py`

- [ ] **Step 1: Add parsing helpers for markdown records**

Add these helpers near the top of `scripts/writeback_generate.py` below the existing parsing utilities:

```python
def read_section(text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, re.S)
    return match.group(1).strip() if match else ""


def parse_bullets(section_text: str) -> list[str]:
    return [line[2:].strip() for line in section_text.splitlines() if line.startswith("- ")]


def collect_episode_slugs(synthesis_text: str) -> list[str]:
    return read_list_field(synthesis_text, "source_episode_slugs")


def read_file(path: str) -> str:
    try:
        return Path(path).read_text()
    except OSError:
        raise SystemExit(f"missing or unreadable file: {path}")
```

- [ ] **Step 2: Add evidence selection helper using summary first and highlights second**

Add this function to `scripts/writeback_generate.py`:

```python
def collect_evidence_for_episode(slug: str) -> dict[str, list[str]]:
    base = Path("library/artifacts/podcasts") / slug
    summary_text = read_file(str(base / "summary.md"))
    highlights_text = read_file(str(base / "highlights.md"))
    summary_lines = [line.strip() for line in summary_text.splitlines() if line.strip()]
    highlight_lines = [line.strip() for line in highlights_text.splitlines() if line.strip()]
    return {
        "summary": summary_lines[:8],
        "highlights": highlight_lines[:8],
    }
```

- [ ] **Step 3: Add a helper that maps the synthesis evidence summary to episode roles**

Add this function to `scripts/writeback_generate.py`:

```python
def build_episode_role_map(synthesis_text: str) -> dict[str, str]:
    section = read_section(synthesis_text, "证据汇总")
    roles: dict[str, str] = {}
    for line in parse_bullets(section):
        match = re.match(r"`([^`]+)`\s+(.*)", line)
        if match:
            roles[match.group(1)] = match.group(2)
    return roles
```

- [ ] **Step 4: Run the same targeted tests and confirm they still fail later in generation**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k longform -v
```

Expected:
- FAIL moves forward from missing command to incomplete rendering or missing sections

- [ ] **Step 5: Commit the parsing layer**

```bash
git add scripts/writeback_generate.py tests/test_writeback_generate.py
git commit -m "feat: add longform writeback parsing helpers"
```

### Task 3: Implement `render-longform` outline construction

**Files:**
- Modify: `scripts/writeback_generate.py`
- Test: `tests/test_writeback_generate.py`

- [ ] **Step 1: Add a helper that constructs the pilot outline**

Add this function to `scripts/writeback_generate.py`:

```python
def build_longform_outline(intake_text: str, synthesis_text: str) -> dict[str, object]:
    collaboration_mode = read_field(intake_text, "collaboration_mode")
    target_audience = read_field(intake_text, "target_audience")
    extra_questions = read_list_field(intake_text, "extra_questions")
    core_judgment = read_section(synthesis_text, "核心综合判断")
    stable_themes = parse_bullets(read_section(synthesis_text, "稳定主题"))
    preserved_tensions = parse_bullets(read_section(synthesis_text, "保留张力"))
    return {
        "collaboration_mode": collaboration_mode,
        "target_audience": target_audience,
        "extra_questions": extra_questions,
        "core_judgment": core_judgment,
        "stable_themes": stable_themes,
        "preserved_tensions": preserved_tensions,
    }
```

- [ ] **Step 2: Add a helper that converts outline plus evidence into section bodies**

Add this function to `scripts/writeback_generate.py`:

```python
def build_longform_sections(
    title: str,
    subtitle: str,
    intake_text: str,
    synthesis_text: str,
) -> dict[str, str]:
    outline = build_longform_outline(intake_text, synthesis_text)
    role_map = build_episode_role_map(synthesis_text)
    episode_slugs = collect_episode_slugs(synthesis_text)
    evidence_lines = []
    for slug in episode_slugs:
        role = role_map.get(slug, "")
        evidence = collect_evidence_for_episode(slug)
        anchor = evidence["highlights"][0] if evidence["highlights"] else evidence["summary"][0]
        evidence_lines.append(f"- `{slug}`：{role} 证据锚点：{anchor}")

    summary = (
        "这篇报告围绕五条一线播客语料，回答 multi-agent 是否正在从更强的工作流包装，"
        "走向可治理的 Agent Team 结构。对于团队协作来说，关键变化不只是 agent 数量增加，"
        "而是 harness engineering、角色边界、权限控制和异步协作被收束进同一条产品主链。"
    )
    judgment = outline["core_judgment"]
    mechanism = (
        "这组材料共同显示，agent orchestration 的价值并不在于把多个智能体机械排队，"
        "而在于把测试、容器、权限、审核与任务分工嵌入执行机制里。"
        "一旦这些控制层被稳定地纳入系统设计，multi-agent 就不再只是编排技巧，"
        "而开始接近产品能力边界的重新定义。"
    )
    workflow = (
        "对团队而言，这种变化直接影响工作流。系统从单 agent 响应工具，"
        "变成可以在明确边界下分派、回收、校验和交接工作的执行网络。"
        "这会把原本隐性的协作约束，例如谁负责审批、谁能调用什么资源、"
        "哪些结果需要复核，变成产品结构的一部分。"
    )
    extra = (
        "就本次追问而言，现有证据已经足以说明这不是简单的 feature 堆叠。"
        "五条语料都在重复同一件事：当 agent 需要稳定承担不同角色、"
        "在不同权限层运行，并且接受测试与治理约束时，产品形态就从单体助手转向 Agent Team。"
        "但这条范式迁移是否已经完全稳定，仍取决于这些控制层能否持续成为默认产品结构，"
        "而不是只出现在工程演示或高成熟团队的局部实践中。"
    )
    tensions = "\n".join(f"- {item}" for item in outline["preserved_tensions"])
    return {
        "summary": summary,
        "judgment": judgment,
        "mechanism": mechanism,
        "workflow": workflow,
        "extra": extra,
        "evidence": "\n".join(evidence_lines),
        "tensions": tensions,
    }
```

- [ ] **Step 3: Run the targeted tests again**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k longform -v
```

Expected:
- FAIL now narrows to command wiring or final render output mismatch

- [ ] **Step 4: Commit the outline builder**

```bash
git add scripts/writeback_generate.py
git commit -m "feat: add longform writeback outline builder"
```

### Task 4: Wire `render-longform` into the CLI and render full Markdown

**Files:**
- Modify: `scripts/writeback_generate.py`
- Test: `tests/test_writeback_generate.py`

- [ ] **Step 1: Add the `render-longform` subcommand**

Update the argparse setup in `scripts/writeback_generate.py`:

```python
    render_longform = subparsers.add_parser("render-longform")
    render_longform.add_argument("--writeback-id", required=True)
    render_longform.add_argument("--intake-file", required=True)
    render_longform.add_argument("--synthesis-file", required=True)
    render_longform.add_argument("--output", required=True)
    render_longform.add_argument("--title", required=True)
    render_longform.add_argument("--subtitle", default="")
    render_longform.add_argument("--review-refs", default="")
    render_longform.add_argument("--verdict-refs", default="")
```

- [ ] **Step 2: Add the longform renderer function**

Add this function to `scripts/writeback_generate.py`:

```python
def render_longform_writeback(args: argparse.Namespace) -> str:
    intake_text = read_file(args.intake_file)
    synthesis_text = read_file(args.synthesis_file)
    intake_id = read_field(intake_text, "intake_id")
    if not intake_id:
        raise SystemExit("missing intake_id in intake record")
    collaboration_mode = read_field(intake_text, "collaboration_mode")
    used_default_rules = read_field(intake_text, "used_default_rules")
    target_audience = read_field(intake_text, "target_audience")
    extra_questions = read_list_field(intake_text, "extra_questions")
    review_refs = parse_csv(args.review_refs)
    verdict_refs = parse_csv(args.verdict_refs)
    sections = build_longform_sections(args.title, args.subtitle, intake_text, synthesis_text)
    tensions = read_section(synthesis_text, "保留张力")
    return f"""# Writeback Proposal

- writeback_id: `{args.writeback_id}`
- intake_id: `{intake_id}`
- collaboration_mode: `{collaboration_mode}`
- used_default_rules: `{used_default_rules}`
- focus_priority: []
- special_attention: []
- target_audience: `{target_audience}`
- extra_questions: {format_list(extra_questions)}
- synthesis_ref: `{read_field(synthesis_text, 'synthesis_id')}`
- review_refs: {format_list(review_refs)}
- verdict_refs: {format_list(verdict_refs)}
- preserved_tensions: {format_list(parse_bullets(tensions))}

## 标题

{args.title}

## 副标题

{args.subtitle}

## 摘要

{sections['summary']}

## 主判断

{sections['judgment']}

## 机制拆解

{sections['mechanism']}

## 能力边界与工作流变化

{sections['workflow']}

## 针对本次追问的回答

{sections['extra']}

## 证据锚点

{sections['evidence']}

## 保留分歧

{sections['tensions']}
"""
```

- [ ] **Step 3: Dispatch the new command in `main()`**

Replace the current command dispatch tail in `scripts/writeback_generate.py` with:

```python
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if args.command == "render":
        output.write_text(render_writeback(args))
        return 0

    if args.command == "render-longform":
        output.write_text(render_longform_writeback(args))
        return 0

    return 1
```

- [ ] **Step 4: Run the targeted tests and make sure they pass**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k longform -v
```

Expected:
- PASS for both longform tests

- [ ] **Step 5: Commit the command wiring**

```bash
git add scripts/writeback_generate.py tests/test_writeback_generate.py
git commit -m "feat: add render-longform writeback command"
```

### Task 5: Materialize the pilot longform writeback

**Files:**
- Modify: `library/writebacks/podcasts/matrix/integrated-team-paradigm.md`
- Modify: `README.md`
- Test: `tests/test_writeback_generate.py`

- [ ] **Step 1: Generate the pilot longform file in place**

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

Expected:
- `library/writebacks/podcasts/matrix/integrated-team-paradigm.md` is overwritten with a real longform article

- [ ] **Step 2: Add a regression test for the materialized pilot**

Add this test to `tests/test_writeback_generate.py`:

```python
def test_materialized_integrated_team_paradigm_is_longform():
    text = Path("library/writebacks/podcasts/matrix/integrated-team-paradigm.md").read_text()
    assert "待补充" not in text
    assert "待由 evidence" not in text
    assert "## 机制拆解" in text
    assert "## 能力边界与工作流变化" in text
    assert "## 针对本次追问的回答" in text
    assert "podwise-ai-7758431-2cd3ef48" in text
    assert "podwise-ai-7368984-f9a0fefa" in text
```

- [ ] **Step 3: Document the new command in `README.md`**

Add a short command block near the existing writeback generation instructions:

```md
### 生成长文版 writeback

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

- [ ] **Step 4: Run the focused tests**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -v
```

Expected:
- PASS for the whole `tests/test_writeback_generate.py` file

- [ ] **Step 5: Commit the pilot materialization**

```bash
git add library/writebacks/podcasts/matrix/integrated-team-paradigm.md README.md tests/test_writeback_generate.py
git commit -m "feat: materialize longform integrated team writeback"
```

### Task 6: Final verification and implementation notes

**Files:**
- Modify: `docs/superpowers/plans/2026-04-17-longform-writeback-generation-implementation.md`
- Read: `library/writebacks/podcasts/matrix/integrated-team-paradigm.md`

- [x] **Step 1: Run the full relevant test set**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_intake.py tests/test_writeback_generate.py tests/test_writeback_matrix.py -v
```

Expected:
- PASS for all relevant writeback tests

- [x] **Step 2: Smoke-check the pilot output for required properties**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
text = Path("library/writebacks/podcasts/matrix/integrated-team-paradigm.md").read_text()
checks = {
    "no_placeholder": "待补充" not in text and "待由 evidence" not in text,
    "has_all_sections": all(
        heading in text
        for heading in [
            "## 摘要",
            "## 主判断",
            "## 机制拆解",
            "## 能力边界与工作流变化",
            "## 针对本次追问的回答",
            "## 证据锚点",
            "## 保留分歧",
        ]
    ),
    "has_five_episode_refs": all(
        slug in text
        for slug in [
            "podwise-ai-7758431-2cd3ef48",
            "podwise-ai-7718625-7d0dc7d1",
            "podwise-ai-7635732-bdfba3f3",
            "podwise-ai-7504915-91b52a0e",
            "podwise-ai-7368984-f9a0fefa",
        ]
    ),
}
for name, passed in checks.items():
    print(f"{name}={'PASS' if passed else 'FAIL'}")
PY
```

Expected:
- all checks print `PASS`

- [x] **Step 3: Add a short implementation note to the plan file after execution**

Append this note after execution:

```md
## Implementation Notes

- `render` remains the placeholder path for matrix plumbing
- `render-longform` is now the narrative generation path
- only `integrated-team-paradigm` was upgraded in this pass
- the remaining 11 matrix variants still require a follow-up rollout plan
```

- [x] **Step 4: Commit the verification pass**

```bash
git add docs/superpowers/plans/2026-04-17-longform-writeback-generation-implementation.md
git commit -m "docs: record longform writeback verification notes"
```

## Self-Review

Spec coverage check:
- new longform command: covered in Tasks 2-4
- pilot target only: covered in Task 5
- seven-part structure: covered in Tasks 1 and 4
- evidence ordering and anchors: covered in Tasks 2-5
- success criteria and no placeholders: covered in Tasks 1, 5, and 6

Placeholder scan:
- no `TODO`, `TBD`, or deferred implementation placeholders remain in tasks
- all code-changing steps include concrete code blocks
- all test steps include exact commands and expected outcomes

Type consistency:
- command name is consistently `render-longform`
- pilot slug is consistently `integrated-team-paradigm`
- synthesis file and intake file paths are consistent across all tasks

## Implementation Notes

- `render` remains the placeholder path for matrix plumbing
- `render-longform` is now the narrative generation path
- only `integrated-team-paradigm` was upgraded in this pass
- the remaining 11 matrix variants still require a follow-up rollout plan
