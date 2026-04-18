# Search Relevance And Source Balancing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add search-stage relevance scoring and source balancing for `podwise` and `xiaohongshu`, so search results become reviewed source candidates that can be approved and handed into the existing ingestion and report flow.

**Architecture:** Introduce a shared search selection module that scores candidates using topic, ontology, authority, evidence richness, and hype penalty; then apply balancing rules before writing a reviewed candidate record. Extend `link_to_report.py` with `search-podwise` and `search-xiaohongshu` entry points, but keep approval explicit before ingestion.

**Tech Stack:** Python CLI scripts, Markdown candidate records, existing `watch-profile.yaml`, `link_to_report.py`, `link_to_report_lib.py`, and pytest.

---

### Task 1: Add shared relevance scoring utilities

**Files:**
- Create: `scripts/search_selection.py`
- Test: `tests/test_search_selection.py`

- [ ] **Step 1: Write the failing scoring tests**

```python
def test_score_candidate_records_component_scores():
    from scripts.search_selection import score_candidate

    candidate = {
        "title": "Galaxy AI true AI companion",
        "summary": "system-level ai companion with cross-app workflow",
        "platform": "podwise",
        "source_type": "structured_commentary",
        "authority_level": "structured_commentary",
    }
    profile = {
        "domains": ["agent", "ai"],
        "brands": ["Samsung", "Galaxy"],
        "active_topics": ["AI 手机", "系统级智能体"],
        "candidate_rules": {"downgrade_if_contains": ["颠覆一切"]},
        "authority_rules": {"preferred_channel_bonus": 2, "preferred_speaker_bonus": 2},
    }
    scored = score_candidate(candidate, topic="AI 手机", research_direction="系统级 agent", watch_profile=profile)

    assert scored["relevance_score"] > 0
    assert scored["topic_matches"]
    assert "workflow" in scored["ontology_matches"] or scored["ontology_matches"]
    assert scored["authority_level"] == "structured_commentary"
```

```python
def test_score_candidate_applies_hype_penalty():
    from scripts.search_selection import score_candidate

    candidate = {
        "title": "AI 手机将颠覆一切",
        "summary": "遥遥领先 彻底改变世界",
        "platform": "xiaohongshu",
        "source_type": "social_signal",
        "authority_level": "social_signal",
    }
    profile = {
        "domains": ["agent"],
        "brands": [],
        "active_topics": ["AI 手机"],
        "candidate_rules": {"downgrade_if_contains": ["颠覆一切", "遥遥领先", "彻底改变世界"]},
        "authority_rules": {},
    }
    scored = score_candidate(candidate, topic="AI 手机", research_direction="", watch_profile=profile)

    assert scored["hype_penalty"] > 0
    assert scored["downgrade_reasons"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_search_selection.py -q
```

Expected: FAIL because `scripts/search_selection.py` does not exist yet.

- [ ] **Step 3: Implement minimal shared scoring**

Create `scripts/search_selection.py` with:

