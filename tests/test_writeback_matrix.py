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
    assert {(row["collaboration_mode"], row["target_audience"]) for row in rows} == {
        ("integrated", "self"),
        ("integrated", "team"),
        ("integrated", "exec"),
        ("integrated", "research_archive"),
        ("sectioned", "self"),
        ("sectioned", "team"),
        ("sectioned", "exec"),
        ("sectioned", "research_archive"),
        ("appendix", "self"),
        ("appendix", "team"),
        ("appendix", "exec"),
        ("appendix", "research_archive"),
    }
