from pathlib import Path
import json


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
