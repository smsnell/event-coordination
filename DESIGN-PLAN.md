# Event planning — proposed design for approval

Status: revised design approved by user for P1 implementation and G1 verification; later gates remain planned. Business clock: **2026-08-26T12:00:00+08:00 (Asia/Taipei)**. Actual planning observations: 2026-10-14 UTC. Interview export time is source metadata, not the business clock.

## Outcome and evidence

Produce a review-ready Fellowship Demo Day package that stays consistent after changes. The interview (original `interviews/interview-C-1.md`, 02:04–02:33) supports the 17 October 2026 TICC event, 09:30–17:00 programme, TWD 520,000 ceiling, step-free access, wheelchair seating, live captions and staffed quiet room. Success targets are at least 80% registered-attendee check-in and documented responses to every accessibility request. These are business targets, not outcomes observed here. Familiar suppliers are a preference, never grounds to relax constraints.

All supplied local inputs were read: AGENTS, REQUIREMENTS, README, unchanged schema and the sole interview export. The repository has no application, dependency manifest or existing workflow engine. The authorized `inputs/event-brief.md` is now the versioned business brief; it is not a fresh Notion retrieval. Bounded values from all four disclosed Sheets were read on 2026-10-14, and official venue pages were accessed. Required PDF bytes were retained. The September 12 clarifications retain that authorship date while applying to the August 26 simulated clock. The README's external assignment and course guide were not fetched; capture verification remains a prerequisite. Source inventory and preflight results are in PROJECT-TRACKER.md. No interview was conducted or scripted.

Minimum scope: one Agent Skills-compatible skill, one sequential runner, inspectable evidence, nine boundary snapshots and four local drafts. Exclude booking, payment, vendor commitments, invitations, calendar writes, message delivery, UI, database, unattended scheduling and optional video acquisition.

## Resolved basis and remaining decisions

The explicit Markdown brief input supersedes the earlier brief-access blocker. Preserve its exact bytes/hash, local path, `EVENT-BRIEF-2026-08-26`, `VEN-2026-08-26-R2`, `PROG-2026-08-26-R3`, clarification authorship date **2026-09-12**, and actual read time separately. Runtime should accept `brief_path` explicitly; never silently substitute a local file for a requested remote brief. Conflicting later inputs remain traceable.

CAL-005 supplies the plan/budget decision deadline **2026-09-04T17:00:00+08:00**. It can populate schema stage 01; no distinct new decision deadline is required by the evidence. Quote/hold expiry on September 5 is a different fact. Bootstrap reads the selected brief and calendar before stage 01; stage 02 records their actual observations without inventing a second retrieval. If a future run lacks any supported deadline, fail explicitly rather than fabricate one.

| Class / remaining issue | Owner and treatment |
|---|---|
| NONBLOCKING draft decisions: preferred package and extra headcount buffer | Operations reviews the proposed 245-person basis and catering headroom. The brief supplies 245, so an additional buffer policy is not needed to build this draft. Growth beyond capacity triggers replanning. |
| DECISION-BLOCKING only for optional livestream inclusion: network test responsibility/result and venue confirmation | Operations/Programme resolve Q-008 conditions if streaming is desired; exclude it from both base bundles. No inferred test completion. |
| SOURCE-DEPENDENT execution check: inspect a rendered PDF and record page/region observations | Delivery owner establishes a viewing route in G1. Bytes are retained, but this pass does not claim visually verified spatial observations. Withhold dependent public-plan claims until inspected. |
| NONBLOCKING operations/handover: future walkthrough, detailed quiet-room usage, named delivery owner, operator availability, labor rates | Relevant owners track these; nine quiet-room requests fit even if simultaneous within the stated capacity of 20. Do not block the confirmed exercise base bundles on an unknown peak schedule. Real venue operation still requires current confirmation. |

Operations and category approvals remain pending by design; producing the review package does not require obtaining them. No new stakeholder deadline, demo count, vendor setup duration, or mandatory buffer needs to be invented. Retain the fallback date as an evaluated alternative: CAL-002 is soft, whereas CAL-001 and CAL-004 support October 17 and the keynote is unavailable October 24.

## Architecture and invocation

