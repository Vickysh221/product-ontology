from __future__ import annotations

import argparse
import importlib.util
import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
LINK_TO_REPORT_ROOT = ROOT / "library" / "sessions" / "link-to-report"
DISCOVERY_ROOT = ROOT / "library" / "sessions" / "web-discovery"
INTAKE_ROOT = ROOT / "library" / "writeback-intakes" / "link-to-report"
REVIEW_PACK_ROOT = ROOT / "library" / "review-packs" / "link-to-report"
WRITEBACK_ROOT = ROOT / "library" / "writebacks" / "link-to-report"

LINK_TYPE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("xiaohongshu", ("xiaohongshu.com", "xhslink.com", "xhs.cn")),
    ("wechat", ("weixin.qq.com", "mp.weixin.qq.com", "wechat.com")),
    ("podcast", ("podcast", "spotify.com", "podcasts.apple.com", "apple.com/podcast")),
    ("video", ("youtube.com", "bilibili.com", "tiktok.com", "douyin.com")),
)
INGESTION_ADAPTERS: dict[str, callable] = {}


def load_script_module(module_filename: str, module_name: str):
    module_path = Path(__file__).resolve().parent / module_filename
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    previous_module = sys.modules.get(module_name)
    try:
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except Exception:
        if previous_module is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous_module
        raise
    return module


source_ingest = load_script_module("source_ingest.py", "source_ingest")
podcast_import = load_script_module("podcast_import.py", "podcast_import")
xiaohongshu_redbook_import = load_script_module("xiaohongshu_redbook_import.py", "xiaohongshu_redbook_import")
writeback_generate = load_script_module("writeback_generate.py", "writeback_generate")

import_episode = podcast_import.import_episode
write_artifact_record = source_ingest.write_artifact_record
write_source_record = source_ingest.write_source_record
import_note_url = xiaohongshu_redbook_import.import_note_url


