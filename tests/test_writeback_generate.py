from pathlib import Path


def test_sample_reviews_exist_for_promoted_podcast_claim():
    assert Path("library/reviews/podcasts/review-product-podwise-ai-7650271-dfb97270-16.md").exists()
    assert Path("library/reviews/podcasts/review-ux-podwise-ai-7650271-dfb97270-16.md").exists()
    assert Path("library/reviews/podcasts/review-contrarian-podwise-ai-7650271-dfb97270-16.md").exists()
    assert Path("library/verdicts/podcasts/verdict-podwise-ai-7650271-dfb97270-16.md").exists()