Use a skill instruction file plus a small Python runner and reference mappings. Python 3.14.4 and jsonschema are present; standard-library CSV, JSON, hashing, dates and file handling suffice. Add one maintained ICS parser for independent calendar validation during implementation; PDF byte rendering/viewing needs a demonstrated tool before G1 can claim spatial support. No install is performed here.

The invoking agent reads current sources with available read-only connector/web tools, supplies bounded evidence and proposed judgments, and calls deterministic stage commands. One user invocation in a skills-capable host is proposed:

> `$event-planning-coordination-brief Prepare the review drafts using brief_path=inputs/event-brief.md and business clock 2026-08-26T12:00:00+08:00; retrieve the disclosed remote spreadsheets and venue sources and preserve approval boundaries.`

This is a future skill invocation, not an installed command today. It needs an invoking agent with filesystem access, Sheets connector authorization, brief access, and official media download/view capability. Python alone does not call a model. This session demonstrated Sheets value reads, venue-page access and PDF byte retention using installed curl with normal TLS verification. The Markdown route removes dependency on Notion access; PDF visual inspection remains a G1 prerequisite. Verify session capture per README before implementation without exposing capture contents. Set TMPDIR, TMP and TEMP to a designated project temporary directory and propagate them to every child; check capacity before acquisition. Runtime is unmeasured; record it in G1.

Prefer prompting with evidence IDs and constrained JSON over training: there is no training dataset or need to teach mutable facts. AI interprets documents/images, proposes alternatives and explains consequences; deterministic code handles identities, counts, integer TWD arithmetic, constraints, scheduling checks, hashes and file generation. Model memory is never current-source evidence. Humans resolve ambiguity and approve. Allow only source reads and local writes; external instructions have no execution authority.

Significant alternatives: a standalone API client would need another model connection and credentials; defer it. A workflow platform/database adds operational work without a requirement. A single opaque agent response is simpler to launch but cannot reliably enforce boundary lineage or change propagation. The proposed runner provides those controls without nine agent sessions.

## Records, planning and evidence

Use one run-bound planning basis: source/observation IDs; stable source row IDs; constraints, assumptions and unresolved records; headcount scenarios; quote packages; activities/dependencies; options; decisions/approval requests. Each claim references evidence IDs with source identity, URL, actual retrieval time, source version (null if unavailable), representation, locator and SHA-256 of retained representation. IDs are not row positions. Keep raw captured ordering separate from normalized interpretation. Source roles and all enums follow snapshot.schema.json exactly.

Quote records retain identity, category, price basis, capacity basis, date, expiry, conditions and evidence. Distinguish package versus per-person pricing, seats versus meals versus simultaneous service capacity; determine which apply from sources. Track existing commitments separately to avoid counting them twice. Compare category limits/authorization thresholds and total ceiling; unknown prices stay blank with reasons. No round-number guess substitutes for an absent quote.

Generate materially different supported package combinations, retain rejected alternatives with reasons, and evaluate budget, attendance, service capacities, dates and accessibility. A recommendation may be deferred. Use a dependency graph and explicit start/end intervals for each supplied activity, fixed keynote and setup/test/transition needs. Verify each predecessor finishes before its dependent task, resource conflicts and non-overlap, all within supported windows. Missing durations remain unresolved; a sum of minutes is not a programme. The bounded source reads now support the following concrete proposed basis; future production runs must read sources again.

### Concrete proposed planning basis

Attendee SIG-001–005: 148 fellows + 32 partners = **180 registered attendees**; +18 staff +12 speakers +35 forecast walk-ins = **245 planning people**, agreeing with the brief. SIG-006–013 are overlapping needs, not additive people: six wheelchair spaces, four companions using ordinary places, 23 caption requests, seven hearing-loop requests, nine quiet-room requests, 28 vegetarian meals, 12 halal meals and four allergy follow-ups. Twelve demos are team slots, not extra people. The check-in target is at least 144 of the 180 registered attendees, not 80% of staff plus forecasts.

The synthetic venue allocates 500 audience places including six wheelchair spaces and the V.I.P. Room for up to 20; do not substitute the public hall's full capacity or tariff for this negotiated case. The brief confirms coordinated dietary responses for both caterers, base accessibility services, setup/check readiness and teardown feasibility. This is exercise planning evidence, not completed physical checks or booking approval.

