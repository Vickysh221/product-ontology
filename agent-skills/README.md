# Product Ontological Analysis

Shareable Agent Skills-compatible skill for provenance-preserving evidence -> review pack -> writeback workflows.

This directory is meant to be published as its own repository. It ships one reusable public skill and one example repo profile.

## Included

### Public skill

- `product-ontological-analysis/`
  - Generic skill for evidence-constrained research and traceable writeback generation.

### Example profile

- `profiles/product-ontology.md`
  - Concrete example of how one repository narrows the generic skill into specific scripts, paths, and verification checks.

## Repository Layout

```text
product-ontological-analysis/
  README.md
  product-ontological-analysis/
    SKILL.md
  profiles/
    product-ontology.md
```

If you publish from the current `product-ontology` repository, the publishable root should be the contents of `agent-skills/`, not the surrounding repo.

## Install

### Codex / OpenClaw-style shared install

Use `~/.agents/skills` when you want a shared local install that Agent Skills-compatible runtimes can see:

```bash
mkdir -p ~/.agents/skills
cp -R product-ontological-analysis ~/.agents/skills/
```

### Claude Code install

Claude Code reads skills from `~/.claude/skills/<skill-name>/SKILL.md` for personal installs and `.claude/skills/<skill-name>/SKILL.md` for project-scoped installs.

For a personal install:

```bash
mkdir -p ~/.claude/skills
cp -R product-ontological-analysis ~/.claude/skills/
```

### Project-scoped install

If you want the skill to apply only inside one workspace, copy it into that workspace:

```bash
mkdir -p .agents/skills
cp -R product-ontological-analysis .agents/skills/
```

## Portability Rule

Keep the public skill portable:

- no machine-specific absolute paths
- no repo-private assumptions in the generic `SKILL.md`
- no hardcoded runtime binaries tied to one workstation

Put repo-specific constraints in a profile file instead. A workspace can keep that profile in its own docs folder, or a public repo can keep examples under `profiles/`.

## Adaptation

1. Keep the generic skill body stable.
2. Copy the example profile and replace its repo-specific paths, commands, and verification rules with your own.
3. In the target workspace, tell agents to read the repo profile before execution when one exists.

## Quick Check

After copying, the installed skill directory should contain a `SKILL.md` entrypoint:

```bash
find ~/.agents/skills ~/.claude/skills .agents/skills 2>/dev/null -path '*/product-ontological-analysis/SKILL.md' | sort
```