def slugify_bundle_id(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized or "bundle"


def derive_bundle_id(links: list[str], requested: str) -> str:
    if requested:
        return slugify_bundle_id(requested)
    digest = hashlib.sha1("|".join(sorted(links)).encode("utf-8")).hexdigest()[:8]
    return f"bundle-{digest}"


def bundle_dir(bundle_id: str) -> Path:
    return LINK_TO_REPORT_ROOT / bundle_id


def direction_path(bundle_id: str) -> Path:
    return bundle_dir(bundle_id) / "direction.md"


def run_summary_path(bundle_id: str) -> Path:
    return bundle_dir(bundle_id) / "run-summary.md"


def detect_link_type(link: str) -> str:
    normalized = link.strip().lower()
    if not normalized:
        return "unknown"
    if normalized.startswith("file://") or normalized.startswith("/"):
        return "local-file"
    parsed = urlparse(normalized)
    haystack = f"{parsed.netloc}{parsed.path}"
    if not parsed.netloc:
        return "unknown"
    for link_type, needles in LINK_TYPE_RULES:
        if any(needle in haystack for needle in needles):
            return link_type
    return "web"


def format_list(values: list[str]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(f"`{value}`" for value in values) + "]"


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def read_markdown_field(text: str, field_name: str) -> str:
    prefix = f"- {field_name}: `"
    for line in text.splitlines():
        if line.startswith(prefix) and line.endswith("`"):
            return line[len(prefix) : -1]
    return ""


def read_markdown_list_field(text: str, field_name: str) -> list[str]:
    prefix = f"- {field_name}: ["
    for line in text.splitlines():
        if not line.startswith(prefix) or not line.endswith("]"):
            continue
        inner = line[len(prefix) : -1].strip()
        if not inner:
            return []
        return re.findall(r"`([^`]*)`", inner)
    return []


def summarize_bundle_cues(link_results: list[dict[str, object]]) -> tuple[list[str], list[str]]:
    link_types: list[str] = []
    artifact_kinds: list[str] = []
    for result in link_results:
        link_type = str(result.get("link_type", "")).strip()
        if link_type and link_type not in link_types:
            link_types.append(link_type)
        for artifact_path in result.get("artifact_paths", []) or []:
            kind = Path(str(artifact_path)).stem.strip()
            if kind and kind not in artifact_kinds:
                artifact_kinds.append(kind)
    return link_types, artifact_kinds


def build_proposed_direction_from_bundle_outputs(link_results: list[dict[str, object]]) -> str:
    link_types, artifact_kinds = summarize_bundle_cues(link_results)
    if link_types or artifact_kinds:
        link_type_hint = "、".join(link_types) if link_types else "多种来源"
        artifact_hint = "、".join(artifact_kinds) if artifact_kinds else "可见证据"
        return (
            f"当前 bundle 主要包含 {link_type_hint} 材料，且可见证据类型包括 {artifact_hint}。"
            "这些线索是否共同指向协作边界、责任边界或工作流结构的变化？"
        )
    return "这组链接共同指向的产品问题是什么，尤其是它们是否在重写协作边界、责任边界或工作流结构"


def normalize_source_candidate(
    *,
    title: str,
    url: str,
    source_type: str,
    platform: str,
    authority: str,
    why_relevant: str,
) -> dict[str, str]:
    return {
        "title": title.strip(),
        "url": url.strip(),
        "source_type": source_type.strip(),
        "platform": platform.strip(),
        "authority": authority.strip(),
        "why_relevant": why_relevant.strip(),
    }


def render_discovery_record(
    *,
    request_id: str,
    mode: str,
    topic: str,
    candidates: list[dict[str, str]],
) -> str:
    grouped: dict[str, list[dict[str, str]]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate["authority"], []).append(candidate)

    sections: list[str] = [
        "# Web Discovery Record",
        "",
        f"- request_id: `{request_id}`",
        f"- mode: `{mode}`",
        f"- topic: `{topic}`",
        "",
    ]
    title_map = {
        "official": "Official",
        "first_hand_operator": "First-Hand Operator",
        "structured_commentary": "Structured Commentary",
        "social_signal": "Social Signal",
    }
    for authority in ["official", "first_hand_operator", "structured_commentary", "social_signal"]:
        items = grouped.get(authority, [])
        if not items:
            continue
        sections.extend([f"## {title_map[authority]}", ""])
        for item in items:
            sections.extend(
                [
                    f"- [{item['title']}]({item['url']})",
                    f"  - source_type: `{item['source_type']}`",
                    f"  - platform: `{item['platform']}`",
                    f"  - why_relevant: {item['why_relevant']}",
                ]
            )
        sections.append("")
    return "\n".join(sections)


def build_discovery_candidates(topic: str, mode: str, brands: list[str]) -> list[dict[str, str]]:
    normalized_brands = [brand.strip() for brand in brands if brand.strip()]
    candidates: list[dict[str, str]] = []
    topic_slug = slugify_bundle_id(topic)

    if mode == "official-update":
        titles = normalized_brands or [topic]
        for title in titles:
            candidates.append(
                normalize_source_candidate(
                    title=f"{title} Official Update",
                    url=f"manual://official/{slugify_bundle_id(title)}",
                    source_type="official_update",
                    platform="official_site",
                    authority="official",
                    why_relevant=f"Official update candidate for {title} in topic {topic}.",
                )
            )
        return candidates

    if mode == "research-guided-collection":
        titles = normalized_brands or [topic]
        for title in titles:
            candidates.append(
                normalize_source_candidate(
                    title=f"{title} Structured Commentary",
                    url=f"manual://research/{slugify_bundle_id(title)}",
                    source_type="structured_commentary",
                    platform="web",
                    authority="structured_commentary",
                    why_relevant=f"Research-guided commentary candidate for {title} in topic {topic}.",
                )
            )
        if not candidates:
            candidates.append(
                normalize_source_candidate(
                    title=f"{topic} Social Signal",
                    url=f"manual://social/{topic_slug}",
                    source_type="social_signal",
                    platform="web",
                    authority="social_signal",
                    why_relevant=f"Social signal candidate for topic {topic}.",
                )
            )
        return candidates

    candidates.append(
        normalize_source_candidate(
            title=f"{topic} Structured Commentary",
            url=f"manual://discovery/{topic_slug}",
            source_type="structured_commentary",
            platform="web",
            authority="structured_commentary",
            why_relevant=f"Discovery candidate for topic {topic}.",
        )
    )
    for brand in normalized_brands:
        candidates.append(
            normalize_source_candidate(
                title=f"{brand} Social Signal",
                url=f"manual://social/{slugify_bundle_id(brand)}",
                source_type="social_signal",
                platform="web",
                authority="social_signal",
                why_relevant=f"Discovery signal around {brand} for topic {topic}.",
            )
        )
    return candidates


def command_discover_web(args: argparse.Namespace) -> int:
    request_id = slugify_bundle_id(args.request_id)
    brands = parse_csv(getattr(args, "brands", ""))
    candidates = build_discovery_candidates(args.topic, args.mode, brands)
    record = render_discovery_record(
        request_id=request_id,
        mode=args.mode,
        topic=args.topic,
        candidates=candidates,
    )
    path = DISCOVERY_ROOT / request_id / "discovery.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(record, encoding="utf-8")
    try:
        print(path.relative_to(ROOT))
    except ValueError:
        print(path)
    return 0


def command_approve_sources(args: argparse.Namespace) -> int:
    urls = [url.strip() for url in getattr(args, "urls", []) if url.strip()]
    if not urls:
        print("urls are required for approve-sources", file=sys.stderr)
        return 2
    return command_ingest_links(
        argparse.Namespace(
            links=urls,
            bundle_id=args.bundle_id,
            force=False,
            dry_run=False,
        )
    )


def parse_link_result_blocks(text: str) -> list[dict[str, object]]:
    blocks: list[list[str]] = []
    current_block: list[str] = []
    in_section = False

    for line in text.splitlines():
        if line == "## Per-Link Results":
            in_section = True
            current_block = []
            continue
        if not in_section:
            continue
        if line.startswith("## ") and line != "## Per-Link Results":
            if any(item.strip() for item in current_block):
                blocks.append(current_block)
            current_block = []
            break
        if line.startswith("### Link Result"):
            if any(item.strip() for item in current_block):
                blocks.append(current_block)
                current_block = []
            continue
        current_block.append(line)

    if in_section and any(item.strip() for item in current_block):
        blocks.append(current_block)

    results: list[dict[str, object]] = []
    for block_lines in blocks:
        block_text = "\n".join(block_lines)
        results.append(
            {
                "link": read_markdown_field(block_text, "link"),
                "link_type": read_markdown_field(block_text, "link_type"),
                "status": read_markdown_field(block_text, "status"),
                "source_path": read_markdown_field(block_text, "source_path"),
                "artifact_paths": read_markdown_list_field(block_text, "artifact_paths"),
                "failure_reason": read_markdown_field(block_text, "failure_reason"),
            }
        )
    return results


def collect_bundle_artifact_paths(link_results: list[dict[str, object]]) -> list[str]:
    artifact_paths: list[str] = []
    for result in link_results:
        for path in result.get("artifact_paths", []) or []:
            path_text = str(path)
            if path_text and path_text not in artifact_paths:
                artifact_paths.append(path_text)
    return artifact_paths


def load_official_target_urls() -> list[str]:
    official_sources_file = ROOT / "seed" / "official-sources.yaml"
    if not official_sources_file.exists():
        return []
    targets: list[str] = []
    for line in official_sources_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("url: "):
            continue
        target = stripped.split("url:", 1)[1].strip()
        if target and not target.startswith("manual://"):
            targets.append(target)
    return targets


def is_official_target(link: str) -> bool:
    normalized = link.strip().rstrip("/")
    for target in load_official_target_urls():
        target_normalized = target.strip().rstrip("/")
        if normalized == target_normalized or normalized.startswith(f"{target_normalized}/"):
            return True
    return False


def to_repo_relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def validate_ingestion_adapter_result(result: object, link: str, link_type: str) -> dict[str, object]:
    if not isinstance(result, dict):
        raise TypeError("ingestion adapter must return a dict result")

    status = result.get("status", "success")
    if status not in {"success", "dry_run", "failed"}:
        raise ValueError(f"ingestion adapter returned unsupported status: {status!r}")

    source_path = result.get("source_path", "")
    if not isinstance(source_path, str):
        raise TypeError("ingestion adapter source_path must be a string")

    failure_reason = result.get("failure_reason", "")
    if not isinstance(failure_reason, str):
        raise TypeError("ingestion adapter failure_reason must be a string")

    artifact_paths = result.get("artifact_paths", [])
    if not isinstance(artifact_paths, list) or any(not isinstance(path, str) for path in artifact_paths):
        raise TypeError("ingestion adapter artifact_paths must be a list of strings")

    return {
        "link": str(result.get("link", link)),
        "link_type": str(result.get("link_type", link_type)),
        "status": str(status),
        "source_path": source_path,
        "artifact_paths": artifact_paths,
        "failure_reason": failure_reason,
    }


def invoke_ingestion_adapter(adapter: object, link: str, force: bool, link_type: str) -> dict[str, object]:
    if not callable(adapter):
        raise TypeError("ingestion adapter must be callable")
    result = adapter(link, force=force)
    return validate_ingestion_adapter_result(result, link, link_type)


def ingest_podcast_link(link: str, *, force: bool) -> dict[str, object]:
    slug = import_episode(link, force=force)
    source_path = ROOT / "library" / "sources" / "podcasts" / f"{slug}.md"
    artifact_root = ROOT / "library" / "artifacts" / "podcasts" / slug
    return {
        "link": link,
        "link_type": "podcast",
        "status": "success",
        "source_path": to_repo_relative(source_path),
        "artifact_paths": [
            to_repo_relative(artifact_root / "transcript.md"),
            to_repo_relative(artifact_root / "summary.md"),
            to_repo_relative(artifact_root / "highlights.md"),
        ],
        "failure_reason": "",
    }


def ingest_xiaohongshu_link(link: str, *, force: bool) -> dict[str, object]:
    slug = import_note_url(link, force=force)
    source_path = ROOT / "library" / "sources" / "xiaohongshu" / f"{slug}.md"
    artifact_root = ROOT / "library" / "artifacts" / "xiaohongshu" / slug
    artifact_paths = [to_repo_relative(artifact_root / "full_text.md")]
    for optional_name in ("transcript.md", "comment_batch.md"):
        optional_path = artifact_root / optional_name
        if optional_path.exists():
            artifact_paths.append(to_repo_relative(optional_path))
    return {
        "link": link,
        "link_type": "xiaohongshu",
        "status": "success",
        "source_path": to_repo_relative(source_path),
        "artifact_paths": artifact_paths,
        "failure_reason": "",
    }


def fetch_official_content(link: str) -> str | None:
    return None


def ingest_official_link(link: str, *, force: bool) -> dict[str, object]:
    if not is_official_target(link):
        raise ValueError("non-official web url is unsupported in this phase")
    body = fetch_official_content(link)
    if not body or not body.strip():
        raise ValueError("official content fetch unavailable in this phase")

    _source_id, source_path, _artifact_dir = write_source_record(
        channel="official",
        source_label=link,
        url=link,
        source_type="official_release",
        ingestion_method="link_to_report",
        publisher=urlparse(link).netloc or "unknown",
        author_or_speaker="unknown",
        published_at="unknown",
        title=link,
        canonical_url=link,
        perspective="first_hand_official",
        confidence="high",
        notes=["Official page imported through link-to-report."],
    )
    artifact_path = write_artifact_record(
        channel="official",
        source_label=link,
        source_url=link,
        slice_type="full_text",
        location="full_text",
        perspective="official_release",
        why_relevant="Stores the official page content for later extraction.",
        body=body,
    )
    return {
        "link": link,
        "link_type": "web",
        "status": "success",
        "source_path": to_repo_relative(source_path),
        "artifact_paths": [to_repo_relative(artifact_path)],
        "failure_reason": "",
    }


INGESTION_ADAPTERS = {
    "podcast": ingest_podcast_link,
    "xiaohongshu": ingest_xiaohongshu_link,
    "web": ingest_official_link,
}


def render_link_result_block(result: dict[str, object] | str) -> str:
    if isinstance(result, str):
        result = {
            "link": result,
            "link_type": detect_link_type(result),
            "status": "success",
            "source_path": "",
            "artifact_paths": [],
            "failure_reason": "",
        }

    artifact_paths = [str(path) for path in result.get("artifact_paths", []) or []]
    source_path = str(result.get("source_path", ""))
    failure_reason = str(result.get("failure_reason", ""))
    return "\n".join(
        [
            f"- link: `{str(result.get('link', ''))}`",
            f"- link_type: `{str(result.get('link_type', 'unknown'))}`",
            f"- status: `{str(result.get('status', 'failed'))}`",
            f"- source_path: `{source_path}`",
            f"- artifact_paths: {format_list(artifact_paths)}",
            f"- failure_reason: `{failure_reason}`",
        ]
    )


def render_run_summary_markdown(bundle_id: str, results: list[dict[str, object] | str], dry_run: bool) -> str:
    normalized_results = [
        result
        if isinstance(result, dict)
        else {
            "link": result,
            "link_type": detect_link_type(result),
            "status": "success",
            "source_path": "",
            "artifact_paths": [],
            "failure_reason": "",
        }
        for result in results
    ]
    successful_results = [result for result in normalized_results if str(result.get("status", "")) == "success"]
    failed_results = [result for result in normalized_results if str(result.get("status", "")) != "success"]
    source_paths = [str(result.get("source_path", "")) for result in successful_results if str(result.get("source_path", ""))]
    artifact_paths = [
        str(path)
        for result in successful_results
        for path in (result.get("artifact_paths", []) or [])
        if str(path)
    ]
    lines = [
        "# Link Bundle Run Summary",
        "",
        f"- bundle_id: `{bundle_id}`",
        f"- dry_run: `{'true' if dry_run else 'false'}`",
        f"- successful_link_count: `{len(successful_results)}`",
        f"- failed_link_count: `{len(failed_results)}`",
        f"- source_paths: {format_list(source_paths)}",
        f"- artifact_paths: {format_list(artifact_paths)}",
        "",
        "## Per-Link Results",
        "",
    ]
    for index, result in enumerate(normalized_results, start=1):
        lines.extend(
            [
                "### Link Result",
                "",
                render_link_result_block(result),
                "",
            ]
        )
    return "\n".join(lines)


def render_intake_markdown(
    bundle_id: str,
    links: list[str],
    direction_text: str,
    direction_status: str,
    link_types: list[str],
) -> str:
    return "\n".join(
        [
            "# Writeback Intake Record",
            "",
            f"- intake_id: `intake-{bundle_id}`",
            f"- bundle_id: `{bundle_id}`",
            f"- research_direction: `{direction_text}`",
            f"- direction_status: `{direction_status}`",
            f"- link_count: `{len(links)}`",
            f"- link_types: {format_list(link_types)}",
            f"- successful_links: {format_list(links)}",
            "- used_default_rules: `true`",
            "",
        ]
    )


def render_review_pack_markdown(
    bundle_id: str,
    direction_text: str,
    direction_status: str,
    link_types: list[str],
    links: list[str],
) -> str:
    theme_lines: list[str] = []
    for index, link in enumerate(links, start=1):
        theme_lines.extend(
            [
                f"### Link {index}",
                "",
                f"- url: `{link}`",
                f"- detected_type: `{detect_link_type(link)}`",
                "",
            ]
        )
    return "\n".join(
        [
            "# Research Review Pack",
            "",
            f"- bundle_id: `{bundle_id}`",
            f"- direction_status: `{direction_status}`",
            f"- research_direction: `{direction_text}`",
            f"- link_types: {format_list(link_types) if link_types else '[]'}",
            "",
            "## Link Themes",
            "",
            *theme_lines,
            "## Counter-Signals And Tensions",
            "",
            "- MVP 占位：当前只保留链接结构和方向状态，后续再补跨链接主题聚类。",
            "",
        ]
    )


def render_writeback_markdown(
    bundle_id: str,
    direction_text: str,
    direction_status: str,
    link_types: list[str],
) -> str:
    return "\n".join(
        [
            "# Writeback Proposal",
            "",
            f"- writeback_id: `writeback-{bundle_id}`",
            f"- intake_id: `intake-{bundle_id}`",
            f"- bundle_id: `{bundle_id}`",
            f"- direction_status: `{direction_status}`",
            f"- research_direction: `{direction_text}`",
            f"- link_types: {format_list(link_types) if link_types else '[]'}",
            "",
            "## 主判断",
            "",
            "MVP 占位：先把写回链路打通，后续再补真正的结构化 synthesis。",
            "",
            "## Review Pack 引用",
            "",
            f"- review_pack_ref: `library/review-packs/link-to-report/{bundle_id}.md`",
            "",
            "## 保留张力",
            "",
            "- 当前版本只阻止 `system_suggested_pending` 的方向继续生成。",
            "",
        ]
    )


def render_direction_markdown(bundle_id: str, research_direction: str, direction_status: str) -> str:
    return "\n".join(
        [
            "# Research Direction Record",
            "",
            f"- bundle_id: `{bundle_id}`",
            f"- research_direction: `{research_direction}`",
            f"- direction_status: `{direction_status}`",
            "",
        ]
    )


def command_ingest_links(args: argparse.Namespace) -> int:
    links = [link.strip() for link in args.links if link.strip()]
    if not links:
        print("links are required for ingest-links", file=sys.stderr)
        return 2

    bundle_id = slugify_bundle_id(args.bundle_id) if args.bundle_id else derive_bundle_id(links, "")
    results: list[dict[str, object]] = []
    for link in links:
        link_type = detect_link_type(link)
        if args.dry_run:
            results.append(
                {
                    "link": link,
                    "link_type": link_type,
                    "status": "dry_run",
                    "source_path": "",
                    "artifact_paths": [],
                    "failure_reason": "",
                }
            )
            continue

        adapter = INGESTION_ADAPTERS.get(link_type)
        if adapter is None:
            results.append(
                {
                    "link": link,
                    "link_type": link_type,
                    "status": "failed",
                    "source_path": "",
                    "artifact_paths": [],
                    "failure_reason": f"unsupported link type: {link_type}",
                }
            )
            continue

        try:
            adapter_result = invoke_ingestion_adapter(adapter, link, args.force, link_type)
        except Exception as exc:
            results.append(
                {
                    "link": link,
                    "link_type": link_type,
                    "status": "failed",
                    "source_path": "",
                    "artifact_paths": [],
                    "failure_reason": f"{exc}",
                }
            )
            continue

        results.append(adapter_result)

    summary_path = run_summary_path(bundle_id)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(render_run_summary_markdown(bundle_id, results, args.dry_run), encoding="utf-8")
    print(summary_path.relative_to(ROOT))
    return 0


def command_propose_direction(args: argparse.Namespace) -> int:
    bundle_id = slugify_bundle_id(args.bundle_id)
    summary_path = run_summary_path(bundle_id)
    if not summary_path.exists():
        print("bundle run summary is missing", file=sys.stderr)
        return 2
    summary_text = summary_path.read_text(encoding="utf-8")

    if args.direction:
        research_direction = args.direction.strip()
        direction_status = "user_provided"
    else:
        link_results = [
            result for result in parse_link_result_blocks(summary_text) if str(result.get("status", "")) == "success"
        ]
        research_direction = build_proposed_direction_from_bundle_outputs(link_results)
        direction_status = "system_suggested_pending"

    path = direction_path(bundle_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_direction_markdown(bundle_id, research_direction, direction_status),
        encoding="utf-8",
    )
    print(path.relative_to(ROOT))
    return 0


def load_direction_input(args: argparse.Namespace) -> tuple[str, str]:
    if args.direction_file:
        path = Path(args.direction_file)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            raise SystemExit("missing or unreadable direction file")
        direction_text = read_markdown_field(text, "research_direction") or text.strip()
        direction_status = read_markdown_field(text, "direction_status") or "user_provided"
        return direction_text, direction_status
    return args.direction.strip(), "user_provided"


def write_output_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def command_generate_report(args: argparse.Namespace) -> int:
    if not args.direction and not args.direction_file:
        print("direction is required for generate-report", file=sys.stderr)
        return 2

    bundle_id = slugify_bundle_id(args.bundle_id)
    summary_path = run_summary_path(bundle_id)
    if not summary_path.exists():
        print("bundle run summary is missing", file=sys.stderr)
        return 2

    summary_text = summary_path.read_text(encoding="utf-8")
    link_results = parse_link_result_blocks(summary_text)
    successful_results = [result for result in link_results if str(result.get("status", "")) == "success"]
    links = [str(result.get("link", "")) for result in successful_results if str(result.get("link", ""))]
    link_types = sorted({str(result.get("link_type", "")) for result in successful_results if str(result.get("link_type", ""))})
    source_paths = [
        str(result.get("source_path", ""))
        for result in successful_results
        if str(result.get("source_path", ""))
    ]
    direction_text, direction_status = load_direction_input(args)
    if direction_status == "system_suggested_pending":
        print("system_suggested_pending directions must be approved before generate-report", file=sys.stderr)
        return 2
    artifact_paths = collect_bundle_artifact_paths(successful_results)
    if not artifact_paths:
        print("no artifact paths available for generate-report", file=sys.stderr)
        return 2

    intake_text = render_intake_markdown(bundle_id, links, direction_text, direction_status, link_types)
    try:
        review_pack_text = writeback_generate.generate_real_review_pack(
            bundle_id=bundle_id,
            source_paths=source_paths,
            artifact_paths=artifact_paths,
            direction_text=direction_text,
            direction_status=direction_status,
            links=links,
            link_types=link_types,
            link_results=successful_results,
            root=ROOT,
        )
        writeback_text = writeback_generate.generate_real_writeback(
            bundle_id=bundle_id,
            source_paths=source_paths,
            artifact_paths=artifact_paths,
            direction_text=direction_text,
            direction_status=direction_status,
            links=links,
            link_types=link_types,
            link_results=successful_results,
            review_pack_text=review_pack_text,
            root=ROOT,
        )
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    intake_path = INTAKE_ROOT / f"{bundle_id}.md"
    review_pack_path = REVIEW_PACK_ROOT / f"{bundle_id}.md"
    writeback_path = WRITEBACK_ROOT / f"{bundle_id}.md"

    write_output_file(intake_path, intake_text)
    write_output_file(review_pack_path, review_pack_text)
    write_output_file(writeback_path, writeback_text)

    if getattr(args, "review_pack_output", ""):
        write_output_file(Path(args.review_pack_output), review_pack_text)
    if getattr(args, "writeback_output", ""):
        write_output_file(Path(args.writeback_output), writeback_text)

    print(intake_path.relative_to(ROOT))
    print(review_pack_path.relative_to(ROOT))
    print(writeback_path.relative_to(ROOT))
    return 0
