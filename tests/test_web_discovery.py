from pathlib import Path
import importlib.util


def load_web_discovery():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "web_discovery.py"
    spec = importlib.util.spec_from_file_location("web_discovery", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_normalize_source_candidate_contains_required_fields():
    mod = load_web_discovery()

    candidate = mod.normalize_source_candidate(
        title="Google Gemini on Android",
        url="https://blog.google/products/android/gemini-android/",
        source_type="official_update",
        platform="official_site",
        authority="official",
        why_relevant="Covers Gemini as an on-device/system AI entry point.",
    )

    assert candidate["title"] == "Google Gemini on Android"
    assert candidate["url"] == "https://blog.google/products/android/gemini-android/"
    assert candidate["source_type"] == "official_update"
    assert candidate["platform"] == "official_site"
    assert candidate["authority"] == "official"
    assert candidate["why_relevant"]


def test_render_discovery_record_groups_candidates_by_authority():
    mod = load_web_discovery()
    text = mod.render_discovery_record(
        request_id="ai-phone-demo",
        mode="discovery",
        topic="AI 手机",
        candidates=[
            {
                "title": "Apple Intelligence",
                "url": "https://www.apple.com/apple-intelligence/",
                "source_type": "official_update",
                "platform": "official_site",
                "authority": "official",
                "why_relevant": "Official product framing.",
            },
            {
                "title": "AI 手机综述",
                "url": "https://example.com/ai-phone-overview",
                "source_type": "structured_commentary",
                "platform": "web",
                "authority": "structured_commentary",
                "why_relevant": "Cross-vendor comparison.",
            },
        ],
    )

    assert "# Web Discovery Record" in text
    assert "## Official" in text
    assert "## Structured Commentary" in text
    assert "Apple Intelligence" in text
    assert "AI 手机综述" in text