```python
from __future__ import annotations

import re
from typing import Any


ONTOLOGY_HINTS = {
    "capability": ["能力", "capability", "功能边界"],
    "workflow": ["workflow", "工作流", "跨应用", "一步直达", "执行"],
    "governance": ["治理", "权限", "审核", "控制", "责任"],
    "trust": ["信任", "解释", "前台", "可解释"],
    "coordination": ["协作", "角色", "分工", "protocol", "协调"],
    "device_boundary": ["设备", "生态", "robot phone", "人车家", "系统级"],
}


def _text(candidate: dict[str, Any]) -> str:
    return " ".join(str(candidate.get(key, "")) for key in ("title", "summary", "body", "notes")).lower()


def _matches(text: str, items: list[str]) -> list[str]:
    return [item for item in items if item and item.lower() in text]


def score_candidate(candidate: dict[str, Any], *, topic: str, research_direction: str, watch_profile: dict[str, Any]) -> dict[str, Any]:
    text = _text(candidate)
    topic_matches = []
    for section in ("domains", "brands", "active_topics"):
        topic_matches.extend(_matches(text, list(watch_profile.get(section, []))))
    if topic and topic.lower() in text:
        topic_matches.append(topic)
    if research_direction:
        topic_matches.extend([token for token in re.split(r"[\\s，,。；;]+", research_direction) if token and token.lower() in text])

    ontology_matches = [name for name, hints in ONTOLOGY_HINTS.items() if any(h.lower() in text for h in hints)]
    downgrade_phrases = list(watch_profile.get("candidate_rules", {}).get("downgrade_if_contains", []))
    downgrade_reasons = [phrase for phrase in downgrade_phrases if phrase.lower() in text]
    hype_penalty = len(downgrade_reasons)

    authority_level = str(candidate.get("authority_level") or candidate.get("authority") or "social_signal")
    authority_map = {"official": 3, "first_hand_operator": 2, "structured_commentary": 1, "social_signal": 0}
    authority_score = authority_map.get(authority_level, 0)

    evidence_richness = 0
    if candidate.get("has_transcript"):
        evidence_richness += 2
    if candidate.get("has_highlights"):
        evidence_richness += 1
    if candidate.get("has_full_text") or candidate.get("body"):
        evidence_richness += 1

    relevance_score = len(set(topic_matches)) + len(ontology_matches) + authority_score + evidence_richness - hype_penalty
    return {
        **candidate,
        "relevance_score": relevance_score,
        "topic_matches": sorted(set(topic_matches)),
        "ontology_matches": ontology_matches,
        "authority_level": authority_level,
        "evidence_richness": evidence_richness,
        "hype_penalty": hype_penalty,
        "downgrade_reasons": downgrade_reasons,
    }
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_search_selection.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/search_selection.py tests/test_search_selection.py
git commit -m "feat: add shared search relevance scoring"
```

### Task 2: Add source balancing utilities

**Files:**
- Modify: `scripts/search_selection.py`
- Modify: `tests/test_search_selection.py`

- [ ] **Step 1: Write the failing balancing tests**

```python
def test_balance_candidates_limits_single_brand_domination():
    from scripts.search_selection import balance_candidates

    candidates = [
        {"candidate_id": "1", "brand": "Samsung", "platform": "podwise", "authority_level": "official", "relevance_score": 9},
        {"candidate_id": "2", "brand": "Samsung", "platform": "podwise", "authority_level": "official", "relevance_score": 8},
        {"candidate_id": "3", "brand": "Xiaomi", "platform": "xiaohongshu", "authority_level": "structured_commentary", "relevance_score": 7},
        {"candidate_id": "4", "brand": "HONOR", "platform": "xiaohongshu", "authority_level": "social_signal", "relevance_score": 6},
    ]

    balanced = balance_candidates(candidates, comparative=True)

    brands = [item["brand"] for item in balanced]
    assert "Xiaomi" in brands
    assert "HONOR" in brands
    assert brands.count("Samsung") <= 2
```

```python
def test_balance_candidates_preserves_strong_unbalanced_set_when_coverage_is_weak():
    from scripts.search_selection import balance_candidates

    candidates = [
        {"candidate_id": "1", "brand": "Samsung", "platform": "podwise", "authority_level": "official", "relevance_score": 9},
        {"candidate_id": "2", "brand": "Samsung", "platform": "podwise", "authority_level": "official", "relevance_score": 8},
    ]

    balanced = balance_candidates(candidates, comparative=True)

    assert len(balanced) == 2
    assert all(item["brand"] == "Samsung" for item in balanced)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_search_selection.py -q
```

Expected: FAIL because `balance_candidates` is not implemented yet.

- [ ] **Step 3: Implement minimal balancing**

Add to `scripts/search_selection.py`:

