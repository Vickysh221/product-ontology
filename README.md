# Product Learning Library

This repository is an event-centered, evidence-constrained, review-updated ontology-based product analysis library.

The operating model is deliberately narrow:
- Product is the anchor object.
- Event is the entrypoint for durable change.
- Artifact is the evidence carrier.
- Review and verdict records are the promotion and downgrade mechanism for long-term judgments.
- The core evidence chain is `Source -> Artifact -> Event -> Claim -> Pattern -> Thesis`.
- The writeback chain is `Source -> Artifact -> Candidate -> Review/Verdict -> Writeback Intake -> Writeback`.

## Why This Exists

This is not a news scraper and not a generic competitor notes repo. It exists to keep product understanding traceable across evidence layers, so long-term judgments can be updated without losing provenance.

The repository is built to answer:
- What changed
- What evidence supports the change
- Which layer changed
- What should be promoted into a stable judgment
- What should be downgraded, reopened, or weakened by review

## Operating Principles

1. Object-centered, not document-centered.
2. Event-centered, not summary-centered.
3. Evidence-first, with explicit Artifact layers.
4. Review-updated, so long-term judgments can move up or down over time.
5. No skipped layers on writeback.
6. Writeback generation always passes through intake, intake fields may be left empty, and default report rules apply when no extra guidance is provided.
7. Traceability is mandatory from thesis-level judgment back to source.

## Repository Structure

```text
product-ontology/
  README.md
  ontology/
    cognition-ontology.md
    product-intelligence-ontology.md
    jury-review-ontology.md
  schemas/
    ontology-manifest.json
    session-progress-record.schema.json
    claim-record.schema.json
    product-record.schema.json
    writeback-intake.schema.json
  library/
    sources/
    events/
    products/
    claims/
    hypotheses/
    patterns/
    methods/
    reviews/
    sessions/
    questions/
    writebacks/
    writeback-intakes/
    _operating-notes.md
  templates/
    source-item.md
    product-record.md
    product-event-card.md
    claim-record.md
    method-card.md
    pattern-card.md
    jury-review-record.md
    session-progress-record.md
    writeback-intake.md
    writeback-proposal.md
    today-brief.md
    weekly-pattern-review.md
    monthly-thesis-update.md
  seed/
    watchlist.md
    initial-questions.md
    first-tracking-theses.md
  PRD Session Summary.md
```

Directory responsibilities:
- Current `library/` directories store sources, events, products, claims, hypotheses, patterns, methods, reviews, sessions, questions, and writebacks.
- `library/writeback-intakes/` stores human-in-the-loop report intent records, including empty/default intake runs.
- Current `schemas/` files cover the manifest, product records, claim records, session progress records, and writeback intake records.
- Upcoming workstreams include artifact, counterclaim, thesis, verdict, and review-lens layers once those files are added to the tree.

## Getting Started

1. Read [`ontology/cognition-ontology.md`](./ontology/cognition-ontology.md) and [`ontology/product-intelligence-ontology.md`](./ontology/product-intelligence-ontology.md) first.
2. Then inspect the current templates for `source-item`, `product-record`, `product-event-card`, `claim-record`, `pattern-card`, `jury-review-record`, `session-progress-record`, `writeback-intake`, and `writeback-proposal`.
3. Start with `seed/watchlist.md` to choose products and their first event streams.
4. Capture evidence in source notes and event cards before forming claims.
5. Use review records to adjust the status of claims, patterns, and theses rather than rewriting history.
6. Treat artifact, counterclaim, thesis, and verdict layers as upcoming repository additions until those files exist in the tree.

## Podcast Ingestion

This repository includes a phase-1 Podwise ingestion flow for podcast and video episode materials.

Prerequisites:
- `podwise` is installed and authorized.
- The repository-level MCP configuration in [`.codex/config.toml`](./.codex/config.toml) remains available when running commands from this repo.

Commands:

```bash
python3 scripts/podcast_import.py add-url https://example.com/episode-1 https://example.com/episode-2
python3 scripts/podcast_import.py import-list
python3 scripts/source_ingest.py init-source official "OpenAI blog" --url https://openai.com/news/ --source-type official_release --ingestion-method official_list
python3 scripts/wechat_wewe_rss_import.py import-feed <feed-url> <source-label>
python3 scripts/wechat_candidates.py extract <wechat-slug>
python3 scripts/wechat_candidates.py promote <wechat-slug> --event-ids <event-candidate-id> --claim-ids <claim-candidate-id>
python3 scripts/xiaohongshu_redbook_import.py import-note <source-label> <title> <note-url> --body-file <path>
python3 scripts/xiaohongshu_video_transcript.py queue <note-url>
python3 scripts/xiaohongshu_video_transcript.py import-transcript <note-url> --body-file <path>
python3 scripts/xiaohongshu_candidates.py extract <xiaohongshu-slug>
python3 scripts/xiaohongshu_candidates.py promote <xiaohongshu-slug> --event-ids <event-candidate-id> --claim-ids <claim-candidate-id>
python3 scripts/podcast_candidates.py extract <episode-slug>
python3 scripts/podcast_candidates.py promote <episode-slug> --event-ids <event-candidate-id> --claim-ids <claim-candidate-id>
```

