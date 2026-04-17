import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest


def load_link_to_report_lib_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts/link_to_report_lib.py"
    spec = importlib.util.spec_from_file_location("link_to_report_lib", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cleanup_bundle_outputs(lib, bundle_id: str):
    bundle_dir = lib.bundle_dir(bundle_id)
    if bundle_dir.exists():
        for path in bundle_dir.rglob("*"):
            if path.is_file():
                path.unlink()
        for path in sorted((p for p in bundle_dir.rglob("*") if p.is_dir()), reverse=True):
            path.rmdir()
        bundle_dir.rmdir()


def test_ingestion_adapters_cover_supported_real_ingestion_types():
    lib = load_link_to_report_lib_module()

    assert "podcast" in lib.INGESTION_ADAPTERS
    assert "xiaohongshu" in lib.INGESTION_ADAPTERS
    assert "web" in lib.INGESTION_ADAPTERS


def test_import_episode_returns_slug(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    podcast_import = lib.podcast_import
    monkeypatch.setattr(podcast_import, "ROOT", tmp_path)
    monkeypatch.setattr(podcast_import, "SOURCES_DIR", tmp_path / "library" / "sources" / "podcasts")
    monkeypatch.setattr(podcast_import, "ARTIFACTS_DIR", tmp_path / "library" / "artifacts" / "podcasts")
    monkeypatch.setattr(podcast_import, "run_podwise", lambda args: "stub output")

    slug = podcast_import.import_episode("https://podcasts.apple.com/us/podcast/example/id123", force=True)

    assert isinstance(slug, str)
    assert slug


def test_import_note_url_returns_slug(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    xhs_import = lib.xiaohongshu_redbook_import
    monkeypatch.setattr(xhs_import, "ROOT", tmp_path)

    include_comments_values: list[bool] = []

    def fake_pull_with_redbook(args):
        include_comments_values.append(args.include_comments)
        return 0

    monkeypatch.setattr(xhs_import, "pull_with_redbook", fake_pull_with_redbook)

    slug = xhs_import.import_note_url("https://www.xiaohongshu.com/explore/123", force=True)
    slug_with_comments_enabled = xhs_import.import_note_url(
        "https://www.xiaohongshu.com/explore/123",
        force=True,
        include_comments=True,
    )

    assert isinstance(slug, str)
    assert slug
    assert isinstance(slug_with_comments_enabled, str)
    assert slug_with_comments_enabled
    assert include_comments_values == [False, True]


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


def test_official_ingest_fails_without_fetchable_content(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    monkeypatch.setattr(lib, "ROOT", tmp_path)
    monkeypatch.setattr(lib, "load_official_target_urls", lambda: ["https://openai.com/news/"])
    monkeypatch.setattr(lib, "fetch_official_content", lambda link: None)

    with pytest.raises(ValueError, match="official content fetch unavailable"):
        lib.ingest_official_link("https://openai.com/news/", force=False)


def test_official_ingest_returns_source_and_artifact_paths_when_content_available(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    monkeypatch.setattr(lib, "ROOT", tmp_path)
    monkeypatch.setattr(lib, "load_official_target_urls", lambda: ["https://openai.com/news/"])
    monkeypatch.setattr(lib, "fetch_official_content", lambda link: "real official page body")

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


def test_propose_direction_uses_bundle_outputs_and_marks_pending(tmp_path):
    lib = load_link_to_report_lib_module()
    workspace_root = tmp_path / "workspace"
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(lib, "ROOT", workspace_root)
    monkeypatch.setattr(lib, "LINK_TO_REPORT_ROOT", workspace_root / "library" / "sessions" / "link-to-report")
    bundle_id = "bundle-output-direction"
    try:
        cleanup_bundle_outputs(lib, bundle_id)
        bundle_dir = lib.bundle_dir(bundle_id)
        bundle_dir.mkdir(parents=True, exist_ok=True)
        (bundle_dir / "run-summary.md").write_text(
            "\n".join(
                [
                    "# Link Bundle Run Summary",
                    "",
                    f"- bundle_id: `{bundle_id}`",
                    "- dry_run: `false`",
                    "- successful_link_count: `1`",
                    "- failed_link_count: `0`",
                    "- source_paths: [`library/sources/podcasts/demo.md`]",
                    "- artifact_paths: [`library/artifacts/podcasts/demo/transcript.md`]",
                    "",
                    "## Per-Link Results",
                    "",
                    "### Link Result",
                    "",
                    "- link: `https://podcasts.apple.com/us/podcast/example/id123`",
                    "- link_type: `podcast`",
                    "- status: `success`",
                    "- source_path: `library/sources/podcasts/demo.md`",
                    "- artifact_paths: [`library/artifacts/podcasts/demo/transcript.md`]",
                    "- failure_reason: ``",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        result = lib.command_propose_direction(argparse.Namespace(bundle_id=bundle_id, direction=""))
        assert result == 0
        text = (bundle_dir / "direction.md").read_text(encoding="utf-8")
        assert "- direction_status: `system_suggested_pending`" in text
        assert "podcast" in text
        assert "transcript" in text
        assert "library/sources/podcasts/demo.md" not in text
    finally:
        cleanup_bundle_outputs(lib, bundle_id)
        monkeypatch.undo()


def test_generate_report_uses_reusable_report_builders(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    workspace_root = tmp_path / "workspace"
    monkeypatch.setattr(lib, "ROOT", workspace_root)
    monkeypatch.setattr(lib, "LINK_TO_REPORT_ROOT", workspace_root / "library" / "sessions" / "link-to-report")
    monkeypatch.setattr(lib, "INTAKE_ROOT", workspace_root / "library" / "writeback-intakes" / "link-to-report")
    monkeypatch.setattr(lib, "REVIEW_PACK_ROOT", workspace_root / "library" / "review-packs" / "link-to-report")
    monkeypatch.setattr(lib, "WRITEBACK_ROOT", workspace_root / "library" / "writebacks" / "link-to-report")
    bundle_id = "bundle-report-builders"
    bundle_dir = lib.bundle_dir(bundle_id)
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "run-summary.md").write_text(
        "\n".join(
            [
                "# Link Bundle Run Summary",
                "",
                f"- bundle_id: `{bundle_id}`",
                "- dry_run: `false`",
                "- successful_link_count: `1`",
                "- failed_link_count: `0`",
                "- source_paths: [`library/sources/podcasts/demo.md`]",
                "- artifact_paths: [`library/artifacts/podcasts/demo/transcript.md`]",
                "",
                "## Per-Link Results",
                "",
                "### Link Result",
                "",
                "- link: `https://podcasts.apple.com/us/podcast/example/id123`",
                "- link_type: `podcast`",
                "- status: `success`",
                "- source_path: `library/sources/podcasts/demo.md`",
                "- artifact_paths: [`library/artifacts/podcasts/demo/transcript.md`]",
                "- failure_reason: ``",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bundle_dir / "direction.md").write_text(
        "# Research Direction Record\n\n- bundle_id: `bundle-report-builders`\n- research_direction: `bundle-aware direction`\n- direction_status: `user_provided`\n",
        encoding="utf-8",
    )
    calls: dict[str, object] = {}

    def fake_generate_real_review_pack(**kwargs):
        calls["review_pack"] = kwargs
        return "review-pack-from-writer"

    def fake_generate_real_writeback(**kwargs):
        calls["writeback"] = kwargs
        return "writeback-from-writer"

    monkeypatch.setattr(lib.writeback_generate, "generate_real_review_pack", fake_generate_real_review_pack)
    monkeypatch.setattr(lib.writeback_generate, "generate_real_writeback", fake_generate_real_writeback)

    result = lib.command_generate_report(
        argparse.Namespace(
            bundle_id=bundle_id,
            direction="bundle-aware direction",
            direction_file="",
            review_pack_output="",
            writeback_output="",
        )
    )

    assert result == 0
    assert calls["review_pack"]["source_paths"] == ["library/sources/podcasts/demo.md"]
    assert calls["review_pack"]["artifact_paths"] == ["library/artifacts/podcasts/demo/transcript.md"]
    assert calls["writeback"]["source_paths"] == ["library/sources/podcasts/demo.md"]
    assert calls["writeback"]["artifact_paths"] == ["library/artifacts/podcasts/demo/transcript.md"]
    assert (lib.REVIEW_PACK_ROOT / f"{bundle_id}.md").read_text(encoding="utf-8") == "review-pack-from-writer"
    assert (lib.WRITEBACK_ROOT / f"{bundle_id}.md").read_text(encoding="utf-8") == "writeback-from-writer"
    assert "MVP 占位" not in (lib.REVIEW_PACK_ROOT / f"{bundle_id}.md").read_text(encoding="utf-8")
    cleanup_bundle_outputs(lib, bundle_id)


def test_render_writeback_from_bundle_keeps_research_direction_metadata_single_line():
    lib = load_link_to_report_lib_module()

    text = lib.writeback_generate.render_writeback_from_bundle(
        bundle_id="bundle-writeback-shape",
        source_paths=["library/sources/podcasts/demo.md"],
        artifact_paths=["library/artifacts/podcasts/demo/transcript.md"],
        direction_text="bundle-aware direction",
        direction_status="user_provided",
        links=["https://podcasts.apple.com/us/podcast/example/id123"],
        link_types=["podcast"],
        link_results=[
            {
                "link": "https://podcasts.apple.com/us/podcast/example/id123",
                "link_type": "podcast",
                "status": "success",
                "source_path": "library/sources/podcasts/demo.md",
                "artifact_paths": ["library/artifacts/podcasts/demo/transcript.md"],
                "failure_reason": "",
            }
        ],
    )

    assert "- research_direction: `bundle-aware direction`" in text
    assert "## 本轮 Research Direction" in text
    assert "- 当前状态：" in text


def test_generate_report_preserves_per_link_lineage_for_reusable_builders(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    workspace_root = tmp_path / "workspace"
    monkeypatch.setattr(lib, "ROOT", workspace_root)
    monkeypatch.setattr(lib, "LINK_TO_REPORT_ROOT", workspace_root / "library" / "sessions" / "link-to-report")
    monkeypatch.setattr(lib, "INTAKE_ROOT", workspace_root / "library" / "writeback-intakes" / "link-to-report")
    monkeypatch.setattr(lib, "REVIEW_PACK_ROOT", workspace_root / "library" / "review-packs" / "link-to-report")
    monkeypatch.setattr(lib, "WRITEBACK_ROOT", workspace_root / "library" / "writebacks" / "link-to-report")
    bundle_id = "bundle-lineage"
    bundle_dir = lib.bundle_dir(bundle_id)
    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "run-summary.md").write_text(
        "\n".join(
            [
                "# Link Bundle Run Summary",
                "",
                f"- bundle_id: `{bundle_id}`",
                "- dry_run: `false`",
                "- successful_link_count: `2`",
                "- failed_link_count: `0`",
                "- source_paths: [`library/sources/xiaohongshu/xhs.md`, `library/sources/podcasts/pod.md`]",
                "- artifact_paths: [`library/artifacts/xiaohongshu/xhs/full_text.md`, `library/artifacts/xiaohongshu/xhs/comment_batch.md`, `library/artifacts/podcasts/pod/transcript.md`]",
                "",
                "## Per-Link Results",
                "",
                "### Link Result",
                "",
                "- link: `https://www.xiaohongshu.com/explore/123`",
                "- link_type: `xiaohongshu`",
                "- status: `success`",
                "- source_path: `library/sources/xiaohongshu/xhs.md`",
                "- artifact_paths: [`library/artifacts/xiaohongshu/xhs/full_text.md`, `library/artifacts/xiaohongshu/xhs/comment_batch.md`]",
                "- failure_reason: ``",
                "",
                "### Link Result",
                "",
                "- link: `https://podcasts.apple.com/us/podcast/example/id123`",
                "- link_type: `podcast`",
                "- status: `success`",
                "- source_path: `library/sources/podcasts/pod.md`",
                "- artifact_paths: [`library/artifacts/podcasts/pod/transcript.md`]",
                "- failure_reason: ``",
                "",
            ]
        ),
        encoding="utf-8",
    )
    calls: dict[str, object] = {}

    def fake_generate_real_review_pack(**kwargs):
        calls["review_pack"] = kwargs
        return "review-pack-from-writer"

    def fake_generate_real_writeback(**kwargs):
        calls["writeback"] = kwargs
        return "writeback-from-writer"

    monkeypatch.setattr(lib.writeback_generate, "generate_real_review_pack", fake_generate_real_review_pack)
    monkeypatch.setattr(lib.writeback_generate, "generate_real_writeback", fake_generate_real_writeback)

    result = lib.command_generate_report(
        argparse.Namespace(
            bundle_id=bundle_id,
            direction="bundle-aware direction",
            direction_file="",
            review_pack_output="",
            writeback_output="",
        )
    )

    assert result == 0
    review_lineage = calls["review_pack"]["link_results"]
    writeback_lineage = calls["writeback"]["link_results"]
    assert review_lineage[0]["link_type"] == "xiaohongshu"
    assert review_lineage[0]["artifact_paths"] == [
        "library/artifacts/xiaohongshu/xhs/full_text.md",
        "library/artifacts/xiaohongshu/xhs/comment_batch.md",
    ]
    assert review_lineage[1]["link_type"] == "podcast"
    assert review_lineage[1]["artifact_paths"] == ["library/artifacts/podcasts/pod/transcript.md"]
    assert writeback_lineage == review_lineage
    cleanup_bundle_outputs(lib, bundle_id)


def test_real_ingestion_end_to_end_smoke(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    workspace_root = tmp_path / "workspace"
    monkeypatch.setattr(lib, "ROOT", workspace_root)
    monkeypatch.setattr(lib, "LINK_TO_REPORT_ROOT", workspace_root / "library" / "sessions" / "link-to-report")
    monkeypatch.setattr(lib, "INTAKE_ROOT", workspace_root / "library" / "writeback-intakes" / "link-to-report")
    monkeypatch.setattr(lib, "REVIEW_PACK_ROOT", workspace_root / "library" / "review-packs" / "link-to-report")
    monkeypatch.setattr(lib, "WRITEBACK_ROOT", workspace_root / "library" / "writebacks" / "link-to-report")
    monkeypatch.setattr(lib, "load_official_target_urls", lambda: ["https://openai.com/news/"])
    monkeypatch.setattr(lib.source_ingest, "ROOT", workspace_root)
    monkeypatch.setattr(lib.source_ingest, "SOURCES_ROOT", workspace_root / "library" / "sources")
    monkeypatch.setattr(lib.source_ingest, "ARTIFACTS_ROOT", workspace_root / "library" / "artifacts")
    monkeypatch.setattr(lib, "fetch_official_content", lambda link: None)

    podcast_import = lib.podcast_import
    monkeypatch.setattr(podcast_import, "ROOT", workspace_root)
    monkeypatch.setattr(podcast_import, "SOURCES_DIR", workspace_root / "library" / "sources" / "podcasts")
    monkeypatch.setattr(podcast_import, "ARTIFACTS_DIR", workspace_root / "library" / "artifacts" / "podcasts")
    monkeypatch.setattr(
        podcast_import,
        "run_podwise",
        lambda args: {
            ("process", "https://podcasts.apple.com/us/podcast/example/id123"): "processed",
            ("get", "transcript", "https://podcasts.apple.com/us/podcast/example/id123"): "podcast transcript",
            ("get", "summary", "https://podcasts.apple.com/us/podcast/example/id123"): "podcast summary",
            ("get", "highlights", "https://podcasts.apple.com/us/podcast/example/id123"): "podcast highlights",
        }.get(tuple(args), "podwise output"),
    )

    xhs_import = lib.xiaohongshu_redbook_import
    monkeypatch.setattr(xhs_import, "ROOT", workspace_root)

    def fake_pull_with_redbook(args):
        args.body = "xiaohongshu body"
        args.comments_body = "xiaohongshu comments"
        args.body_file = ""
        args.comments_file = ""
        return xhs_import.import_note(args)

    monkeypatch.setattr(xhs_import, "pull_with_redbook", fake_pull_with_redbook)

    links = [
        "https://podcasts.apple.com/us/podcast/example/id123",
        "https://www.xiaohongshu.com/explore/123",
        "https://openai.com/news/",
    ]
    bundle_id = "real-ingestion-smoke"
    cleanup_bundle_outputs(lib, bundle_id)
    try:
        result = lib.command_ingest_links(
            argparse.Namespace(links=links, bundle_id=bundle_id, dry_run=False, force=False)
        )
        assert result == 0
        summary_path = lib.run_summary_path(bundle_id)
        summary_text = summary_path.read_text(encoding="utf-8")
        parsed_results = lib.parse_link_result_blocks(summary_text)
        assert [entry["status"] for entry in parsed_results] == ["success", "success", "failed"]
        assert "library/sources/podcasts" in summary_text
        assert "library/sources/xiaohongshu" in summary_text
        assert "official content fetch unavailable" in summary_text

        propose = lib.command_propose_direction(argparse.Namespace(bundle_id=bundle_id, direction=""))
        assert propose == 0
        direction_path = lib.direction_path(bundle_id)
        direction_text = direction_path.read_text(encoding="utf-8")
        assert "- direction_status: `system_suggested_pending`" in direction_text
        approved_direction_text = direction_text.replace(
            "- direction_status: `system_suggested_pending`",
            "- direction_status: `user_provided`",
        )
        direction_path.write_text(approved_direction_text, encoding="utf-8")

        generate = lib.command_generate_report(
            argparse.Namespace(
                bundle_id=bundle_id,
                direction="",
                direction_file=str(direction_path),
                review_pack_output="",
                writeback_output="",
            )
        )
        assert generate == 0
        intake_text = (lib.INTAKE_ROOT / f"{bundle_id}.md").read_text(encoding="utf-8")
        review_pack_text = (lib.REVIEW_PACK_ROOT / f"{bundle_id}.md").read_text(encoding="utf-8")
        writeback_text = (lib.WRITEBACK_ROOT / f"{bundle_id}.md").read_text(encoding="utf-8")
        assert "- link_count: `2`" in intake_text
        assert "- direction_status: `user_provided`" in intake_text
        assert "direction_status: `user_provided`" in review_pack_text
        assert "direction_status: `user_provided`" in writeback_text
        assert "MVP 占位" not in review_pack_text
        assert "MVP 占位" not in writeback_text
    finally:
        cleanup_bundle_outputs(lib, bundle_id)


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
