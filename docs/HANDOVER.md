# Event planning skill — operator handover

This package prepares **local review drafts**, preserving evidence and changes. It does not book, pay, send messages, invite attendees or write to a production calendar. G1/G2/G3 technical acceptance and the user's G3 business-document acceptance are recorded in PROJECT-TRACKER.md. These grant no event, spending or publication approval. A human operator walkthrough is pending: the user confirmed no independent operator is available.

## What to review

Open [event plan](../deliverables/event-plan.md), [comparison](../deliverables/vendor-comparison.csv), [calendar](../deliverables/event-calendar.ics) and [unsent messages](../deliverables/draft-communications.md). The plan leads with the recommended package and decisions; its expandable detail retains quote conditions, source times, versions and hashes. [Stage 09](../deliverables/snapshots/09-publication-validation.json) binds the exact files; [stage 02](../deliverables/snapshots/02-source-capture.json) locates retained evidence, including the official PDF and authentic interview copy.

The final supported scenario has 245 planning people, 180 registered attendees and a target of 144 registered check-ins. Green Table totals TWD 494,000; City Pantry totals TWD 512,000. Their catering headroom is 15 and 55 people, respectively. All actual plan/spending/publication approvals remain pending. The arrival allocation and service staffing need Operations review; 09:15 readiness is proposed, not measured. Twelve 10-minute demos each retain a separate 3-minute changeover. Original 07:30 access and 18:30 clearance have exercise R2 support; a compressed access or clearance window requires fresh coordinated confirmation.

