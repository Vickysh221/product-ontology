import importlib.util
from pathlib import Path
import subprocess


def load_link_to_report_lib_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts/link_to_report_lib.py"
    spec = importlib.util.spec_from_file_location("link_to_report_lib", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_link_to_report_helpers_normalize_bundle_paths():
    lib = load_link_to_report_lib_module()

    assert lib.slugify_bundle_id(" Demo Bundle! ") == "demo-bundle"
    assert lib.slugify_bundle_id("!!!") == "bundle"
    assert lib.derive_bundle_id(["b", "a"], "") == lib.derive_bundle_id(["a", "b"], "")
    assert lib.bundle_dir("demo-bundle") == lib.LINK_TO_REPORT_ROOT / "demo-bundle"
    assert lib.run_summary_path("demo-bundle") == lib.LINK_TO_REPORT_ROOT / "demo-bundle" / "run-summary.md"
    assert lib.direction_path("demo-bundle") == lib.LINK_TO_REPORT_ROOT / "demo-bundle" / "direction.md"


def test_propose_direction_writes_default_direction_record(tmp_path):
    bundle_id = "demo-bundle"
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


def test_propose_direction_accepts_user_direction_and_marks_it_user_provided(tmp_path):
    bundle_id = "user-direction-bundle"
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
