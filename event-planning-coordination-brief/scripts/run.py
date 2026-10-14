#!/usr/bin/env python3
"""Local deterministic stages; source retrieval and visual judgment belong to the invoking agent."""
import argparse
import csv
import hashlib
import io
import json
import math
import re
import shutil
import sys
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import jsonschema
from icalendar import Calendar, Event

ROOT = Path(__file__).resolve().parents[2]
CLOCK = datetime.fromisoformat('2026-08-26T12:00:00+08:00')
STAGES = ['scope-and-approval-gates', 'source-capture', 'constraint-model', 'planning-baseline',
          'option-generation', 'feasibility-testing', 'decision-and-approval', 'draft-propagation',
          'publication-validation']
FILES = ['vendor-comparison.csv', 'event-plan.md', 'event-calendar.ics', 'draft-communications.md']
COLUMNS = ['option_id', 'quote_ids', 'planning_people', 'cost_twd', 'currency', 'feasibility',
           'availability_status', 'evidence_ids', 'tradeoffs', 'unresolved', 'approval_status']
TABLES = {
    'attendees': ('signal_id', 'signal_id source segment signal value unit observed_at confidence'.split()),
    'budget': ('category', 'category planned_amount_twd approval_limit_twd committed_amount_twd owner record_version'.split()),
    'vendors': ('quote_id', 'quote_id vendor category option quote_amount_twd capacity available_date valid_until status notes'.split()),
    'calendar': ('constraint_id', 'constraint_id owner constraint_type start_at end_at priority notes record_version'.split()),
}
ROLES = {'attendees': 'attendee-signals', 'budget': 'budget', 'vendors': 'vendor-record',
         'calendar': 'calendar', 'hall': 'venue-page', 'accessibility': 'venue-page'}


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def rec(id, summary, evidence=(), owner=None, **fields):
    return dict(id=id, summary=summary, evidence_ids=list(evidence), owner=owner, **fields)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def timestamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(result.tzinfo is not None, 'Timestamp requires explicit timezone')
    return result


def integer(value):
    require(re.fullmatch(r'\d+', str(value)) is not None, 'Invalid required nonnegative integer')
    return int(value)


def privacy_check(data):
    text = data.decode('utf-8', errors='ignore')
    require(not re.search(r'(?i)(authorization\s*:\s*bearer|access_token["\s:=]+|refresh_token["\s:=]+|sk-[A-Za-z0-9]{20,})', text),
            'Restricted credential pattern in publication candidate')


def table(capture, key):
    rows = capture['capture']['values']
    require(bool(rows), 'Empty required table')
    header = rows[0]
    identity, required = TABLES[key]
    require(len(header) == len(set(header)) and set(required) <= set(header), 'Missing/duplicate required headers')
    require(not any(re.search(r'(?i)(email|phone|medical_detail|contact_name)', h) for h in header), 'Restricted private fields')
    result = {}
    for position, values in enumerate(rows[1:], 2):
        if not any(values):
            continue
        row = dict(zip(header, values))
        require(all(row.get(h, '') != '' for h in required), 'Missing required value')
        ident = row[identity]
        require(ident not in result, 'Duplicate stable identity')
        if key == 'attendees':
            row['value'] = integer(row['value'])
            date.fromisoformat(row['observed_at'])
            require(row['unit'] in ['people', 'meals'], 'Unsupported attendee unit')
        elif key == 'budget':
            for h in ['planned_amount_twd', 'approval_limit_twd', 'committed_amount_twd']:
                row[h] = integer(row[h])
        elif key == 'vendors':
            for h in ['quote_amount_twd', 'capacity']:
                row[h] = integer(row[h])
            for h in ['available_date', 'valid_until']:
                date.fromisoformat(row[h])
            require(row['status'] in ['held', 'available', 'conditional', 'unavailable'], 'Unknown quote status meaning')
        elif key == 'calendar':
            require(timestamp(row['start_at']) <= timestamp(row['end_at']), 'Reversed calendar interval')
            require(row['priority'] in ['hard', 'soft'], 'Unknown calendar priority')
        row['evidence_id'] = 'src-' + key
        row['locator'] = f"{capture['capture']['range']}; row {position}"
        result[ident] = row
    return result