| Category (Budget owner) | Green Table A | City Pantry B | Planned allocation / approval limit, TWD |
|---|---:|---:|---:|
| Venue (Operations), Q-001 | 155000 | 155000 | 155000 / 180000 |
| Catering (Operations), Q-003 or Q-004 | 108000 | 126000 | 115000 / 135000 |
| Accessibility (Learner Experience), Q-005 + Q-010 | 60000 | 60000 | 65000 / 80000 |
| Production (Programme), Q-006 | 78000 | 78000 | 85000 / 100000 |
| Communications (Communications), allowance | 25000 | 25000 | 25000 / 30000 |
| Security (Operations), Q-009 | 28000 | 28000 | 25000 / 35000 |
| Contingency (Operations), allowance | 40000 | 40000 | 40000 / 50000 |
| **Total / headroom below 520000** | **494000 / 26000** | **512000 / 8000** | Planned allocations total 510000 |

All recorded commitments are zero. Use quoted package amounts once, not capacity × price; do not invent added taxes or discounts. Communications/contingency are retained budget allowances, not vendor bundles. Both options are exercise-feasible at 245 under R2, with spending approvals pending: catering capacities 260/300 leave 15/55 places of service headroom. Both exceed security's planned allocation by 3000; B also exceeds catering's allocation by 11000, but both stay within the listed approval limits. Planned allocation is not the same as approval limit or actual authorization.

Propose **A** for lower cost and 26000 remaining ceiling; retain **B** as a materially different capacity/cost alternative if Operations prefers 40 additional catering places for 18000. Do not claim either received approval. Retain Q-002/fallback as infeasible for the required keynote; Q-007 lacks the needed hearing loop. Q-008 remains conditional on test/venue evidence and, added to A/B, yields 549000/567000 including allowances and production 133000: it also exceeds total/category limits. It is not a third feasible option. All quote validity dates (September 5–15) are after the fixed August 26 business clock; no fresh real-world availability is implied.

Proposed run of show, **2026-10-17, +08:00**. R2 permits choosing compatible setup/check and teardown sequences; these are planner allocations, not measured vendor durations. Setup 07:30–08:45 → readiness checks 08:45–09:15 → ready/arrival 09:15–09:30 → opening 09:30–10:00 → fixed keynote 10:00–11:00. Demo blocks follow; each changeover depends on its presentation and precedes the next programme item.

| Team slot | Presentation | Separate changeover |
|---|---|---|
| DEMO-01 | 11:00–11:10 | 11:10–11:13 |
| DEMO-02 | 11:13–11:23 | 11:23–11:26 |
| DEMO-03 | 11:26–11:36 | 11:36–11:39 |
| DEMO-04 | 11:39–11:49 | 11:49–11:52 |
| DEMO-05 | 11:52–12:02 | 12:02–12:05 |
| DEMO-06 | 12:05–12:15 | 12:15–12:18 |
| DEMO-07 | 13:33–13:43 | 13:43–13:46 |
| DEMO-08 | 13:46–13:56 | 13:56–13:59 |
| DEMO-09 | 13:59–14:09 | 14:09–14:12 |
| DEMO-10 | 14:12–14:22 | 14:22–14:25 |
| DEMO-11 | 14:25–14:35 | 14:35–14:38 |
| DEMO-12 | 14:38–14:48 | 14:48–14:51 |

First break 12:18–12:33 → lunch 12:33–13:33 → second demo block → second break 14:51–15:06 → partner overview/discussion 15:06–16:30 → closing 16:30–17:00 → teardown 17:00–18:15 → clearance check 18:15–18:30. Non-source meal/break/discussion allocations are explicitly proposed. Demo time is 12 × (10+3) = **156 minutes**, with twelve separate changeovers, including the final one. No overlap or shortened keynote is needed. Live captions/quiet staffing/security support the programme rather than competing for its stage slots.

