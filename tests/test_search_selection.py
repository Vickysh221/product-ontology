from pathlib import Path
import importlib.util


def load_search_selection():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "search_selection.py"
    spec = importlib.util.spec_from_file_location("search_selection", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_score_candidate_records_component_scores():
    mod = load_search_selection()

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
    scored = mod.score_candidate(candidate, topic="AI 手机", research_direction="系统级 agent", watch_profile=profile)

    assert scored["relevance_score"] > 0
    assert scored["topic_matches"]
    assert "workflow" in scored["ontology_matches"] or scored["ontology_matches"]
    assert scored["authority_level"] == "structured_commentary"


def test_score_candidate_applies_hype_penalty():
    mod = load_search_selection()

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
    scored = mod.score_candidate(candidate, topic="AI 手机", research_direction="", watch_profile=profile)

    assert scored["hype_penalty"] > 0
    assert scored["downgrade_reasons"]


def test_balance_candidates_limits_single_brand_domination():
    mod = load_search_selection()

    candidates = [
        {"candidate_id": "1", "brand": "Samsung", "platform": "podwise", "authority_level": "official", "relevance_score": 9},
        {"candidate_id": "2", "brand": "Samsung", "platform": "podwise", "authority_level": "official", "relevance_score": 8},
        {"candidate_id": "3", "brand": "Xiaomi", "platform": "xiaohongshu", "authority_level": "structured_commentary", "relevance_score": 7},
        {"candidate_id": "4", "brand": "HONOR", "platform": "xiaohongshu", "authority_level": "social_signal", "relevance_score": 6},
    ]

    balanced = mod.balance_candidates(candidates, comparative=True)

    brands = [item["brand"] for item in balanced]
    assert "Xiaomi" in brands
    assert "HONOR" in brands
    assert brands.count("Samsung") <= 2


def test_balance_candidates_preserves_strong_unbalanced_set_when_coverage_is_weak():
    mod = load_search_selection()

    candidates = [
        {"candidate_id": "1", "brand": "Samsung", "platform": "podwise", "authority_level": "official", "relevance_score": 9},
        {"candidate_id": "2", "brand": "Samsung", "platform": "podwise", "authority_level": "official", "relevance_score": 8},
    ]

    balanced = mod.balance_candidates(candidates, comparative=True)

    assert len(balanced) == 2
    assert all(item["brand"] == "Samsung" for item in balanced)
