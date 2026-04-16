from pathlib import Path
import subprocess


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
    assert "## 摘要" in text
    assert "## 主判断" in text
    assert "## 机制拆解" in text
    assert "## 能力边界与工作流变化" in text
    assert "## 针对本次追问的回答" in text
    assert "## 证据锚点" in text
    assert "## 保留分歧" in text


def test_writeback_generate_render_longform_has_real_evidence_and_no_placeholders(tmp_path):
    result, target = run_render_longform(tmp_path)
    assert result.returncode == 0, result.stderr
    text = target.read_text()
    assert "待补充" not in text
    assert "待由 evidence" not in text
    assert "## 针对本次追问的回答" in text
    assert "## 证据锚点" in text
    assert "- `podwise-ai-7758431-2cd3ef48`" in text
    assert "- `podwise-ai-7718625-7d0dc7d1`" in text
    assert "- `podwise-ai-7635732-bdfba3f3`" in text
    assert "- `podwise-ai-7504915-91b52a0e`" in text
    assert "- `podwise-ai-7368984-f9a0fefa`" in text


def test_materialized_integrated_team_paradigm_is_longform():
    text = Path("library/writebacks/podcasts/matrix/integrated-team-paradigm.md").read_text()
    assert "待补充" not in text
    assert "待由 evidence" not in text
    assert "## 机制拆解" in text
    assert "## 能力边界与工作流变化" in text
    assert "## 针对本次追问的回答" in text
    assert "podwise-ai-7758431-2cd3ef48" in text
    assert "podwise-ai-7368984-f9a0fefa" in text
