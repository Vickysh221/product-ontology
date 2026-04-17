# Generation Mechanism Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace pilot-specific quality patching in the writeback generator with a reusable evidence-role and cluster-composition mechanism for the `integrated-team-paradigm` pilot.

**Architecture:** Keep the current `research direction -> review pack -> writeback` chain, but insert explicit intermediate objects for evidence candidates, evidence roles, theme clusters, review objects, and final writeback objects. Keep scope locked to the pilot while proving that better output now comes from generation logic instead of hardcoded prose.

**Tech Stack:** Python 3, argparse, pathlib, regex parsing, pytest, existing Markdown artifacts under `library/`, and the current generator in `scripts/writeback_generate.py`

---

## File Structure

### Existing files to modify

- `scripts/writeback_generate.py`
  - Replace pilot hardcoded prose blocks with evidence-role composition helpers
  - Build structured cluster, review, and final writeback objects
- `tests/test_writeback_generate.py`
  - Add mechanism-quality regressions
- `library/review-packs/podcasts/review-pack-agent-team-paradigm.md`
  - Regenerate the pilot review pack
- `library/writebacks/podcasts/matrix/integrated-team-paradigm.md`
  - Regenerate the pilot final writeback

### Scope lock

Do not modify:
- `scripts/writeback_intake.py`
- any matrix-wide output path
- any ontology file
- any unrelated review-pack or writeback artifact

This implementation is only for the one pilot.

---

### Task 1: Add failing tests for evidence-role-based cluster composition

**Files:**
- Modify: `tests/test_writeback_generate.py`

- [ ] **Step 1: Write the failing test for evidence-role markers inside the review-pack build path**

Add a test in `tests/test_writeback_generate.py` that runs `render-review-pack` and asserts the materialized pilot review pack includes evidence-role diversity signals rather than only identical quote slots.

Use this shape:

```python
def test_materialized_review_pack_clusters_use_mixed_evidence_roles(tmp_path):
    result, target = run_render_review_pack(tmp_path)
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "### 主题：" in text
    assert text.count("**Direct quote") >= 3
    assert "Counter-signal" in text or "保留分歧" in text or "反向信号" in text
```

- [ ] **Step 2: Write the failing test for counter-signal preservation**

Add a test in `tests/test_writeback_generate.py`:

```python
def test_materialized_review_pack_preserves_counter_signal(tmp_path):
    result, target = run_render_review_pack(tmp_path)
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "## Counter-Signals And Tensions" in text
    assert "multi-agent" in text
```

- [ ] **Step 3: Run the targeted tests to confirm failure**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k "mixed_evidence_roles or preserves_counter_signal" -v
```

Expected:
- FAIL because the current pilot review pack is still rendered from hardcoded cluster prose rather than evidence-role composition

- [ ] **Step 4: Commit**

```bash
git add tests/test_writeback_generate.py
git commit -m "test: add failing mechanism-level review pack checks"
```

### Task 2: Introduce evidence candidate and evidence role helpers

**Files:**
- Modify: `scripts/writeback_generate.py`
- Test: `tests/test_writeback_generate.py`

- [ ] **Step 1: Add typed intermediate helper constructors**

Add helpers near the parsing utilities in `scripts/writeback_generate.py`:

```python
def build_evidence_candidate(slug: str, source_type: str, text: str) -> dict[str, str]:
    return {
        "slug": slug,
        "source_type": source_type,
        "text": text.strip(),
    }


def assign_evidence_roles(text: str) -> list[str]:
    roles: list[str] = []
    normalized = text.lower()
    if re.search(r"\[[0-9:]+\]", text):
        roles.append("speaker_force_quote")
    if any(term in normalized for term in ["权限", "审核", "测试", "sandbox", "review"]):
        roles.append("governance_signal")
    if any(term in normalized for term in ["协作", "角色", "员工", "异步", "分工"]):
        roles.append("mechanism_signal")
    if any(term in normalized for term in ["前台", "体验", "环境", "责任", "attention", "ux"]):
        roles.append("ux_surface_signal")
    if any(term in normalized for term in ["过渡", "仍待验证", "瓶颈", "不确定"]):
        roles.append("counter_signal")
    return roles or ["mechanism_signal"]
