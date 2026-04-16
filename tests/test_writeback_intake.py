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
