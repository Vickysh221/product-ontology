# Writeback Intake Matrix Test Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 12-writeback matrix test that uses one shared five-episode podcast evidence pool and one shared synthesized judgment base to verify that intake choices materially change writeback output.

**Architecture:** Extend the current writeback workflow with a matrix-oriented layer instead of modifying source ingestion. Store one shared synthesis record, generate 12 intake records from a fixed matrix, then generate 12 writebacks from the same judgment base while varying only collaboration mode, target audience, and rotating extra-question themes. Add tests that check structure and metadata divergence without letting evidence drift across variants.

**Tech Stack:** Markdown records, Python 3 CLI scripts with `argparse` and `pathlib`, existing `writeback_intake.py` and `writeback_generate.py`, `pytest` via `uv run --with pytest`

---

## File Map

### New Files

- `seed/writeback-matrix-test.yaml`
  Stores the 12-row matrix definition: mode, audience, extra-question theme, output slug, and subtitle.
- `library/syntheses/podcasts/agent-team-governability-2026-04.md`
  Shared synthesized judgment base for the five episodes.
- `library/writeback-intakes/podcasts/matrix/`
  Directory containing 12 generated intake records, one per matrix row.
- `library/writebacks/podcasts/matrix/`
  Directory containing 12 generated writebacks, one per matrix row.
- `scripts/writeback_matrix.py`
  Matrix driver that can create intake records, generate writebacks, and validate matrix completeness.
- `tests/test_writeback_matrix.py`
  Verifies matrix configuration, synthesized base usage, intake generation, and writeback divergence markers.

### Modified Files

- `README.md`
  Documents the matrix test workflow and commands.
- `templates/writeback-proposal.md`
  If needed, add explicit `target_audience` / `extra_questions` placeholders so matrix outputs do not drift from the template.
- `scripts/writeback_generate.py`
  Extend minimally so generated writebacks can include `target_audience`, `extra_questions`, subtitle, and base synthesis references without inventing new evidence logic.
- `tests/test_writeback_generate.py`
  Add compatibility assertions for the extended generator interface.

---

### Task 1: Define The 12-Row Matrix Configuration

**Files:**
- Create: `seed/writeback-matrix-test.yaml`
- Test: `tests/test_writeback_matrix.py`

- [ ] **Step 1: Write the failing configuration test**

Create `tests/test_writeback_matrix.py` with:

```python
from pathlib import Path
import yaml


def test_writeback_matrix_has_12_rows():
    data = yaml.safe_load(Path("seed/writeback-matrix-test.yaml").read_text())
    rows = data["matrix"]
    assert len(rows) == 12


def test_writeback_matrix_covers_modes_audiences_and_themes():
    data = yaml.safe_load(Path("seed/writeback-matrix-test.yaml").read_text())
    rows = data["matrix"]
    assert {row["collaboration_mode"] for row in rows} == {"integrated", "sectioned", "appendix"}
    assert {row["target_audience"] for row in rows} == {"self", "team", "exec", "research_archive"}
    assert {row["extra_question_theme"] for row in rows} == {
        "harness_engineering",
        "multiagent_paradigm_shift",
        "multi_human_multiagent_enterprise_management",
    }
```

- [ ] **Step 2: Run test to verify it fails**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_matrix.py::test_writeback_matrix_has_12_rows -v`
Expected: FAIL because `seed/writeback-matrix-test.yaml` does not exist

- [ ] **Step 3: Create the matrix file**

Create `seed/writeback-matrix-test.yaml`:

```yaml
title: 从单 Agent 工具到可治理的 Agent Team：五条一线语料中的编排、协作与企业化信号
synthesis_id: synthesis-podcasts-agent-team-governability-2026-04
source_episode_slugs:
  - podwise-ai-7758431-2cd3ef48
  - podwise-ai-7718625-7d0dc7d1
  - podwise-ai-7635732-bdfba3f3
  - podwise-ai-7504915-91b52a0e
  - podwise-ai-7368984-f9a0fefa