```

- [ ] **Step 2: Add a candidate collector for each pilot episode**

Add:

```python
def collect_pilot_evidence_candidates(slug: str) -> list[dict[str, object]]:
    evidence = collect_evidence_for_episode(slug)
    candidates: list[dict[str, object]] = []
    for source_type in ["highlights", "summary"]:
        for line in evidence[source_type][:8]:
            text = strip_number_prefix(line)
            if not text:
                continue
            candidates.append(
                {
                    **build_evidence_candidate(slug, source_type, text),
                    "roles": assign_evidence_roles(text),
                }
            )
    return candidates
```

- [ ] **Step 3: Run the existing review-pack tests and confirm failure moves forward**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k "review_pack or mixed_evidence_roles or preserves_counter_signal" -v
```

Expected:
- FAIL later in rendering because the new helpers exist but are not yet wired into cluster composition

- [ ] **Step 4: Commit**

```bash
git add scripts/writeback_generate.py tests/test_writeback_generate.py
git commit -m "feat: add evidence candidate and role helpers"
```

### Task 3: Replace hardcoded pilot cluster prose with composed cluster objects

**Files:**
- Modify: `scripts/writeback_generate.py`
- Test: `tests/test_writeback_generate.py`

- [ ] **Step 1: Replace `PILOT_REVIEW_PACK_THEME_CLUSTERS` with a cluster schema**

Refactor the pilot constant to store only:
- cluster title
- target slugs
- preferred role mix
- question-facing description

Use a shape like:

```python
PILOT_CLUSTER_SCHEMAS = [
    {
        "title": "执行控制层",
        "slugs": ["podwise-ai-7758431-2cd3ef48", "podwise-ai-7368984-f9a0fefa"],
        "preferred_roles": ["speaker_force_quote", "governance_signal", "mechanism_signal"],
    },
    ...
]
```

- [ ] **Step 2: Build composed cluster objects from candidates**

Add a helper:

```python
def build_pilot_cluster(schema: dict[str, object], research_direction: str) -> dict[str, object]:
    candidates: list[dict[str, object]] = []
    for slug in schema["slugs"]:
        candidates.extend(collect_pilot_evidence_candidates(str(slug)))
    selected_quotes = [c for c in candidates if "speaker_force_quote" in c["roles"]][:2]
    support_signals = [c for c in candidates if "mechanism_signal" in c["roles"] or "governance_signal" in c["roles"]]
    counter_signals = [c for c in candidates if "counter_signal" in c["roles"]]
    return {
        "title": schema["title"],
        "quotes": selected_quotes,
        "support_signals": support_signals[:2],
        "counter_signals": counter_signals[:1],
        "paraphrase": f"围绕“{research_direction}”，这组材料共同把讨论推进到{schema['title']}这一层，而不再只是分散观点。",
        "why": f"{schema['title']}之所以重要，是因为它直接改变了研究问题在产品结构中的解释方式。",
    }
```

- [ ] **Step 3: Update review-pack rendering to consume composed clusters**

Update `build_pilot_review_pack_sections()` so that it:
- builds cluster objects from schemas
- renders quotes from `selected_quotes`
- renders evidence from selected quote and support-signal slugs
- appends cluster-level counter-signals into the tensions section

- [ ] **Step 4: Run targeted tests and make sure they pass**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k "review_pack or mixed_evidence_roles or preserves_counter_signal" -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/writeback_generate.py tests/test_writeback_generate.py library/review-packs/podcasts/review-pack-agent-team-paradigm.md
git commit -m "feat: compose pilot review clusters from evidence roles"
```

### Task 4: Add failing tests for final-writeback derivation quality

**Files:**
- Modify: `tests/test_writeback_generate.py`

- [ ] **Step 1: Write the failing test for non-restated synthesis**

Add:

```python
def test_materialized_pilot_writeback_judgment_is_not_direct_review_restating(tmp_path):
    review_result, review_target = run_render_review_pack(tmp_path)
    longform_result, longform_target = run_render_longform(tmp_path)
    assert review_result.returncode == 0, review_result.stderr
    assert longform_result.returncode == 0, longform_result.stderr
    review_text = review_target.read_text()
    longform_text = longform_target.read_text()
    assert "## 综合判断" in longform_text
    assert review_text.count("Paraphrase") >= 3
