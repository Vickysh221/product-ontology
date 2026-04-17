import argparse
import importlib.util
from pathlib import Path


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

    def ingest_podcast_link(link_url: str, bundle_name: str):
        source_path = workspace_root / "library" / "sources" / "podcasts" / f"{bundle_name}.md"
        artifact_path = workspace_root / "library" / "artifacts" / "podcasts" / bundle_name / "transcript.md"
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
        argparse.Namespace(links=[link], bundle_id=bundle_id, dry_run=False)
    )

    assert result == 0
    summary_path = link_root / bundle_id / "run-summary.md"
    text = summary_path.read_text(encoding="utf-8")
    assert "- successful_link_count: `1`" in text
    assert "- failed_link_count: `0`" in text
    assert "library/sources/podcasts/demo.md" in text
    assert "library/artifacts/podcasts/demo/transcript.md" in text
