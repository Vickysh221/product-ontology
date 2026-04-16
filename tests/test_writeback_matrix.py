from pathlib import Path
import subprocess
import yaml


def matrix_writeback_paths() -> list[Path]:
    writeback_dir = Path("library/writebacks/podcasts/matrix")
    return sorted(
        path
        for path in writeback_dir.glob("*.md")
        if path.name != "integrated-team-paradigm.md"
    )


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


def test_shared_synthesis_record_exists():
    path = Path("library/syntheses/podcasts/agent-team-governability-2026-04.md")
    assert path.exists()


def test_shared_synthesis_mentions_all_five_episode_slugs():
    text = Path("library/syntheses/podcasts/agent-team-governability-2026-04.md").read_text()
    assert "- synthesis_id: `synthesis-podcasts-agent-team-governability-2026-04`" in text
    assert "- status: `draft`" in text
    assert "## 核心综合判断" in text
    assert "## 稳定主题" in text
    assert "## 证据汇总" in text
    assert "## 保留张力" in text
    for slug in [
        "podwise-ai-7758431-2cd3ef48",
        "podwise-ai-7718625-7d0dc7d1",
        "podwise-ai-7635732-bdfba3f3",
        "podwise-ai-7504915-91b52a0e",
        "podwise-ai-7368984-f9a0fefa",
    ]:
        assert slug in text


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
    assert len(list(intake_dir.glob("*.md"))) == 12
    assert len(list(writeback_dir.glob("*.md"))) == 12
    sample_writeback = sorted(writeback_dir.glob("*.md"))[0].read_text()
    assert "- synthesis_ref:" in sample_writeback
    assert "- target_audience:" in sample_writeback
    assert "## 副标题" in sample_writeback


def test_library_matrix_has_12_intakes_and_12_writebacks():
    intake_dir = Path("library/writeback-intakes/podcasts/matrix")
    assert len(list(intake_dir.glob("*.md"))) == 12
    assert len(matrix_writeback_paths()) == 12
    sample_intake = sorted(intake_dir.glob("*.md"))[0].read_text()
    sample_writeback = matrix_writeback_paths()[0].read_text()
    assert "- collaboration_mode:" in sample_intake
    assert "- target_audience:" in sample_intake
    assert "- extra_questions:" in sample_intake
    assert "- synthesis_ref:" in sample_writeback
    assert "- target_audience:" in sample_writeback
    assert "## 副标题" in sample_writeback


def test_matrix_outputs_do_not_collapse_to_identical_headers():
    headers = []
    for path in matrix_writeback_paths():
        text = path.read_text()
        headers.append((path.name, "## 副标题" in text, "- target_audience:" in text, "- synthesis_ref:" in text))
    assert len({item[0] for item in headers}) == 12
    assert all(item[1] and item[2] and item[3] for item in headers)


def test_matrix_outputs_cover_all_audiences_and_modes():
    text = "\n".join(path.read_text() for path in matrix_writeback_paths())
    for token in ["`self`", "`team`", "`exec`", "`research_archive`"]:
        assert token in text
    for token in ["`integrated`", "`sectioned`", "`appendix`"]:
        assert token in text
