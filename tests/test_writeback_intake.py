from pathlib import Path
import json
import subprocess


def test_writeback_intake_schema_exists():
    path = Path("schemas/writeback-intake.schema.json")
    assert path.exists(), "missing writeback intake schema"


def test_writeback_templates_are_not_placeholders():
    intake_template = Path("templates/writeback-intake.md").read_text()
    writeback_template = Path("templates/writeback-proposal.md").read_text()
    assert "intake_id" in intake_template
    assert "collaboration_mode" in writeback_template
    assert "used_default_rules" in writeback_template


def test_writeback_intake_schema_matches_relaxed_requirements():
    schema = json.loads(Path("schemas/writeback-intake.schema.json").read_text())
    assert schema["required"] == ["intake_id"]
    assert schema["properties"]["collaboration_mode"]["enum"] == [
        "integrated",
        "sectioned",
        "appendix",
        None,
    ]
    assert "used_default_rules" in schema["properties"]


def test_writeback_intake_cli_writes_default_record(tmp_path):
    target = tmp_path / "intake.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_intake.py",
            "create",
            "--intake-id",
            "intake-demo",
            "--output",
            str(target),
            "--use-defaults",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- intake_id: `intake-demo`" in text
    assert "- used_default_rules: `true`" in text


def test_writeback_intake_cli_preserves_user_fields(tmp_path):
    target = tmp_path / "intake.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_intake.py",
            "create",
            "--intake-id",
            "intake-demo",
            "--output",
            str(target),
            "--collaboration-mode",
            "sectioned",
            "--focus-priority",
            "mechanism,user_trust",
            "--special-attention",
            "memory continuity",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- collaboration_mode: `sectioned`" in text
    assert "- used_default_rules: `false`" in text
    assert "`mechanism`" in text and "`user_trust`" in text


def test_writeback_intake_cli_treats_empty_parsed_lists_as_default(tmp_path):
    target = tmp_path / "intake.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_intake.py",
            "create",
            "--intake-id",
            "intake-demo",
            "--output",
            str(target),
            "--focus-priority",
            ",",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- used_default_rules: `true`" in text


def test_writeback_intake_cli_rejects_invalid_collaboration_mode(tmp_path):
    target = tmp_path / "intake.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_intake.py",
            "create",
            "--intake-id",
            "intake-demo",
            "--output",
            str(target),
            "--collaboration-mode",
            "narrative",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "invalid choice" in result.stderr


def test_writeback_intake_cli_records_audience_and_extra_questions(tmp_path):
    target = tmp_path / "intake.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_intake.py",
            "create",
            "--intake-id",
            "intake-demo",
            "--output",
            str(target),
            "--target-audience",
            "team",
            "--extra-questions",
            "这是不是范式迁移",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- target_audience: `team`" in text
    assert "`这是不是范式迁移`" in text


def test_writeback_intake_cli_records_research_direction_and_status(tmp_path):
    target = tmp_path / "intake.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_intake.py",
            "create",
            "--intake-id",
            "intake-research-demo",
            "--output",
            str(target),
            "--collaboration-mode",
            "integrated",
            "--target-audience",
            "team",
            "--research-direction",
            "multi-agent 是否已经从高级 workflow 包装进入可治理的 Agent Team 范式迁移",
            "--direction-status",
            "user_provided",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- research_direction: `multi-agent 是否已经从高级 workflow 包装进入可治理的 Agent Team 范式迁移`" in text
    assert "- direction_status: `user_provided`" in text


def test_writeback_intake_cli_research_direction_disables_default_rules(tmp_path):
    target = tmp_path / "intake.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_intake.py",
            "create",
            "--intake-id",
            "intake-research-default-check",
            "--output",
            str(target),
            "--research-direction",
            "multi-agent 是否已经从高级 workflow 包装进入可治理的 Agent Team 范式迁移",
            "--direction-status",
            "user_provided",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- research_direction: `multi-agent 是否已经从高级 workflow 包装进入可治理的 Agent Team 范式迁移`" in text
    assert "- direction_status: `user_provided`" in text
    assert "- used_default_rules: `false`" in text
