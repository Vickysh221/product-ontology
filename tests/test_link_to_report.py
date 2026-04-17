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
        ["python3", "scripts/link_to_report.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "ingest-links" in result.stdout
    assert "propose-direction" in result.stdout
    assert "generate-report" in result.stdout


def test_ingest_links_requires_at_least_one_link():
    result = subprocess.run(
        ["python3", "scripts/link_to_report.py", "ingest-links"],
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
            "python3",
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
                "python3",
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
        assert "- link_types: [`podcast`, `xiaohongshu`]" in text
    finally:
        cleanup_bundle_outputs(lib, expected_bundle_id)


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
                "python3",
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
                "python3",
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
                "python3",
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
        (bundle_dir / "run-summary.md").write_text(
            "\n".join(
                [
                    "# Link Bundle Run Summary",
                    "",
                    f"- bundle_id: `{bundle_id}`",
                    "- dry_run: `true`",
                    "- link_count: `2`",
                    "- link_types: [`podcast`, `xiaohongshu`]",
                    f"- links: {lib.format_list(links)}",
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
                    "- research_direction: `link-to-report 最小闭环是否成立`",
                    "- direction_status: `user_provided`",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                "python3",
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
        assert "- direction_status: `user_provided`" in intake_text
        assert f"- bundle_id: `{bundle_id}`" in review_pack_text
        assert "- research_direction: `link-to-report 最小闭环是否成立`" in review_pack_text
        assert f"- writeback_id: `writeback-{bundle_id}`" in writeback_text
        assert "- research_direction: `link-to-report 最小闭环是否成立`" in writeback_text
    finally:
        cleanup_bundle_outputs(lib, bundle_id)


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
                "python3",
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
                "python3",
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
        assert generate.returncode == 0, generate.stderr
        assert (lib.INTAKE_ROOT / f"{bundle_id}.md").exists()
        assert (lib.REVIEW_PACK_ROOT / f"{bundle_id}.md").exists()
        assert (lib.WRITEBACK_ROOT / f"{bundle_id}.md").exists()
    finally:
        cleanup_bundle_outputs(lib, bundle_id)