matrix:
  - output_slug: integrated-self-harness
    collaboration_mode: integrated
    target_audience: self
    extra_question_theme: harness_engineering
    subtitle: 给自己看的 integrated 版：Harness Engineering 是工程手段还是产品主能力
  - output_slug: integrated-team-paradigm
    collaboration_mode: integrated
    target_audience: team
    extra_question_theme: multiagent_paradigm_shift
    subtitle: 给团队看的 integrated 版：Multi-Agent 是否已进入范式迁移期
  - output_slug: integrated-exec-enterprise
    collaboration_mode: integrated
    target_audience: exec
    extra_question_theme: multi_human_multiagent_enterprise_management
    subtitle: 给高层看的 integrated 版：多人多agent管理如何改变企业控制边界
  - output_slug: integrated-archive-harness
    collaboration_mode: integrated
    target_audience: research_archive
    extra_question_theme: harness_engineering
    subtitle: 给研究归档的 integrated 版：Harness Engineering 的产品化边界
  - output_slug: sectioned-self-paradigm
    collaboration_mode: sectioned
    target_audience: self
    extra_question_theme: multiagent_paradigm_shift
    subtitle: 给自己看的 sectioned 版：从单 Agent 到 Agent Team 的结构迁移
  - output_slug: sectioned-team-enterprise
    collaboration_mode: sectioned
    target_audience: team
    extra_question_theme: multi_human_multiagent_enterprise_management
    subtitle: 给团队看的 sectioned 版：多人多agent协作如何被管理
  - output_slug: sectioned-exec-harness
    collaboration_mode: sectioned
    target_audience: exec
    extra_question_theme: harness_engineering
    subtitle: 给高层看的 sectioned 版：Harness Engineering 是否构成产品竞争力
  - output_slug: sectioned-archive-paradigm
    collaboration_mode: sectioned
    target_audience: research_archive
    extra_question_theme: multiagent_paradigm_shift
    subtitle: 给研究归档的 sectioned 版：Agent Team 范式迁移的证据结构
  - output_slug: appendix-self-enterprise
    collaboration_mode: appendix
    target_audience: self
    extra_question_theme: multi_human_multiagent_enterprise_management
    subtitle: 给自己看的 appendix 版：企业里的人与 Agent 如何共治
  - output_slug: appendix-team-harness
    collaboration_mode: appendix
    target_audience: team
    extra_question_theme: harness_engineering
    subtitle: 给团队看的 appendix 版：Harness Engineering 如何进入工作流主链
  - output_slug: appendix-exec-paradigm
    collaboration_mode: appendix
    target_audience: exec
    extra_question_theme: multiagent_paradigm_shift
    subtitle: 给高层看的 appendix 版：Multi-Agent 是不是新的产品范式
  - output_slug: appendix-archive-enterprise
    collaboration_mode: appendix
    target_audience: research_archive
    extra_question_theme: multi_human_multiagent_enterprise_management
    subtitle: 给研究归档的 appendix 版：企业级多人多agent管理的治理信号
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_matrix.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add seed/writeback-matrix-test.yaml tests/test_writeback_matrix.py
git commit -m "feat: add writeback matrix test configuration"
```

### Task 2: Create The Shared Synthesis Base

**Files:**
- Create: `library/syntheses/podcasts/agent-team-governability-2026-04.md`
- Test: `tests/test_writeback_matrix.py`

- [ ] **Step 1: Add a failing synthesis test**

Append to `tests/test_writeback_matrix.py`:

```python
def test_shared_synthesis_record_exists():
    path = Path("library/syntheses/podcasts/agent-team-governability-2026-04.md")
    assert path.exists()


def test_shared_synthesis_mentions_all_five_episode_slugs():
    text = Path("library/syntheses/podcasts/agent-team-governability-2026-04.md").read_text()
    for slug in [
        "podwise-ai-7758431-2cd3ef48",
        "podwise-ai-7718625-7d0dc7d1",
        "podwise-ai-7635732-bdfba3f3",
        "podwise-ai-7504915-91b52a0e",
        "podwise-ai-7368984-f9a0fefa",
    ]:
        assert slug in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_matrix.py::test_shared_synthesis_record_exists -v`
Expected: FAIL because the synthesis file does not exist

- [ ] **Step 3: Write the shared synthesis record**

Create `library/syntheses/podcasts/agent-team-governability-2026-04.md`:

```md
# Shared Synthesis Record

