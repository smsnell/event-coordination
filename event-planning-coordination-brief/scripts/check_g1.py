#!/usr/bin/env python3
"""Bounded G1 observed-artifact checks and isolated synthetic degradation cases."""
import argparse
import copy
import json
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace

from icalendar import Calendar
from run import CLOCK, FILES, Run, digest, read_json, timestamp, validate, write_json


def check_live(out):
    validate(out)
    snapshots = sorted((out / 'snapshots').glob('[0-9][0-9]-*.json'))
    stages = [read_json(p) for p in snapshots]
    assert stages[-1]['status'] == 'complete'
    assert stages[0]['state']['business_clock'] == CLOCK.isoformat()
    assert stages[0]['state']['decision_deadline'] == '2026-09-04T17:00:00+08:00'
    basis = stages[3]['state']
    assert (basis['planning_people'], basis['registered_attendees'], basis['checkin_target']) == (245, 180, 144)
    options = stages[5]['state']['option_results']
    assert [(o['cost_twd'], o['feasibility']) for o in options[:2]] == [(494000, 'feasible'), (512000, 'feasible')]
    assert all(o['feasibility'] == 'infeasible' and o['rejected_reasons'] for o in options[2:])
    assert all(a['status'] == 'pending' for a in stages[6]['state']['approval_requirements'])
    rows = basis['schedule_dependencies'][0]['intervals']
    demos = [r for r in rows if r['id'].startswith('DEMO-') and not r['id'].endswith('-changeover')]
    changes = [r for r in rows if r['id'].endswith('-changeover')]
    assert len(demos) == len(changes) == 12
    assert {r['id'] for r in demos} == {f'DEMO-{i:02}' for i in range(1, 13)}
    by_id = {r['id']: r for r in rows}
    for demo in demos:
        change = by_id[demo['id'] + '-changeover']
        assert (timestamp(demo['end']) - timestamp(demo['start'])).total_seconds() == 600
        assert (timestamp(change['end']) - timestamp(change['start'])).total_seconds() == 180
        assert change['start'] == demo['end'] and change['depends_on'] == [demo['id']]
    for previous, current in zip(rows, rows[1:]):
        assert timestamp(previous['end']) <= timestamp(current['start'])
        assert current['depends_on'] == [previous['id']]
    assert by_id['keynote']['start'] == '2026-10-17T10:00:00+08:00'
    assert by_id['keynote']['end'] == '2026-10-17T11:00:00+08:00'
    assert by_id['opening']['start'] == '2026-10-17T09:30:00+08:00'
    assert by_id['closing']['end'] == '2026-10-17T17:00:00+08:00'
    assert len(basis['calendar_records']) == 8
    pdf = next(s for s in stages[1]['state']['sources'] if s['id'] == 'src-floor-plan')
    assert pdf['retrieval_status'] == 'retrieved' and len(pdf['observations']) == 3
    assert Path(pdf['local_reference']).read_bytes().startswith(b'%PDF-')
    assert all(o['locator']['kind'] == 'page-region' for o in pdf['observations'])
    assert not (out / 'failure.json').exists()
    return stages[0]['run_id']