Behavior:
- URLs are stored in [`seed/podcast-import-list.md`](./seed/podcast-import-list.md).
- Duplicate URLs are ignored using `source_url` as the dedupe key.
- Each imported episode creates one source record in `library/sources/podcasts/`.
- Each imported episode creates three artifact records in `library/artifacts/podcasts/<episode-slug>/`: `transcript.md`, `summary.md`, and `highlights.md`.
- The import flow stops at `Source -> Artifact`; Phase 2 candidate extraction is a separate step and does not write directly into durable `events/` or `claims/`.

Candidate extraction:
- Dynamic filtering and scoring are controlled by [`seed/watch-profile.yaml`](./seed/watch-profile.yaml).
- Phase 2 writes only candidate files into `library/sessions/podcast-candidates/<episode-slug>/`.
- The extractor reads `summary + highlights` first and keeps `transcript` as follow-up evidence for later refinement.
- Candidate outputs use Chinese explanatory fields and try to attach transcript timestamps even for summary-derived candidates.
- Manual promotion writes durable records into `library/events/podcasts/` and `library/claims/podcasts/`, and appends a decision trail to `library/sessions/podcast-candidates/<episode-slug>/promotion-log.md`.

## Source Architecture

The repository now treats four initial channels as parallel ingestion sources:
- `podwise` for podcast episodes
- `wewe-rss` for WeChat Official Account articles
- `redbook` for Xiaohongshu notes and comments
- `official` for official websites, OTA pages, release notes, and engineering blogs

Normalization rules:
- Every channel writes a normalized source record with `source_type`, `platform`, `ingestion_method`, `source_url`, and `canonical_url`.
- Every channel writes normalized artifacts such as `transcript`, `summary`, `highlights`, `full_text`, `comment_batch`, or `metadata_snapshot`.
- Official pages are listed in [`seed/official-sources.yaml`](./seed/official-sources.yaml) by brand and page label.
- Shared source scaffolding lives in [`scripts/source_ingest.py`](./scripts/source_ingest.py) so channel-specific adapters can reuse one repository structure instead of inventing their own paths.

Adapter entrypoints:
- [`scripts/wechat_wewe_rss_import.py`](./scripts/wechat_wewe_rss_import.py) imports WeChat article text from a wewe-rss RSS feed or from manual article exports. Feed targets can be tracked in [`seed/wechat-sources.yaml`](./seed/wechat-sources.yaml).
- [`scripts/wechat_candidates.py`](./scripts/wechat_candidates.py) extracts candidates from WeChat `full_text.md` artifacts and supports manual promotion into durable `events/wechat/` and `claims/wechat/` records with a promotion log.
- [`scripts/xiaohongshu_redbook_import.py`](./scripts/xiaohongshu_redbook_import.py) imports Xiaohongshu notes from manual exports, saved redbook JSON payloads, or direct `redbook read/comments` calls when the CLI is installed. Targets can be tracked in [`seed/xiaohongshu-sources.yaml`](./seed/xiaohongshu-sources.yaml).
- [`scripts/xiaohongshu_video_transcript.py`](./scripts/xiaohongshu_video_transcript.py) adds a tool-agnostic transcript workflow for Xiaohongshu video sources. It writes `transcript-request.md` into the note artifact directory, then later imports a finished `transcript.md` without binding the repo to a specific ASR provider.
- [`scripts/xiaohongshu_candidates.py`](./scripts/xiaohongshu_candidates.py) extracts candidates from `full_text.md`, `transcript.md`, and `comment_batch.md` for Xiaohongshu sources, and it also supports manual promotion into durable `events/xiaohongshu/` and `claims/xiaohongshu/` records with a promotion log.

## Main Tracking Lines

### AI Coding / Agent Workflow

Focus on harness, orchestration, runtime, workspace, reviewer loops, long-running tasks, and real friction in environment, cost, and stability.

### Multi-Agent Collaboration / Memory / Workspace

Focus on persistent identity, object continuity, long-term memory, writeback, approval boundaries, and role-based collaboration.

### Assisted Driving / Trust Framing / Vehicle AI

Focus on capability packaging, HMI, trust, safety communication, regulation, and the gap between demo and durable product behavior.

## Output Layers

### Daily Brief

Keep only high-signal changes:
- what changed
- why it matters
- how it affects the long-term chain

### Weekly Pattern Review

Answer which changes are repeating across events and which ones are still isolated.

### Monthly Thesis Update

Update the long-term judgment set with explicit promotion, weakening, or downgrade decisions.