```python
def balance_candidates(candidates: list[dict[str, Any]], *, comparative: bool) -> list[dict[str, Any]]:
    ordered = sorted(candidates, key=lambda item: item.get("relevance_score", 0), reverse=True)
    if not comparative:
        return ordered

    selected: list[dict[str, Any]] = []
    brand_counts: dict[str, int] = {}
    platform_seen: set[str] = set()

    for candidate in ordered:
        brand = str(candidate.get("brand") or "unknown")
        platform = str(candidate.get("platform") or "unknown")
        if brand_counts.get(brand, 0) >= 2 and len({item.get("brand") for item in ordered}) >= 3:
            continue
        selected.append(candidate)
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
        platform_seen.add(platform)

    if len(selected) < min(len(ordered), 3):
        return ordered
    return selected
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_search_selection.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/search_selection.py tests/test_search_selection.py
git commit -m "feat: add source balancing rules"
```

### Task 3: Add reviewed candidate record rendering

**Files:**
- Modify: `scripts/search_selection.py`
- Test: `tests/test_search_selection.py`

- [ ] **Step 1: Write the failing rendering test**

```python
def test_render_search_selection_record_includes_scores_and_reasons():
    from scripts.search_selection import render_search_selection_record

    text = render_search_selection_record(
        request_id="ai-phone-search",
        source="podwise",
        topic="AI 手机",
        candidates=[
            {
                "candidate_id": "pod-1",
                "title": "Galaxy AI as agentic companion",
                "url": "https://podwise.ai/dashboard/episodes/demo",
                "platform": "podwise",
                "source_type": "podcast_episode",
                "authority_level": "structured_commentary",
                "relevance_score": 8,
                "topic_matches": ["AI 手机"],
                "ontology_matches": ["workflow", "device_boundary"],
                "evidence_richness": 3,
                "downgrade_reasons": [],
                "coverage_role": "core",
            }
        ],
    )

    assert "# Search Selection Record" in text
    assert "relevance_score" in text
    assert "ontology_matches" in text
    assert "coverage_role" in text
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_search_selection.py -q
```

Expected: FAIL because `render_search_selection_record` is missing.

- [ ] **Step 3: Implement record rendering**

Add to `scripts/search_selection.py`:

```python
def render_search_selection_record(*, request_id: str, source: str, topic: str, candidates: list[dict[str, Any]]) -> str:
    lines = [
        "# Search Selection Record",
        "",
        f"- request_id: `{request_id}`",
        f"- source: `{source}`",
        f"- topic: `{topic}`",
        "",
    ]
    for item in candidates:
        lines.extend(
            [
                "## Candidate",
                "",
                f"- candidate_id: `{item['candidate_id']}`",
                f"- title: `{item['title']}`",
                f"- url: `{item['url']}`",
                f"- platform: `{item['platform']}`",
                f"- source_type: `{item['source_type']}`",
                f"- authority_level: `{item['authority_level']}`",
                f"- relevance_score: `{item['relevance_score']}`",
                f"- topic_matches: `{', '.join(item.get('topic_matches', []))}`",
                f"- ontology_matches: `{', '.join(item.get('ontology_matches', []))}`",
                f"- evidence_richness: `{item.get('evidence_richness', 0)}`",
                f"- downgrade_reasons: `{', '.join(item.get('downgrade_reasons', []))}`",
                f"- coverage_role: `{item.get('coverage_role', 'core')}`",
                "",
            ]
        )
    return "\n".join(lines)
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_search_selection.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/search_selection.py tests/test_search_selection.py
git commit -m "feat: add reviewed search selection records"
```

### Task 4: Add CLI entry points for podwise and xiaohongshu search

**Files:**
- Modify: `scripts/link_to_report.py`
- Modify: `scripts/link_to_report_lib.py`
- Modify: `tests/test_link_to_report.py`

- [ ] **Step 1: Write failing CLI tests**