def synthetic_case(root, captures, brief, mutate, expected):
    target = root / 'captures'
    target.mkdir(parents=True)
    for path in captures.glob('*'):
        if path.is_file() and path.suffix in ['.json', '.pdf']:
            (target / path.name).write_bytes(path.read_bytes())
    model = read_json(target / 'interpretation.json')
    mutate(target, model)
    model['capture_hashes'] = {key: digest((target / (key + '.json')).read_bytes()) for key in model['capture_hashes'] if (target / (key + '.json')).exists()}
    write_json(target / 'interpretation.json', model)
    out = root / 'result'
    run = Run(SimpleNamespace(out=out, captures=target, interpretation=target / 'interpretation.json', brief=brief))
    result = None
    try:
        result = run.execute()
    except ValueError as exc:
        # Execute the public CLI failure contract for a true bootstrap failure.
        if expected != 'failed':
            raise
        import os
        import subprocess
        import sys
        invocation = subprocess.run([sys.executable, str(Path(__file__).with_name('run.py')), '--brief', str(brief),
                                     '--captures', str(target), '--interpretation', str(target / 'interpretation.json'), '--out', str(out)],
                                    capture_output=True, text=True, env=os.environ.copy())
        assert invocation.returncode == 1
        failure = read_json(out / 'failure.json')
        assert set(['run_id', 'observed_at', 'error', 'affected_stage', 'available_evidence', 'affected_artifacts', 'next_owner', 'recovery_action']) <= set(failure)
        assert not list((out / 'snapshots').glob('[0-9][0-9]-*.json'))
        assert not any((out / f).exists() for f in FILES)
        result = 'failed'
    assert result == expected
    if result != 'failed':
        validate(out)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--captures', type=Path, required=True)
    parser.add_argument('--report', type=Path, default=Path('.planning-tmp/g1-checks/report.json'))
    args = parser.parse_args()
    run_id = check_live(args.out)
    results = [{'check': 'live shared basis / lineage / drafts / programme / inspected media', 'result': 'passed', 'run_id': run_id}]
    # Retain designated test attempts; synthetic evidence cannot enter live deliverables.
    work = Path(tempfile.mkdtemp(prefix='g1-synthetic-', dir=os.environ.get('TMPDIR', '.planning-tmp')))
    brief = Path('inputs/event-brief.md').resolve()
    def media_unavailable(path, model):
        (path / 'floor-plan.pdf').unlink()
        meta = read_json(path / 'floor-plan-meta.json')
        meta['retrieval_status'] = 'unavailable'
        meta['error'] = 'SYNTHETIC bounded source unavailability'
        write_json(path / 'floor-plan-meta.json', meta)
        model['media_visually_inspected_at'] = None
    out = synthetic_case(work / 'media-unavailable', args.captures, brief, media_unavailable, 'partial')
    evidence = read_json(out / 'snapshots/02-source-capture.json')['state']['sources']
    assert next(s for s in evidence if s['id'] == 'src-floor-plan')['observations'] == []
    assert 'Official spatial observations withheld' in (out / 'event-plan.md').read_text()
    results.append({'check': 'SYNTHETIC unavailable media: partial, withheld claims, nine snapshots/four drafts', 'result': 'passed'})
    def vendor_unavailable(path, model):
        d = read_json(path / 'vendors.json')
        d['retrieval_status'] = 'unavailable'
        d['capture'] = None
        write_json(path / 'vendors.json', d)
    out = synthetic_case(work / 'vendor-unavailable', args.captures, brief, vendor_unavailable, 'blocked')
    assert len(Calendar.from_ical((out / 'event-calendar.ics').read_bytes()).walk('VEVENT')) == 0
    assert read_json(out / 'snapshots/07-decision-and-approval.json')['state']['recommendation'] is None
    results.append({'check': 'SYNTHETIC unavailable vendors: blocked, empty calendar, unknown costs and unsent clarification', 'result': 'passed'})
    def bad_required(path, model):
        d = read_json(path / 'attendees.json')
        d['capture']['values'][1][4] = 'invalid-required-number'
        write_json(path / 'attendees.json', d)
    synthetic_case(work / 'invalid-required', args.captures, brief, bad_required, 'blocked')
    results.append({'check': 'SYNTHETIC invalid required number held before headcount interpretation', 'result': 'passed'})
    def no_deadline(path, model):
        d = read_json(path / 'calendar.json')
        d['capture']['values'] = [d['capture']['values'][0]] + [r for r in d['capture']['values'][1:] if r[0] != 'CAL-005']
        write_json(path / 'calendar.json', d)
    synthetic_case(work / 'missing-deadline', args.captures, brief, no_deadline, 'failed')
    results.append({'check': 'SYNTHETIC missing supported deadline: failure.json, no invented stage/draft success', 'result': 'passed'})
    report = {'observed_at': __import__('run').now(), 'run_id': run_id, 'checks': results, 'synthetic_path': str(work),
              'scope': 'G1 checks only; this report does not establish G2 acceptance or G3 independent review/operator feedback'}
    write_json(args.report, report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