Keep all eight calendar records: preferred and fallback windows; venue hold/expiry; keynote; decision milestone; September 25 14:00–16:00 accessibility walkthrough dependent on venue confirmation; October 16 15:00–18:00 rehearsal with remote backup allowed; and October 17 teardown clearance. Scheduled walkthrough/rehearsal is not observed completion. Record the official technical coordination/safety briefing obligation for Operations without inventing its date. R2 readiness covers base on-day setup, not completed real-world obligations.

All four drafts render from that basis without independent recalculation. CSV uses exact required columns and JSON arrays for lists. Plan includes category/total costs, programme, evidence limits, changes and owners. ICS uses VERSION:2.0, METHOD:PUBLISH, stable UID per semantic event, actual DTSTAMP, UTC Z timestamps converted from supported +08:00 times, STATUS:TENTATIVE and no attendees. Keep every calendar source record and its meaning in the basis; not every deadline becomes an event. With no supported time, emit empty valid VCALENDAR. Every communication is UNSENT DRAFT with audience, purpose, conditions and approval owner. Operations approves plan/date/venue and publication; named category owners approve spending; Marketing owns communication drafting. Approval binds to exact decision/basis; material changes reopen affected requests.

Capture design precedes retrieval: use bounded structured reads and claim-bearing extracts, never credential-bearing HTML dumps. Exclude private attendee contact/medical details from logs and artifacts; retain only needed aggregate evidence. Preserve source identity, exact relevant values, original representation/locator and extract hash; do not label an extract hash as full-source hash. If safe retention is impossible, record the restriction and withhold the dependent claim. For used official images/PDFs retain original bytes under evidence/, page number and region coordinates plus coordinate system, observation and evidence ID. A depicted lift does not establish an uninterrupted accessible route, seating allocation, staffing, quiet-room peak capacity or availability. Resolve those separately. No historical interview or Entire transcript cleanup.

## Runtime boundaries and recovery

Every row below writes its snapshot immediately after that boundary. Use the nine exact REQUIREMENTS filenames; stage 01 has null predecessor and empty consumed list. Subsequent stages hash the immutable immediately preceding snapshot in this run. Stable record references resolve to captured or stage-produced records; unique snapshot IDs include run identity.

| Stage | Consumed → produced at boundary |
|---|---|
| 01 Scope | No consumed records → objective, evidenced deadline, owners, approval gates; supersedes_run_id/change IDs/reason on rerun |
| 02 Capture | Scope → attempted-source records, safe captures, observations, retrieval states |
| 03 Constraints | Scope + evidence → hard constraints, preferences, assumptions, unknowns, conflicts |
| 04 Baseline | Constraints + evidence → headcount, budget, accessibility and schedule dependencies |
| 05 Options | Baseline + quotes → supported options and rejected_early reasons |
| 06 Feasibility | Options + constraints → feasibility results and unresolved conditions |
| 07 Decisions | Results → recommendation or null, tradeoffs, actual learner decisions and approval requirements |
| 08 Propagation | Basis + decisions → four written drafts, hashes, affected dependencies and unresolved items |
| 09 Publication | Written drafts + chain → actual readback checks, exact paths/hashes, publication status |

Complete requires supported comparison and justified recommendation, nine valid linked snapshots and consistent drafts; approvals may be pending. Partial retains supported work plus conditional/unverified claims in all nine snapshots/four drafts. Blocked retains nine snapshots where schema-valid evidence is possible, explanatory comparison/plan, empty calendar and unsent clarification drafts. Failed writes the specified failure.json fields including recovery action, never claims unproduced snapshots. A not-produced artifact cannot carry a fabricated hash: omit it from hash-bearing arrays and explicitly explain absence/failure.

Before material changes, retain previous current run in history/<run_id>/, verify retained identities/hashes, and create a new run. Preserve source/output failures too. Recompute affected basis, options, approvals and all four drafts; explain unchanged evidence. Reuse identical retained media by hash only after required current reads. Even unchanged inputs require content and binding inspection. Repair outputs through a new coherent run, retaining damage evidence; never rewrite an upstream snapshot and leave downstream hashes stale. Stage 09 validates staged outputs before promoting the coherent set; on failure, failure.json makes current failure explicit and old success cannot masquerade as current. Recovery grants no approval or completed prerequisite.

