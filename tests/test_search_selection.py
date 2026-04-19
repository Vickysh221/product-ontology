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
        "preferred_sources": {"channels": ["AI炼金术"], "speakers": ["Sam Altman"]},
        "authority_rules": {"preferred_channel_bonus": 2, "preferred_speaker_bonus": 2},
    }
    scored = mod.score_candidate(candidate, topic="AI 手机", research_direction="系统级 agent", watch_profile=profile)

    assert scored["relevance_score"] > 0
    assert scored["topic_matches"]
    assert "workflow" in scored["ontology_matches"] or scored["ontology_matches"]
    assert scored["authority_level"] == "structured_commentary"


def test_score_candidate_reuses_watch_profile_authority_rules():
    mod = load_search_selection()

    candidate = {
        "title": "Sam Altman on AI 手机",
        "summary": "deep operator commentary",
        "platform": "podwise",
        "source_type": "first_hand_interview",
        "authority_level": "structured_commentary",
        "speaker_name": "Sam Altman",
        "channel_name": "AI炼金术",
    }
    profile = {
        "domains": ["ai"],
        "brands": [],
        "active_topics": ["AI 手机"],
        "preferred_sources": {"channels": ["AI炼金术"], "speakers": ["Sam Altman"]},
        "authority_rules": {
            "source_types": {"first_hand_interview": 3},
            "preferred_channel_bonus": 2,
            "preferred_speaker_bonus": 2,
        },
        "candidate_rules": {},
    }

    scored = mod.score_candidate(candidate, topic="AI 手机", research_direction="", watch_profile=profile)

    assert scored["authority_score"] >= 8


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


def test_balance_candidates_keeps_source_type_and_authority_mix_when_available():
    mod = load_search_selection()

    candidates = [
        {"candidate_id": "1", "brand": "Samsung", "platform": "podwise", "source_type": "podcast_episode", "authority_level": "official", "relevance_score": 9},
        {"candidate_id": "2", "brand": "Samsung", "platform": "podwise", "source_type": "podcast_episode", "authority_level": "official", "relevance_score": 8},
        {"candidate_id": "3", "brand": "Xiaomi", "platform": "xiaohongshu", "source_type": "social_signal", "authority_level": "structured_commentary", "relevance_score": 7},
        {"candidate_id": "4", "brand": "HONOR", "platform": "xiaohongshu", "source_type": "social_signal", "authority_level": "social_signal", "relevance_score": 6},
    ]

    balanced = mod.balance_candidates(candidates, comparative=True)

    assert {item["source_type"] for item in balanced} >= {"podcast_episode", "social_signal"}
    assert {item["authority_level"] for item in balanced} >= {"official", "structured_commentary"}


def test_balance_candidates_still_checks_mix_with_two_brands():
    mod = load_search_selection()

    candidates = [
        {"candidate_id": "1", "brand": "Samsung", "platform": "podwise", "source_type": "podcast_episode", "authority_level": "official", "relevance_score": 9},
        {"candidate_id": "2", "brand": "Samsung", "platform": "podwise", "source_type": "podcast_episode", "authority_level": "official", "relevance_score": 8},
        {"candidate_id": "3", "brand": "Xiaomi", "platform": "xiaohongshu", "source_type": "social_signal", "authority_level": "structured_commentary", "relevance_score": 7},
    ]

    balanced = mod.balance_candidates(candidates, comparative=True)

    assert {item["source_type"] for item in balanced} >= {"podcast_episode", "social_signal"}
    assert {item["authority_level"] for item in balanced} >= {"official", "structured_commentary"}


def test_balance_candidates_limits_domination_in_two_brand_case():
    mod = load_search_selection()

    candidates = [
        {"candidate_id": "1", "brand": "Samsung", "platform": "podwise", "source_type": "podcast_episode", "authority_level": "official", "relevance_score": 10},
        {"candidate_id": "2", "brand": "Samsung", "platform": "podwise", "source_type": "podcast_episode", "authority_level": "official", "relevance_score": 9},
        {"candidate_id": "3", "brand": "Samsung", "platform": "podwise", "source_type": "podcast_episode", "authority_level": "official", "relevance_score": 8},
        {"candidate_id": "4", "brand": "Xiaomi", "platform": "xiaohongshu", "source_type": "social_signal", "authority_level": "structured_commentary", "relevance_score": 7},
    ]

    balanced = mod.balance_candidates(candidates, comparative=True)

    assert [item["brand"] for item in balanced].count("Samsung") <= 2
    assert "Xiaomi" in [item["brand"] for item in balanced]
