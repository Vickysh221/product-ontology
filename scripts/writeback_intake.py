import argparse
from pathlib import Path


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


def format_list(values: list[str]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(f"`{value}`" for value in values) + "]"


def build_markdown(args: argparse.Namespace) -> str:
    collaboration_mode = normalize_text(args.collaboration_mode)
    # Preserve matrix-guidance fields exactly as entered for downstream rendering.
    target_audience = normalize_text(args.target_audience)
    decision_intent = normalize_text(args.decision_intent)
    evidence_posture = normalize_text(args.evidence_posture)
    focus_priority = parse_csv(args.focus_priority)
    special_attention = parse_csv(args.special_attention)
    extra_questions = parse_csv(args.extra_questions)
    avoidances = parse_csv(args.avoidances)
    preserve_tensions = parse_csv(args.preserve_tensions)
    used_default_rules = args.use_defaults or not any(
        [
            collaboration_mode,
            focus_priority,
            target_audience,
            decision_intent,
            evidence_posture,
            special_attention,
            extra_questions,
            avoidances,
            preserve_tensions,
        ]
    )
    return f"""# Writeback Intake Record

- intake_id: `{args.intake_id}`
- collaboration_mode: `{collaboration_mode}`
- focus_priority: {format_list(focus_priority)}
- target_audience: `{target_audience}`
- decision_intent: `{decision_intent}`
- evidence_posture: `{evidence_posture}`
- special_attention: {format_list(special_attention)}
- extra_questions: {format_list(extra_questions)}
- avoidances: {format_list(avoidances)}
- preserve_tensions: {format_list(preserve_tensions)}
- used_default_rules: `{'true' if used_default_rules else 'false'}`
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a writeback intake record.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    create.add_argument("--intake-id", required=True)
    create.add_argument("--output", required=True)
    create.add_argument("--use-defaults", action="store_true")
    create.add_argument("--collaboration-mode", choices=["integrated", "sectioned", "appendix"])
    create.add_argument("--focus-priority")
    create.add_argument("--target-audience")
    create.add_argument("--decision-intent")
    create.add_argument("--evidence-posture")
    create.add_argument("--special-attention")
    create.add_argument("--extra-questions")
    create.add_argument("--avoidances")
    create.add_argument("--preserve-tensions")

    args = parser.parse_args()
    if args.command != "create":
        return 1

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_markdown(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