## Phases and acceptance mapping

PROJECT-TRACKER.md specifies gate evidence, personal inspection and commit checkpoints. All checks below are planned.

| Phase | Grouped mandatory coverage | Starting model/effort; escalation |
|---|---|---|
| P0 Design | Evidence/unknowns, architecture, BPMN, estimates and approval | gpt-6.1-sol high; gpt-6-astra high only for unresolved semantic conflict |
| P1 / G1 | Skill contract, disclosed retrieval/media, safe publication, nine boundaries, options/programme, four consistent drafts and incomplete states | gpt-6.1-sol high; escalate to gpt-6-astra high if bounded slice cannot reconcile documented constraints |
| P2 / G2 | Combined reorder/extra-column tolerance, invalid inputs, changes, history, repair, approval boundaries | gpt-6.1-sol medium; high for a reproduced lineage/propagation defect |
| P3 / G3 | Final artifacts/current bindings, focused regression/security, independent judgment review and handover | gpt-6.1-sol medium; proposed bounded gpt-6-astra high second-model review of grounding, trade-offs, uncertainty and usefulness |

Choices are exposed in this session, not pricing or account entitlement claims. No model switch or worker launch is authorized here. BPMN sources model responsibility and handoffs; their validation limits are recorded in the tracker.

## P1 implementation note

P1/G1 technical checks have now executed; current result and actual limitations are recorded in PROJECT-TRACKER.md. The project skill and deterministic runner exist, with icalendar6.3.2 and pypdfium2 5.0.0 in a workspace dependency target. Required PDF bytes were freshly retrieved, rendered and visually inspected. Stage09 validates actual written drafts; current failure status is explicit and earlier attempts are retained. P2 full change/history/repair behavior and stronger promotion/recovery checks remain planned. The invoking agent performs current source reads and hash-bound interpretation; the runner alone consumes those captures and does not call a model API. Session-capture hooks are installed but active continuity is unverified because Entire reports a stuck/exited process. No implementation phase beyond G1 is authorized by this result.

## P2 implementation note

P2/G2 was authorized and implemented; observed gate evidence is in PROJECT-TRACKER.md and docs/g2/. The runner now retains/inspects exact history, stages and validates all nine snapshots/four drafts before guarded promotion, and recovers through a new attempt. Approval requests bind to the new run and remain pending. Manager-facing tables and expandable evidence details preserve the shared basis. The current proposed first break supersedes the earlier allocation above:11:00–11:15 after keynote, DEMO-01–06/changeovers11:15–12:33, unchanged lunch12:33–13:33 and later schedule. Arrival09:15–09:30 remains a disclosed capacity risk for Operations review; earlier readiness is not inferred. Both base options are explicitly exercise-feasible with real booking unconfirmed. G2 technical checks have passed; user acceptance, P3 independent review/operator walkthrough and final business acceptance remain pending. No P2 commit/push authorized.

## P3 implementation note

P3 was explicitly authorized after G1/G2 acceptance/commits. Independent technical and bounded gpt-6-astra high business reviews identified five actionable findings; targeted fixes and each reviewer's focused follow-up resolved them. Clearance coverage now includes the effective teardown deadline; hold expiry is source-derived; supplier preference cites the authentic interview;09:15 readiness is explicitly proposed; the shared calendar basis includes the point decision milestone and timed walkthrough/rehearsal with source conditions. The latest complete draft run and actual gate reports are recorded in PROJECT-TRACKER.md and docs/g3/. No schema or authentic source/history edits, new architecture or model API service were introduced. G3 technical work is complete; personal acceptance, unavailable human walkthrough and capture continuity/guide evidence remain explicit limits. Handover is in docs/HANDOVER.md. No P3 commit/push has occurred.

## Final acceptance note

The user accepted the G3 business-document review subject to final documentation cleanup and bounded reproducibility checks. Those checks passed; technical acceptance and remaining limitations are recorded in PROJECT-TRACKER.md. The current run, all generated artifacts and retained evidence/history were preserved. A local final checkpoint is authorized; event/spending/publication approvals, unavailable human walkthrough and capture continuity/guide confirmation remain separate. No fresh-host success or push authorization is implied.
