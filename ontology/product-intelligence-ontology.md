## Objective

This ontology organizes product intelligence around durable change, explicit evidence, and reviewable judgments.

## 1. Primary Object Families

### 1. Product
Product is the anchor object, not the ingestion entrypoint.
Minimum fields:
- `product_id`
- `name`
- `company`
- `domain`
- `core_problem`
- `target_user`
- `status`
- `confidence`
- `last_updated`

### 2. Event
Event is the primary ingestion object and the smallest durable change unit.

Minimum Event fields:
- `event_id`
- `product_id`
- `title`
- `event_type`
- `date_detected`
- `time_window`
- `what_changed`
- `change_layer`
- `affected_capabilities`
- `target_problems`
- `evidence_refs`
- `status`

### 3. Source
Source is the source container with perspective metadata.
Minimum fields:
- `source_id`
- `source_type`
- `source_container`
- `publisher`
- `published_at`
- `title`
- `url_or_ref`
- `perspective`
- `confidence`

### 4. Artifact
Artifact is the evidence slice used to anchor interpretation.
Minimum fields:
- `artifact_id`
- `source_id`
- `slice_type`
- `quote_or_segment`
- `location`
- `perspective`
- `why_relevant`

### 5. Claim
A claim is a judged statement about a product, event, pattern, or thesis.
Minimum fields:
- `claim_id`
- `claim_text`
- `about_objects`
- `evidence_refs`
- `counterevidence_refs`
- `status`
- `confidence`

### 6. Pattern
A pattern is a reusable abstraction formed only after evidence accumulates across events and claims.
Minimum fields:
- `pattern_id`
- `pattern_name`
- `abstraction`
- `supported_by_claims`
- `evidence_refs`
- `status`
- `confidence`

### 7. Thesis
A thesis is a long-term judgment that survives review and can be promoted or downgraded.
Minimum fields:
- `thesis_id`
- `thesis_text`
- `scope`
- `supporting_patterns`
- `counterclaims`
- `status`
- `confidence`

### 8. Verdict
A verdict records the review outcome that updates long-term judgment status.
Minimum fields:
- `verdict_id`
- `target_type`
- `target_id`
- `outcome`
- `rationale`
- `evidence_refs`
- `judge`
- `status_change`

### 9. Counterclaim
A counterclaim is a first-class objection object that records the strongest known disagreement against a claim, pattern, or thesis.
Minimum fields:
- `counterclaim_id`
- `counterclaim_text`
- `against_object`
- `evidence_refs`
- `status`

### 10. WhyNowHypothesis
A WhyNowHypothesis is a first-class timing hypothesis that explains why an observed change is happening now rather than earlier or later.
Minimum fields:
- `why_now_hypothesis_id`
- `hypothesis_text`
- `trigger_event_ids`
- `evidence_refs`
- `status`
- `confidence`

## 2. Key Relations

- `Source CONTAINS Artifact`
- `Artifact ANCHORS Event`
- `Event UPDATES Product`
- `Event SUPPORTS Claim`
- `Claim ABSTRACTS_TO Pattern`
- `Pattern SUPPORTS Thesis`
- `Counterclaim CONTESTS Claim | Pattern | Thesis`
- `Event TESTS WhyNowHypothesis`
- `Verdict UPDATES Claim | Pattern | Thesis`

## 3. Knowledge Status Vocabulary

- `observed`
- `described`
- `inferred`
- `hypothesized`
- `contested`
- `confirmed`
- `deferred`
- `rejected`
- `written_back`

## 4. Evidence Quality Vocabulary

- `first_hand_official`
- `first_hand_engineering`
- `first_hand_demo`
- `first_hand_user_signal`
- `second_hand_media`
- `community_signal`
- `benchmark_or_research`
- `regulatory_or_policy`
- `mixed`
