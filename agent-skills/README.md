# Agent Skills

Shareable skill pack for evidence-heavy research and structured collaboration workflows.

This folder is meant to be publishable as its own GitHub repository. The skills are kept generic; repo-specific rules live in example profiles.

## Included

- `product-ontological-analysis/`
  - Generic skill for provenance-preserving evidence -> review pack -> writeback workflows.
- `human-agent-coop-ux-init/`
  - Generic skill for durable human-agent or agent-agent progression records.
- `profiles/product-ontology.md`
  - Example of how a specific repository narrows a generic skill into concrete scripts, paths, and checks.

## Recommended Structure

```text
agent-skills/
  README.md
  product-ontological-analysis/
    SKILL.md
  human-agent-coop-ux-init/
    SKILL.md
  profiles/
    product-ontology.md
```

## Installation

Publish the contents of this folder as a standalone repository, or copy individual skill folders directly.

For Codex-style local install:

```bash
mkdir -p ~/.agents/skills
cp -R product-ontological-analysis ~/.agents/skills/
cp -R human-agent-coop-ux-init ~/.agents/skills/
```

## Packaging Rule

Keep the skill itself portable:

- no machine-specific absolute paths
- no repo-private assumptions in the generic `SKILL.md`
- no hardcoded runtime binaries tied to one workstation

Put repo-specific constraints in a profile file instead. A workspace can keep that profile in its own docs folder, or a public skill repo can keep examples under `profiles/`.

## How To Adapt

1. Keep the generic skill body stable.
2. Copy a profile template and replace the example repo details with your own scripts, artifact priorities, and verification commands.
3. In the target workspace, tell agents to read the repo profile before execution when one exists.

## Notes

- `profiles/product-ontology.md` is an example, not a universal contract.
- If you publish this folder directly, the repository root should be the contents of `agent-skills/`, not the surrounding `product-ontology` repo.