```python
def test_link_to_report_help_shows_search_commands():
    result = run_cli("--help")
    assert "search-podwise" in result.stdout
    assert "search-xiaohongshu" in result.stdout
```

```python
def test_search_commands_write_selection_record(tmp_path, monkeypatch):
    import scripts.link_to_report_lib as lib
    monkeypatch.setattr(lib, "SEARCH_SELECTION_ROOT", tmp_path)
    monkeypatch.setattr(
        lib,
        "search_podwise_candidates",
        lambda query, limit, watch_profile: [{"candidate_id": "pod-1", "title": "demo", "url": "https://podwise.ai/dashboard/episodes/demo", "platform": "podwise", "source_type": "podcast_episode", "authority_level": "structured_commentary", "relevance_score": 7, "topic_matches": ["AI 手机"], "ontology_matches": ["workflow"], "evidence_richness": 3, "downgrade_reasons": [], "coverage_role": "core"}],
    )
    result = lib.command_search_podwise(argparse.Namespace(request_id="ai-phone", topic="AI 手机", research_direction="", limit=5))
    assert result == 0
    assert (tmp_path / "ai-phone" / "podwise.md").exists()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k "search_podwise or search_xiaohongshu or shows_search_commands" -q
```

Expected: FAIL because the CLI commands do not exist yet.

- [ ] **Step 3: Implement minimal CLI plumbing**

Modify `scripts/link_to_report.py` to add:

```python
search_podwise = subparsers.add_parser("search-podwise", help="Search podwise and write a scored candidate record.")
search_podwise.add_argument("--request-id", required=True)
search_podwise.add_argument("--topic", required=True)
search_podwise.add_argument("--research-direction", default="")
search_podwise.add_argument("--limit", type=int, default=10)

search_xhs = subparsers.add_parser("search-xiaohongshu", help="Search xiaohongshu and write a scored candidate record.")
search_xhs.add_argument("--request-id", required=True)
search_xhs.add_argument("--topic", required=True)
search_xhs.add_argument("--research-direction", default="")
search_xhs.add_argument("--limit", type=int, default=10)
```

Modify `scripts/link_to_report_lib.py` to add:

```python
SEARCH_SELECTION_ROOT = ROOT / "library" / "sessions" / "search-selection"
search_selection = load_script_module("search_selection.py", "search_selection")
```

and command handlers that:

- load `seed/watch-profile.yaml`
- call placeholder search functions
- score and balance results
- write records under `library/sessions/search-selection/<request-id>/podwise.md` and `.../xiaohongshu.md`

Use stub search functions in MVP:

```python
def search_podwise_candidates(query: str, limit: int, watch_profile: dict[str, object]) -> list[dict[str, object]]:
    return []

def search_xiaohongshu_candidates(query: str, limit: int, watch_profile: dict[str, object]) -> list[dict[str, object]]:
    return []
```