```

- [ ] **Step 2: Write the failing test for UX proposition traceability**

Add:

```python
def test_materialized_pilot_writeback_ux_section_is_cluster_traceable(tmp_path):
    result, target = run_render_longform(tmp_path)
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "责任状态卡" in text
    assert "分级决策卡" in text
    assert "异步沟通面板" in text
    assert "审计与证据抽屉" in text
```

- [ ] **Step 3: Run the targeted tests to confirm failure**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k "not_direct_review_restating or cluster_traceable" -v
```

Expected:
- FAIL because the current final writeback still derives too directly from fixed prose helpers

- [ ] **Step 4: Commit**

```bash
git add tests/test_writeback_generate.py
git commit -m "test: add failing final-writeback mechanism checks"
```

### Task 5: Split final writeback generation into review-derived section objects

**Files:**
- Modify: `scripts/writeback_generate.py`
- Modify: `library/writebacks/podcasts/matrix/integrated-team-paradigm.md`
- Test: `tests/test_writeback_generate.py`

- [ ] **Step 1: Add explicit final section builders from review objects**

Refactor the final writeback path so it first builds a `review_object`, then derives:
- `judgment_object`
- `problem_object`
- `assumption_object`
- `ux_object`

Each builder should consume review-derived inputs rather than fixed pilot prose constants.

- [ ] **Step 2: Make `Problem Statement` and `Assumptions` depend on role-aware clusters**

Update the builders so:
- governance-heavy clusters shape `Problem Statement`
- supported assumptions depend on repeated mechanism and governance signals
- open assumptions depend on counter-signals and unresolved tensions

- [ ] **Step 3: Make AI-native UX propositions depend on cluster evidence**

Update the UX builder so:
- execution-control evidence yields `责任状态卡` or `审计与证据抽屉`
- collaboration-role evidence yields `异步沟通面板`
- governance and escalation evidence yield `分级决策卡`

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

- [ ] **Step 5: Run targeted tests and make sure they pass**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_writeback_generate.py -k "longform or not_direct_review_restating or cluster_traceable or review_pack" -v
```

Expected:
- PASS

- [ ] **Step 6: Commit**

```bash
git add scripts/writeback_generate.py tests/test_writeback_generate.py library/review-packs/podcasts/review-pack-agent-team-paradigm.md library/writebacks/podcasts/matrix/integrated-team-paradigm.md
git commit -m "feat: derive pilot final writeback from evidence-composed review objects"
```

### Task 6: Run full pilot verification and inspect regenerated artifacts

**Files:**
- Modify: `library/review-packs/podcasts/review-pack-agent-team-paradigm.md`
- Modify: `library/writebacks/podcasts/matrix/integrated-team-paradigm.md`
- Test: `tests/test_writeback_generate.py`

- [ ] **Step 1: Run the full relevant test suite**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest --with pyyaml python -m pytest tests/test_writeback_generate.py tests/test_writeback_matrix.py -v
```

Expected:
- PASS

- [ ] **Step 2: Inspect the regenerated pilot artifacts for mechanism-level quality**

Check that the regenerated review pack and final writeback now show:
- quote retention before synthesis
- visibly different roles across evidence items
- preserved tensions that look derived rather than fixed
- UX propositions that feel grounded in earlier review sections

- [ ] **Step 3: Commit**

```bash
git add library/review-packs/podcasts/review-pack-agent-team-paradigm.md library/writebacks/podcasts/matrix/integrated-team-paradigm.md
git commit -m "chore: regenerate pilot artifacts after mechanism upgrade"
```

## Exit Criteria

Do not call this complete until all of the following are true:
- the pilot review pack is evidence-composed instead of mostly prewritten
- the final writeback sections come from distinct review-derived objects
- counter-signals survive into the final output
- UX propositions are traceable to reviewed evidence
- tests enforce mechanism quality rather than only headings and keywords
