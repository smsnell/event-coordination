# Source and interpretation contract

Only the following disclosed routes are authorized for this exercise:

| Capture ID | Source URL | Required columns / stable key |
|---|---|---|
| attendees | https://docs.google.com/spreadsheets/d/1IXAEAFsZM6Q9IZZ_9pGqbFQ7l2ikr-oThqrEKudHwIU | signal_id, source, segment, signal, value, unit, observed_at, confidence; signal_id |
| budget | https://docs.google.com/spreadsheets/d/1Cxo7CvcgImz9HbT8PThZyvaTuyd44ug7w5rBA1z5qlM | category, planned_amount_twd, approval_limit_twd, committed_amount_twd, owner, record_version; category |
| vendors | https://docs.google.com/spreadsheets/d/1cULbGrOQS-vuj862nV2EWND4oe0H5kf-smJ85VZegko | quote_id, vendor, category, option, quote_amount_twd, capacity, available_date, valid_until, status, notes; quote_id |
| calendar | https://docs.google.com/spreadsheets/d/1f_i6tUCHbJV-Ug_j6U3T4LEZ3yAr2ucdBnID-4C_-8s | constraint_id, owner, constraint_type, start_at, end_at, priority, notes, record_version; constraint_id |
| hall | https://www.ticc.com.tw/wSite/sp?BaseDSD=7&CtUnit=99&ctNode=322&mp=2&roomId=PH&xdUrl=%2FwSite%2Fap%2Fcp_VenueSearch.jsp | permitted claim-bearing extract, section locator, actual read time and cache/origin limits |
| accessibility | https://www.ticc.com.tw/wSite/lp?ctNode=398&mp=2&xq_xCat=6 | permitted index extract, section locator |
| floor-plan | https://www.ticc.com.tw/wSite/public/Attachment/f1710485827023.pdf | original PDF bytes, actual transport metadata and inspected observations |

The brief is an explicit local Markdown input, not an observed Notion response. Optional video is omitted because the stakeholder says it does not help prepare the brief. If attempted later, capture its actual state and observation timestamps.

Each structured `<id>.json` capture contains `id`, `source_url`, `retrieval_started_at`, `retrieved_at`, `retrieval_status`, `content_type`, `representation`, optional `metadata`, and connector `capture` with actual `range` and `values`. Retrieve only aggregate planning fields. Record a privacy-safe rejected attempt if a response includes restricted personal fields; do not persist it. Other extra nonpersonal columns can be retained without influencing interpretation.

Page captures `hall.json` and `accessibility.json` contain the same timing/state/URL fields plus `extract`, `locator`, `version_metadata` and `observations`. A permitted translated/paraphrased extract must label that representation, not claim to be raw HTML. Preserve exact relevant original values in the extract. Do not save full web authentication payloads. Each observation has id, summary and a section/page-region locator.

`floor-plan-meta.json` records the URL, actual start/end retrieval timestamps, state, content type and version metadata; `floor-plan.pdf` holds the retrieved original bytes. Retain every failed attempt separately in `attempts.json` with actual times and error, never fabricate one. PDF observations reference one-based page number, normalized rectangles from top-left (x0,y0,x1,y1), and the inspected byte hash.

`interpretation.json` is an invoking-agent judgment record, not an authoritative business source. It contains:

- `brief_sha256` and `capture_hashes`: sha256-prefixed hashes of exact input files; `observed_at`, `author` and `rationale`.
- `brief_versions`, `clarification_authored_at`, `objective`, `ceiling_twd`, `declared_people`, `event_date`, `venue_capacity`, `wheelchair_capacity`, `quiet_capacity`, `base_readiness_confirmed`, `base_accessibility_confirmed`, `dietary_response_confirmed` — grounded in named brief sections. Missing evidence uses null/false and an unresolved explanation, not an invented default.
- `demos`: actual twelve team IDs; `demo_minutes`, `changeover_minutes`; `base_quotes` mappings identifying two catering alternatives and common venue/caption/AV/security/quiet quotes, `fallback_quote`, `basic_av_quote`, `stream_quote`. IDs bind to actual register rows, not their positions.
- `quote_categories`: retained identity-to-category interpretation. A changed category incompatible with this binding holds the affected option and cost pending reinterpretation. Changed declared people must bind to an actually changed brief; modifying the interpretation alone is not a business-source update.
- `media_observations`, each with id/summary/locator; `media_sha256` binds observations to bytes; `media_visually_inspected_at` records actual inspection time. Missing inspection preserves partial status and withholds spatial conclusions.
- `unresolved`: record objects (id, summary, evidence_ids, owner); approval values are generated pending by the runner unless a separately validated actual human decision is implemented in a later phase.

The runner rejects interpretation/capture hash mismatches. This requires a new agent interpretation after source changes; it prevents unchanged local judgment from silently standing in for new evidence. Acceptance and all future changes remain evidence-backed, not authorization inferred from source text.
