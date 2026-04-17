from pathlib import Path
import importlib.util
import pytest


def load_artifact_evidence():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "artifact_evidence.py"
    spec = importlib.util.spec_from_file_location("artifact_evidence", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_collect_report_artifacts_prioritizes_podcast_summary_and_highlights(tmp_path):
    mod = load_artifact_evidence()
    artifact_root = tmp_path / "library" / "artifacts" / "podcasts" / "demo"
    artifact_root.mkdir(parents=True)
    (artifact_root / "summary.md").write_text("## Content\nsummary line\n", encoding="utf-8")
    (artifact_root / "highlights.md").write_text("## Content\n1. [00:31] key highlight\n", encoding="utf-8")
    (artifact_root / "transcript.md").write_text("## Content\n[00:31] long transcript line\n", encoding="utf-8")

    artifacts = mod.collect_report_artifacts(
        channel="podcasts",
        artifact_paths=[
            "library/artifacts/podcasts/demo/transcript.md",
            "library/artifacts/podcasts/demo/summary.md",
            "library/artifacts/podcasts/demo/highlights.md",
        ],
        root=tmp_path,
    )

    assert [item["slice_type"] for item in artifacts] == ["summary", "highlights", "transcript"]


def test_build_evidence_candidates_returns_required_schema_fields(tmp_path):
    mod = load_artifact_evidence()
    artifact_file = tmp_path / "library" / "artifacts" / "xiaohongshu" / "demo" / "full_text.md"
    artifact_file.parent.mkdir(parents=True)
    artifact_file.write_text(
        "## Content\nAgent 真正难的不是执行，而是跨轮次保持责任边界。\n",
        encoding="utf-8",
    )

    candidates = mod.build_evidence_candidates(
        research_direction="agent team 的责任边界如何被产品化",
        channel="xiaohongshu",
        artifact_items=[
            {
                "slice_type": "full_text",
                "path": artifact_file,
                "content": "Agent 真正难的不是执行，而是跨轮次保持责任边界。",
            }
        ],
    )

    candidate = candidates[0]
    assert candidate["research_direction"] == "agent team 的责任边界如何被产品化"
    assert candidate["quote"]
    assert candidate["paraphrase"]
    assert candidate["artifact_ref"].endswith("full_text.md")
    assert candidate["claim_role"] in {"support", "counter_signal", "tension", "open_question"}
    assert candidate["confidence"] in {"high", "medium", "low"}


def test_cluster_candidates_groups_by_theme_hint_and_limits_theme_count():
    mod = load_artifact_evidence()
    candidates = [
        {
            "candidate_id": "c1",
            "research_direction": "agent team 的责任边界如何被产品化",
            "theme_hint": "governance_or_control",
            "quote": "责任边界必须清楚。",
            "speaker_or_source": "podcast",
            "artifact_ref": "a.md",
            "why_selected": "control signal",
            "paraphrase": "这里讨论治理边界。",
            "claim_role": "support",
            "confidence": "high",
        },
        {
            "candidate_id": "c2",
            "research_direction": "agent team 的责任边界如何被产品化",
            "theme_hint": "coordination_protocol",
            "quote": "多个 agent 需要明确沟通协议。",
            "speaker_or_source": "podcast",
            "artifact_ref": "b.md",
            "why_selected": "coordination signal",
            "paraphrase": "这里讨论协作协议。",
            "claim_role": "support",
            "confidence": "high",
        },
    ]

    clusters = mod.cluster_evidence_candidates(candidates)

    assert len(clusters) == 2
    assert clusters[0]["theme"]
    assert clusters[0]["entries"]


def test_build_evidence_candidates_keeps_counter_signal_lines():
    mod = load_artifact_evidence()
    artifact_items = [
        {
            "slice_type": "comment_batch",
            "path": Path("library/artifacts/xiaohongshu/demo/comment_batch.md"),
            "content": "## Content\n这更像包装话术，并没有真正改变协作边界。\n",
        }
    ]

    candidates = mod.build_evidence_candidates(
        research_direction="multi-agent 是否进入范式迁移",
        channel="xiaohongshu",
        artifact_items=artifact_items,
    )

    assert candidates[0]["claim_role"] in {"counter_signal", "tension", "open_question", "support"}


def test_collect_report_artifacts_raises_when_artifact_is_missing(tmp_path):
    mod = load_artifact_evidence()

    with pytest.raises(FileNotFoundError, match="missing artifact paths"):
        mod.collect_report_artifacts(
            channel="podcasts",
            artifact_paths=["library/artifacts/podcasts/demo/summary.md"],
            root=tmp_path,
        )
