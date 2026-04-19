import argparse
import sys
import importlib.util
from pathlib import Path
import shutil
import subprocess


def load_link_to_report_lib_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts/link_to_report_lib.py"
    spec = importlib.util.spec_from_file_location("link_to_report_lib", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cleanup_bundle_outputs(lib, bundle_id: str):
    shutil.rmtree(lib.bundle_dir(bundle_id), ignore_errors=True)
    for root in [lib.INTAKE_ROOT, lib.REVIEW_PACK_ROOT, lib.WRITEBACK_ROOT]:
        path = root / f"{bundle_id}.md"
        if path.exists():
            path.unlink()


def test_link_to_report_help_lists_three_subcommands():
    result = subprocess.run(
        [sys.executable, "scripts/link_to_report.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "ingest-links" in result.stdout
    assert "propose-direction" in result.stdout
    assert "generate-report" in result.stdout


def test_link_to_report_help_shows_discovery_commands():
    result = subprocess.run(
        [sys.executable, "scripts/link_to_report.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "discover-web" in result.stdout
    assert "approve-sources" in result.stdout


def test_link_to_report_help_shows_search_commands():
    result = subprocess.run(
        [sys.executable, "scripts/link_to_report.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "search-podwise" in result.stdout
    assert "search-xiaohongshu" in result.stdout
    assert "approve-search-candidates" in result.stdout


def test_ingest_links_requires_at_least_one_link():
    result = subprocess.run(
        [sys.executable, "scripts/link_to_report.py", "ingest-links"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "links" in result.stderr.lower()


def test_generate_report_requires_direction_input(tmp_path):
    tmp_path.mkdir(exist_ok=True)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/link_to_report.py",
            "generate-report",
            "--bundle-id",
            "demo-bundle",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "direction" in result.stderr.lower()


def test_link_to_report_detect_link_type():
    lib = load_link_to_report_lib_module()

    assert lib.detect_link_type("https://www.xiaohongshu.com/explore/123") == "xiaohongshu"
    assert lib.detect_link_type("https://podcasts.apple.com/us/podcast/example/id123") == "podcast"
    assert lib.detect_link_type("https://mp.weixin.qq.com/s/example") == "wechat"
    assert lib.detect_link_type("/tmp/local-note.md") == "local-file"
    assert lib.detect_link_type("not-a-url") == "unknown"


def test_link_to_report_helpers_normalize_bundle_paths():
    lib = load_link_to_report_lib_module()

    assert lib.slugify_bundle_id(" Demo Bundle! ") == "demo-bundle"
    assert lib.slugify_bundle_id("!!!") == "bundle"
    assert lib.derive_bundle_id(["b", "a"], "") == lib.derive_bundle_id(["a", "b"], "")
    assert lib.bundle_dir("demo-bundle") == lib.LINK_TO_REPORT_ROOT / "demo-bundle"
    assert lib.run_summary_path("demo-bundle") == lib.LINK_TO_REPORT_ROOT / "demo-bundle" / "run-summary.md"
    assert lib.direction_path("demo-bundle") == lib.LINK_TO_REPORT_ROOT / "demo-bundle" / "direction.md"


def test_render_discovery_record_groups_candidates_by_authority():
    lib = load_link_to_report_lib_module()
    text = lib.render_discovery_record(
        request_id="ai-phone-demo",
        mode="discovery",
        topic="AI 手机",
        candidates=[
            {
                "title": "Apple Intelligence",
                "url": "https://www.apple.com/apple-intelligence/",
                "source_type": "official_update",
                "platform": "official_site",
                "authority": "official",
                "why_relevant": "Official product framing.",
            },
            {
                "title": "AI 手机综述",
                "url": "https://example.com/ai-phone-overview",
                "source_type": "structured_commentary",
                "platform": "web",
                "authority": "structured_commentary",
                "why_relevant": "Cross-vendor comparison.",
            },
        ],
    )

    assert "# Web Discovery Record" in text
    assert "## Official" in text
    assert "## Structured Commentary" in text
    assert "Apple Intelligence" in text
    assert "AI 手机综述" in text


def test_command_discover_web_writes_discovery_record(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    discovery_root = tmp_path / "library" / "sessions" / "web-discovery"
    monkeypatch.setattr(lib, "DISCOVERY_ROOT", discovery_root)

    result = lib.command_discover_web(
        argparse.Namespace(
            request_id="ai-phone-demo",
            mode="research-guided-collection",
            topic="AI 手机",
            brands="Apple, Google",
        )
    )

    assert result == 0
    record_path = discovery_root / "ai-phone-demo" / "discovery.md"
    assert record_path.exists()
    text = record_path.read_text(encoding="utf-8")
    assert "- request_id: `ai-phone-demo`" in text
    assert "- mode: `research-guided-collection`" in text
    assert "## Structured Commentary" in text


def test_search_commands_write_selection_record(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()
    selection_root = tmp_path / "library" / "sessions" / "search-selection"
    monkeypatch.setattr(lib, "SEARCH_SELECTION_ROOT", selection_root)

    scored_inputs = {}

    def fake_score_candidate(candidate, *, topic, research_direction, watch_profile):
        scored_inputs["topic"] = topic
        scored_inputs["research_direction"] = research_direction
        scored_inputs["watch_profile"] = watch_profile
        return {
            **candidate,
            "relevance_score": 7,
            "topic_matches": [topic],
            "ontology_matches": ["workflow"],
            "evidence_richness": 3,
            "downgrade_reasons": [],
            "coverage_role": "core",
        }

    balanced_called = {}

    def fake_balance_candidates(candidates, *, comparative):
        balanced_called["comparative"] = comparative
        balanced_called["count"] = len(candidates)
        return candidates

    monkeypatch.setattr(lib.search_selection, "score_candidate", fake_score_candidate)
    monkeypatch.setattr(lib.search_selection, "balance_candidates", fake_balance_candidates)

    monkeypatch.setattr(
        lib,
        "search_podwise_candidates",
        lambda query, limit, watch_profile: [
            {
                "candidate_id": "pod-1",
                "title": "demo",
                "summary": "demo summary",
                "url": "https://podwise.ai/dashboard/episodes/demo",
                "platform": "podwise",
                "source_type": "podcast_episode",
                "authority_level": "structured_commentary",
                "brand": "Samsung",
            }
        ][:limit],
    )

    result = lib.command_search_podwise(
        argparse.Namespace(
            request_id="ai-phone",
            topic="AI 手机",
            research_direction="系统级 agent",
            limit=5,
        )
    )

    assert result == 0
    assert scored_inputs["topic"] == "AI 手机"
    assert scored_inputs["research_direction"] == "系统级 agent"
    assert balanced_called["comparative"] is True
    record_path = selection_root / "ai-phone" / "podwise.md"
    assert record_path.exists()
    text = record_path.read_text(encoding="utf-8")
    assert "# Search Selection Record" in text
    assert "pod-1" in text
    assert "relevance_score" in text

    monkeypatch.setattr(
        lib,
        "search_xiaohongshu_candidates",
        lambda query, limit, watch_profile: [
            {
                "candidate_id": "xhs-1",
                "title": "demo xhs",
                "summary": "demo summary",
                "url": "https://www.xiaohongshu.com/explore/demo",
                "platform": "xiaohongshu",
                "source_type": "social_signal",
                "authority_level": "social_signal",
                "brand": "Xiaomi",
            }
        ][:limit],
    )
    result = lib.command_search_xiaohongshu(
        argparse.Namespace(
            request_id="ai-phone",
            topic="AI 手机",
            research_direction="系统级 agent",
            limit=5,
        )
    )
    assert result == 0
    assert (selection_root / "ai-phone" / "xiaohongshu.md").exists()


def test_ingest_links_dry_run_writes_run_summary_and_derives_bundle_path(tmp_path):
    lib = load_link_to_report_lib_module()
    links = [
        "https://www.xiaohongshu.com/explore/123",
        "https://podcasts.apple.com/us/podcast/example/id123",
    ]
    expected_bundle_id = lib.derive_bundle_id(links, "")
    cleanup_bundle_outputs(lib, expected_bundle_id)
    try:
        summary_path = lib.run_summary_path(expected_bundle_id)
        result = subprocess.run(
            [
                sys.executable,
                "scripts/link_to_report.py",
                "ingest-links",
                "--dry-run",
                *links,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert summary_path.exists()
        text = summary_path.read_text(encoding="utf-8")
        assert f"- bundle_id: `{expected_bundle_id}`" in text
        assert "- dry_run: `true`" in text
    finally:
        cleanup_bundle_outputs(lib, expected_bundle_id)


def test_approve_sources_hands_urls_to_ingest_bundle(monkeypatch):
    lib = load_link_to_report_lib_module()
    captured = {}

    def fake_command_ingest_links(args):
        captured["links"] = args.links
        captured["bundle_id"] = args.bundle_id
        return 0

    monkeypatch.setattr(lib, "command_ingest_links", fake_command_ingest_links)

    result = lib.command_approve_sources(
        argparse.Namespace(
            request_id="ai-phone-demo",
            bundle_id="ai-phone-bundle",
            urls=["https://www.apple.com/apple-intelligence/"],
        )
    )

    assert result == 0
    assert captured["bundle_id"] == "ai-phone-bundle"
    assert captured["links"] == ["https://www.apple.com/apple-intelligence/"]


def test_approve_search_candidates_hands_selected_urls_to_ingest_bundle(tmp_path, monkeypatch):
    lib = load_link_to_report_lib_module()

    selection_root = tmp_path / "search-selection"
    record_dir = selection_root / "ai-phone"
    record_dir.mkdir(parents=True)
    (record_dir / "podwise.md").write_text(
        "# Search Selection Record\n\n## Candidate\n\n- candidate_id: `pod-1`\n- title: `demo`\n- url: `https://podwise.ai/dashboard/episodes/demo`\n- platform: `podwise`\n- source_type: `podcast_episode`\n- authority_level: `structured_commentary`\n- relevance_score: `7`\n- topic_matches: [`AI 手机`]\n- ontology_matches: [`workflow`]\n- evidence_richness: `3`\n- downgrade_reasons: []\n- coverage_role: `core`\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(lib, "SEARCH_SELECTION_ROOT", selection_root)
    captured = {}

    def fake_command_ingest_links(args):
        captured["links"] = list(args.links)
        captured["bundle_id"] = args.bundle_id
        return 0

    monkeypatch.setattr(lib, "command_ingest_links", fake_command_ingest_links)

    result = lib.command_approve_search_candidates(
        argparse.Namespace(
            request_id="ai-phone",
            bundle_id="ai-phone-bundle",
            candidate_ids=["pod-1"],
        )
    )

    assert result == 0
    assert captured["bundle_id"] == "ai-phone-bundle"
    assert captured["links"] == ["https://podwise.ai/dashboard/episodes/demo"]


def test_approve_search_candidates_rejects_missing_ids(capsys):
    lib = load_link_to_report_lib_module()
    result = lib.command_approve_search_candidates(
        argparse.Namespace(
            request_id="ai-phone",
            bundle_id="ai-phone-bundle",
            candidate_ids=[],
        )
    )
    captured = capsys.readouterr()
    assert result == 2
    assert "candidate_ids are required for approve-search-candidates" in captured.err


def test_approve_sources_rejects_empty_urls(capsys):
    lib = load_link_to_report_lib_module()
    result = lib.command_approve_sources(
        argparse.Namespace(
            request_id="ai-phone-demo",
            bundle_id="ai-phone-bundle",
            urls=[],
        )
    )

    captured = capsys.readouterr()
    assert result == 2
    assert "urls are required for approve-sources" in captured.err


def test_propose_direction_writes_default_direction_record(tmp_path):
    lib = load_link_to_report_lib_module()
    bundle_id = "demo-bundle"
    cleanup_bundle_outputs(lib, bundle_id)
    try:
        bundle_dir = Path("library/sessions/link-to-report") / bundle_id
        bundle_dir.mkdir(parents=True, exist_ok=True)
        (bundle_dir / "run-summary.md").write_text(
            "# Link Bundle Run Summary\n\n- bundle_id: `demo-bundle`\n- successful_sources: [`source-demo`]\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "scripts/link_to_report.py",
                "propose-direction",
                "--bundle-id",
                bundle_id,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        direction_path = Path("library/sessions/link-to-report/demo-bundle/direction.md")
        assert direction_path.exists()
        text = direction_path.read_text(encoding="utf-8")
        assert "- bundle_id: `demo-bundle`" in text
        assert "- direction_status: `system_suggested_pending`" in text
    finally:
        cleanup_bundle_outputs(lib, bundle_id)


def test_propose_direction_accepts_user_direction_and_marks_it_user_provided(tmp_path):
    lib = load_link_to_report_lib_module()
    bundle_id = "user-direction-bundle"
    cleanup_bundle_outputs(lib, bundle_id)
    try:
        bundle_dir = Path("library/sessions/link-to-report") / bundle_id
        bundle_dir.mkdir(parents=True, exist_ok=True)
        (bundle_dir / "run-summary.md").write_text(
            "# Link Bundle Run Summary\n\n- bundle_id: `user-direction-bundle`\n- successful_sources: [`source-demo`]\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "scripts/link_to_report.py",
                "propose-direction",
                "--bundle-id",
                bundle_id,
                "--direction",
                "agent 编排是否正在进入默认产品结构",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        text = (bundle_dir / "direction.md").read_text(encoding="utf-8")
        assert "- research_direction: `agent 编排是否正在进入默认产品结构`" in text
        assert "- direction_status: `user_provided`" in text
    finally:
        cleanup_bundle_outputs(lib, bundle_id)


def test_generate_report_blocks_pending_direction_from_file(tmp_path):
    lib = load_link_to_report_lib_module()
    bundle_id = "pending-bundle"
    cleanup_bundle_outputs(lib, bundle_id)
    try:
        bundle_dir = Path("library/sessions/link-to-report") / bundle_id
        bundle_dir.mkdir(parents=True, exist_ok=True)
        (bundle_dir / "run-summary.md").write_text(
            "# Link Bundle Run Summary\n\n- bundle_id: `pending-bundle`\n- dry_run: `true`\n- link_count: `1`\n- link_types: [`wechat`]\n- links: [`https://mp.weixin.qq.com/s/example`]\n",
            encoding="utf-8",
        )
        direction_file = tmp_path / "direction.md"
        direction_file.write_text(
            "# Research Direction Record\n\n- bundle_id: `pending-bundle`\n- research_direction: `待批准的方向`\n- direction_status: `system_suggested_pending`\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "scripts/link_to_report.py",
                "generate-report",
                "--bundle-id",
                bundle_id,
                "--direction-file",
                str(direction_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "approved" in result.stderr.lower()
    finally:
        cleanup_bundle_outputs(lib, bundle_id)


def test_parse_link_result_blocks_ignores_trailing_sections():
    lib = load_link_to_report_lib_module()
    text = "\n".join(
        [
            "# Link Bundle Run Summary",
            "",
            "- bundle_id: `demo`",
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
            "## Counter-Signals And Tensions",
            "",
            "- MVP 占位",
            "",
        ]
    )
    results = lib.parse_link_result_blocks(text)
    assert len(results) == 1
    assert results[0]["link"] == "https://podcasts.apple.com/us/podcast/example/id123"
    assert results[0]["status"] == "success"


def test_collect_bundle_artifact_paths_preserves_unique_per_link_outputs():
    lib = load_link_to_report_lib_module()
    results = [
        {
            "artifact_paths": [
                "library/artifacts/podcasts/demo/summary.md",
                "library/artifacts/podcasts/demo/highlights.md",
            ]
        },
        {
            "artifact_paths": [
                "library/artifacts/podcasts/demo/highlights.md",
                "library/artifacts/xiaohongshu/demo/full_text.md",
            ]
        },
    ]

    artifact_paths = lib.collect_bundle_artifact_paths(results)

    assert artifact_paths == [
        "library/artifacts/podcasts/demo/summary.md",
        "library/artifacts/podcasts/demo/highlights.md",
        "library/artifacts/xiaohongshu/demo/full_text.md",
    ]


def test_generate_report_accepts_task_1_run_summary_shape(tmp_path):
    lib = load_link_to_report_lib_module()
    bundle_id = "task-1-bundle"
    cleanup_bundle_outputs(lib, bundle_id)
    try:
        bundle_dir = Path("library/sessions/link-to-report") / bundle_id
        bundle_dir.mkdir(parents=True, exist_ok=True)
        artifact_root = Path("library/artifacts/podcasts/demo")
        artifact_root.mkdir(parents=True, exist_ok=True)
        (artifact_root / "transcript.md").write_text("## Content\n[00:31] transcript line\n", encoding="utf-8")
        (bundle_dir / "run-summary.md").write_text(
            "\n".join(
                [
                    "# Link Bundle Run Summary",
                    "",
                    f"- bundle_id: `{bundle_id}`",
                    "- dry_run: `false`",
                    "- successful_link_count: `1`",
                    "- failed_link_count: `1`",
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
                    "### Link Result",
                    "",
                    "- link: `https://mp.weixin.qq.com/s/example`",
                    "- link_type: `wechat`",
                    "- status: `failed`",
                    "- source_path: ``",
                    "- artifact_paths: []",
                    "- failure_reason: `unsupported link type: wechat`",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        summary_text = (bundle_dir / "run-summary.md").read_text(encoding="utf-8")
        parsed_results = lib.parse_link_result_blocks(summary_text)
        assert len(parsed_results) == 2
        assert parsed_results[0]["status"] == "success"
        assert parsed_results[1]["status"] == "failed"
        result = subprocess.run(
            [
                sys.executable,
                "scripts/link_to_report.py",
                "generate-report",
                "--bundle-id",
                bundle_id,
                "--direction",
                "task 1 compatibility",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        intake_text = (lib.INTAKE_ROOT / f"{bundle_id}.md").read_text(encoding="utf-8")
        review_pack_text = (lib.REVIEW_PACK_ROOT / f"{bundle_id}.md").read_text(encoding="utf-8")
        writeback_text = (lib.WRITEBACK_ROOT / f"{bundle_id}.md").read_text(encoding="utf-8")
        assert "- link_count: `1`" in intake_text
        assert "- link_types: [`podcast`]" in intake_text
        assert "https://mp.weixin.qq.com/s/example" not in intake_text
        assert "https://podcasts.apple.com/us/podcast/example/id123" in review_pack_text
        assert "https://mp.weixin.qq.com/s/example" not in review_pack_text
        assert "- link_types: [`podcast`]" in review_pack_text
        assert "- link_types: [`podcast`]" in writeback_text
    finally:
        cleanup_bundle_outputs(lib, bundle_id)
        if artifact_root.exists():
            for path in sorted(artifact_root.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            artifact_root.rmdir()


def test_generate_report_writes_three_files_from_direction_file(tmp_path):
    lib = load_link_to_report_lib_module()
    links = [
        "https://www.xiaohongshu.com/explore/123",
        "https://podcasts.apple.com/us/podcast/example/id123",
    ]
    bundle_id = lib.derive_bundle_id(links, "")
    cleanup_bundle_outputs(lib, bundle_id)
    try:
        bundle_dir = lib.bundle_dir(bundle_id)
        bundle_dir.mkdir(parents=True, exist_ok=True)
        xhs_artifact_root = Path("library/artifacts/xiaohongshu/demo")
        xhs_artifact_root.mkdir(parents=True, exist_ok=True)
        (xhs_artifact_root / "full_text.md").write_text("## Content\nxiaohongshu note body\n", encoding="utf-8")
        podcast_artifact_root = Path("library/artifacts/podcasts/demo")
        podcast_artifact_root.mkdir(parents=True, exist_ok=True)
        (podcast_artifact_root / "transcript.md").write_text("## Content\n[00:31] podcast transcript body\n", encoding="utf-8")
        (bundle_dir / "run-summary.md").write_text(
            "\n".join(
                [
                    "# Link Bundle Run Summary",
                    "",
                    f"- bundle_id: `{bundle_id}`",
                    "- dry_run: `true`",
                    "",
                    "## Per-Link Results",
                    "",
                    "### Link Result",
                    "",
                    f"- link: `{links[0]}`",
                    "- link_type: `xiaohongshu`",
                    "- status: `success`",
                    "- source_path: `library/sources/xiaohongshu/demo.md`",
                    "- artifact_paths: [`library/artifacts/xiaohongshu/demo/full_text.md`]",
                    "- failure_reason: ``",
                    "",
                    "### Link Result",
                    "",
                    f"- link: `{links[1]}`",
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
        parsed_results = lib.parse_link_result_blocks((bundle_dir / "run-summary.md").read_text(encoding="utf-8"))
        assert [result["status"] for result in parsed_results] == ["success", "success"]
        direction_file = tmp_path / "direction.md"
        direction_file.write_text(
            "\n".join(
                [
                    "# Research Direction Record",
                    "",
                    f"- bundle_id: `{bundle_id}`",
                    "- research_direction: `link-to-report 最小闭环是否成立`",
                    "- direction_status: `user_provided`",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "scripts/link_to_report.py",
                "generate-report",
                "--bundle-id",
                bundle_id,
                "--direction-file",
                str(direction_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr

        intake_path = lib.INTAKE_ROOT / f"{bundle_id}.md"
        review_pack_path = lib.REVIEW_PACK_ROOT / f"{bundle_id}.md"
        writeback_path = lib.WRITEBACK_ROOT / f"{bundle_id}.md"
        assert intake_path.exists()
        assert review_pack_path.exists()
        assert writeback_path.exists()

        intake_text = intake_path.read_text(encoding="utf-8")
        review_pack_text = review_pack_path.read_text(encoding="utf-8")
        writeback_text = writeback_path.read_text(encoding="utf-8")
        assert f"- intake_id: `intake-{bundle_id}`" in intake_text
        assert f"- bundle_id: `{bundle_id}`" in intake_text
        assert f"- link_count: `2`" in intake_text
        assert "- link_types: [`podcast`, `xiaohongshu`]" in intake_text
        assert "- direction_status: `user_provided`" in intake_text
        assert f"- bundle_id: `{bundle_id}`" in review_pack_text
        assert "https://podcasts.apple.com/us/podcast/example/id123" in review_pack_text
        assert "- research_direction: `link-to-report 最小闭环是否成立`" in review_pack_text
        assert f"- writeback_id: `writeback-{bundle_id}`" in writeback_text
        assert "link-to-report 最小闭环是否成立" in writeback_text
        assert "source_paths" in writeback_text
        assert "artifact_paths" in writeback_text
    finally:
        cleanup_bundle_outputs(lib, bundle_id)
        for artifact_root in [xhs_artifact_root, podcast_artifact_root]:
            if artifact_root.exists():
                for path in sorted(artifact_root.rglob("*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()
                artifact_root.rmdir()


def test_generate_report_fails_when_artifact_path_is_missing(tmp_path):
    bundle_id = "missing-artifact-bundle"
    bundle_dir = Path("library/sessions/link-to-report") / bundle_id
    bundle_dir.mkdir(parents=True, exist_ok=True)
    try:
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
                    "- artifact_paths: [`library/artifacts/podcasts/demo/summary.md`]",
                    "",
                    "## Per-Link Results",
                    "",
                    "### Link Result",
                    "",
                    "- link: `https://podcasts.apple.com/us/podcast/example/id123`",
                    "- link_type: `podcast`",
                    "- status: `success`",
                    "- source_path: `library/sources/podcasts/demo.md`",
                    "- artifact_paths: [`library/artifacts/podcasts/demo/summary.md`]",
                    "- failure_reason: ``",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "scripts/link_to_report.py",
                "generate-report",
                "--bundle-id",
                bundle_id,
                "--direction",
                "missing artifact path should fail",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "missing artifact paths" in result.stderr
    finally:
        cleanup_bundle_outputs(load_link_to_report_lib_module(), bundle_id)


def test_generate_report_consumes_artifact_content_in_outputs(tmp_path):
    lib = load_link_to_report_lib_module()
    bundle_id = "artifact-content-bundle"
    cleanup_bundle_outputs(lib, bundle_id)
    try:
        bundle_dir = Path("library/sessions/link-to-report") / bundle_id
        bundle_dir.mkdir(parents=True, exist_ok=True)
        artifact_root = Path("library/artifacts/podcasts/demo")
        artifact_root.mkdir(parents=True, exist_ok=True)
        (artifact_root / "summary.md").write_text(
            "## Content\nmulti-agent 的关键不在更多 agent，而在治理边界。\n",
            encoding="utf-8",
        )
        (artifact_root / "highlights.md").write_text(
            "## Content\n1. [00:31] Harness engineering 让 agent 能在围栏内协作。\n",
            encoding="utf-8",
        )
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
                    "- artifact_paths: [`library/artifacts/podcasts/demo/summary.md`, `library/artifacts/podcasts/demo/highlights.md`]",
                    "",
                    "## Per-Link Results",
                    "",
                    "### Link Result",
                    "",
                    "- link: `https://podcasts.apple.com/us/podcast/example/id123`",
                    "- link_type: `podcast`",
                    "- status: `success`",
                    "- source_path: `library/sources/podcasts/demo.md`",
                    "- artifact_paths: [`library/artifacts/podcasts/demo/summary.md`, `library/artifacts/podcasts/demo/highlights.md`]",
                    "- failure_reason: ``",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        direction_file = tmp_path / "direction.md"
        direction_file.write_text(
            "\n".join(
                [
                    "# Research Direction Record",
                    "",
                    f"- bundle_id: `{bundle_id}`",
                    "- research_direction: `multi-agent 是否已经进入可治理的 Agent Team 范式迁移`",
                    "- direction_status: `user_provided`",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "scripts/link_to_report.py",
                "generate-report",
                "--bundle-id",
                bundle_id,
                "--direction-file",
                str(direction_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, result.stderr
        review_pack_text = (lib.REVIEW_PACK_ROOT / f"{bundle_id}.md").read_text(encoding="utf-8")
        writeback_text = (lib.WRITEBACK_ROOT / f"{bundle_id}.md").read_text(encoding="utf-8")
        assert "Direct quote" in review_pack_text
        assert "Harness engineering" in review_pack_text
        assert "Why it matters" in review_pack_text
        assert "## 文献综述" in writeback_text
        assert "Harness engineering" in writeback_text
        assert "## AI-native UX 视角" in writeback_text
    finally:
        cleanup_bundle_outputs(lib, bundle_id)
        if artifact_root.exists():
            for path in sorted(artifact_root.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
            artifact_root.rmdir()


def test_link_to_report_dry_run_end_to_end_smoke(tmp_path):
    lib = load_link_to_report_lib_module()
    links = [
        "https://www.xiaohongshu.com/explore/123",
        "https://podcasts.apple.com/us/podcast/example/id123",
    ]
    bundle_id = lib.derive_bundle_id(links, "")
    cleanup_bundle_outputs(lib, bundle_id)
    try:
        summary_path = lib.run_summary_path(bundle_id)

        ingest = subprocess.run(
            [
                sys.executable,
                "scripts/link_to_report.py",
                "ingest-links",
                "--dry-run",
                "--bundle-id",
                bundle_id,
                *links,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert ingest.returncode == 0, ingest.stderr
        assert summary_path.exists()

        direction_file = tmp_path / "direction.md"
        direction_file.write_text(
            "\n".join(
                [
                    "# Research Direction Record",
                    "",
                    f"- bundle_id: `{bundle_id}`",
                    "- research_direction: `link-to-report 是否形成最小闭环`",
                    "- direction_status: `user_provided`",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        generate = subprocess.run(
            [
                sys.executable,
                "scripts/link_to_report.py",
                "generate-report",
                "--bundle-id",
                bundle_id,
                "--direction-file",
                str(direction_file),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert generate.returncode != 0
        assert "no artifact paths available" in generate.stderr
    finally:
        cleanup_bundle_outputs(lib, bundle_id)