These exist so the scoring and record flow can land first; real CLI calls come in the next task.

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k "search_podwise or search_xiaohongshu or shows_search_commands" -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/link_to_report.py scripts/link_to_report_lib.py tests/test_link_to_report.py
git commit -m "feat: add search selection cli entry points"
```

### Task 5: Connect search output to approval and ingestion

**Files:**
- Modify: `scripts/link_to_report_lib.py`
- Modify: `tests/test_link_to_report.py`

- [ ] **Step 1: Write the failing approval test**

```python
def test_approve_search_candidates_hands_selected_urls_to_ingest_bundle(tmp_path, monkeypatch):
    import scripts.link_to_report_lib as lib

    selection_root = tmp_path / "search-selection"
    record_dir = selection_root / "ai-phone"
    record_dir.mkdir(parents=True)
    (record_dir / "podwise.md").write_text(
        "# Search Selection Record\n\n## Candidate\n\n- candidate_id: `pod-1`\n- title: `demo`\n- url: `https://podwise.ai/dashboard/episodes/demo`\n- platform: `podwise`\n- source_type: `podcast_episode`\n- authority_level: `structured_commentary`\n- relevance_score: `7`\n- topic_matches: `AI 手机`\n- ontology_matches: `workflow`\n- evidence_richness: `3`\n- downgrade_reasons: ``\n- coverage_role: `core`\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(lib, "SEARCH_SELECTION_ROOT", selection_root)
    captured = {}
    monkeypatch.setattr(lib, "command_ingest_links", lambda args: captured.setdefault("links", list(args.links)) or 0)

    result = lib.command_approve_search_candidates(argparse.Namespace(request_id="ai-phone", bundle_id="ai-phone-bundle", candidate_ids=["pod-1"]))

    assert result == 0
    assert captured["links"] == ["https://podwise.ai/dashboard/episodes/demo"]
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k approve_search_candidates -q
```

Expected: FAIL because approval by candidate id is missing.

- [ ] **Step 3: Implement approval by candidate id**

Add to `scripts/link_to_report.py`:

```python
approve_search = subparsers.add_parser("approve-search-candidates", help="Approve scored search candidates into a bundle.")
approve_search.add_argument("--request-id", required=True)
approve_search.add_argument("--bundle-id", required=True)
approve_search.add_argument("candidate_ids", nargs="+")
```

Add to `scripts/link_to_report_lib.py`:

```python
def command_approve_search_candidates(args: argparse.Namespace) -> int:
    ...
```

Behavior:

- read all selection records under `library/sessions/search-selection/<request-id>/`
- map `candidate_id -> url`
- hand approved URLs to existing `command_ingest_links`

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_link_to_report.py -k approve_search_candidates -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/link_to_report.py scripts/link_to_report_lib.py tests/test_link_to_report.py
git commit -m "feat: add approval flow for search candidates"
```

### Task 6: Document and verify the end-to-end search-selection flow

**Files:**
- Modify: `README.md`
- Test: `tests/test_search_selection.py`
- Test: `tests/test_link_to_report.py`
- Test: `tests/test_link_to_report_real_ingestion.py`

- [ ] **Step 1: Add README usage**

Append a section like:

```md
## Search Relevance And Source Balancing

Use search when you want scored source candidates before ingestion:

```bash
python3 scripts/link_to_report.py search-podwise --request-id ai-phone --topic "AI 手机" --research-direction "系统级 agent"
python3 scripts/link_to_report.py search-xiaohongshu --request-id ai-phone --topic "AI 手机" --research-direction "系统级 agent"
python3 scripts/link_to_report.py approve-search-candidates --request-id ai-phone --bundle-id ai-phone-bundle pod-1 xhs-2
```

Search creates reviewed candidate records under `library/sessions/search-selection/`.
Approved candidates still flow through `Source -> Artifact -> Review Pack -> Writeback`.
```

- [ ] **Step 2: Run the relevant test slice**

Run:

```bash
"/Users/vickyshou/.local/bin/uv" run --offline --with pytest python -m pytest tests/test_search_selection.py tests/test_link_to_report.py tests/test_link_to_report_real_ingestion.py -q
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add README.md tests/test_search_selection.py tests/test_link_to_report.py tests/test_link_to_report_real_ingestion.py
git commit -m "docs: add search relevance workflow usage"
```

## Spec Coverage Check

- shared relevance model: Tasks 1 and 2
- reviewed candidate record: Task 3
- podwise/xiaohongshu search entry points: Task 4
- approval before ingestion: Task 5
- reuse of existing downstream flow: Tasks 5 and 6

## Placeholder Scan

- no `TODO` / `TBD`
- all new functions named explicitly
- all commands and expected outputs are included

## Type Consistency Check

- `relevance_score`, `topic_matches`, `ontology_matches`, `authority_level`, `evidence_richness`, `downgrade_reasons`, and `coverage_role` are used consistently in tests, rendering, and approval flow.
