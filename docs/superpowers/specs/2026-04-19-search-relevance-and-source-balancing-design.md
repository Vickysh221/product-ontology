# Search Relevance And Source Balancing Design

## Goal

Define how `podwise search`, `xiaohongshu search`, and future discovery-style source search decide which results are relevant enough to enter the system, and how the system avoids letting a single source type, brand, or hype-heavy result dominate downstream reports.

This spec treats search as a discovery-and-selection layer. Search results do **not** bypass `Source -> Artifact -> Review Pack -> Writeback`.

## Why This Exists

The current system can already turn standardized artifacts into review packs and writebacks. The missing piece is upstream selection quality:

- `podwise` search will return many episodes that mention a keyword without materially advancing the current research direction.
- `xiaohongshu` search will return many notes whose title or tags match a topic but whose content is marketing, reposted hype, or weak evidence.
- `web discovery` can find official pages, but stronger keyword density in one source can bias the final report if selection is not balanced.

The system therefore needs a consistent answer to two questions:

1. What does “highly relevant” mean for a search result?
2. How do we prevent a report from being overfit to one source type, one brand, or one loud sample?

## Scope

This spec covers:

- search result scoring for `podwise` and `xiaohongshu`
- a shared relevance model reusable by future source search
- source balancing before ingestion into a report bundle
- how approved search results enter the existing discovery / ingestion / report flow

This spec does **not** cover:

- full crawler implementation
- transcript generation for platforms that lack it
- long-term subscription harvesting
- changes to the downstream artifact-driven writeback architecture

## Design Principles

### 1. Search is discovery-first, not report-first

Search returns candidate sources. Candidates must still be normalized into `Source` and `Artifact` before they can influence a report.

### 2. Relevance is multi-factor, not keyword-only

A result is relevant only when it aligns with:

- the current research direction or search topic
- ontology-bearing signals such as capability, workflow, governance, trust, or device boundary
- sufficient evidence density
- acceptable source authority

### 3. Strong signals should not erase coverage

A single source type or a single brand with stronger wording should not monopolize the evidence pool if the research question is comparative.

### 4. Search output must stay reviewable

The system should show why a result was selected:

- matched topics
- matched ontology signals
- authority level
- evidence richness
- downgrade reasons

## Shared Search Relevance Model

Each search result is scored across five dimensions.

### A. Topic Relevance

Measures overlap with:

- user-supplied search topic
- current `research direction`
- `seed/watch-profile.yaml`
  - `domains`
  - `brands`
  - `active_topics`

High score examples:

- result explicitly discusses `AI 手机`, `agent 手机`, `系统级智能体`, `跨应用执行`
- result is about one of the target brands in the current round

Low score examples:

- result only mentions `AI` generically
- result hits a brand keyword but not the current product question

### B. Ontology Relevance

Measures whether the result contains signals that can realistically become product-analysis evidence.

Preferred ontology-bearing signals:

- capability boundary
- workflow shift
- governance / control
- trust / explainability
- role delegation
- coordination protocol
- device boundary expansion

Low ontology relevance examples:

- generic praise
- broad trend slogans
- “AI 很强”“非常智能” without a product mechanism

### C. Source Authority

Measures the credibility of the result’s speaking position.

Authority tiers:

- `official`
- `first_hand_operator`
- `structured_commentary`
- `social_signal`

This should reuse existing authority ideas from `watch-profile.yaml`, but the scoring is explicit at search time rather than only later during candidate extraction.

### D. Evidence Richness

Measures whether the result is likely to produce usable artifacts.

High richness examples:

- podwise result with transcript + summary + highlights
- xiaohongshu result with substantial `full_text`
- official page with clear product framing and multiple mechanism-bearing statements

Low richness examples:

- short title-only result
- xiaohongshu note with only hashtags
- social result with no extractable body

### E. Hype Penalty

Measures whether the result over-indexes on hype language and under-indexes on mechanism.

Penalty triggers include:

- exaggerated future claims
- empty superlatives
- pure launch-posturing with no product structure

This should reuse and extend the downgrade logic already present in `watch-profile.yaml`.

## Relevance Score Shape

The scoring model should remain interpretable.

Suggested shape:

`relevance_score = topic + ontology + authority + evidence - hype_penalty`

MVP does **not** need machine-learned ranking. A deterministic, explainable weighted score is preferred.

The system must also expose the components, not only the final score.

Each selected candidate should record:

- `relevance_score`
- `topic_matches`
- `ontology_matches`
- `authority_level`
- `evidence_richness`
- `downgrade_reasons`

## Source-Specific Relevance Rules

### Podwise Search