def programme(model, calendar):
    def one(kind):
        rows = [r for r in calendar.values() if r['constraint_type'] == kind]
        require(len(rows) == 1, 'Missing/ambiguous calendar meaning: ' + kind)
        return rows[0]
    window, keynote, hold = map(one, ['preferred_event_window', 'keynote_availability', 'venue_hold'])
    start, end, key_start, key_end = map(timestamp, [window['start_at'], window['end_at'], keynote['start_at'], keynote['end_at']])
    require(start.date().isoformat() == model['event_date'], 'Brief/calendar date conflict')
    rows = []
    def add(id, title, a, b, basis, scope='programme'):
        require(a < b, 'Nonpositive programme interval')
        rows.append(dict(id=id, title=title, start=a.isoformat(), end=b.isoformat(),
                         depends_on=[rows[-1]['id']] if rows else [], basis=basis, scope=scope))
    setup_start = timestamp(hold['start_at'])
    add('setup', 'Setup (proposed allocation)', setup_start, start - timedelta(minutes=45), 'VEN-R2', 'operations')
    add('readiness', 'Base readiness checks (proposed allocation)', start - timedelta(minutes=45), start - timedelta(minutes=15), 'VEN-R2', 'operations')
    add('arrival', 'Ready / arrival', start - timedelta(minutes=15), start, 'planner', 'operations')
    add('opening', 'Opening', start, key_start, 'brief/CAL-001')
    add('keynote', 'Keynote', key_start, key_end, keynote['constraint_id'])
    cursor = key_end
    demos = model['demos']
    require(len(demos) > 0 and len(demos) == len(set(demos)), 'Missing/duplicate demo IDs')
    for index, demo in enumerate(demos):
        if index == math.ceil(len(demos) / 2):
            add('break-1', 'First break (proposed)', cursor, cursor + timedelta(minutes=15), 'planner')
            cursor += timedelta(minutes=15)
            add('lunch', 'Lunch (proposed)', cursor, cursor + timedelta(minutes=60), 'planner')
            cursor += timedelta(minutes=60)
        finish = cursor + timedelta(minutes=integer(model['demo_minutes']))
        add(demo, demo + ' presentation', cursor, finish, 'PROG-R3')
        cursor = finish + timedelta(minutes=integer(model['changeover_minutes']))
        add(demo + '-changeover', demo + ' separate changeover', finish, cursor, 'PROG-R3')
    add('break-2', 'Second break (proposed)', cursor, cursor + timedelta(minutes=15), 'planner')
    cursor += timedelta(minutes=15)
    add('partner-overview', 'Partner overview / discussion (proposed)', cursor, end - timedelta(minutes=30), 'planner')
    add('closing', 'Closing (proposed)', end - timedelta(minutes=30), end, 'brief/planner')
    clear = timestamp(one('teardown_deadline')['end_at'])
    add('teardown', 'Teardown (proposed allocation)', end, clear - timedelta(minutes=15), 'VEN-R2', 'operations')
    add('clearance', 'Clearance check (proposed allocation)', clear - timedelta(minutes=15), clear, 'CAL-008', 'operations')
    for previous, current in zip(rows, rows[1:]):
        require(timestamp(previous['end']) <= timestamp(current['start']), 'Programme overlap/dependency violation')
    require(timestamp(rows[0]['start']) >= setup_start and timestamp(rows[-1]['end']) <= timestamp(hold['end_at']), 'Venue window exceeded')
    return rows


def make_options(model, quotes, budget, people, needs, supported):
    options = []
    configs = model['base_quotes']
    variants = [(x['id'], x['quotes'], []) for x in configs]
    first = configs[0]['quotes']
    variants += [('fallback', [model['fallback_quote'] if quotes.get(q, {}).get('category') == 'venue' else q for q in first], ['Keynote unavailable on fallback date; hard preferred event window retained']),
                 ('basic-av', [model['basic_av_quote'] if q == model['hearing_loop_quote'] else q for q in first], ['No hearing loop for required requests']),
                 ('livestream', first + [model['stream_quote']], [])]
    for id, ids, known_reasons in variants:
        missing = [q for q in ids if q not in quotes]
        errors, conditions = list(known_reasons), []
        amounts = {}
        if not missing:
            for qid in ids:
                q = quotes[qid]
                amounts[q['category']] = amounts.get(q['category'], 0) + q['quote_amount_twd']
                if date.fromisoformat(q['valid_until']) < CLOCK.date():
                    errors.append(qid + ' expired at business clock')
                if q['available_date'] != model['event_date']:
                    errors.append(qid + ' date mismatch')
                if q['status'] == 'unavailable':
                    errors.append(qid + ' unavailable')
                if q['status'] == 'conditional':
                    conditions.append(qid + ': network test and venue confirmation unresolved')
                needed = needs.get('quiet_room_requests', 0) if qid == model['quiet_quote'] else people
                if needed is not None and q['capacity'] < needed:
                    errors.append(qid + ' insufficient service capacity')
            for category in ['communications', 'contingency']:
                if category not in budget:
                    missing.append('budget:' + category)
                else:
                    amounts[category] = budget[category]['planned_amount_twd']
            for category, row in budget.items():
                # Existing commitments are retained separately, never silently merged with quotes.
                if row['committed_amount_twd']:
                    conditions.append(category + ': nonzero commitments require overlap reconciliation')
                if category in amounts and amounts[category] > row['approval_limit_twd']:
                    errors.append(category + ' approval limit exceeded')
        cost = sum(amounts.values()) if not missing else None
        if cost is not None and cost > model['ceiling_twd']:
            errors.append('Total planning ceiling exceeded')
        if people is None or not supported:
            conditions.append('Required planning basis incomplete')
        for flag in ['base_readiness_confirmed', 'base_accessibility_confirmed', 'dietary_response_confirmed']:
            if model.get(flag) is not True:
                conditions.append(flag + ' unresolved')
        if needs.get('wheelchair_spaces', 0) > model['wheelchair_capacity']:
            errors.append('Wheelchair allocation insufficient')
        if needs.get('quiet_room_requests', 0) > model['quiet_capacity']:
            errors.append('Quiet-space occupancy insufficient')
        if people is not None and people > model['venue_capacity']:
            errors.append('Audience allocation insufficient')
        feasibility = 'unverified' if missing else ('infeasible' if errors else ('conditional' if conditions else 'feasible'))
        catering_capacity = min((quotes[q]['capacity'] for q in ids if q in quotes and quotes[q]['category'] == 'catering'), default=None)
        options.append(rec('option-' + id, ' / '.join(ids), ['src-vendors', 'src-budget', 'src-brief', 'src-attendees', 'src-calendar'],
                           'Operations', quote_ids=ids, planning_people=people, cost_twd=cost, currency='TWD',
                           category_amounts=amounts, feasibility=feasibility,
                           availability_status='exercise planning states; not booked',
                           tradeoffs=[f"Quoted services plus communications/contingency allowances; cost {cost} TWD",
                                      f"Catering capacity {catering_capacity}; service headroom {catering_capacity-people if catering_capacity is not None and people is not None else 'unknown'}; ceiling headroom {model['ceiling_twd']-cost if cost is not None else 'unknown'} TWD"],
                           unresolved=conditions + ['Missing ' + q for q in missing], rejected_reasons=errors,
                           approval_status='pending'))
    return options


