# Event Planning Coordination Brief — Requirements

## Scenario

You are an automation specialist at Quillhaven Academy. Its Event and Operations Manager needs a review-ready event plan that stays consistent when attendance, quotes and venue information change. The exercise's business clock is **26 August 2026, 12:00, Asia/Taipei**; record actual source retrieval times separately. Company planning records are authored exercise data; official venue sources remain real and mutable.

## Your task

Using the provided interview file(s), build and execute an Agent Skills-compliant skill named `event-planning-coordination-brief`. It must retrieve the current disclosed sources, compare supported options and produce consistent planning drafts. Discover the workflow, source meanings, business constraints and approval requirements through the provided interview file(s) and supplied sources. Explain your automation choices, uncertainty policy and trade-offs.

Document one end-to-end command, its runtime, dependencies and setup. Use any suitable implementation language or maintained libraries. Keep calendars and communications as drafts: do not book, pay, invite, commit to vendors, write to production calendars, expose secrets or bypass human approval. Do not copy private attendee medical/contact details into general artifacts.

## Deliverables

**Interview records — `interviews/*.md`.** Include the original Work Sim Markdown export for every interview session, with its session metadata and complete participant-visible messages. Keep one final complete export per session without rewriting or summarizing it.

The starter supplies its entry README and unchanged [`snapshot.schema.json`](https://github.com/GitRollTraining/event-coordination/blob/main/snapshot.schema.json). Create the Skill and these outputs; the tree describes your completed repository, not supplied implementation:

```text
interviews/
└── <original-export-filename>.md
event-planning-coordination-brief/
├── SKILL.md
├── scripts/
└── references/
deliverables/
├── snapshots/
│   ├── 01-scope-and-approval-gates.json
│   ├── 02-source-capture.json
│   ├── 03-constraint-model.json
│   ├── 04-planning-baseline.json
│   ├── 05-option-generation.json
│   ├── 06-feasibility-testing.json
│   ├── 07-decision-and-approval.json
│   ├── 08-draft-propagation.json
│   ├── 09-publication-validation.json
│   └── evidence/
├── vendor-comparison.csv
├── event-plan.md
├── event-calendar.ics
└── draft-communications.md
```

**Snapshots and captured sources.** Write each snapshot at its corresponding boundary, conforming to the supplied schema. All nine share a `run_id`; from stage 02, `predecessor` identifies and hashes the immediately preceding snapshot. Each transition identifies the records it consumed and produced. Stage 08 records draft propagation; stage 09 records exact final artifact paths/hashes and validation after writing the drafts. Keep evidence and decision references resolvable throughout the chain.

Capture every attempted structured, web, image, video and calendar source with its actual retrieval state. Preserve the source content or permitted extracts needed to inspect every claim, with ID, URL, version, retrieval time, locator and hash. Use at least one required official floor-plan or image source disclosed by the stakeholder. Preserve successfully retrieved image/PDF bytes used for spatial or accessibility claims in `deliverables/snapshots/evidence/`; stage 02 records their path and page/region locator, and later stages reference their evidence ID. Optional video evidence needs timestamps if used. Read the actual disclosed remote sources; do not substitute undisclosed local copies.

Use the schema's states: run `complete/partial/blocked/failed`; retrieval `retrieved/unavailable/invalid/unverified/stale`; option `feasible/infeasible/conditional/unverified`; approval `pending/approved/rejected/not-required`. Keep missing, conflicting, stale or unresolved facts traceable until an evidence-backed resolution or actual human decision changes them. Record assumptions separately from source facts, and planned actions separately from observed completion.

**Final drafts.** Keep amounts, dates, options, decisions and evidence consistent across all files:

| File | Required content and format |
| --- | --- |
| `vendor-comparison.csv` | Compare materially different options and retain rejected options with reasons. Columns: `option_id`, `quote_ids`, `planning_people`, `cost_twd`, `currency`, `feasibility`, `availability_status`, `evidence_ids`, `tradeoffs`, `unresolved`, `approval_status`. Use integer TWD amounts; leave unknown costs blank with the reason. CSV lists may be JSON arrays or a documented unambiguous delimiter. Preserve quote identity, category, capacity, date, conditions and evidence. |
| `event-plan.md` | Objective, source/run basis, headcount and uncertainty policy, timing/dependencies, category/total amounts, option comparison, feasibility, accessibility/safety evidence and limits, recommendation or deferral, risks, unknowns, change impacts, remaining owners and draft review requests. Explain choices through source-grounded consequences; no predetermined recommendation is required. |
| `event-calendar.ics` | Valid VCALENDAR with `VERSION:2.0`, draft `METHOD:PUBLISH`, stable event `UID`, `DTSTAMP` and supported `DTSTART`/`DTEND`. Proposed events use `STATUS:TENTATIVE`; timestamps carry an explicit timezone. Keep the calendar consistent with the plan and include no attendees or delivery actions. If no event time is supportable, submit an empty valid calendar and explain the deferral. |
| `draft-communications.md` | Label every message `UNSENT DRAFT` with intended audience, purpose, conditions and approval owner. Preserve uncertainty and dependencies; never claim a booking, payment or invitation was sent. |

Use the interview-supplied source definitions and business criteria when interpreting headcounts, service capacities, prices, budgets and calendar records. Show a non-overlapping programme that accounts for supplied activities and their dependencies; do not replace it with only a total-minute calculation. Keep all relevant calendar records and their meaning. Do not infer a missing value, confirmation or approval from a convenient label or number.

**Incomplete results.** Supported independent work may continue when one source or vendor cannot be verified. Preserve its actual failed attempt, the affected claims and the owner or evidence needed to resolve them. If image evidence is unavailable, withhold dependent spatial/accessibility claims. Do not invent options, facts or approvals to obtain a normal result.

| Run state | Required result |
| --- | --- |
| `complete` | Nine valid linked snapshots and four consistent review drafts, supported comparisons and a justified recommendation. Human approval may remain pending because the result is a draft. |
| `partial` | Nine linked snapshots and four drafts preserving supported work, unavailable sources, conditional claims and resolution owners. |
| `blocked` | Nine snapshots when valid evidence can be retained, comparison/plan explaining the blockage, an empty draft calendar and unsent clarification drafts. |
| `failed` | `deliverables/failure.json` with `run_id`, `observed_at`, `error`, `affected_stage`, `available_evidence`, `affected_artifacts`, `next_owner` and recovery action. Preserve only evidence actually obtained; do not claim completed snapshots or reuse old successful outputs as the current result. |

**Changed inputs and recovery.** Read structured sources by disclosed meanings and stable identities. Accept reordered headers/records and unrelated extra columns, including combinations of those changes, when required fields and values remain valid. Preserve the representation actually captured and its observation metadata. Hold missing fields, ambiguous/duplicate identities, incompatible meanings or invalid required values before dependent interpretation; do not guess renamed fields or silently choose a conflicting record.

Before processing a material change, retain the previous current run under `deliverables/history/<run_id>/`. Write a coherent new set at the same nine current filenames with a new run ID and unique snapshot IDs. Stage 01 records `supersedes_run_id`, changed source/decision IDs and the reason. Keep predecessor links within the new run. Inspect historical identities/hashes before reuse; do not reconstruct missing observations. Identical retained media may be referenced by hash without copying its bytes again.

Reconsider every affected planning basis, comparison, decision, approval request and draft, explaining which evidence remains unchanged. Even when inputs are unchanged, inspect actual output content and run/hash bindings before reporting success. Repair missing, corrupt or stale outputs and revalidate, or return an explicit incomplete/failure result. Preserve failed source/output attempts and earlier evidence as history. After recovery, record the actual new attempt and revalidate affected work; old or partial outputs cannot masquerade as current success. Recovery does not establish a completed prerequisite, granted approval or sent message.
