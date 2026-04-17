import argparse
import importlib.util
from pathlib import Path

import pytest


def load_link_to_report_lib_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts/link_to_report_lib.py"
    spec = importlib.util.spec_from_file_location("link_to_report_lib", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_summary_records_real_link_results(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    workspace_root = tmp_path / "workspace"
    link_root = workspace_root / "library" / "sessions" / "link-to-report"
    bundle_id = "demo"
    link = "https://podcasts.apple.com/us/podcast/example/id123"

    monkeypatch.setattr(lib, "ROOT", workspace_root)
    monkeypatch.setattr(lib, "LINK_TO_REPORT_ROOT", link_root)
    monkeypatch.setattr(lib, "detect_link_type", lambda _: "podcast")

    def ingest_podcast_link(link_url: str, force: bool = False):
        assert force is False
        source_path = workspace_root / "library" / "sources" / "podcasts" / "demo.md"
        artifact_path = workspace_root / "library" / "artifacts" / "podcasts" / "demo" / "transcript.md"
        source_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text("# source\n", encoding="utf-8")
        artifact_path.write_text("# transcript\n", encoding="utf-8")
        return {
            "link": link_url,
            "link_type": "podcast",
            "status": "success",
            "source_path": "library/sources/podcasts/demo.md",
            "artifact_paths": ["library/artifacts/podcasts/demo/transcript.md"],
            "failure_reason": "",
        }

    monkeypatch.setattr(lib, "INGESTION_ADAPTERS", {"podcast": ingest_podcast_link})

    result = lib.command_ingest_links(
        argparse.Namespace(links=[link], bundle_id=bundle_id, dry_run=False, force=False)
    )

    assert result == 0
    summary_path = link_root / bundle_id / "run-summary.md"
    text = summary_path.read_text(encoding="utf-8")
    parsed_results = lib.parse_link_result_blocks(text)
    assert len(parsed_results) == 1
    assert parsed_results[0]["link"] == link
    assert parsed_results[0]["link_type"] == "podcast"
    assert parsed_results[0]["status"] == "success"
    expected_lines = [
        "# Link Bundle Run Summary",
        f"- bundle_id: `{bundle_id}`",
        "- dry_run: `false`",
        "- successful_link_count: `1`",
        "- failed_link_count: `0`",
        "- source_paths: [`library/sources/podcasts/demo.md`]",
        "- artifact_paths: [`library/artifacts/podcasts/demo/transcript.md`]",
        "## Per-Link Results",
        "### Link Result",
        "- source_path: `library/sources/podcasts/demo.md`",
        "- artifact_paths: [`library/artifacts/podcasts/demo/transcript.md`]",
        "- failure_reason: ``",
    ]
    for line in expected_lines:
        assert line in text
    assert "### Link Result 1" not in text
    for line in ["- link_count:", "- link_types:", "- links:", "- successful_links:", "- failed_links:", "## Link Results"]:
        assert line not in text


@pytest.mark.parametrize(
    "bad_result, expected_error",
    [
        ({"status": "maybe", "source_path": "", "artifact_paths": [], "failure_reason": ""}, "unsupported status"),
        ({"status": "success", "source_path": "", "artifact_paths": "oops", "failure_reason": ""}, "artifact_paths"),
        ({"status": "success", "source_path": 1, "artifact_paths": [], "failure_reason": ""}, "source_path"),
        ({"status": "success", "source_path": "", "artifact_paths": [], "failure_reason": 1}, "failure_reason"),
    ],
)
def test_validate_ingestion_adapter_result_rejects_malformed_dict(bad_result, expected_error):
    lib = load_link_to_report_lib_module()
    with pytest.raises((TypeError, ValueError), match=expected_error):
        lib.validate_ingestion_adapter_result(bad_result, "https://podcasts.apple.com/us/podcast/example/id123", "podcast")


def test_command_ingest_links_records_failed_result_for_malformed_adapter_output(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    workspace_root = tmp_path / "workspace"
    monkeypatch.setattr(lib, "ROOT", workspace_root)
    monkeypatch.setattr(lib, "LINK_TO_REPORT_ROOT", workspace_root / "library" / "sessions" / "link-to-report")
    monkeypatch.setattr(lib, "detect_link_type", lambda _: "podcast")

    def adapter(link_url: str, force: bool = False):
        if "good" in link_url:
            return {
                "link": link_url,
                "link_type": "podcast",
                "status": "success",
                "source_path": "library/sources/podcasts/good.md",
                "artifact_paths": ["library/artifacts/podcasts/good/transcript.md"],
                "failure_reason": "",
            }
        return {
            "link": link_url,
            "link_type": "podcast",
            "status": "maybe",
            "source_path": "",
            "artifact_paths": [],
            "failure_reason": "",
        }

    monkeypatch.setattr(lib, "INGESTION_ADAPTERS", {"podcast": adapter})

    result = lib.command_ingest_links(
        argparse.Namespace(
            links=[
                "https://podcasts.apple.com/us/podcast/good/id123",
                "https://podcasts.apple.com/us/podcast/bad/id123",
            ],
            bundle_id="demo",
            dry_run=False,
            force=False,
        )
    )

    assert result == 0
    summary_path = workspace_root / "library" / "sessions" / "link-to-report" / "demo" / "run-summary.md"
    text = summary_path.read_text(encoding="utf-8")
    parsed_results = lib.parse_link_result_blocks(text)
    assert [entry["status"] for entry in parsed_results] == ["success", "failed"]
    assert "unsupported status" in text