def record_ids(value):
    found = set()
    if isinstance(value, dict):
        if isinstance(value.get('id'), str):
            found.add(value['id'])
        for child in value.values():
            found |= record_ids(child)
    elif isinstance(value, list):
        for child in value:
            found |= record_ids(child)
    return found


class Run:
    def __init__(self, args):
        self.args = args
        self.id = 'run-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
        self.out = Path(args.out).resolve()
        self.schema = read_json(ROOT / 'snapshot.schema.json')
        self.previous = None
        self.available = set()
        self.stage = 'bootstrap'
        self.evidence = []
        self.unresolved = []
        self.status = 'complete'

    def snapshot(self, index, state, consumed, decisions=()):
        self.stage = STAGES[index - 1]
        produced = record_ids(state) - self.available
        require(set(consumed) <= self.available, 'Unresolvable consumed record ID')
        # Each boundary creates a named boundary record even when a stage repeats existing records.
        boundary = rec('boundary-' + str(index), 'Observed completion of ' + self.stage)
        state = dict(state, boundary=boundary)
        produced.add(boundary['id'])
        snap = dict(schema_version='event-coordination-stage-snapshot/2', snapshot_id=self.id + f'-{index:02}',
                    run_id=self.id, stage=self.stage, sequence=index, created_at=now(), status=self.status,
                    predecessor=self.previous, consumed_record_ids=sorted(set(consumed)), produced_record_ids=sorted(produced),
                    state=state, unresolved=self.unresolved, decisions=list(decisions))
        jsonschema.Draft202012Validator(self.schema, format_checker=jsonschema.FormatChecker()).validate(snap)
        path = self.out / 'snapshots' / f'{index:02}-{self.stage}.json'
        write_json(path, snap)
        self.previous = dict(snapshot_id=snap['snapshot_id'], path=str(path), sha256=digest(path.read_bytes()))
        self.available |= produced

    def collect(self, model):
        captures = Path(self.args.captures)
        evidence_dir = self.out / 'snapshots' / 'evidence'
        evidence_dir.mkdir(parents=True, exist_ok=True)
        datasets = {}
        inputs = list(ROLES)
        for key in inputs:
            path = captures / (key + '.json')
            if not path.exists():
                source = rec('src-' + key, 'Source capture missing', owner='Operations')
                source.update(source_role=ROLES[key], locator='disclosed:' + key, retrieved_at=now(), retrieval_status='unverified',
                              content_type='application/json', version_metadata=None, content_hash=None, local_reference=None, observations=[])
                self.evidence.append(source)
                self.unresolved.append(rec('gap-' + key, 'Missing capture; current availability unverified', [source['id']], 'Operations'))
                datasets[key] = {}
                continue
            data = path.read_bytes()
            require(model['capture_hashes'].get(key) == digest(data), 'Interpretation/capture hash mismatch: ' + key)
            privacy_check(data)
            capture = json.loads(data)
            timestamp(capture['retrieved_at'])
            target = evidence_dir / path.name
            target.write_bytes(data)
            source = rec('src-' + key, 'Actual bounded source capture: ' + key, owner='Operations')
            source.update(source_role=ROLES[key], locator=capture['source_url'], retrieved_at=capture['retrieved_at'],
                          retrieval_status=capture['retrieval_status'], content_type=capture['content_type'],
                          version_metadata=capture.get('version_metadata') or {'representation': capture.get('representation'),
                                                                            'metadata': capture.get('metadata')},
                          content_hash=digest(data), local_reference=str(target), observations=capture.get('observations', []))
            if key in TABLES and source['retrieval_status'] == 'retrieved':
                try:
                    datasets[key] = table(capture, key)
                except (KeyError, ValueError, TypeError) as exc:
                    datasets[key] = {}
                    source['retrieval_status'] = 'invalid'
                    source['summary'] = 'Held required data: ' + str(exc)
            else:
                datasets[key] = {}
            if source['retrieval_status'] != 'retrieved':
                self.unresolved.append(rec('gap-' + key, source['summary'], [source['id']], 'Operations'))
            self.evidence.append(source)
        brief = Path(self.args.brief).read_bytes()
        require(model['brief_sha256'] == digest(brief), 'Interpretation/brief hash mismatch')
        privacy_check(brief)
        target = evidence_dir / 'event-brief.md'
        target.write_bytes(brief)
        self.evidence.append(dict(rec('src-brief', 'Authorized local Markdown business brief', owner='Operations'),
                                 source_role='event-brief', locator=str(Path(self.args.brief).resolve()), retrieved_at=now(),
                                 retrieval_status='retrieved', content_type='text/markdown',
                                 version_metadata={'versions': model['brief_versions'], 'clarification_authored_at': model['clarification_authored_at'],
                                                   'source_kind': 'user-provided scenario; not Notion retrieval'},
                                 content_hash=digest(brief), local_reference=str(target), observations=[]))
        # Keep the judgment and its hash bindings inspectable, without labeling it an official fact source.
        judgement = Path(self.args.interpretation).read_bytes()
        privacy_check(judgement)
        target = evidence_dir / 'interpretation.json'
        target.write_bytes(judgement)
        self.evidence.append(dict(rec('src-interpretation', 'Invoking-agent interpretation, not business authority'),
                                 source_role='other', locator=str(Path(self.args.interpretation).resolve()), retrieved_at=model['observed_at'],
                                 retrieval_status='retrieved', content_type='application/json', version_metadata={'author': model['author']},
                                 content_hash=digest(judgement), local_reference=str(target), observations=[]))
        pdf = captures / 'floor-plan.pdf'
        meta_path = captures / 'floor-plan-meta.json'
        meta = read_json(meta_path) if meta_path.exists() else {}
        inspected = False
        pdf_hash = None
        target = None
        if pdf.exists() and meta.get('retrieval_status') == 'retrieved':
            data = pdf.read_bytes()
            require(data.startswith(b'%PDF-'), 'Invalid PDF signature')
            pdf_hash = digest(data)
            target = evidence_dir / 'floor-plan.pdf'
            target.write_bytes(data)
            inspected = model.get('media_sha256') == pdf_hash and bool(model.get('media_visually_inspected_at')) and bool(model.get('media_observations'))
        self.evidence.append(dict(rec('src-floor-plan', 'Official 4F PDF; visually inspected' if inspected else 'Spatial claims withheld: media inspection unavailable'),
                                 source_role='floor-plan-or-image', locator=meta.get('source_url', 'https://www.ticc.com.tw/wSite/public/Attachment/f1710485827023.pdf'),
                                 retrieved_at=meta.get('retrieved_at', now()), retrieval_status='retrieved' if target else meta.get('retrieval_status', 'unverified'),
                                 content_type='application/pdf', version_metadata=meta.get('version_metadata'), content_hash=pdf_hash,
                                 local_reference=str(target) if target else None, observations=model.get('media_observations', []) if inspected else []))
        for key in ['floor-plan-meta', 'attempts']:
            path = captures / (key + '.json')
            if path.exists():
                data = path.read_bytes()
                privacy_check(data)
                target = evidence_dir / path.name
                target.write_bytes(data)
                self.evidence.append(dict(rec('src-' + key, 'Actual media acquisition metadata/attempts'), source_role='other',
                                         locator=str(path.resolve()), retrieved_at=now(), retrieval_status='retrieved', content_type='application/json',
                                         version_metadata=None, content_hash=digest(data), local_reference=str(target), observations=[]))
        if not inspected:
            self.unresolved.append(rec('gap-media', 'Official spatial observations withheld pending retained-byte visual inspection', ['src-floor-plan'], 'Delivery owner'))
        return datasets, inspected

    def execute(self):
        started = time.monotonic()
        model = read_json(self.args.interpretation)
        require(model.get('ceiling_twd') is not None and model.get('objective'), 'Missing interpreted scope')
        old = sorted((self.out / 'snapshots').glob('01-*.json')) if self.out.exists() else []
        supersedes = None
        prior_hashes = {}
        recovering = (self.out / 'failure.json').exists()
        if old:
            supersedes = read_json(old[0])['run_id']
            capture_snapshot = self.out / 'snapshots' / '02-source-capture.json'
            if capture_snapshot.exists():
                prior_hashes = {s['id']: s['content_hash'] for s in read_json(capture_snapshot)['state']['sources']}
            destination = self.out / 'history' / supersedes
            require(not destination.exists(), 'History identity already exists; inspect before reuse')
            destination.mkdir(parents=True)
            for path in list((self.out / 'snapshots').glob('*')):
                if path.is_dir():
                    shutil.copytree(path, destination / 'snapshots' / path.name)
                else:
                    (destination / 'snapshots').mkdir(exist_ok=True)
                    shutil.copy2(path, destination / 'snapshots' / path.name)
            for name in FILES + ['failure.json']:
                path = self.out / name
                if path.exists():
                    shutil.copy2(path, destination / name)
            # Stage 09 cannot remain a current success marker for a new attempt.
            final_snapshot = self.out / 'snapshots' / '09-publication-validation.json'
            if final_snapshot.exists():
                final_snapshot.unlink()  # Exact bytes already retained in this run's history.
        self.out.mkdir(parents=True, exist_ok=True)
        datasets, inspected = self.collect(model)
        calendar, budget, quotes, signals = [datasets[k] for k in ['calendar', 'budget', 'vendors', 'attendees']]
        deadline = [r for r in calendar.values() if r['constraint_type'] == 'decision_deadline']
        require(len(deadline) == 1, 'No unique supported decision deadline; cannot serialize stage 01 safely')
        self.unresolved += model.get('unresolved', [])
        core = bool(calendar and budget and quotes and signals)
        self.status = 'blocked' if not core else ('partial' if any(s['retrieval_status'] != 'retrieved' for s in self.evidence) or not inspected else 'complete')
        scope = rec('scope', model['objective'], ['src-brief', 'src-calendar'], 'Operations')
        self.snapshot(1, dict(objective=model['objective'], decision_deadline=deadline[0]['start_at'],
                              owners=sorted(set(r['owner'] for r in budget.values()) | {'Operations', 'Programme', 'Learner Experience'}),
                              approval_gates=['Operations plan/date/venue/publication', 'Budget category owners spending'],
                              business_clock=CLOCK.isoformat(), supersedes_run_id=supersedes,
                              changed_source_ids=[s['id'] for s in self.evidence if prior_hashes.get(s['id']) != s['content_hash']] if supersedes else [],
                              changed_decision_ids=[], change_reason='Recovery after failed validation; unchanged capture hashes remain bound to their original observation times' if recovering else ('New execution using supplied source observations' if supersedes else 'First live G1 run'), records=[scope]), [])
        # Source IDs are first produced here, even when bootstrap read the evidence before scope serialization.
        self.snapshot(2, dict(sources=self.evidence, structured_records=datasets), ['scope'])
        hard = [rec('hard-budget', f"Ceiling {model['ceiling_twd']} TWD", ['src-brief'], 'Operations'),
                rec('hard-window', '17 October opening 09:30 and completion 17:00; keynote fixed', ['src-brief', 'src-calendar'], 'Programme'),
                rec('hard-access', 'Step-free programme/restrooms, wheelchair seating, captions and staffed quiet room', ['src-brief', 'src-attendees'], 'Operations'),
                rec('hard-demos', 'Each supplied team demo and separate changeover once', ['src-brief'], 'Programme')]
        assumptions = [rec('assumption-allocations', 'Setup, breaks, lunch, partner discussion and teardown intervals are planner allocations, not vendor durations', ['src-brief'], 'Programme')]
        self.snapshot(3, dict(hard_constraints=hard, preferences=[rec('preference-familiar', 'Familiar vendors preferred, not mandatory', ['src-brief'])],
                              assumptions=assumptions, unknowns=self.unresolved, conflicts=[]), ['scope'] + [s['id'] for s in self.evidence])
        people = registered = None
        needs = {}
        schedule = []
        if signals:
            registered = sum(r['value'] for r in signals.values() if r['signal'] == 'registered_attendees')
            people = sum(r['value'] for r in signals.values() if r['signal'] in ['registered_attendees', 'required_on_site', 'expected_attendees'])
            needs = {r['signal']: r['value'] for r in signals.values() if r['signal'] not in ['registered_attendees', 'required_on_site', 'expected_attendees']}
            if people != model['declared_people']:
                self.unresolved.append(rec('gap-headcount', 'Structured total conflicts with declared brief people; Operations must reconcile', ['src-attendees', 'src-brief'], 'Operations'))
                self.status = 'partial'
        if calendar and core:
            try:
                schedule = programme(model, calendar)
            except (ValueError, KeyError, TypeError) as exc:
                self.unresolved.append(rec('gap-programme', str(exc), ['src-calendar', 'src-brief'], 'Programme'))
                self.status = 'blocked'
        basis = rec('basis', 'Shared run-bound planning basis', ['src-attendees', 'src-budget', 'src-calendar', 'src-brief', 'src-floor-plan'])
        self.snapshot(4, dict(headcount_basis=[rec('headcount', f"Planning {people}; registered {registered}; needs overlap", ['src-attendees', 'src-brief'])],
                              schedule_dependencies=[rec('schedule', 'Non-overlapping timed programme with predecessor dependencies', ['src-calendar', 'src-brief'], intervals=schedule)],
                              budget_baseline=[rec('budget-basis', 'Package prices, zero/nonzero commitments retained separately; category allowances', ['src-budget'], categories=list(budget.values()))],
                              accessibility_baseline=[rec('access-basis', 'Exercise routes/allocation from coordination brief; public spatial observations bounded', ['src-brief', 'src-floor-plan'], needs=needs)],
                              records=[basis], planning_people=people, registered_attendees=registered,
                              checkin_target=math.ceil(registered * .8) if registered is not None else None, calendar_records=list(calendar.values())),
                      ['hard-budget', 'hard-window', 'hard-access', 'hard-demos'] + [s['id'] for s in self.evidence])
        supported = core and bool(schedule) and not any(r['id'] == 'gap-headcount' for r in self.unresolved)
        options = make_options(model, quotes, budget, people, needs, supported)
        self.snapshot(5, dict(options=options, rejected_early=[rec('rejected-' + o['id'], '; '.join(o['rejected_reasons']), o['evidence_ids']) for o in options if o['rejected_reasons']]), ['basis', 'src-vendors', 'src-budget'])
        self.snapshot(6, dict(option_results=options, unresolved_conditions=[rec('conditions-' + o['id'], '; '.join(o['unresolved']), o['evidence_ids'], 'Operations') for o in options if o['unresolved']]), [o['id'] for o in options] + ['hard-budget', 'hard-window', 'hard-access'])
        feasible = [o for o in options if o['feasibility'] == 'feasible']
        recommendation = min(feasible, key=lambda o: o['cost_twd'])['id'] if feasible and supported else None
        if self.status == 'complete' and (len(feasible) < 2 or recommendation is None):
            self.status = 'partial' if core else 'blocked'
        decision = rec('decision-recommendation', recommendation or 'Defer recommendation', ['src-vendors', 'src-budget', 'src-brief'],
                       'Operations', rationale='Lowest supported feasible package cost with all base services; alternative buys additional catering capacity' if recommendation else 'Required evidence/constraints unresolved',
                       tradeoffs=['Catering headroom versus total remaining ceiling', 'Hard requirements remain fixed'])
        approvals = [rec('approval-plan', 'Plan/date/venue and publication review', ['src-brief'], 'Operations', status='pending')]
        approvals += [rec('approval-' + category, 'Authorize category spending against this exact run', ['src-budget'], row['owner'], status='pending') for category, row in budget.items()]
        self.snapshot(7, dict(recommendation=recommendation, tradeoffs=[rec('tradeoff', decision['rationale'], decision['evidence_ids'])],
                              learner_decisions=[decision], approval_requirements=approvals), [o['id'] for o in options] + ['basis'], [decision])
        self.write_drafts(model, options, recommendation, schedule, people, registered, needs, budget, quotes, calendar, inspected)
        artifacts = self.artifacts()
        self.snapshot(8, dict(artifact_drafts=artifacts, affected_dependencies=[rec('propagation', 'All four drafts rendered from this run basis', ['src-brief', 'src-vendors', 'src-calendar'])],
                              unresolved_items=self.unresolved), ['basis', 'decision-recommendation'] + [o['id'] for o in options], [decision])
        checks = validate(self.out, allow_eight=True)
        self.snapshot(9, dict(artifacts=self.artifacts(), validation_checks=checks, publication_status='blocked' if self.status == 'blocked' else 'validated'),
                      [a['id'] for a in artifacts] + ['boundary-8'], [decision])
        validate(self.out)
        failed_marker = self.out / 'failure.json'
        if failed_marker.exists():
            require(supersedes is not None and (self.out / 'history' / supersedes / 'failure.json').exists(),
                    'Failure marker must be retained in history before successful recovery')
            failed_marker.unlink()
        print(json.dumps(dict(run_id=self.id, status=self.status, runtime_seconds=round(time.monotonic() - started, 3), output=str(self.out),
                              recommendation=recommendation, approval='pending')))
        return self.status

    def artifacts(self):
        return [dict(id='artifact-' + str(i + 1), path=str(self.out / name), sha256=digest((self.out / name).read_bytes()), validation_status='valid') for i, name in enumerate(FILES)]

    def write_drafts(self, model, options, recommendation, schedule, people, registered, needs, budget, quotes, calendar, inspected):
        with (self.out / FILES[0]).open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            for o in options:
                row = {k: o.get(k) for k in COLUMNS}
                row['option_id'] = o['id']
                row['tradeoffs'] = o['tradeoffs'] + o['rejected_reasons']
                for k in ['quote_ids', 'evidence_ids', 'tradeoffs', 'unresolved']:
                    row[k] = json.dumps(row[k], ensure_ascii=False)
                writer.writerow(row)
        basis = f"Run: {self.id}\nBusiness clock: {CLOCK.isoformat()}\nStatus: {self.status}; review drafts only; approvals pending.\n"
        plan = '# Fellowship Demo Day — review draft\n\n' + basis + '\n' + model['objective'] + '\n\n'
        plan += f"Planning people: {people}; registered attendees: {registered}; check-in target: {math.ceil(registered*.8) if registered is not None else 'unresolved'}. Registered, required staff/speakers and forecast walk-ins are distinct; overlapping needs are not added. Twelve team demo slots add no people. Buffer: no additional invented percentage; review package capacities.\n\n"
        plan += f"Recommendation: {recommendation or 'deferred'}. Lowest supported feasible base total; alternative preserves additional catering headroom. This is an engineer recommendation, not Operations acceptance.\n\n"
        plan += '## Options and category costs (integer TWD)\n\n'
        for o in options:
            plan += f"- {o['id']}: {o['cost_twd'] if o['cost_twd'] is not None else 'unknown'} TWD; {o['feasibility']}; approval pending. Categories: {json.dumps(o['category_amounts'])}. Ceiling remaining: {model['ceiling_twd']-o['cost_twd'] if o['cost_twd'] is not None else 'unknown'}. Tradeoffs: {'; '.join(o['tradeoffs'])}. Reasons/conditions: {'; '.join(o['rejected_reasons']+o['unresolved']) or 'Supported exercise base bundle'}.\n"
            for category, amount in o['category_amounts'].items():
                if category in budget and amount > budget[category]['planned_amount_twd']:
                    plan += f"  Allocation review: {category} is {amount-budget[category]['planned_amount_twd']} above planned allocation; limit {budget[category]['approval_limit_twd']}; owner {budget[category]['owner']}. Not spending authorization.\n"
        plan += '\nCommunications/contingency are budget allowances, not readiness-confirmed vendor services. Existing commitments remain separately recorded; quoted package amounts are counted once. A held/available label is not a booking.\n\n## Quote identities, dates, capacities and conditions\n\n'
        for q in quotes.values():
            plan += f"- {q['quote_id']} {q['vendor']} / {q['category']} / {q['option']}: {q['quote_amount_twd']} TWD package, capacity {q['capacity']}, date {q['available_date']}, expires {q['valid_until']}, {q['status']}; {q['notes']} [src-vendors, {q['locator']}].\n"
        plan += '\n## Programme and dependencies (+08:00)\n\nAll intervals are proposed, not observed execution. Setup/readiness/teardown compatibility is confirmed for base bundles by VEN-R2; chosen allocations are not measured vendor durations.\n\n| Activity | Start | End | Predecessor | Basis |\n|---|---|---|---|---|\n'
        for row in schedule:
            plan += f"| {row['id']} {row['title']} | {row['start']} | {row['end']} | {','.join(row['depends_on'])} | {row['basis']} |\n"
        if not schedule:
            plan += '\nProgramme unsupported; calendar deferred.\n'
        plan += '\n## Calendar records and remaining operational work\n\n'
        for row in calendar.values():
            plan += f"- {row['constraint_id']}: {row['constraint_type']} {row['start_at']} → {row['end_at']}, {row['priority']}, owner {row['owner']}; {row['notes']}. Record is a planning constraint, not completed work.\n"
        plan += '\nWalkthrough requires venue confirmation first; rehearsal allows remote backup; venue hold is not booking; deadline is not an event duration. Operations must arrange required venue technical coordination/safety briefing, without an invented date.\n\n## Accessibility, safety and evidence limits\n\n'
        plan += f"Aggregate needs: {json.dumps(needs)}. Exercise allocation: {model['venue_capacity']} audience places including {model['wheelchair_capacity']} wheelchair spaces; companions use ordinary places; quiet room capacity {model['quiet_capacity']}. The local fictional coordination record supplies case routes, base hearing loop/captions/staffing and coordinated dietary response; personal contacts remain with Operations. Allergy response is planning evidence, not medical advice or observed treatment.\n\n"
        if inspected:
            for observation in model['media_observations']:
                plan += f"- {observation['id']}: {observation['summary']} [src-floor-plan; {observation['locator']['value']}].\n"
        else:
            plan += 'Official spatial observations withheld until PDF bytes can be retained and visually inspected.\n'
        plan += '\nDepicted symbols do not prove current lift operation, clear routes, allocated seating, acoustic performance or real reservation. Public hall tariff/full capacity are distinct from synthetic negotiated allocation. Official restrictions on externally supplied food/AV and streaming remain relevant; case offers are TICC-coordinated. [src-hall, section rental rules; src-accessibility, accessible facilities index; src-brief, venue coordination]\n\n## Source/run basis and uncertainty\n\n'
        for source in self.evidence:
            plan += f"- {source['id']}: {source['retrieval_status']}, retrieved {source['retrieved_at']}, {source['locator']}; retained {source['local_reference']}; {source['content_hash']}.\n"
        plan += f"\nBrief versions: {model['brief_versions']}; clarifications authored {model['clarification_authored_at']}, not business clock or fresh Notion retrieval. Public web extracts can be cache-served; origin update time unknown.\n\n"
        for row in self.unresolved:
            plan += f"- {row['id']}: {row['summary']}; owner {row.get('owner')}; evidence {row['evidence_ids']}.\n"
        plan += '\nChange impact: attendance, quotes, calendar, budget and accessibility changes require a new planning basis, options, decision review and all four drafts. Earlier evidence/failed attempts remain retained; G2 recovery behavior has not been accepted. Review owners: Operations plan/date/venue/publication, Learner Experience accessibility, Programme schedule/production, Communications allowance, and listed category owners spending.\n'
        (self.out / FILES[1]).write_text(plan)
        cal = Calendar()
        cal.add('prodid', '-//Quillhaven//Event planning draft//EN')
        cal.add('version', '2.0')
        cal.add('method', 'PUBLISH')
        events = schedule if self.status != 'blocked' else []
        for row in events:
            event = Event()
            event.add('uid', f"fellowship-demo-day-{row['id']}@quillhaven.example")
            event.add('dtstamp', datetime.now(timezone.utc))
            event.add('dtstart', timestamp(row['start']).astimezone(timezone.utc))
            event.add('dtend', timestamp(row['end']).astimezone(timezone.utc))
            event.add('status', 'TENTATIVE')
            event.add('summary', row['title'])
            event.add('description', f"UNSENT DRAFT; run {self.id}; {row['basis']}; dependent on {row['depends_on']}; approvals pending")
            cal.add_component(event)
        (self.out / FILES[2]).write_bytes(cal.to_ical())
        comm = '# Draft communications\n\n' + basis
        base_costs = '; '.join(f"{o['id']} {o['cost_twd']} TWD ({o['feasibility']})" for o in options[:2])
        for audience, purpose, owner in [('Operations and category owners', 'Review versioned plan/date/venue, costs and headcount policy', 'Operations and respective category owners'),
                                         ('Attendees', 'Proposed event information; dietary/accessibility response process', 'Operations publication; Marketing drafting'),
                                         ('Vendors', 'Confirm proposed date, quote validity and coordinated services; no commitment', 'Operations; category owners spending')]:
            comm += f"\n## UNSENT DRAFT — {audience}\n\nAudience: {audience}\nPurpose: {purpose}\nApproval owner: {owner}\nConditions: {self.status}; release requires the stated human approvals.\n\n"
            if audience == 'Operations and category owners':
                comm += f"Please review run {self.id} for the proposed {model['event_date']} event, 09:30–17:00 +08:00, at TICC. Planning people {people}; registered {registered}. Recommendation {recommendation or 'deferred'}. Base options: {base_costs}. Review category allocations, remaining ceiling and 15/55 catering headroom where supported. All twelve demo/changeover pairs are retained in the supported programme. Please record approve/reject/defer/change-request with actor, subject, plan revision, timestamp and reasons; no response has yet been received.\n"
                comm += '\n'.join(r['summary'] + ' — owner ' + str(r.get('owner')) for r in self.unresolved) + '\n'
            elif audience == 'Attendees':
                comm += f"We are preparing Fellowship Demo Day for {model['event_date']} at TICC, with the proposed main programme from 09:30 to 17:00 +08:00. The review plan includes twelve team demonstrations, live captions, wheelchair seating and a staffed quiet space. Operations will coordinate responses to accessibility and dietary requests before the event through its existing process. This proposed information awaits Operations review; venue booking and invitation release have not occurred.\n"
            else:
                comm += f"Please review the proposed {model['event_date']} coordinated service plan for {people} people, 09:30–17:00 +08:00, with setup access from 07:30 and clearance by 18:30. Our review comparison is {base_costs}; selection and spending authorization are pending. Please confirm the cited package scope/capacity and validity before any commitment. Operations will arrange the required coordination/safety briefing and retain named dietary contacts.\n"
                comm += 'Base captioning/hearing loop/quiet staffing/security readiness follows the exercise coordination record. Optional Q-008 livestream needs separate network-test and venue-provider confirmation; it is excluded from the base and the priced add-on exceeds the current ceilings. This message makes no booking or payment commitment.\n'
        (self.out / FILES[3]).write_text(comm)


