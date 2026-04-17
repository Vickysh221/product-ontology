import argparse
import importlib.util
import sys
from pathlib import Path

import pytest


def load_link_to_report_lib_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts/link_to_report_lib.py"
    scripts_dir = str(module_path.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location("link_to_report_lib", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_script_module(module_filename: str, module_name: str):
    module_path = Path(__file__).resolve().parents[1] / "scripts" / module_filename
    scripts_dir = str(module_path.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ingestion_adapters_cover_supported_real_ingestion_types():
    lib = load_link_to_report_lib_module()

    assert "podcast" in lib.INGESTION_ADAPTERS
    assert "xiaohongshu" in lib.INGESTION_ADAPTERS
    assert "web" in lib.INGESTION_ADAPTERS


def test_import_episode_returns_slug(tmp_path, monkeypatch):
    podcast_import = load_script_module("podcast_import.py", "podcast_import")
    monkeypatch.setattr(podcast_import, "ROOT", tmp_path)
    monkeypatch.setattr(podcast_import, "SOURCES_DIR", tmp_path / "library" / "sources" / "podcasts")
    monkeypatch.setattr(podcast_import, "ARTIFACTS_DIR", tmp_path / "library" / "artifacts" / "podcasts")
    monkeypatch.setattr(podcast_import, "run_podwise", lambda args: "stub output")

    slug = podcast_import.import_episode("https://podcasts.apple.com/us/podcast/example/id123", force=True)

    assert isinstance(slug, str)
    assert slug


def test_import_note_url_returns_slug(tmp_path, monkeypatch):
    xhs_import = load_script_module("xiaohongshu_redbook_import.py", "xiaohongshu_redbook_import")
    monkeypatch.setattr(xhs_import, "ROOT", tmp_path)
    monkeypatch.setattr(xhs_import, "pull_with_redbook", lambda args: 0)

    slug = xhs_import.import_note_url("https://www.xiaohongshu.com/explore/123", force=True)

    assert isinstance(slug, str)
    assert slug


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


def test_official_ingest_returns_source_and_artifact_paths(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    monkeypatch.setattr(lib, "ROOT", tmp_path)
    monkeypatch.setattr(lib, "load_official_target_urls", lambda: ["https://openai.com/news/"])

    def fake_write_source_record(**kwargs):
        path = tmp_path / "library" / "sources" / "official" / "demo.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("source", encoding="utf-8")
        return "source-official-demo", path, tmp_path / "library" / "artifacts" / "official" / "demo"

    def fake_write_artifact_record(**kwargs):
        path = tmp_path / "library" / "artifacts" / "official" / "demo" / "full_text.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(kwargs["body"], encoding="utf-8")
        return path

    monkeypatch.setattr(lib, "write_source_record", fake_write_source_record)
    monkeypatch.setattr(lib, "write_artifact_record", fake_write_artifact_record)

    result = lib.ingest_official_link("https://openai.com/news/", force=False)

    assert result["status"] == "success"
    assert result["source_path"].endswith("library/sources/official/demo.md")
    assert result["artifact_paths"] == ["library/artifacts/official/demo/full_text.md"]


def test_non_official_web_links_fail_cleanly(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    monkeypatch.setattr(lib, "ROOT", tmp_path)
    monkeypatch.setattr(lib, "LINK_TO_REPORT_ROOT", tmp_path / "library" / "sessions" / "link-to-report")
    monkeypatch.setattr(lib, "load_official_target_urls", lambda: ["https://openai.com/news/"])

    result = lib.command_ingest_links(
        argparse.Namespace(links=["https://example.com/blog/post"], bundle_id="demo", dry_run=False, force=False)
    )

    assert result == 0
    text = (tmp_path / "library" / "sessions" / "link-to-report" / "demo" / "run-summary.md").read_text(encoding="utf-8")
    parsed_results = lib.parse_link_result_blocks(text)
    assert len(parsed_results) == 1
    assert parsed_results[0]["status"] == "failed"
    assert "non-official" in parsed_results[0]["failure_reason"].lower()


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
