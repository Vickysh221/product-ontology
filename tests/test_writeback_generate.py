import re
import importlib.util
import os
from pathlib import Path
import subprocess
import pytest


def load_writeback_generate_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts/writeback_generate.py"
    spec = importlib.util.spec_from_file_location("writeback_generate", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sample_reviews_exist_for_promoted_podcast_claim():
    product_review = Path("library/reviews/podcasts/review-product-podwise-ai-7650271-dfb97270-16.md").read_text()
    ux_review = Path("library/reviews/podcasts/review-ux-podwise-ai-7650271-dfb97270-16.md").read_text()
    contrarian_review = Path("library/reviews/podcasts/review-contrarian-podwise-ai-7650271-dfb97270-16.md").read_text()
    verdict = Path("library/verdicts/podcasts/verdict-podwise-ai-7650271-dfb97270-16.md").read_text()

    assert "- target_id: `claim-podwise-ai-7650271-dfb97270-16`" in product_review
    assert "- target_id: `claim-podwise-ai-7650271-dfb97270-16`" in ux_review
    assert "- target_id: `claim-podwise-ai-7650271-dfb97270-16`" in contrarian_review
    assert "- produces_verdict_id: `verdict-podwise-ai-7650271-dfb97270-16`" in product_review
    assert "- produces_verdict_id: `verdict-podwise-ai-7650271-dfb97270-16`" in ux_review
    assert "- produces_verdict_id: `verdict-podwise-ai-7650271-dfb97270-16`" in contrarian_review
    assert "- target_id: `claim-podwise-ai-7650271-dfb97270-16`" in verdict
    assert "- outcome: `supported_with_preserved_tension`" in verdict


def test_writeback_generate_requires_intake(tmp_path):
    target = tmp_path / "writeback.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_generate.py",
            "render",
            "--writeback-id",
            "writeback-demo",
            "--intake-file",
            str(tmp_path / "missing-intake.md"),
            "--output",
            str(target),
            "--title",
            "Demo",
            "--subtitle",
            "Demo subtitle",
            "--summary",
            "Demo summary",
            "--synthesis-ref",
            "synthesis-demo",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "intake" in result.stderr.lower()


def test_writeback_generate_with_default_intake(tmp_path):
    intake = tmp_path / "intake.md"
    intake.write_text(
        """# Writeback Intake Record
- intake_id: `intake-demo`
- collaboration_mode: ``
- focus_priority: []
- target_audience: ``
- decision_intent: ``
- evidence_posture: ``
- special_attention: []
- extra_questions: []
- avoidances: []
- preserve_tensions: []
- used_default_rules: `true`
"""
    )
    target = tmp_path / "writeback.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_generate.py",
            "render",
            "--writeback-id",
            "writeback-demo",
            "--intake-file",
            str(intake),
            "--output",
            str(target),
            "--title",
            "Demo",
            "--subtitle",
            "Demo subtitle",
            "--summary",
            "Demo summary",
            "--synthesis-ref",
            "synthesis-demo",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- intake_id: `intake-demo`" in text
    assert "- used_default_rules: `true`" in text
    assert "## 评审视角" in text


def test_sample_writeback_records_intake_and_reviews():
    text = Path("library/writebacks/2026-04-16-xiaopeng-v2a-explainability-writeback.md").read_text()
    intake = Path("library/writeback-intakes/podcasts/intake-podwise-ai-7650271-dfb97270-default.md").read_text()
    assert "- intake_id:" in text
    assert "- focus_priority:" in text
    assert "- special_attention:" in text
    assert "- review_refs:" in text
    assert "- verdict_refs:" in text
    assert "## 评审视角" in text
    assert "- preserve_tensions: [`真实用户是否看见并理解了解释能力`]" in intake
    assert "- used_default_rules: `false`" in intake


def test_writeback_generate_renders_audience_and_subtitle(tmp_path):
    intake = tmp_path / "intake.md"
    intake.write_text(
        """# Writeback Intake Record
- intake_id: `intake-demo`
- collaboration_mode: `integrated`
- focus_priority: [`机制`, `用户信任`]
- target_audience: `team`
- decision_intent: `understand`
- evidence_posture: `balanced`
- special_attention: []
- extra_questions: [`这是不是范式迁移`, `是否真的改变协作结构`]
- avoidances: []
- preserve_tensions: []
- used_default_rules: `false`
"""
    )
    target = tmp_path / "writeback.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_generate.py",
            "render",
            "--writeback-id",
            "writeback-demo",
            "--intake-file",
            str(intake),
            "--output",
            str(target),
            "--title",
            "父标题",
            "--subtitle",
            "副标题",
            "--summary",
            "摘要",
            "--synthesis-ref",
            "synthesis-demo",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "- target_audience: `team`" in text
    assert "- extra_questions: [`这是不是范式迁移`, `是否真的改变协作结构`]" in text
    assert "## 副标题" in text
    assert "副标题" in text
    assert "- synthesis_ref: `synthesis-demo`" in text


def run_render_longform(tmp_path):
    target = tmp_path / "writeback-longform.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_generate.py",
            "render-longform",
            "--writeback-id",
            "writeback-integrated-team-paradigm",
            "--intake-file",
            "library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md",
            "--synthesis-file",
            "library/syntheses/podcasts/agent-team-governability-2026-04.md",
            "--output",
            str(target),
            "--title",
            "从单 Agent 工具到可治理的 Agent Team：五条一线语料中的编排、协作与企业化信号",
            "--subtitle",
            "给团队看的 integrated 版：Multi-Agent 是否已进入范式迁移期",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return result, target


def test_writeback_generate_render_longform_creates_real_sections(tmp_path):
    result, target = run_render_longform(tmp_path)
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "## 研究问题" in text
    assert "## 综述导言" in text
    assert "## 文献综述" in text
    assert "## 综合判断" in text
    assert "## Problem Statement" in text
    assert "## Assumptions" in text
    assert "## AI-native UX 视角" in text
    assert "## 本轮 Research Direction" in text
    assert "## 保留分歧" in text


def test_writeback_generate_render_longform_has_real_evidence_and_no_placeholders(tmp_path):
    result, target = run_render_longform(tmp_path)
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "待补充" not in text
    assert "待由 evidence" not in text
    assert "- research_direction: `multi-agent 是否已经从高级 workflow 包装，进入可治理的 Agent Team 范式迁移`" in text
    assert "- direction_status: `user_provided`" in text
    assert "### 主题 1：执行控制层" in text
    assert "代表引文 1：" in text
    assert "代表引文 2：" in text
    assert "观察：" in text
    assert "证据来源：" in text
    assert "为什么重要：" in text
    assert "责任状态卡" in text
    assert "分级决策卡" in text
    assert "异步沟通面板" in text
    assert "审计与证据抽屉" in text
    assert "## Review Introduction" not in text
    assert "[43:02] 写代码的本质不在于快速产出，而在于管理复杂度。" in text
    assert "[11:38] 是不是我反而成为了未来人机协作最大的一个瓶颈。" in text
    assert "[18:56] 和你把一个人当一个员工时，你就直接这么去想，你发现他就完全不一样。" in text
    assert "[01:16:57] 是我认为我这个人是一个一百人的公司。" in text
    assert "[01:04:46] 你不应该干活嘛，你应该给 AI 塑造一个良好的工作环境嘛，" in text
    assert "[00:02] AI 是人类历史上最激动人心的技术革命" not in text


def run_render_review_pack(tmp_path):
    target = tmp_path / "writeback-review-pack.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_generate.py",
            "render-review-pack",
            "--intake-file",
            "library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md",
            "--synthesis-file",
            "library/syntheses/podcasts/agent-team-governability-2026-04.md",
            "--output",
            str(target),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return result, target


def test_writeback_generate_render_review_pack_creates_research_sections(tmp_path):
    result, target = run_render_review_pack(tmp_path)
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "## Research Question" in text
    assert "## Review Introduction" in text
    assert "## Thematic Literature Review" in text
    assert "## Counter-Signals And Tensions" in text
    assert "## Draft Problem Statement" in text
    assert "## Draft Assumptions" in text
    assert "multi-agent 是否已经从高级 workflow 包装，进入可治理的 Agent Team 范式迁移" in text


def test_pilot_review_pack_cluster_roles_are_assigned_from_real_evidence():
    module = load_writeback_generate_module()
    intake = Path("library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md").read_text()
    synthesis = Path("library/syntheses/podcasts/agent-team-governability-2026-04.md").read_text()

    clusters = module.build_pilot_review_pack_clusters(intake, synthesis)

    assert [cluster["title"] for cluster in clusters] == [
        "执行控制层",
        "协作与角色层",
        "治理与前台 UX 外显层",
    ]

    first_roles = {item["role"]: item["text"] for item in clusters[0]["evidence_roles"]}
    second_roles = {item["role"]: item["text"] for item in clusters[1]["evidence_roles"]}
    third_roles = {item["role"]: item["text"] for item in clusters[2]["evidence_roles"]}

    assert "写代码的本质不在于快速产出" in first_roles["anchor"]
    assert "自动化的测试" in first_roles["support"] or "代码审核" in first_roles["support"]
    assert "成果很少" in first_roles["counter_signal"]

    assert "瓶颈" in second_roles["anchor"] or "协作" in second_roles["anchor"]
    assert "员工" in second_roles["support"] or "分工" in second_roles["support"]
    assert "组织会缩小" in second_roles["counter_signal"] or "效率更高" in second_roles["counter_signal"]

    assert "一百人的公司" in third_roles["anchor"] or "治理" in third_roles["anchor"]
    assert "工作环境" in third_roles["support"] or "安全" in third_roles["support"]
    assert "我拥有 AI" in third_roles["counter_signal"] or "封闭的系统" in third_roles["counter_signal"]


def test_pilot_review_pack_requires_matching_role_candidates():
    module = load_writeback_generate_module()
    with pytest.raises(SystemExit, match="required role: anchor|matched required role: anchor"):
        module.pick_evidence_candidate(
            [
                {
                    "slug": "demo",
                    "source_kind": "summary",
                    "text": "generic line",
                    "role": "support",
                    "role_score": 0,
                }
            ],
            "anchor",
            ["demo"],
            strict=True,
        )


def test_pilot_review_pack_requires_pilot_evidence_files():
    module = load_writeback_generate_module()
    with pytest.raises(SystemExit, match="missing highlights evidence for pilot slug: demo-slug"):
        module.require_pilot_evidence(
            "demo-slug",
            {
                "summary": ["summary line"],
                "highlights": [],
                "transcript": [],
            },
        )


def test_render_review_pack_includes_cluster_counter_signals(tmp_path):
    result, target = run_render_review_pack(tmp_path)
    assert result.returncode == 0, result.stderr
    text = target.read_text()

    assert "## Counter-Signals And Tensions" in text
    assert "- 执行控制层：" in text
    assert "成果很少" in text
    assert "- 协作与角色层：" in text
    assert "组织会缩小" in text or "效率更高" in text
    assert "- 治理与前台 UX 外显层：" in text
    assert "我拥有 AI" in text or "封闭的系统" in text


def test_render_review_pack_keeps_pilot_mechanism_scoped_to_integrated_team_paradigm(tmp_path):
    target = tmp_path / "non-pilot-review-pack.md"
    result = subprocess.run(
        [
            "python3",
            "scripts/writeback_generate.py",
            "render-review-pack",
            "--intake-file",
            "library/writeback-intakes/podcasts/intake-podwise-ai-7650271-dfb97270-default.md",
            "--synthesis-file",
            "library/syntheses/podcasts/agent-team-governability-2026-04.md",
            "--output",
            str(target),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    text = target.read_text()

    assert "### 主题：执行控制层" not in text
    assert "### 主题：协作与角色层" not in text
    assert "### 主题：治理与前台 UX 外显层" not in text
    assert "- 执行控制层：" not in text
    assert "multi-agent 是否已经从高级 workflow 包装，进入可治理的 Agent Team 范式迁移" not in text


def test_review_pack_preserves_quote_paraphrase_evidence_shape(tmp_path):
    result, target = run_render_review_pack(tmp_path)
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "Direct quote" in text
    assert "Paraphrase" in text
    assert "Evidence" in text
    assert "Why it matters" in text
    assert "podwise-ai-7758431-2cd3ef48" in text
    assert text.count("### 主题：") >= 2
    assert "因为它在强调 强调" not in text
    assert "。。" not in text
    assert "写代码的本质不在于快速产出" in text
    assert "自动化的测试" in text
    assert "把一个人当一个员工" in text
    assert "一百人的公司" in text
    assert "塑造一个良好的工作环境" in text
    assert "[00:02] AI 是人类历史上最激动人心的技术革命" not in text


def test_research_direction_writeback_contains_review_driven_sections(tmp_path):
    result, target = run_render_longform(tmp_path)
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "## 研究问题" in text
    assert "## 综述导言" in text
    assert "## 文献综述" in text
    assert "代表引文 1：" in text
    assert "代表引文 2：" in text
    assert "观察：" in text
    assert "证据来源：" in text
    assert "为什么重要：" in text
    assert "## Problem Statement" in text
    assert "## Assumptions" in text
    assert "## AI-native UX 视角" in text
    assert "## 本轮 Research Direction" in text
    assert "责任状态卡" in text
    assert "分级决策卡" in text
    assert "异步沟通面板" in text
    assert "审计与证据抽屉" in text
    assert "## Research Question" not in text
    assert "## Review Introduction" not in text


def test_pilot_final_writeback_sections_are_review_derived():
    module = load_writeback_generate_module()
    intake = Path("library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md").read_text()
    synthesis = Path("library/syntheses/podcasts/agent-team-governability-2026-04.md").read_text()

    review = module.build_pilot_review_pack_sections(intake, synthesis)
    final = module.build_pilot_final_writeback_objects(intake, synthesis)

    review_paraphrases = [cluster["paraphrase"] for cluster in review["clusters"]]
    judgment_text = final["judgment"]["text"]
    for paraphrase in review_paraphrases:
        assert paraphrase not in judgment_text

    assert final["judgment"]["basis"]
    assert [item["title"] for item in final["judgment"]["basis"]] == [
        "执行控制层",
        "协作与角色层",
        "治理与前台 UX 外显层",
    ]
    assert final["problem"]["source_clusters"] == [
        "执行控制层",
        "协作与角色层",
        "治理与前台 UX 外显层",
    ]
    assert final["problem"]["why_clauses"]
    for clause in final["problem"]["why_clauses"]:
        assert clause in final["problem"]["text"]
    assert final["problem"]["counter_clauses"]
    for clause in final["problem"]["counter_clauses"]:
        assert clause in final["problem"]["text"]

    for item in final["assumptions"]["supported"]:
        assert item["cluster"] in item["text"]
        assert item["reason"]
        assert item["reason"] in item["text"]
        assert item["evidence"]
    for item in final["assumptions"]["pending"]:
        assert item["cluster"] in item["text"]
        assert item["reason"]
        assert item["reason"] in item["text"]
        assert item["evidence"]


def test_pilot_final_ai_native_ux_propositions_trace_cluster_evidence():
    module = load_writeback_generate_module()
    intake = Path("library/writeback-intakes/podcasts/matrix/integrated-team-paradigm.md").read_text()
    synthesis = Path("library/syntheses/podcasts/agent-team-governability-2026-04.md").read_text()

    final = module.build_pilot_final_writeback_objects(intake, synthesis)
    propositions = final["ux"]["propositions"]

    assert [item["name"] for item in propositions] == [
        "责任状态卡",
        "分级决策卡",
        "异步沟通面板",
        "审计与证据抽屉",
    ]
    assert propositions[0]["source_cluster_ids"] == ["collaboration_roles", "governance_frontstage_ux"]
    assert propositions[1]["source_cluster_ids"] == ["execution_control", "governance_frontstage_ux"]
    assert propositions[2]["source_cluster_ids"] == ["collaboration_roles"]
    assert propositions[3]["source_cluster_ids"] == ["execution_control", "governance_frontstage_ux"]
    for proposition in propositions:
        assert proposition["source_evidence"]
        assert proposition["cluster_notes"]
        assert proposition["reason_clause"]
        assert proposition["reason_clause"] in proposition["description"]
        for note in proposition["cluster_notes"]:
            assert note in proposition["description"]


def test_materialized_review_pack_has_research_sections():
    text = Path("library/review-packs/podcasts/review-pack-agent-team-paradigm.md").read_text()
    assert "# Research Review Pack" in text
    assert "## Research Question" in text
    assert "## Review Introduction" in text
    assert "## Thematic Literature Review" in text
    assert "## Counter-Signals And Tensions" in text
    assert "## Draft Problem Statement" in text
    assert "## Draft Assumptions" in text
    assert "因为它在强调 强调" not in text
    assert "。。" not in text
    assert "写代码的本质不在于快速产出" in text
    assert "自动化的测试" in text
    assert "把一个人当一个员工" in text
    assert "一百人的公司" in text
    assert "塑造一个良好的工作环境" in text
    assert "[00:02] AI 是人类历史上最激动人心的技术革命" not in text


def test_materialized_review_pack_uses_three_theme_clusters():
    text = Path("library/review-packs/podcasts/review-pack-agent-team-paradigm.md").read_text()
    cluster_titles = re.findall(r"^### 主题：(.+)$", text, flags=re.M)
    assert cluster_titles == ["执行控制层", "协作与角色层", "治理与前台 UX 外显层"]
    assert text.count("### 主题：") == 3


def test_generate_real_review_pack_is_artifact_driven(tmp_path):
    module = load_writeback_generate_module()
    artifact_root = tmp_path / "library" / "artifacts" / "podcasts" / "demo"
    artifact_root.mkdir(parents=True, exist_ok=True)
    (artifact_root / "summary.md").write_text(
        "## Content\nmulti-agent 的关键不在更多 agent，而在治理边界。\n",
        encoding="utf-8",
    )
    (artifact_root / "highlights.md").write_text(
        "## Content\n1. [00:31] Harness engineering 让 agent 能在围栏内协作。\n",
        encoding="utf-8",
    )

    cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        text = module.generate_real_review_pack(
            bundle_id="demo",
            source_paths=["library/sources/podcasts/demo.md"],
            artifact_paths=[
                "library/artifacts/podcasts/demo/summary.md",
                "library/artifacts/podcasts/demo/highlights.md",
            ],
            direction_text="multi-agent 是否已经进入可治理的 Agent Team 范式迁移",
            direction_status="user_provided",
            links=["https://podcasts.apple.com/us/podcast/example/id123"],
            link_types=["podcast"],
            link_results=[
                {
                    "link": "https://podcasts.apple.com/us/podcast/example/id123",
                    "link_type": "podcast",
                    "source_path": "library/sources/podcasts/demo.md",
                    "artifact_paths": [
                        "library/artifacts/podcasts/demo/summary.md",
                        "library/artifacts/podcasts/demo/highlights.md",
                    ],
                }
            ],
        )
    finally:
        os.chdir(cwd)

    assert "Direct quote" in text
    assert "Paraphrase" in text
    assert "Evidence" in text
    assert "Why it matters" in text
    assert "Harness engineering" in text
    assert "治理边界" in text


def test_generate_real_writeback_uses_artifact_evidence(tmp_path):
    module = load_writeback_generate_module()
    artifact_root = tmp_path / "library" / "artifacts" / "xiaohongshu" / "demo"
    artifact_root.mkdir(parents=True, exist_ok=True)
    (artifact_root / "full_text.md").write_text(
        "## Content\nAgent 真正难的不是执行，而是跨轮次保持责任边界。\n",
        encoding="utf-8",
    )

    cwd = Path.cwd()
    try:
        os.chdir(tmp_path)
        text = module.generate_real_writeback(
            bundle_id="demo",
            source_paths=["library/sources/xiaohongshu/demo.md"],
            artifact_paths=["library/artifacts/xiaohongshu/demo/full_text.md"],
            direction_text="agent team 的责任边界如何被产品化",
            direction_status="user_provided",
            links=["https://www.xiaohongshu.com/explore/123"],
            link_types=["xiaohongshu"],
            link_results=[
                {
                    "link": "https://www.xiaohongshu.com/explore/123",
                    "link_type": "xiaohongshu",
                    "source_path": "library/sources/xiaohongshu/demo.md",
                    "artifact_paths": ["library/artifacts/xiaohongshu/demo/full_text.md"],
                }
            ],
        )
    finally:
        os.chdir(cwd)

    assert "## 文献综述" in text
    assert "## AI-native UX 视角" in text
    assert "责任边界" in text
    assert "attention arbitration" in text or "责任状态" in text or "handoff" in text


def test_materialized_review_pack_has_multiple_quotes_per_cluster():
    text = Path("library/review-packs/podcasts/review-pack-agent-team-paradigm.md").read_text()
    clusters = re.split(r"^### 主题：.+$", text, flags=re.M)[1:]
    assert len(clusters) == 3
    for cluster in clusters:
        assert cluster.count("**Direct quote**") == 2


def test_writeback_generate_render_review_pack_matches_committed_pilot(tmp_path):
    result, target = run_render_review_pack(tmp_path)
    assert result.returncode == 0, result.stderr
    generated = target.read_text()
    committed = Path("library/review-packs/podcasts/review-pack-agent-team-paradigm.md").read_text()
    assert generated == committed


def test_writeback_generate_render_longform_matches_committed_pilot(tmp_path):
    result, target = run_render_longform(tmp_path)
    assert result.returncode == 0, result.stderr
    generated = target.read_text()
    committed = Path("library/writebacks/podcasts/matrix/integrated-team-paradigm.md").read_text()
    assert generated == committed


def test_materialized_integrated_team_paradigm_is_longform():
    text = Path("library/writebacks/podcasts/matrix/integrated-team-paradigm.md").read_text()
    assert "待补充" not in text
    assert "待由 evidence" not in text
    assert "## 研究问题" in text
    assert "## 综述导言" in text
    assert "## 文献综述" in text
    assert "## 综合判断" in text
    assert "## Problem Statement" in text
    assert "## Assumptions" in text
    assert "## AI-native UX 视角" in text
    assert "## 本轮 Research Direction" in text
    assert "- research_direction: `multi-agent 是否已经从高级 workflow 包装，进入可治理的 Agent Team 范式迁移`" in text
    assert "- direction_status: `user_provided`" in text
    assert "### 主题 1：执行控制层" in text
    assert "### 主题 2：协作与角色层" in text
    assert "### 主题 3：治理与前台 UX 外显层" in text
    assert "代表引文 1：" in text
    assert "代表引文 2：" in text
    assert "观察：" in text
    assert "证据来源：" in text
    assert "为什么重要：" in text
    assert "## Review Introduction" not in text
    assert "责任状态卡" in text
    assert "分级决策卡" in text
    assert "异步沟通面板" in text
    assert "审计与证据抽屉" in text
    assert "（协作与角色层 / 治理与前台 UX 外显层）" in text
    assert "（执行控制层 / 治理与前台 UX 外显层）" in text


def test_materialized_pilot_writeback_uses_three_review_clusters():
    text = Path("library/writebacks/podcasts/matrix/integrated-team-paradigm.md").read_text()
    cluster_titles = re.findall(r"^### 主题 \d+：(.+)$", text, flags=re.M)
    assert cluster_titles == ["执行控制层", "协作与角色层", "治理与前台 UX 外显层"]
    assert text.count("代表引文 1：") == 3
    assert text.count("代表引文 2：") == 3
    assert text.count("证据来源：") == 3


def test_materialized_pilot_writeback_ai_native_ux_has_design_objects():
    text = Path("library/writebacks/podcasts/matrix/integrated-team-paradigm.md").read_text()
    assert "## AI-native UX 视角" in text
    assert "责任状态卡" in text
    assert "分级决策卡" in text
    assert "异步沟通面板" in text
    assert "审计与证据抽屉" in text