def validate(out, allow_eight=False):
    out = Path(out)
    snapshots = sorted((out / 'snapshots').glob('[0-9][0-9]-*.json'))
    require(len(snapshots) == (8 if allow_eight else 9), 'Incorrect snapshot count')
    schema = read_json(ROOT / 'snapshot.schema.json')
    available, run_id = set(), None
    # Evidence is retained before stage 01 bootstrap. Scope/unresolved records may
    # cite it while formal source records are produced at the stage 02 boundary.
    source_ids = {s['id'] for s in read_json(snapshots[1])['state']['sources']}
    previous = None
    for index, path in enumerate(snapshots, 1):
        snap = read_json(path)
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(snap)
        require(snap['sequence'] == index and snap['stage'] == STAGES[index-1], 'Stage/sequence mismatch')
        run_id = run_id or snap['run_id']
        require(snap['run_id'] == run_id, 'Mixed runs')
        require(snap['predecessor'] == previous, 'Predecessor identity/path/hash mismatch')
        require(set(snap['consumed_record_ids']) <= available, 'Unresolvable transition')
        if index == 2:
            source_ids = {s['id'] for s in snap['state']['sources']}
            for source in snap['state']['sources']:
                if source['local_reference']:
                    require(digest(Path(source['local_reference']).read_bytes()) == source['content_hash'], 'Evidence hash mismatch')
        available |= set(snap['produced_record_ids'])
        for record in walk_records(snap):
            require(set(record.get('evidence_ids', [])) <= (source_ids or available | {'src-brief', 'src-calendar'}), 'Unresolvable evidence ID')
        previous = dict(snapshot_id=snap['snapshot_id'], path=str(path.resolve()), sha256=digest(path.read_bytes()))
    stage4, stage6, stage7 = [read_json(snapshots[i])['state'] for i in [3, 5, 6]]
    artifact_records = read_json(snapshots[-1])['state'].get('artifacts', read_json(snapshots[-1])['state'].get('artifact_drafts', []))
    require(len(artifact_records) == 4, 'Four draft artifacts required')
    for artifact in artifact_records:
        require(digest(Path(artifact['path']).read_bytes()) == artifact['sha256'], 'Artifact hash mismatch')
        privacy_check(Path(artifact['path']).read_bytes())
    with (out / FILES[0]).open(newline='') as f:
        reader = csv.DictReader(f)
        require(reader.fieldnames == COLUMNS, 'CSV columns incorrect')
        comparison = list(reader)
    expected = stage6['option_results']
    require(len(comparison) == len(expected), 'Option count inconsistency')
    for row, option in zip(comparison, expected):
        require(row['option_id'] == option['id'] and row['feasibility'] == option['feasibility'], 'Option identity/feasibility mismatch')
        require(row['cost_twd'] == (str(option['cost_twd']) if option['cost_twd'] is not None else ''), 'Option cost mismatch')
        require(row['approval_status'] == 'pending', 'Invented approval')
    cal = Calendar.from_ical((out / FILES[2]).read_bytes())
    require(str(cal['VERSION']) == '2.0' and str(cal['METHOD']) == 'PUBLISH', 'Calendar headers invalid')
    require(not cal.errors, 'Calendar parser errors')
    events = cal.walk('VEVENT')
    intervals = stage4['schedule_dependencies'][0]['intervals']
    blocked = read_json(snapshots[-1])['status'] == 'blocked'
    require(len(events) == (0 if blocked else len(intervals)), 'Calendar/programme count mismatch')
    uids = set()
    for event, interval in zip(events, intervals):
        require(not event.errors and 'ATTENDEE' not in event and str(event['STATUS']) == 'TENTATIVE', 'Calendar draft boundary failed')
        require(str(event['UID']) not in uids, 'Duplicate event UID')
        uids.add(str(event['UID']))
        require(event.decoded('DTSTART') == timestamp(interval['start']) and event.decoded('DTEND') == timestamp(interval['end']), 'Calendar interval mismatch')
        require(event.decoded('DTSTAMP').tzinfo is not None, 'Calendar DTSTAMP timezone absent')
    for name in [FILES[1], FILES[3]]:
        text = (out / name).read_text()
        require(run_id in text, 'Draft run binding absent')
        require(str(stage4['planning_people']) in text, 'Headcount propagation missing')
        for option in expected[:2]:
            require(str(option['cost_twd']) in text and option['id'] in text, 'Cost propagation missing')
    require((out / FILES[3]).read_text().count('## UNSENT DRAFT') == 3, 'Unsent message boundaries missing')
    return [rec('validation-chain', 'Schema, format, sequence, same-run predecessor hashes and references passed'),
            rec('validation-evidence', 'Actual retained source hashes and privacy-pattern checks passed'),
            rec('validation-drafts', 'Four exact artifact hashes, CSV/plan/message bindings and independently parsed ICS intervals passed')]


def walk_records(value):
    if isinstance(value, dict):
        if 'evidence_ids' in value:
            yield value
        for child in value.values():
            yield from walk_records(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_records(child)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--brief', required=True)
    parser.add_argument('--captures', required=True)
    parser.add_argument('--interpretation', required=True)
    parser.add_argument('--out', default='deliverables')
    args = parser.parse_args()
    run = Run(args)
    try:
        run.execute()
        return 0
    except Exception as exc:
        run.out.mkdir(parents=True, exist_ok=True)
        write_json(run.out / 'failure.json', dict(run_id=run.id, observed_at=now(), error=type(exc).__name__ + ': ' + str(exc),
                    affected_stage=run.stage, available_evidence=run.evidence,
                    affected_artifacts=[str(run.out / f) for f in FILES], next_owner='Delivery owner',
                    recovery_action='Retain this failed attempt; resolve source/validation issue, then invoke a new run. No approval is granted.'))
        print(json.dumps(dict(run_id=run.id, status='failed', affected_stage=run.stage, error=type(exc).__name__)), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
