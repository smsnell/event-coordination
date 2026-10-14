#!/usr/bin/env python3
"""Bounded G2 checks; mutations are isolated synthetic evidence, never live inputs."""
import argparse
import contextlib
import csv
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

from icalendar import Calendar
from check_g1 import check_live
from run import FILES, Run, digest, now, read_json, validate, write_json


def stages(out):
    return [read_json(p) for p in sorted((out/'snapshots').glob('[0-9][0-9]-*.json'))]


def fingerprints(out):
    return {str(p.relative_to(out)): digest(p.read_bytes()) for folder in ['snapshots']
            for p in (out/folder).rglob('*') if p.is_file()} | {f:digest((out/f).read_bytes()) for f in FILES if (out/f).exists()}


def update(captures, key, identity, field, value):
    d=read_json(captures/(key+'.json')); h=d['capture']['values'][0]
    row=next(r for r in d['capture']['values'][1:] if r[0]==identity)
    row[h.index(field)]=str(value);write_json(captures/(key+'.json'),d)


def bind(captures, model):
    model['capture_hashes']={k:digest((captures/(k+'.json')).read_bytes()) for k in model['capture_hashes']}
    model['author']='SYNTHETIC G2 fixture; not a live retrieval';model['rationale']='Controlled isolated mutation of retained actual observations; no fresh retrieval or approval asserted.'
    write_json(captures/'interpretation.json',model)


def execute(out, captures, model, brief, expected='complete'):
    bind(captures,model)
    r=Run(SimpleNamespace(out=out,captures=captures,interpretation=captures/'interpretation.json',brief=brief,reason='SYNTHETIC G2 verification'))
    with contextlib.redirect_stdout(io.StringIO()):
        result=r.execute()
    assert result==expected,(result,expected)
    validate(out)
    s=stages(out)
    assert all(a['status']=='pending' and a['basis_run_id']==s[0]['run_id'] for a in s[6]['state']['approval_requirements'])
    assert (out/FILES[3]).read_text().count('## UNSENT DRAFT')==3
    for e in Calendar.from_ical((out/FILES[2]).read_bytes()).walk('VEVENT'):
        assert 'ATTENDEE' not in e and str(e['STATUS'])=='TENTATIVE'
    return s