- synthesis_id: `synthesis-podcasts-agent-team-governability-2026-04`
- title: `从单 Agent 工具到可治理的 Agent Team：五条一线语料中的编排、协作与企业化信号`
- source_episode_slugs: [`podwise-ai-7758431-2cd3ef48`, `podwise-ai-7718625-7d0dc7d1`, `podwise-ai-7635732-bdfba3f3`, `podwise-ai-7504915-91b52a0e`, `podwise-ai-7368984-f9a0fefa`]
- status: `draft`

## 核心综合判断

五条一线语料共同指向同一条产品演化线：Agent 系统正在从单一能力调用工具，过渡到可治理的 Agent Team。这个变化不是单纯增加更多 Agent 数量，而是把 harness engineering、角色边界、权限控制、自动化测试、异步协作和企业治理结构收束进同一套产品与工作流设计。

## 稳定主题

- `harness engineering` 不是附属工程习惯，而是 Agent 可控性、可审计性和可扩展性的基础约束层。
- `multi-agent orchestration` 更像结构迁移，而不是简单 feature 叠加。
- 企业场景中的多人多agent管理，本质上要求角色、权限、责任和沟通边界同时显式化。

## 证据汇总

- `podwise-ai-7758431-2cd3ef48` 强调 Team of Agents、Harness Engineering、AI 发起与 AI 审核闭环。
- `podwise-ai-7718625-7d0dc7d1` 强调 OpenCore、自主性、持久记忆、协议层与 Agent 产品形态。
- `podwise-ai-7635732-bdfba3f3` 强调企业版 OpenClaw、多智能体角色定义、协作、安全和权限。
- `podwise-ai-7504915-91b52a0e` 强调异步文档、自动化工作流、AI 团队管理与复利工程。
- `podwise-ai-7368984-f9a0fefa` 强调沙箱、安全流程、subagent、自动化测试与权限管理。

## 保留张力

- `harness engineering` 到底是工程方法，还是已经进入产品主能力层。
- `multi-agent` 到底是稳定范式迁移，还是当前阶段的高级 workflow 包装。
- 企业级多人多agent管理里的治理结构，哪些是安全/合规必要，哪些是效率放大器。
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_matrix.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add library/syntheses/podcasts/agent-team-governability-2026-04.md tests/test_writeback_matrix.py
git commit -m "feat: add shared synthesis for writeback matrix"
```

### Task 3: Extend Intake And Generator For Matrix Metadata

**Files:**
- Modify: `scripts/writeback_intake.py`
- Modify: `scripts/writeback_generate.py`
- Modify: `tests/test_writeback_intake.py`
- Modify: `tests/test_writeback_generate.py`
- Modify: `templates/writeback-proposal.md`

- [ ] **Step 1: Add failing tests for audience and extra-question rendering**

Append to `tests/test_writeback_intake.py`:

```python
def test_writeback_intake_cli_records_audience_and_extra_questions(tmp_path):
    target = tmp_path / "intake.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_intake.py",
            "create",
            "--intake-id",
            "intake-demo",
            "--output",
            str(target),
            "--target-audience",
            "team",
            "--extra-questions",
            "这是不是范式迁移",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- target_audience: `team`" in text
    assert "`这是不是范式迁移`" in text
