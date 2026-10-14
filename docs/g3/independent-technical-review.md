# Independent technical review — P3 / G3

Observed 2026-10-14. Reviewer: independent technical review agent, which did not implement the skill. This is technical evidence, not manager acceptance, an operator walkthrough, a spending decision or publication approval.

The current live run passes the bounded binding and baseline checks. Two source-change defects remain: an earlier clearance deadline can receive unsupported feasible classification, and a changed hold expiry does not update the plan's decision sentence. The review does not support closing G3 without resolving these findings and checking the affected behavior.

## Scope and method

Read AGENTS.md, REQUIREMENTS.md, the G3 design/tracker rows, the skill and source contract, all runner functions and the G1/G2 checks, current nine snapshots/four drafts and their retained evidence, and the corrected committed G2 synthetic current set and its three retained historical chains. No application, source, existing evidence or hash-bound artifact was edited. No full test suite, remote source retrieval, credential read, authentic session-log inspection, external contact, commit or push was performed.

Executed local Python with `TMPDIR`, `TMP` and `TEMP` set to `/home/mike/event-coordination/.planning-tmp`, `PYTHONDONTWRITEBYTECODE=1`, and `PYTHONPATH=.runtime-deps`. Imported `validate` and `check_live` for read-only artifact inspection. Two isolated synthetic reproductions copied retained captures into new temporary directories, changed one calendar field each, updated its interpretation hash, and ran the public runner implementation against isolated outputs. Their observation times remain historical and their interpretation authors explicitly identify synthetic review work.

## Observed checks

| Check | Observed result / evidence |
|---|---|
| Current final bindings | `check_live(Path('deliverables'))` passed for `run-20261014T215247Z-0376ac6d`. `validate` checks all nine schemas, stage order, same-run lineage, predecessor paths/hashes, source hashes, final four artifact hashes, comparison costs/classifications, and parsed calendar intervals. |
| Current exact stage 08 bindings | Independently hashed all four `artifact_drafts` paths in `deliverables/snapshots/08-draft-propagation.json`; every hash matched. Nine snapshot IDs are unique. |
| Current business baseline | 245 planning people, 180 registered, target144; base totals494000/512000 TWD, feasible at the exercise clock; all12 demos and12 separate changeovers; non-overlapping dependencies; calendar8 source records; three retained PDF observations. `check_g1.py:15` supplies these baseline assertions. |
| Approval and delivery boundaries | Stage07 requests remain pending. Current plan/messages distinguish exercise feasibility from real booking; ICS events are tentative with no attendees; all three messages are UNSENT DRAFT. Code creates local files and has no network, booking, payment, production-calendar or message-delivery call. `run.py:701`, `SKILL.md:20`, source contract final paragraph. |
| Committed corrected G2 synthetic evidence | `validate` passed for `docs/g2/synthetic-change-evidence` using the original binding root from `checkpoint-retention.json`. Both bases are conditional at496000/512000, recommendation deferred, Operations / Programme owns readiness confirmation; all four drafts preserve the condition. The checkpoint manifest's retained hashes matched every named retained file, and all three historical chains passed relocated validation using the same original root. |
| Privacy and outside-source authority | Reviewed the safe structured column contract and credential-pattern checks; all retained live source representations passed `privacy_check`. Instructions identify outside content as evidence and preserve human authorization (`AGENTS.md`, `SKILL.md:12–14`, `references/sources.md`). This is a bounded pattern/contract inspection, not proof that arbitrary personal data could always be classified automatically. |
| Incomplete states and recovery | Inspected collection holds, blocked empty-calendar rendering, failure marker, archive-before-processing, retained byte verification and guarded promotion (`run.py:434`, `run.py:543`, `run.py:588`, `run.py:760`, `run.py:844`). Read G1/G2 degradation and recovery cases. These suites were not rerun; this review's new isolated executions cover only the findings below. |

## Findings

### G3-T1 — High: earlier teardown deadline bypasses readiness coverage

`programme` uses the `teardown_deadline` record's end as the actual clearance deadline (`scripts/run.py:170`) and rebuilds teardown around it. `readiness_coverage` compares the venue hold and preferred programme window to R2 (`scripts/run.py:189–204`), but never compares that teardown deadline. The resulting earlier clearance requirement does not reopen the readiness dependency.

Reproduced in `.planning-tmp/g3-independent-kocvcn3b/result` by changing only CAL-008 `end_at` from `2026-10-17T18:30:00+08:00` to `2026-10-17T18:00:00+08:00`, retaining CAL-003's18:30 hold and the original brief. Update `interpretation.capture_hashes.calendar` to the exact modified capture hash, then invoke `Run.execute` with the copied captures, original brief and isolated output.

Observed:

- Run status `complete`; stage03 `readiness_coverage.supported` is `true`.
- Stage04 teardown is17:00–17:45 and clearance17:45–18:00, with teardown still attributed to VEN-R2.
- Both base options remain `feasible`; stage07 recommends Green Table.
- Nine snapshots/four drafts are generated; `validate` passes all three reported validations.