def check_history(out, prior_id, before):
    history=out/'history'/prior_id
    assert all(digest((history/name).read_bytes())==sha for name,sha in before.items())
    retention=read_json(history/'retention.json')
    assert retention['retained_hashes']==before
    return history


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--captures',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--report',type=Path,default=Path('docs/g2/verification.json'))
    p.add_argument('--only',choices=['changed-access'],help='Run only combined changed-access and harmless-reordering checks')
    args=p.parse_args();started=time.monotonic()
    args.report.parent.mkdir(parents=True,exist_ok=True)
    work=Path(tempfile.mkdtemp(prefix='g2-synthetic-',dir=str(Path(os.environ.get('TMPDIR','.planning-tmp')))))
    brief=Path('inputs/event-brief.md').resolve();results=[]
    def fixture(name):
        root=work/name;cap=root/'captures';shutil.copytree(args.captures,cap)
        return root/'result',cap,read_json(cap/'interpretation.json')
    def passed(name,**details):results.append(dict(check=name,result='passed',**details))
    out,cap,m=fixture('changes');a=execute(out,cap,m,brief);first=a[0]['run_id'];before=fingerprints(out)
    assert a[2]['state']['readiness_coverage']['supported'] is True
    assert all(o['feasibility']=='feasible' for o in a[5]['state']['option_results'][:2])
    update(cap,'attendees','SIG-005','value',45);m['declared_people']=255
    changed_brief=out.parent/'event-brief.md'
    changed_brief.write_text(brief.read_text().replace('Plan for 245 people', 'Plan for 255 people'))
    m['brief_sha256']=digest(changed_brief.read_bytes())
    update(cap,'vendors','Q-003','quote_amount_twd',110000)
    update(cap,'calendar','CAL-003','start_at','2026-10-17T08:00:00+08:00')
    b=execute(out,cap,m,changed_brief,'partial')
    assert b[0]['run_id']!=first and b[0]['state']['supersedes_run_id']==first
    assert {'src-attendees','src-vendors','src-calendar','src-interpretation'} <= set(b[0]['state']['changed_source_ids'])
    assert b[0]['state']['changed_decision_ids']==[] and b[0]['state']['reconsidered_decision_ids']==['decision-recommendation']
    assert b[3]['state']['planning_people']==255
    assert [o['cost_twd'] for o in b[5]['state']['option_results'][:2]]==[496000,512000]
    assert all(o['feasibility']=='conditional' for o in b[5]['state']['option_results'][:2])
    assert b[6]['state']['recommendation'] is None
    assert b[2]['state']['readiness_coverage']['supported'] is False
    gap=next(r for r in b[-1]['unresolved'] if r['id']=='gap-readiness')
    assert gap['owner']=='Operations / Programme'
    assert gap['evidence_ids']==['src-brief','src-calendar']
    for o in b[5]['state']['option_results'][:2]:
        assert any('changed venue access arrangement' in condition and gap['owner'] in condition for condition in o['unresolved'])
    assert b[3]['state']['schedule_dependencies'][0]['intervals'][0]['start']=='2026-10-17T08:00:00+08:00'
    for f in FILES:assert digest((out/f).read_bytes())!=before[f]
    assert '5; ceiling headroom' in (out/FILES[0]).read_text()
    assert '08:00' in (out/FILES[3]).read_text() and '496000' in (out/FILES[2]).read_text()
    with (out/FILES[0]).open() as f:
        rows=list(csv.DictReader(f))
    assert all(r['feasibility']=='conditional' and gap['owner'] in r['unresolved'] for r in rows[:2])
    plan=(out/FILES[1]).read_text()
    assert 'Recommendation deferred' in plan and 'conditional; booking unconfirmed' in plan and gap['summary'] in plan
    messages=(out/FILES[3]).read_text()
    assert 'Recommendation deferred' in messages and messages.count(gap['summary'])>=3
    for event in Calendar.from_ical((out/FILES[2]).read_bytes()).walk('VEVENT'):
        assert '(conditional)' in str(event['DESCRIPTION']) and gap['summary'] in str(event['DESCRIPTION'])
        assert gap['owner'] in str(event['DESCRIPTION'])
    history=check_history(out,first,before);validate(history,binding_root=out.resolve())
    passed('SYNTHETIC original access supported; changed access conditional in all four drafts, recommendation deferred, owner preserved, prices propagated and history exact',run_id=b[0]['run_id'])
    # Headers AND records reordered, with unrelated columns, in all four tables.
    before_basis=b[3]['state'];before_options=b[5]['state']['option_results']
    for key in ['attendees','budget','vendors','calendar']:
        d=read_json(cap/(key+'.json'));values=d['capture']['values'];indices=list(reversed(range(len(values[0]))))
        d['capture']['values']=[['unrelated_extra']+[values[0][i] for i in indices]]+[['ignored']+[r[i] for i in indices] for r in reversed(values[1:])]
        write_json(cap/(key+'.json'),d)
    c=execute(out,cap,m,changed_brief,'partial')
    assert c[3]['state']['planning_people']==before_basis['planning_people']
    assert c[3]['state']['schedule_dependencies']==before_basis['schedule_dependencies']
    assert c[5]['state']['option_results']==before_options
    captured=read_json(out/'snapshots/evidence/attendees.json')
    assert captured['capture']['values'][0][0]=='unrelated_extra'
    passed('SYNTHETIC combined header/row reordering plus harmless extra columns in every structured source preserves normalized meaning and captured representation')
    if args.only:
        report=dict(observed_at=now(),runtime_seconds=round(time.monotonic()-started,3),checks=results,
                    synthetic_path=str(work),current_synthetic_run_id=c[0]['run_id'],
                    scope='Targeted G2 changed-access correction only; full suite not rerun; prior live drafts untouched')
        write_json(args.report,report);print(json.dumps(report,indent=2));return
    # Each defect has its own preserved attempt and resolution owner.
    for name,key,mutation,expected in [
        ('invalid-number','attendees',lambda d:d['capture']['values'][1].__setitem__(4,'NaN'),'blocked'),
        ('missing-field','vendors',lambda d:[r.pop(4) for r in d['capture']['values']],'blocked'),
        ('duplicate-id','vendors',lambda d:d['capture']['values'].append(d['capture']['values'][1][:]),'blocked'),
        ('invalid-unit','attendees',lambda d:d['capture']['values'][1].__setitem__(5,'meals'),'blocked'),
        ('unknown-signal','attendees',lambda d:d['capture']['values'][1].__setitem__(3,'renamed_count'),'blocked'),
        ('conflicting-headcount','attendees',lambda d:d['capture']['values'][5].__setitem__(4,'75'),'partial'),
        ('missing-needs','attendees',lambda d:d['capture']['values'].pop(6),'blocked'),
        ('keynote-conflict','calendar',lambda d:d['capture']['values'][4].__setitem__(3,'2026-10-17T10:15:00+08:00'),'blocked'),
        ('expired-hold','calendar',lambda d:d['capture']['values'][3].__setitem__(6,'Hold expires 2026-08-25'),'blocked'),
    ]:
        x,q,j=fixture(name);d=read_json(q/(key+'.json'));mutation(d);write_json(q/(key+'.json'),d)
        ss=execute(x,q,j,brief,expected)
        assert ss[-1]['unresolved'] and ss[6]['state']['recommendation'] is None
        if expected=='blocked':assert not Calendar.from_ical((x/FILES[2]).read_bytes()).walk('VEVENT')
        passed('SYNTHETIC '+name+': held dependency, explicit '+expected+', no invented recommendation/approval')
    for name,field,value in [('unavailable-quote','status','unavailable'),('capacity-change','capacity','240'),('expired-quote','valid_until','2026-08-25')]:
        x,q,j=fixture(name);update(q,'vendors','Q-003',field,value);ss=execute(x,q,j,brief,'partial')
        assert ss[5]['state']['option_results'][0]['feasibility']=='infeasible'
        assert ss[6]['state']['recommendation']=='option-city-pantry'
        passed('SYNTHETIC '+name+': reject affected option, supported alternative retained, partial status')
    x,q,j=fixture('category-conflict');update(q,'vendors','Q-003','category','production')
    ss=execute(x,q,j,brief,'partial')
    assert ss[5]['state']['option_results'][0]['feasibility']=='unverified' and ss[5]['state']['option_results'][0]['cost_twd'] is None
    assert ss[6]['state']['recommendation']=='option-city-pantry'
    passed('SYNTHETIC incompatible quote category: affected meaning held and cost unknown, supported alternative retained')
    # Output damage must be observed even with unchanged inputs, then archived exactly.
    for name,damage in [('missing-output',lambda x:(x/'event-plan.md').unlink()),('corrupt-output',lambda x:(x/'event-calendar.ics').write_text('CORRUPT SYNTHETIC OUTPUT'))]:
        x,q,j=fixture(name);ss=execute(x,q,j,brief);prior=ss[0]['run_id'];damage(x)
        try:validate(x)
        except (ValueError,FileNotFoundError):pass
        else:raise AssertionError('damage masked')
        damaged=fingerprints(x);new=execute(x,q,j,brief)
        assert new[0]['state']['supersedes_run_id']==prior and new[0]['state']['prior_integrity']['validation']=='incomplete'
        check_history(x,prior,damaged)
        assert 'Recovery' not in new[0]['state']['change_reason'] # caller reason retained; integrity records recovery
        passed('SYNTHETIC '+name+': damage detected with unchanged inputs, exact damaged history retained, coherent actual repair')
    # Failure after a valid run cannot expose that old run as current; retry repairs bootstrap.
    x,q,j=fixture('failure-recovery');ss=execute(x,q,j,brief);prior=ss[0]['run_id'];original=fingerprints(x)
    j['capture_hashes']['attendees']='sha256:'+'0'*64;write_json(q/'interpretation.json',j)
    command=[sys.executable,str(Path(__file__).with_name('run.py')),'--brief',str(brief),'--captures',str(q),'--interpretation',str(q/'interpretation.json'),'--out',str(x)]
    invocation=subprocess.run(command,capture_output=True,text=True,env=os.environ.copy());assert invocation.returncode==1
    failure=read_json(x/'failure.json');assert failure['affected_stage']=='bootstrap'
    assert not (x/'snapshots/09-publication-validation.json').exists() and not any((x/f).exists() for f in FILES)
    check_history(x,prior,original)
    retry=execute(x,q,j,brief);assert retry[0]['state']['supersedes_run_id']==failure['run_id']
    assert read_json(x/'history'/failure['run_id']/'failure.json')==failure and not (x/'failure.json').exists()
    assert (x/'history'/failure['run_id']/'attempt').exists()
    passed('SYNTHETIC bootstrap hash mismatch: explicit failure, old success withdrawn; actual retry retains failed attempt and grants no approval')
    x,q,j=fixture('unsafe-retention');d=read_json(q/'attendees.json');d['capture']['values'][0].append('medical_detail')
    for r in d['capture']['values'][1:]:r.append('SYNTHETIC PRIVATE FIELD')
    write_json(q/'attendees.json',d);bind(q,j)
    invocation=subprocess.run([sys.executable,str(Path(__file__).with_name('run.py')),'--brief',str(brief),'--captures',str(q),'--interpretation',str(q/'interpretation.json'),'--out',str(x)],capture_output=True,text=True,env=os.environ.copy())
    assert invocation.returncode==1 and not list(x.rglob('attendees.json'))
    assert all(b'SYNTHETIC PRIVATE FIELD' not in p.read_bytes() for p in x.rglob('*') if p.is_file())
    passed('SYNTHETIC private-field response: retention refused before raw values enter general outputs or failure evidence')
    # Final live run is not a synthetic fixture.
    live_id=check_live(args.out)
    live=stages(args.out);s=live[3]['state']['schedule_dependencies'][0]['intervals'];by_id={r['id']:r for r in s}
    assert by_id['break-1']['start']=='2026-10-17T11:00:00+08:00' and by_id['lunch']['start']=='2026-10-17T12:33:00+08:00'
    plan=(args.out/'event-plan.md').read_text();assert 'Options at a glance' in plan and '<details>' in plan
    assert '12.0 per minute' in plan and '16.3 per minute' in plan and 'Exercise-feasible; booking unconfirmed' in plan
    passed('Actual current run: nine bindings/four drafts, readable comparison, arrival assumptions, revised break, 12 demos/changeovers, exercise/booking distinction',run_id=live_id)
    report=dict(observed_at=now(),runtime_seconds=round(time.monotonic()-started,3),live_run_id=live_id,checks=results,
                synthetic_path=str(work),scope='G2 focused technical checks; user gate acceptance and G3 independent review/operator use pending')
    write_json(args.report,report);print(json.dumps(report,indent=2))


if __name__=='__main__':main()