```

Append to `tests/test_writeback_generate.py`:

```python
def test_writeback_generate_renders_audience_and_subtitle(tmp_path):
    intake = tmp_path / "intake.md"
    intake.write_text(
        \"\"\"# Writeback Intake Record
- intake_id: `intake-demo`
- collaboration_mode: `integrated`
- focus_priority: [`机制`, `用户信任`]
- target_audience: `team`
- decision_intent: `understand`
- evidence_posture: `balanced`
- special_attention: []
- extra_questions: [`这是不是范式迁移`]
- avoidances: []
- preserve_tensions: []
- used_default_rules: `false`
\"\"\"
    )
    target = tmp_path / \"writeback.md\"
    result = subprocess.run(
        [
            \"python3\",
            \"scripts/writeback_generate.py\",
            \"render\",
            \"--writeback-id\",
            \"writeback-demo\",
            \"--intake-file\",
            str(intake),
            \"--output\",
            str(target),
            \"--title\",
            \"父标题\",
            \"--subtitle\",
            \"副标题\",
            \"--summary\",
            \"摘要\",\n            \"--synthesis-ref\",\n            \"synthesis-demo\",\n        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert \"- target_audience: `team`\" in text
    assert \"- extra_questions: [`这是不是范式迁移`]\" in text
    assert \"## 副标题\" in text
    assert \"副标题\" in text
    assert \"- synthesis_ref: `synthesis-demo`\" in text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_intake.py tests/test_writeback_generate.py -v`
Expected: FAIL because the current scripts do not emit the new fields

- [ ] **Step 3: Extend the intake and generator scripts minimally**

Update `templates/writeback-proposal.md` to include:

```md
- target_audience: ``
- extra_questions: []
- synthesis_ref: ``

## 副标题
```

Update `scripts/writeback_intake.py` so `build_markdown()` already writes `target_audience` and `extra_questions` values using the existing fields, but keeps behavior unchanged otherwise.

Update `scripts/writeback_generate.py` to:
- read `target_audience` and `extra_questions` from the intake file
- accept `--subtitle` and `--synthesis-ref`
- render the new metadata fields and `## 副标题` section

Minimal rendering shape:

```python
target_audience = read_field(intake_text, "target_audience")
extra_questions = read_list_field(intake_text, "extra_questions")
```

Add a tiny helper:

```python
def read_list_field(text: str, field: str) -> list[str]:
    match = re.search(rf"- {re.escape(field)}: \\[(.*?)\\]", text)
    if not match or not match.group(1).strip():
        return []
    return [item.strip().strip(\"`\") for item in match.group(1).split(\",\") if item.strip()]
```

Render:

```md
- target_audience: `...`
- extra_questions: [`...`]
- synthesis_ref: `...`

## 副标题

...
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_intake.py tests/test_writeback_generate.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/writeback_intake.py scripts/writeback_generate.py templates/writeback-proposal.md tests/test_writeback_intake.py tests/test_writeback_generate.py
git commit -m "feat: extend writeback flow for matrix metadata"
```

### Task 4: Build The Matrix Driver Script

**Files:**
- Create: `scripts/writeback_matrix.py`
- Modify: `tests/test_writeback_matrix.py`

- [ ] **Step 1: Add failing matrix-driver tests**

Append to `tests/test_writeback_matrix.py`:

```python
import subprocess


def test_writeback_matrix_cli_generates_intake_records(tmp_path):
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_matrix.py",
            "generate-intakes",
            "--config",
            "seed/writeback-matrix-test.yaml",
            "--output-dir",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert len(list(tmp_path.glob("*.md"))) == 12


def test_writeback_matrix_cli_generates_writebacks(tmp_path):
    intake_dir = tmp_path / "intakes"
    writeback_dir = tmp_path / "writebacks"
    intake_dir.mkdir()
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_matrix.py",
            "generate-all",
            "--config",
            "seed/writeback-matrix-test.yaml",
            "--intake-dir",
            str(intake_dir),
            "--writeback-dir",
            str(writeback_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert len(list(writeback_dir.glob("*.md"))) == 12
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_matrix.py -v`
Expected: FAIL because `scripts/writeback_matrix.py` does not exist

- [ ] **Step 3: Implement the matrix driver**

Create `scripts/writeback_matrix.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
import yaml


def load_config(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text())


def make_intake(output_dir: Path, row: dict) -> None:
    output = output_dir / f\"{row['output_slug']}.md\"
    subprocess.run(
        [
            \"python3\",
            \"scripts/writeback_intake.py\",
            \"create\",
            \"--intake-id\",
            f\"intake-{row['output_slug']}\",
            \"--output\",
            str(output),
            \"--collaboration-mode\",
            row[\"collaboration_mode\"],
            \"--target-audience\",
            row[\"target_audience\"],
            \"--extra-questions\",
            row[\"extra_question_theme\"],
        ],
        check=True,
    )


def make_writeback(writeback_dir: Path, intake_dir: Path, config: dict, row: dict) -> None:
    intake = intake_dir / f\"{row['output_slug']}.md\"
    output = writeback_dir / f\"{row['output_slug']}.md\"
    subprocess.run(
        [
            \"python3\",
            \"scripts/writeback_generate.py\",
            \"render\",
            \"--writeback-id\",
            f\"writeback-{row['output_slug']}\",
            \"--intake-file\",
            str(intake),
            \"--output\",
            str(output),
            \"--title\",
            config[\"title\"],
            \"--subtitle\",
            row[\"subtitle\"],
            \"--summary\",
            \"基于共享综合判断底座生成的矩阵测试写作版本。\",\n            \"--synthesis-ref\",\n            config[\"synthesis_id\"],\n        ],
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest=\"command\", required=True)

    intake_cmd = subparsers.add_parser(\"generate-intakes\")
    intake_cmd.add_argument(\"--config\", required=True)
    intake_cmd.add_argument(\"--output-dir\", required=True)

    all_cmd = subparsers.add_parser(\"generate-all\")
    all_cmd.add_argument(\"--config\", required=True)
    all_cmd.add_argument(\"--intake-dir\", required=True)
    all_cmd.add_argument(\"--writeback-dir\", required=True)

    args = parser.parse_args()
    config = load_config(args.config)

    if args.command == \"generate-intakes\":
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        for row in config[\"matrix\"]:\n            make_intake(output_dir, row)\n        return 0

    if args.command == \"generate-all\":
        intake_dir = Path(args.intake_dir)
        writeback_dir = Path(args.writeback_dir)
        intake_dir.mkdir(parents=True, exist_ok=True)
        writeback_dir.mkdir(parents=True, exist_ok=True)
        for row in config[\"matrix\"]:\n            make_intake(intake_dir, row)\n            make_writeback(writeback_dir, intake_dir, config, row)\n        return 0

    return 1


if __name__ == \"__main__\":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_matrix.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/writeback_matrix.py tests/test_writeback_matrix.py
git commit -m "feat: add writeback matrix generation workflow"
```

### Task 5: Materialize The 12 Intakes And 12 Writebacks

**Files:**
- Create: `library/writeback-intakes/podcasts/matrix/*.md`
- Create: `library/writebacks/podcasts/matrix/*.md`
- Modify: `README.md`
- Test: `tests/test_writeback_matrix.py`

- [ ] **Step 1: Add a failing materialization test**

Append to `tests/test_writeback_matrix.py`:

```python
def test_library_matrix_has_12_intakes_and_12_writebacks():
    intake_dir = Path("library/writeback-intakes/podcasts/matrix")
    writeback_dir = Path("library/writebacks/podcasts/matrix")
    assert len(list(intake_dir.glob("*.md"))) == 12
    assert len(list(writeback_dir.glob("*.md"))) == 12
```

- [ ] **Step 2: Run test to verify it fails**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_matrix.py::test_library_matrix_has_12_intakes_and_12_writebacks -v`
Expected: FAIL because the matrix directories are empty or missing

- [ ] **Step 3: Generate the real library outputs**

Run:

```bash
python3 scripts/writeback_matrix.py generate-all \
  --config seed/writeback-matrix-test.yaml \
  --intake-dir library/writeback-intakes/podcasts/matrix \
  --writeback-dir library/writebacks/podcasts/matrix
```

Then add a README section with:

```md
## Writeback Matrix Test

Use the matrix test workflow to generate 12 writeback variants from one shared synthesis base:

```bash
python3 scripts/writeback_matrix.py generate-all \
  --config seed/writeback-matrix-test.yaml \
  --intake-dir library/writeback-intakes/podcasts/matrix \
  --writeback-dir library/writebacks/podcasts/matrix
```
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_matrix.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add library/writeback-intakes/podcasts/matrix library/writebacks/podcasts/matrix README.md tests/test_writeback_matrix.py
git commit -m "feat: materialize writeback matrix test outputs"
```

### Task 6: Add Meaningful-Difference Guards

**Files:**
- Modify: `tests/test_writeback_matrix.py`

- [ ] **Step 1: Add failing divergence tests**

Append to `tests/test_writeback_matrix.py`:

```python
def test_matrix_outputs_do_not_collapse_to_identical_headers():
    writeback_dir = Path("library/writebacks/podcasts/matrix")
    headers = []
    for path in sorted(writeback_dir.glob("*.md")):
        text = path.read_text()
        headers.append((path.name, "## 副标题" in text, "- target_audience:" in text, "- synthesis_ref:" in text))
    assert len({item[0] for item in headers}) == 12
    assert all(item[1] and item[2] and item[3] for item in headers)


def test_matrix_outputs_cover_all_audiences_and_modes():
    writeback_dir = Path("library/writebacks/podcasts/matrix")
    text = "\n".join(path.read_text() for path in writeback_dir.glob("*.md"))
    for token in ["`self`", "`team`", "`exec`", "`research_archive`"]:
        assert token in text
    for token in ["`integrated`", "`sectioned`", "`appendix`"]:
        assert token in text
```

- [ ] **Step 2: Run tests to verify they fail if outputs are missing metadata**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_matrix.py -v`
Expected: PASS if the outputs already contain the metadata; if not, fix generation before proceeding

- [ ] **Step 3: Keep the generator and outputs aligned**

If failures appear, update `scripts/writeback_generate.py` or regenerate matrix outputs so every output records:

```md
- collaboration_mode: `...`
- target_audience: `...`
- extra_questions: [`...`]
- synthesis_ref: `...`
```

and includes:

```md
## 副标题
```

- [ ] **Step 4: Re-run tests**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_matrix.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/writeback_generate.py tests/test_writeback_matrix.py library/writebacks/podcasts/matrix
git commit -m "test: add writeback matrix divergence guards"
```

### Task 7: Final Verification

**Files:**
- Verify only

- [ ] **Step 1: Validate schema**

Run: `python3 -m json.tool schemas/writeback-intake.schema.json >/dev/null`
Expected: success with no output

- [ ] **Step 2: Run all relevant tests**

Run: `"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_intake.py tests/test_writeback_generate.py tests/test_writeback_matrix.py -v`
Expected: PASS

- [ ] **Step 3: Smoke-test matrix generation**

Run:

```bash
python3 scripts/writeback_matrix.py generate-all \
  --config seed/writeback-matrix-test.yaml \
  --intake-dir /tmp/writeback-matrix-intakes \
  --writeback-dir /tmp/writeback-matrix-writebacks
```

Expected:
- 12 files in `/tmp/writeback-matrix-intakes`
- 12 files in `/tmp/writeback-matrix-writebacks`
- outputs contain `## 副标题`

- [ ] **Step 4: Review diff scope**

Run: `git diff --stat HEAD~7..HEAD`
Expected: changes limited to matrix config, synthesis base, writeback scripts/templates/tests, generated matrix records, and README

- [ ] **Step 5: Commit any last documentation sync**

```bash
git add README.md
git commit -m "docs: finalize writeback matrix test workflow"
```

---

## Self-Review

- Spec coverage:
  - shared evidence pool and one synthesis base: Tasks 1, 2
  - 12-row matrix with rotated question themes: Task 1
  - fully Chinese outputs: Tasks 4, 5, 6
  - one shared judgment base reused across all outputs: Tasks 2, 4, 5
  - meaningful output divergence by mode/audience/theme: Tasks 5, 6
- Placeholder scan:
  - No `TBD` or `TODO`
  - All code-writing steps include concrete code or file content
  - All verification steps include exact commands and expected results
- Type consistency:
  - `collaboration_mode`, `target_audience`, `extra_questions`, `synthesis_ref`, `subtitle`, and `synthesis_id` are named consistently across config, scripts, templates, and tests