Use podwise search to find episodes, but rank them by evidence-bearing potential rather than title match alone.

Primary signals:

- title and summary mention the topic or research direction
- highlights contain mechanism-bearing phrases
- transcript availability exists
- speaker/show authority aligns with watch profile

Podwise-specific upgrades:

- preferred speakers
- preferred shows
- first-hand operator interviews
- deep product or engineering discussion

Podwise-specific downgrades:

- broad AI news roundup with weak product mechanism
- generic market commentary with little product evidence

### Xiaohongshu Search

Use xiaohongshu search as a source of:

- product demos
- launch framing
- user-visible product behavior
- social and experiential signals

Primary signals:

- title and body mention the target object and mechanism
- note body includes concrete claims about what the product can do
- transcript exists or can be requested for video-heavy notes
- comments reveal tension, friction, or user interpretation

Xiaohongshu-specific upgrades:

- visible product behavior
- system-level phrasing
- cross-app or assistant workflow demonstrations
- high-quality screenshots / structured descriptions

Xiaohongshu-specific downgrades:

- only hashtags
- reposted marketing lines
- no body beyond sloganized copy
- purely emotional reactions without product detail

## Source Balancing

Relevance alone is not enough. The selected pool must also be balanced before ingestion into a research bundle.

### Why Balancing Is Needed

Without balancing:

- a single brand with stronger wording can dominate
- a single source type can determine the final report tone
- the report may become a disguised summary of the loudest source

### Balancing Dimensions

For comparative research, the system should balance on:

- brand coverage
- source-type coverage
- authority mix

### Minimum Coverage Rules

For a comparative report, aim for:

- at least 3 brands if the topic is market landscape oriented
- at least 2 source types when available
- at least one higher-authority source per major brand where possible

### Maximum Dominance Rules

Before ingestion, cap overrepresentation:

- do not allow one brand to occupy most of the selected set if the query is comparative
- do not allow one source type to dominate unless the user explicitly asked for that

### Fallback Behavior

If balancing would force very weak sources into the set, the system should:

- keep the stronger unbalanced set
- but explicitly report the coverage gap

This is preferable to pretending balanced evidence exists when it does not.

## Search Output Object

Search results should be normalized into a reviewed candidate list before approval.

Each candidate should include:

- `candidate_id`
- `title`
- `url`
- `platform`
- `source_type`
- `authority_level`
- `relevance_score`
- `topic_matches`
- `ontology_matches`
- `evidence_richness`
- `downgrade_reasons`
- `coverage_role`
  - e.g. `core`, `comparison`, `coverage_gap_fill`

This object is not yet a `Source`. It is a `source candidate`.

## Human-In-The-Loop Boundary

Search should stay reviewable.

The flow should be:

`search request -> scored source candidates -> approve selected sources -> ingest approved sources -> propose/accept research direction -> generate report`

Human approval should happen after scored candidates are produced and before ingestion.

This keeps the system from auto-ingesting a noisy search result set.

## Integration With Existing System

### Existing pieces to reuse

- `seed/watch-profile.yaml`
- `discover-web`
- `approve-sources`
- existing `link-to-report` ingestion and report flow

### New search-facing integration points

Add search-specific commands later, for example:

- `search-podwise`
- `search-xiaohongshu`

These should produce scored source candidates, not direct reports.

### Handoff

Approved candidates become URLs or source records that the current ingestion layer can consume.

The downstream chain remains:

`approved sources -> Source -> Artifact -> Research Direction -> Review Pack -> Writeback`

## Anti-Noise Guardrails

To avoid sliding back into noisy or hype-heavy search:

- reject candidates with only keyword overlap and no ontology signals
- downgrade source candidates that lack usable body text
- reject title-only xiaohongshu notes unless manually approved
- prefer podwise results with transcript/highlights over title-only matches
- record missing coverage rather than hiding it

## MVP Recommendation

For the first implementation pass:

- support scored search for `podwise` and `xiaohongshu`
- reuse `watch-profile.yaml`
- implement deterministic weighted scoring
- implement basic balancing for brand and source type
- write a reviewed candidate record under `library/sessions/search-selection/`
- keep approval explicit before ingestion

Do **not** yet attempt:

- embedding-based semantic ranking
- automatic cross-platform deduplication
- automated multi-round source expansion
- fully unattended ingestion from search

## Success Criteria

This design succeeds when:

- search results are ranked by more than keyword match
- selected candidates are explainable and reviewable
- comparative reports are less biased toward one loud source
- podwise and xiaohongshu search can feed the same downstream ingestion/report system
- the system can clearly say why a result was selected or rejected