R2 supports completing teardown and clearing between17:00 and18:30 and supplies no measured vendor durations (`inputs/event-brief.md:39–41`). As with G2's corrected later setup access, a stricter external clearance deadline cannot establish feasibility merely by shortening a proposed allocation. The business consequence is a recommendation and vendor review draft that classify an unconfirmed compressed service arrangement as supported.

Smallest correction: include the effective teardown/clearance deadline in the readiness coverage assessment. When it imposes an earlier unconfirmed completion requirement, preserve the proposed programme as conditional, request Operations / Programme coordination confirmation, and defer recommendation consistently across all four drafts. Do not invent a minimum teardown duration. Add one focused regression for this case and one unchanged-baseline check.

### G3-T2 — Medium: hold expiry is hardcoded in the plan's decision guidance

`render_plan` interpolates the supported decision deadline but hardcodes “the hold expires September 5” (`scripts/run.py:360–361`). The calendar source table later renders the actual notes, so a valid changed input produces inconsistent dates within the plan.

Reproduced in `.planning-tmp/g3-independent-uyi8afc5/result` by changing only CAL-003 `notes` to `Hold expires 2026-09-06` and rebinding its capture hash as above. Run status is `complete`; `validate` passes. The plan retains “the hold expires September 5” near Decisions needed while its calendar source table says `Hold expires 2026-09-06`.

The business consequence is stale manager decision guidance despite correctly retained changed evidence. The current live expiry is September5, so this defect does not presently alter the live date; it violates the changed-input consistency contract.

Smallest correction: render the hold expiry from the same parsed, supported hold record used in feasibility; preserve an unresolved state if that meaning cannot be read. Check a changed supported expiry and the unchanged baseline. Keep quote validity and hold expiry distinct.

## Independent operator assessment and limitations

The skill gives an independent agent operator a credible route: disclosed URLs and stable columns, capture representations and locators, required interpretation fields and hashes, local dependency installation, an explicit runner command, incomplete-result semantics, recovery instructions and approval boundaries (`SKILL.md:8–22`, `references/sources.md`). It requires an agent host capable of bounded read-only Sheets/web retrieval and visual PDF inspection; the deterministic command alone consumes captures and is not a live retriever. I did not perform a fresh independent connector/host walkthrough, dependency installation or PDF visual interpretation. Those operational capabilities remain unverified by this review.

No fresh venue booking, actual readiness, dietary response delivery, stakeholder approval or attendee communication was observed. Historical technical reports were read as evidence of earlier checks, not reclassified as new executions. Interrupted promotion, disk exhaustion, arbitrary secret forms and unfamiliar personal-data columns were not newly exercised. Authentic session-capture publication paths are outside this inspection; the parent G3 work must record their actual review separately without exposing private logs.

## Focused correction follow-up — 2026-10-14

This section supersedes the opening statement that the two findings remain unresolved. Original observations above are preserved. Both G3-T1 and G3-T2 are resolved within their reproduced scope. No remaining defect was observed in these two affected behaviors; the original operational and acceptance limitations still apply.

Independently copied the new retained live captures into `.planning-tmp/g3-independent-followup-qtrf3nhe`, applied the same one-field calendar mutations and rebound hashes, and executed the revised runner against isolated outputs. No live source, committed G1/G2 evidence or application file was changed by this reviewer. Independently validated actual final live run `run-20261014T224707Z-f9c78a0d`. No full suite or new general review was performed.

| Affected check | Actual result |
|---|---|
| G3-T1: CAL-008 clearance at18:00 | Synthetic run `run-20261014T224819Z-f45a378f` is `partial`; readiness coverage is false; both bases are conditional; recommendation is deferred. Proposed clearance remains18:00 and all four drafts retain Operations / Programme as confirmation owner. Every decoded ICS event preserves the teardown-deadline uncertainty. Local schema/lineage/evidence/artifact and calendar validation passes. |
| G3-T2: CAL-003 hold expiry September6 | Synthetic run `run-20261014T224819Z-0c12ade7` remains `complete`, with unchanged supported readiness. Decision guidance now says `the hold expires **2026-09-06**`, matching the source-record table; the old hardcoded September5 sentence is absent. Quote expiry dates remain separate. Validation passes. |
| Actual final bindings | Revised `validate(Path('deliverables'))` passes against the final run, including the new shared `calendar_entries` basis. This invocation does not replace the parent's reported G1/G2 integration checks. |

Measured final readback took0.180 seconds in Python: live binding validation0.053 seconds, earlier-clearance assertions/validation0.071 seconds, changed-expiry assertions/validation0.055 seconds. The preceding command that generated the two isolated runs returned after1.5 seconds wall time, including startup and an initial assertion that expected an unformatted expiry string. Inspection identified Markdown bold formatting, and the readback assertion was corrected to the actual intended text; no implementation change or additional generation was needed. Generation alone was not separately metered. These durations exclude reviewer reading and report writing.
