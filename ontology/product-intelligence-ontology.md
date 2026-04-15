## 目标

把产品学习从“按资料类型分类”升级成“按对象、关系、证据和判断状态分类”。

## 1. Primary Object Families

### 1. Product
长期对象。
字段建议：
- `id`
- `name`
- `domain`
- `company`
- `core_object`
- `current_problem_it_solves`
- `target_user`
- `primary_workflow`
- `control_boundary`
- `memory_model`
- `collaboration_model`
- `trust_model`
- `current_thesis`
- `status`
- `confidence`
- `last_updated`

### 2. Product Event
最小“新事情”单元。
字段建议：
- `id`
- `product_id`
- `title`
- `date_detected`
- `event_type`
- `what_changed`
- `previous_state`
- `layer_changed`
- `why_now`
- `target_user`
- `core_tension`
- `evidence_refs`
- `user_reaction_summary`
- `impact_assessment`
- `writeback_candidate`

### 3. Source Item
任何一条来源记录。
字段建议：
- `id`
- `source_type`
- `source_domain`
- `publisher`
- `publish_date`
- `title`
- `url_or_ref`
- `products_mentioned`
- `people_mentioned`
- `topics`
- `core_claims`
- `product_changes_mentioned`
- `user_pains_mentioned`
- `timestamps_or_notable_segments`
- `evidence_quality`
- `confidence`

### 4. Claim
被判断的陈述，而非纯摘抄。
字段建议：
- `id`
- `claim_text`
- `about_objects`
- `lens`
- `evidence_refs`
- `evidence_type`
- `confidence`
- `vulnerability`
- `counterargument`
- `what_would_change_my_mind`
- `status`

### 5. Hypothesis
仍待验证的解释。
字段建议：
- `id`
- `hypothesis_text`
- `based_on`
- `missing_evidence`
- `disconfirming_evidence`
- `next_validation_step`
- `confidence`

### 6. Decision
稳定方向承诺。
字段建议：
- `id`
- `decision_text`
- `scope`
- `owner`
- `basis`
- `status`
- `review_due`

### 7. Question
开放问题。
字段建议：
- `id`
- `question_text`
- `domain`
- `related_objects`
- `why_it_matters`
- `blocking_what`
- `priority`
- `status`

### 8. Pattern
跨产品抽象。
字段建议：
- `id`
- `pattern_name`
- `description`
- `abstracted_from`
- `where_it_applies`
- `failure_mode`
- `design_implication`
- `confidence`

### 9. Method
产品经理 / 体验设计师方法论。
字段建议：
- `id`
- `method_name`
- `problem_it_solves`
- `steps`
- `when_to_use`
- `when_not_to_use`
- `evidence_basis`
- `transferability`

### 10. Jury Review
评审团审议记录。
字段建议：
- `id`
- `review_target`
- `review_mode`
- `seats`
- `independent_first_passes`
- `cross_examinations`
- `agreements`
- `open_conflicts`
- `verdict`
- `confidence`

### 11. Evidence Artifact
证据锚点。
字段建议：
- `id`
- `source_item_id`
- `artifact_type`
- `quote_or_segment`
- `timestamp_or_location`
- `why_it_matters`

### 12. Session Trace
研究 session 的 bounded progression。
字段建议：
- `id`
- `session_type`
- `focus_objects`
- `start_state`
- `intent_frame`
- `cognitive_moves`
- `claims`
- `hypotheses`
- `decisions`
- `open_questions`
- `action_items`
- `memory_candidates`
- `next_entry_point`
- `writeback_recommended`

## 2. Key Relations

- `SourceItem SUPPORTS Claim`
- `SourceItem DESCRIBES ProductEvent`
- `ProductEvent UPDATES Product`
- `Claim ABOUTS Product | Pattern | Method | Question`
- `Hypothesis TESTS Claim`
- `SessionTrace PRODUCES Claim | Hypothesis | Decision | Question`
- `JuryReview EVALUATES Product | ProductEvent | Claim | Pattern`
- `Pattern ABSTRACTS_FROM ProductEvent | Claim | Review`
- `Method GUIDES SessionTrace | JuryReview`
- `WritebackProposal PATCHES Product | Pattern | Method | Question`

## 3. Knowledge Status Vocabulary

统一状态词：
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

---
