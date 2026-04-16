from pathlib import Path


def test_sample_reviews_exist_for_promoted_podcast_claim():
    product_review = Path("library/reviews/podcasts/review-product-podwise-ai-7650271-dfb97270-16.md").read_text()
    ux_review = Path("library/reviews/podcasts/review-ux-podwise-ai-7650271-dfb97270-16.md").read_text()
    contrarian_review = Path("library/reviews/podcasts/review-contrarian-podwise-ai-7650271-dfb97270-16.md").read_text()
    verdict = Path("library/verdicts/podcasts/verdict-podwise-ai-7650271-dfb97270-16.md").read_text()

    assert "- target_id: `claim-podwise-ai-7650271-dfb97270-16`" in product_review
    assert "- target_id: `claim-podwise-ai-7650271-dfb97270-16`" in ux_review
    assert "- target_id: `claim-podwise-ai-7650271-dfb97270-16`" in contrarian_review
    assert "- produces_verdict_id: `verdict-podwise-ai-7650271-dfb97270-16`" in product_review
    assert "- produces_verdict_id: `verdict-podwise-ai-7650271-dfb97270-16`" in ux_review
    assert "- produces_verdict_id: `verdict-podwise-ai-7650271-dfb97270-16`" in contrarian_review
    assert "- target_id: `claim-podwise-ai-7650271-dfb97270-16`" in verdict
    assert "- outcome: `supported_with_preserved_tension`" in verdict