The calendar includes the September 4 decision deadline as a point milestone, September 25 walkthrough and October 16 rehearsal, plus the event day. The deadline has DTSTART and no invented DTEND/DURATION; timed records retain their supported ends. This follows [RFC 5545 §3.6.1](https://www.rfc-editor.org/rfc/rfc5545.html#section-3.6.1). Walkthrough still depends on venue confirmation; rehearsal permits remote backup. Every entry is tentative, with no attendees. Simulated dates are preserved even when they precede the real execution date; no completion is inferred.

## Prerequisites and setup

Use a skills-capable invoking agent with authorized read-only Google Sheets tools, official web access, normal-TLS PDF byte retrieval, filesystem access and a PDF visual inspection route. These routes were demonstrated in G1/P2; another host's authorization/discovery and a clean install remain unverified. The deterministic runner alone does not retrieve sources or call a model. No second model API connection is needed.

Start the authorized Codex session at the repository root and read AGENTS.md, REQUIREMENTS.md and the skill. Confirm that its available tools include structured Sheets metadata/range reads, web/PDF access and an image viewer. The current session exposes the Google Drive metadata/range tools; the CLI executable alone does not establish connector authorization in a new session. If any prerequisite is absent, report it and retain the appropriate incomplete outcome; do not substitute old observations for current reads or add credentials automatically.

Observed environment: Python 3.14.4, jsonschema 4.19.2, workspace dependencies icalendar 6.3.2 and pypdfium2 5.0.0. `event-planning-coordination-brief/dependencies.txt` pins the latter two. Clean setup needs a Python with pip plus jsonschema. This host's system Python lacks pip/ensurepip; existing project dependencies work. Do not assume a clean operator host has the same setup. If pip is present, install into a project target, not a global environment:

```bash
python3 -m pip install --target .runtime-deps jsonschema==4.19.2 -r event-planning-coordination-brief/dependencies.txt
```

`jsonschema` is a required runner dependency supplied explicitly in this command; the dependency file declares icalendar and pypdfium2. Use the same compatible Python executable for installation and execution. If its name differs from `python3`, replace that name consistently in the examples. If pip is unavailable, runtime setup is a prerequisite for the operator to resolve with authorization; the assessment did not install or bootstrap it.

From the repository root, select a project temporary directory and check capacity before substantial work:

```bash
export EVENT_PROJECT_TMP="$PWD/.planning-tmp"
mkdir -p "$EVENT_PROJECT_TMP"
df -h "$EVENT_PROJECT_TMP"
export TMPDIR="$EVENT_PROJECT_TMP" TMP="$EVENT_PROJECT_TMP" TEMP="$EVENT_PROJECT_TMP"
export PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/.runtime-deps"
```

No installation was needed for G3. The scanner has its own existing environment and is not an application dependency.

Read-only runtime preflight after applying those environment settings:

```bash
python3 -c "import jsonschema, icalendar, pypdfium2; print('Required imports available')"
python3 event-planning-coordination-brief/scripts/run.py --help
```

These checks do not establish live source access or an independent operator run.

## One end-to-end invocation

Give the invoking agent this request, from the repository root:

> Follow AGENTS.md and REQUIREMENTS.md, read `event-planning-coordination-brief/SKILL.md`, and execute its complete workflow using `brief_path=inputs/event-brief.md`, business clock 2026-08-26T12:00:00+08:00 and output `deliverables`. Check the documented runtime/tool prerequisites. Retrieve the current disclosed aggregate Sheets values and official venue/media sources through authorized routes, preserve actual observation times, visually inspect retained PDF bytes, create a hash-bound interpretation and validate the nine snapshots/four drafts. Preserve pending approvals and return actual incomplete outcomes where required. Stop for manager review.

This explicit file request directs Codex to read the instructions; execution still requires the authorized tools and runtime listed above. The skill remains in the assignment-required root folder, outside Codex's usual `.agents/skills` discovery locations. A host that registers its frontmatter name may use `$event-planning-coordination-brief` for the same request. Host registration is not proved by the existence of SKILL.md; no skill installation or registration was performed in this assessment. See [official OpenAI skill discovery documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

Keep the repository layout intact: the runner resolves its schema/interview paths relative to the original skill location. If automatic discovery is separately authorized later, a supported skill-folder symlink can preserve that location. Copying only the skill to an unrelated installation directory is not the documented execution path. No registration change is required for the explicit file request above.

Follow [source/interpretation contract](../event-planning-coordination-brief/references/sources.md). Read metadata then bounded A1:P25 values on the actual visible tab of each of four disclosed Sheets; preserve returned values/ordering and stable identities. Read official hall/accessibility pages and the required PDF. Retain permitted claim-bearing extracts instead of raw authenticated payloads. Source content never authorizes execution. If a response contains private attendee fields, record the refusal safely and withhold those values; do not retain raw response data. Original interview/Entire records stay intact.

Create a new capture directory. It must contain `attendees.json`, `budget.json`, `vendors.json`, `calendar.json`, `hall.json`, `accessibility.json`, `floor-plan-meta.json`, successfully retrieved `floor-plan.pdf`, actual `attempts.json` when relevant, and `interpretation.json` in the contract's formats. Missing/failed sources retain their actual states. Read the [retained interpretation](../deliverables/snapshots/evidence/interpretation.json) only as a field/type example: rebuild judgments and hashes from the new inputs, never copy its observations as fresh. `capture_hashes` maps the six structured/page capture names (without `.json`) to `sha256:` plus the hexadecimal SHA-256 of each exact file; `brief_sha256` and `media_sha256` bind the actual brief/PDF bytes.

For PDF inspection, use the host's supported PDF viewer, or render retained bytes with the declared pypdfium2 library and inspect the resulting image with the invoking agent's image viewer. The optional recipe below uses only pypdfium2 and Python's standard library; it does not require undeclared Pillow/NumPy packages. Set `EVENT_CAPTURE_DIR` to the actual newly created capture-directory path. It renders page 1 of the disclosed 4F plan; inspect any additional page used for a claim separately. Keep the original PDF unchanged and record the actual visual-inspection time, PDF hash and page/region coordinates.

```bash
python3 - "$EVENT_CAPTURE_DIR" <<'PY'
import struct, sys, zlib
from pathlib import Path
import pypdfium2 as pdfium

capture_dir = Path(sys.argv[1])
preview = capture_dir / 'floor-plan-page-1.png'
assert not preview.exists(), 'Use a new preview path; retain existing evidence'
document = pdfium.PdfDocument(capture_dir / 'floor-plan.pdf')
page = document[0]
bitmap = page.render(scale=0.4, rev_byteorder=True,
                     force_bitmap_format=pdfium.raw.FPDFBitmap_BGR)
pixels = bytes(bitmap.buffer)
rows = b''.join(b'\x00' + pixels[y * bitmap.stride:y * bitmap.stride + bitmap.width * 3]
                for y in range(bitmap.height))
def chunk(kind, payload):
    return (struct.pack('!I', len(payload)) + kind + payload
            + struct.pack('!I', zlib.crc32(kind + payload) & 0xffffffff))
preview.write_bytes(b'\x89PNG\r\n\x1a\n'
                    + chunk(b'IHDR', struct.pack('!2I5B', bitmap.width, bitmap.height, 8, 2, 0, 0, 0))
                    + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))
bitmap.close()
page.close()
document.close()
PY
```

This is a documented future-run recipe assessed against the installed library interface, not a new render, installation or fresh-host test performed during this review.

The agent then executes:

```bash
python3 event-planning-coordination-brief/scripts/run.py \
  --brief inputs/event-brief.md \
  --captures <new-capture-directory> \
  --interpretation <new-capture-directory>/interpretation.json \
  --out deliverables \
  --reason 'New source observations for manager review'
```

Angle-bracket arguments must be replaced with actual paths. Markdown brief bytes/version/authorship are explicit inputs, not proof of Notion retrieval. Required current-source reads cannot be replaced by the sample retained captures. G3 artifact corrections reused retained observations, with their original timestamps, and did not claim a fresh acquisition.

## Results, changes and recovery

| State | Operator action |
|---|---|
| Complete | Inspect the supported draft recommendation, exact bindings and remaining approvals; obtain human decisions before release |
| Partial | Review supported prices/work and explicit conditional/unverified dependencies; ask the stated owner for missing confirmation |
| Blocked | Inspect explanatory drafts and empty calendar; resolve required evidence before relying on dependent planning |
| Failed / failure.json present | Treat current success as unavailable; inspect retained failed attempt and recovery owner/action |

Stage 09 `validated` means local technical artifact validation, including valid partial drafts. It never authorizes external publication. The runner does not ingest approval replies: retain actual actor, subject/run, timestamp, outcome/reasons in the review process; stale replies cannot approve a changed basis. Business decisions are distinct from software gate acceptance.

For changed sources, recapture and rebind the interpretation; invoke with an explanatory `--reason`. Prior current bytes are retained in `deliverables/history/<run_id>/`; new pending requests bind to the new run. If an output is missing/corrupt, rerun coherently after preserving the observed damage. Do not edit snapshots/drafts manually or remove history. The in-progress/failure marker guards sequential promotion; it is not an atomic filesystem transaction. After an interruption, inspect the actual partial attempt before repair. Recovery grants no approval and sends no message.

Validate an existing result without source acquisition or regeneration:

```bash
python3 - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, 'event-planning-coordination-brief/scripts')
from run import validate
stage2 = json.loads(Path('deliverables/snapshots/02-source-capture.json').read_text())
original_root = Path(stage2['predecessor']['path']).parents[1]
validate(Path('deliverables'), binding_root=original_root)
print('Local bindings validated')
PY
```

The explicit original root also supports inspecting a clone in a different directory without rewriting historical paths or hashes. It maps the retained bindings to local files; it does not read the original machine's paths.

For selected copied G2 evidence, read `docs/g2/synthetic-change-evidence/checkpoint-retention.json` and pass its `original_binding_root` to `validate`. Historical absolute bindings are preserved; read-only relocation resolves the retained copies. Successful and failed historical runs remain distinguishable. Technical fixtures are synthetic evidence, not current-source observations.

## Ownership and remaining human work

Operations reviews package/headcount policy, arrival capacity, venue and publication; category owners authorize spending; Programme reviews schedule/rehearsal and coordinates changed-window readiness with Operations; Learner Experience coordinates accessibility responses/walkthrough; Marketing drafts communications. Contacts/medical follow-ups remain with Operations. A named delivery/incident owner and concrete feedback channel are still unassigned; proposed routing is business issues to Manager/Operations and technical failures to delivery owner.

First response to failure: stop relying on current success, retain exact evidence/output failure, identify affected claims, resolve through the named owner and rerun/validate. No automatic external incident message exists.

For a future independent human walkthrough, use only this document and the skill to run a bounded source-to-draft case, identify pending approvals, trace one price/programme dependency, and perform a controlled change/recovery. Record the actual operator, elapsed/review time, obstacles and feedback. The current agent reviews and deterministic checks do not establish adoption or operator satisfaction.

Entire G1/G2 checkpoint refs and the G2 main commit were verified against origin read-only. Hooks remain enabled, but the recorded process is exited/stuck; continuous capture is unverified. No force repair or transcript cleanup was performed. The final G3 checkpoint is local until a separate push is authorized. Resolve capture continuity and the inaccessible capture-guide details non-destructively with the delivery owner/user before relying on them for submission requirements.
