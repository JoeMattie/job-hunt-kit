#!/usr/bin/env python3
"""Local bookkeeping for an agent-assisted job hunt; run with `uv run scripts/hunt.py`. Python 3.10+, no dependencies."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ACTIVE_STATUSES = {'draft', 'reviewed', 'ready'}
ALL_STATUSES = ACTIVE_STATUSES | {'submitted', 'interviewing', 'closed'}

ROOT = Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def slug(s):
    s = re.sub('[^a-z0-9]+', '-', s.lower()).strip('-')
    if not s: raise ValueError('Name must contain letters or numbers')
    return s

def workspace(root):
    w = root/'workspace'
    if not (w/'profile.json').is_file(): raise ValueError('Workspace not initialized; run: uv run scripts/hunt.py init')
    return w

def initialize(root):
    w = root/'workspace'
    w.mkdir(exist_ok=True)
    for src, dest in [('profile.json','profile.json'),('corpus.json','corpus.json'),('style-profile.json','voice/profile.json')]:
        if not (w/dest).exists(): write(w/dest,read(root/'templates'/src))
    for d in ['corpus/excerpts','sources','applications']: (w/d).mkdir(parents=True,exist_ok=True)
    return w

def add_sample(root,a):
    w = initialize(root)
    if not re.fullmatch('[a-z0-9][a-z0-9-]*',a.id): raise ValueError('Invalid sample ID')
    text = Path(a.file).read_text(encoding='utf-8').strip()
    if not text: raise ValueError('Empty sample')
    data = (text+'\n').encode('utf-8')
    digest = hashlib.sha256(data).hexdigest()
    corpus = read(w/'corpus.json')
    if any(s['id']==a.id or s['sha256']==digest for s in corpus['samples']): raise ValueError('Duplicate sample ID or content')
    p = w/'corpus/excerpts'/f'{a.id}.txt'
    if p.exists(): raise ValueError('Excerpt already exists')
    p.write_bytes(data)
    corpus['samples'].append(dict(id=a.id,path=p.relative_to(w).as_posix(),sha256=digest,genre=a.genre,locator=a.locator,authorship=a.authorship,approved=a.authorship=='candidate',notes='Registered '+now()))
    write(w/'corpus.json',corpus)
    return p

def new_job(root,a):
    w = initialize(root)
    ident = slug(a.company)+'-'+slug(a.role)
    text = Path(a.description).read_text(encoding='utf-8') if a.description else 'Posting text pending; do not infer requirements from URL.'
    folder = w/'applications'/ident
    if folder.exists(): raise FileExistsError(f'An application folder named {ident} already exists; edit that packet or use a different role name')
    folder.mkdir()
    app = read(root/'templates/application.json')
    app.update(id=ident,company=a.company,role=a.role,url=a.url,captured_at=now(),profile_snapshot_sha256=sha(w/'profile.json'))
    write(folder/'application.json',app)
    (folder/'job.md').write_text(f'# {a.company} — {a.role}\n\nURL: {a.url or "not supplied"}\nCaptured: {app["captured_at"]}\n\n{text}\n',encoding='utf-8')
    for name in ['resume.md','cover-letter.md','review.md']: shutil.copyfile(root/'templates'/name,folder/name)
    return folder

def render_cv(root):
    w = initialize(root); p = read(w/'profile.json'); claims = {c['id']:c for c in p['claims']}
    lines = ['# '+(p['candidate']['name'] or 'Candidate')+' — master CV','','Exhaustive working inventory; claim status labels are not submission prose.','']
    for e in p['entries']:
        lines += [f'## {e["title"]} — {e["organization"]}','',f'{e["kind"]} | {e.get("start") or "unknown"} – {e.get("end") or "unknown"} | {e.get("location", "")}','',e.get('narrative',''),'']
        for cid in e['claim_ids']:
            c = claims[cid]
            refs = '; '.join(f'{x["source_id"]}: {x["locator"]}' for x in c['source_refs'])
            lines += [f'- [{c["status"]}] {c["text"]} ({cid}; {refs})']
            if c.get('metrics'): lines += ['  Metrics: '+json.dumps(c['metrics'],ensure_ascii=False)]
        lines += ['', '### Full details','','```json',json.dumps(e.get('details',{}),indent=2,ensure_ascii=False),'```','']
    lines += ['## Sources','']+[f'- {s["id"]}: {s["kind"]}; {s["locator"]}' for s in p['sources']]
    lines += ['','## Open questions','']+[f'- {q if isinstance(q,str) else json.dumps(q,ensure_ascii=False)}' for q in p['open_questions']]
    dest = w/'master-cv.md'; dest.write_text('\n'.join(lines)+'\n',encoding='utf-8'); return dest

def validate(root):
    w = workspace(root); errors = []; p = read(w/'profile.json')
    def check(ok,msg):
        if not ok: errors.append(msg)
    def index(items,label):
        ids = [x['id'] for x in items]; check(len(ids)==len(set(ids)),f'Duplicate {label} IDs')
        return {x['id']:x for x in items}
    check(p['schema_version']==1,'Unsupported profile version')
    sources=index(p['sources'],'source'); entries=index(p['entries'],'entry'); claims=index(p['claims'],'claim')
    for e in entries.values():
        check(e['kind'] in {'work','education','project','volunteering','certification','award','publication','other'},f'Unknown entry kind: {e["id"]}')
        for key in ['organization','title','start','end','narrative','details','claim_ids']: check(key in e,f'Entry {e["id"]} missing {key}')
        for cid in e['claim_ids']: check(cid in claims and claims[cid]['entry_id']==e['id'],f'Invalid entry claim: {cid}')
    for c in claims.values():
        check(c['status'] in {'proposed','confirmed','disputed','retired'},f'Unknown claim status: {c["id"]}')
        check(bool(c['text'].strip()),f'Empty claim: {c["id"]}')
        check(c['entry_id'] in entries and c['id'] in entries[c['entry_id']]['claim_ids'],f'Orphan claim: {c["id"]}')
        check(c['status']!='confirmed' or bool(c['source_refs']),f'Confirmed claim lacks evidence: {c["id"]}')
        for ref in c['source_refs']: check(ref['source_id'] in sources and bool(ref['locator']),f'Invalid source: {c["id"]}')
    corpus=read(w/'corpus.json'); samples=index(corpus['samples'],'sample')
    hashes=[s['sha256'] for s in samples.values()]; check(len(hashes)==len(set(hashes)),'Duplicate sample content')
    for s in samples.values():
        path=(w/s['path']).resolve(); safe=path.is_relative_to(w.resolve()); check(safe,f'Unsafe sample path: {s["id"]}')
        if safe:
            check(path.is_file(),f'Missing sample: {s["id"]}')
            if path.is_file(): check(sha(path)==s['sha256'],f'Changed sample hash: {s["id"]}')
        check(not s['approved'] or s['authorship']=='candidate',f'Unattributed approved sample: {s["id"]}')
    voice=read(w/'voice/profile.json'); check(voice['status'] in {'unlearned','draft','approved'},'Unknown voice status')
    for sid in voice['sample_ids']: check(sid in samples and samples[sid]['approved'],f'Invalid voice sample: {sid}')
    for rule in voice['rules']:
        check(bool(rule['sample_ids']),'Voice rule lacks evidence')
        for sid in rule['sample_ids']: check(sid in voice['sample_ids'],f'Invalid rule sample: {sid}')
    if voice['status']=='approved':
        check(bool(voice['sample_ids']) and bool(voice['rules']),'Approved voice lacks samples or rules')
        check(bool(voice['calibration']['approved_by']) and bool(voice['calibration']['approved_at']),'Voice approval missing attribution/date')
        check((w/'voice/SKILL.md').is_file(),'Approved voice lacks generated skill')
    for path in sorted((w/'applications').glob('*/application.json')):
        a=read(path); prefix=a['id']+': '
        check(a['schema_version']==1,prefix+'unsupported version')
        check(a['status'] in ALL_STATUSES,prefix+'unknown status')
        if a['status'] in ACTIVE_STATUSES:
            check(a['profile_snapshot_sha256']==sha(w/'profile.json'),prefix+'profile changed since this draft; recheck its evidence, then run: uv run scripts/hunt.py refresh-snapshot '+a['id'])
        reqs=index(a['requirements'],prefix+'requirement')
        for q in reqs.values():
            check(q['priority'] in {'required','preferred'},prefix+'unknown requirement priority')
            check(bool(q['claim_ids']) or bool(q['gap']),prefix+'requirement lacks evidence or gap')
            for cid in q['claim_ids']: check(cid in claims and claims[cid]['status']=='confirmed',prefix+f'unsupported requirement claim {cid}')
        for e in a['evidence']:
            check(e['artifact'] in {'resume.md','cover-letter.md'},prefix+'unknown artifact')
            check(bool(e['locator']) and bool(e['claim_ids']),prefix+'incomplete assertion evidence')
            for cid in e['claim_ids']: check(cid in claims and claims[cid]['status']=='confirmed',prefix+f'unsupported draft claim {cid}')
        if a['status']!='draft':
            for name in ['resume.md','cover-letter.md']: check('{{' not in (path.parent/name).read_text(encoding='utf-8'),prefix+f'unfilled template in {name}')
            check(bool(a['requirements']) and bool(a['evidence']),prefix+'missing requirement/evidence map')
            check(a['review']['facts_checked'] and a['review']['voice_checked'],prefix+'review incomplete')
            check(voice['status']=='approved',prefix+'approved voice missing')
        if a['status']=='ready': check(bool(a['review']['approved_by']),prefix+'candidate approval missing')
    return errors

def refresh_snapshot(root,a):
    w = workspace(root); path = w/'applications'/a.job/'application.json'
    if not path.is_file(): raise ValueError(f'No application named {a.job}; run status to list them')
    app = read(path); app['profile_snapshot_sha256'] = sha(w/'profile.json'); write(path,app)
    return f'{a.job}: snapshot refreshed to current profile; evidence must already have been rechecked'

def status(root):
    w = workspace(root); p = read(w/'profile.json'); corpus = read(w/'corpus.json'); voice = read(w/'voice/profile.json')
    by_status = {}
    for c in p['claims']: by_status[c['status']] = by_status.get(c['status'],0)+1
    lines = [f"Candidate: {p['candidate']['name'] or '(name not set)'}",
             f"Master CV: {len(p['entries'])} entries, {len(p['claims'])} claims"+(' ('+', '.join(f'{k} {v}' for k,v in sorted(by_status.items()))+')' if by_status else '')+f", {len(p['open_questions'])} open questions",
             f"Writing samples: {sum(1 for s in corpus['samples'] if s['approved'])} approved of {len(corpus['samples'])}",
             f"Voice: {voice['status']}", '', 'Applications:']
    apps = sorted((w/'applications').glob('*/application.json'))
    if not apps: lines.append('  (none yet; run new-job)')
    for path in apps:
        a = read(path); stale = a['status'] in ACTIVE_STATUSES and a['profile_snapshot_sha256']!=sha(w/'profile.json')
        lines.append(f"  {a['id']:40} {a['status']:12} captured {str(a['captured_at'] or '')[:10]}"+('  [profile changed]' if stale else ''))
    return '\n'.join(lines)

def backup(root,a):
    w = workspace(root); dest = Path(a.dest).expanduser().resolve() if a.dest else Path.home()/'Documents'/'job-hunt-kit-backups'
    if dest.is_relative_to(root.resolve()): raise ValueError('Choose a backup folder outside the repository')
    dest.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    archive = shutil.make_archive(str(dest/f'workspace-{stamp}'),'zip',root_dir=root,base_dir='workspace')
    return f'{archive}\nThis zip holds all personal data; keep it somewhere private and delete old copies you no longer need.'

def export_file(root,a):
    source=Path(a.file).resolve()
    if not source.is_relative_to((root/'workspace').resolve()) or source.suffix!='.md': raise ValueError('Export Markdown inside workspace/')
    if not shutil.which('pandoc'): raise ValueError('Pandoc is not installed. Ask the agent to produce the DOCX/PDF with its own document tools, or install Pandoc (brew install pandoc) and retry')
    target=source.with_suffix('.'+a.format)
    if target.exists(): raise ValueError('Export exists; preserve or rename before exporting again')
    subprocess.run(['pandoc',str(source),'-o',str(target)],check=True)
    return target

def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('init',help='create an empty private workspace'); sub.add_parser('validate',help='check IDs, evidence links, and status rules')
    sub.add_parser('render-cv',help='write workspace/master-cv.md from profile.json'); sub.add_parser('status',help='summarize the workspace and applications')
    r=sub.add_parser('refresh-snapshot',help='re-pin an application to the current profile after rechecking evidence'); r.add_argument('job',help='application folder name, e.g. acme-coordinator')
    b=sub.add_parser('backup',help='zip workspace/ to a private folder'); b.add_argument('--dest',help='backup folder (default ~/Documents/job-hunt-kit-backups)')
    a=sub.add_parser('add-sample'); a.add_argument('file')
    for f in ['id','genre','locator']: a.add_argument('--'+f,required=True)
    a.add_argument('--authorship',choices=['candidate','mixed','unknown'],required=True)
    j=sub.add_parser('new-job'); j.add_argument('company'); j.add_argument('role'); j.add_argument('--url'); j.add_argument('--description')
    e=sub.add_parser('export'); e.add_argument('file'); e.add_argument('--format',choices=['docx','pdf'],required=True)
    args=p.parse_args()
    try:
        if args.command=='validate':
            errors=validate(ROOT)
            if errors: print('\n'.join(errors),file=sys.stderr); return 1
            result='Data references valid; prose and layout still require review.'
        elif args.command=='init': result=initialize(ROOT)
        elif args.command=='render-cv': result=render_cv(ROOT)
        elif args.command=='add-sample': result=add_sample(ROOT,args)
        elif args.command=='new-job': result=new_job(ROOT,args)
        elif args.command=='status': result=status(ROOT)
        elif args.command=='refresh-snapshot': result=refresh_snapshot(ROOT,args)
        elif args.command=='backup': result=backup(ROOT,args)
        else: result=export_file(ROOT,args)
        print(result); return 0
    except FileExistsError as exc:
        print(f'Cannot complete: {exc.args[0] if exc.args else exc}',file=sys.stderr); return 1
    except FileNotFoundError as exc:
        print(f'Cannot complete: missing file {exc.filename}',file=sys.stderr); return 1
    except (ValueError,KeyError,TypeError,OSError,subprocess.CalledProcessError) as exc:
        print(f'Cannot complete: {exc}',file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())
