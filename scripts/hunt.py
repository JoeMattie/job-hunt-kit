#!/usr/bin/env python3
"""Local bookkeeping for an agent-assisted job hunt; run with `uv run -q scripts/hunt.py`. Python 3.10+, no dependencies."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ACTIVE_STATUSES = {'draft', 'reviewed', 'ready'}
ALL_STATUSES = ACTIVE_STATUSES | {'submitted', 'interviewing', 'closed'}
ENTRY_KINDS = ['work', 'internship', 'project', 'volunteering', 'education', 'certification', 'award', 'publication', 'statement', 'other']
CAREER_KINDS = {'work', 'internship', 'project', 'volunteering', 'education', 'certification', 'award', 'publication'}
SOURCE_KINDS = ['document', 'interview', 'email', 'message', 'portfolio']
VOICE_MODES = {'learned', 'neutral'}

ROOT = Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.now().astimezone().isoformat(timespec='seconds')  # local time with offset, so dates match the candidate's day
def today(): return datetime.now().strftime('%Y-%m-%d')
def slug(s):
    s = re.sub('[^a-z0-9]+', '-', s.lower()).strip('-')
    if not s: raise ValueError('Name must contain letters or numbers')
    return s
def valid_id(s):
    if not re.fullmatch('[a-z0-9][a-z0-9-]*', s): raise ValueError(f'Invalid ID {s!r}; use lowercase letters, digits, and hyphens')

def workspace(root):
    w = root/'workspace'
    if not (w/'profile.json').is_file(): raise ValueError('Workspace not initialized; run: uv run -q scripts/hunt.py init')
    return w

def initialize(root):
    w = root/'workspace'
    w.mkdir(exist_ok=True)
    for src, dest in [('profile.json','profile.json'),('corpus.json','corpus.json'),('style-profile.json','voice/profile.json')]:
        if not (w/dest).exists(): write(w/dest, read(root/'templates'/src))
    for d in ['corpus/excerpts','sources','applications']: (w/d).mkdir(parents=True, exist_ok=True)
    return w

def add_sample(root, a):
    w = initialize(root); valid_id(a.id)
    text = Path(a.file).read_text(encoding='utf-8').strip()
    if not text: raise ValueError('Empty sample')
    data = (text+'\n').encode('utf-8'); digest = hashlib.sha256(data).hexdigest()
    corpus = read(w/'corpus.json')
    if any(s['id']==a.id or s['sha256']==digest for s in corpus['samples']): raise ValueError('Duplicate sample ID or content')
    p = w/'corpus/excerpts'/f'{a.id}.txt'
    if p.exists(): raise ValueError('Excerpt already exists')
    p.write_bytes(data)
    corpus['samples'].append(dict(id=a.id, path=p.relative_to(w).as_posix(), sha256=digest, genre=a.genre, locator=a.locator, authorship=a.authorship, approved=a.authorship=='candidate', notes='Registered '+now()))
    write(w/'corpus.json', corpus)
    return p

def register_source(w, profile, sid, kind, locator, notes):
    if any(x['id']==sid for x in profile['sources']): raise ValueError(f'Duplicate source ID {sid}')
    profile['sources'].append(dict(id=sid, kind=kind, locator=locator, captured_at=now(), notes=notes))
    write(w/'profile.json', profile)

def add_source(root, a):
    """Copy a candidate-supplied document (old resume, transcript, export) into workspace/sources and register it as career evidence."""
    w = initialize(root); valid_id(a.id)
    src = Path(a.file)
    if not src.is_file(): raise ValueError(f'No such file: {src}')
    dest = w/'sources'/(a.id+src.suffix.lower())
    if dest.exists(): raise ValueError('Source file already exists')
    profile = read(w/'profile.json')
    if any(x['id']==a.id for x in profile['sources']): raise ValueError(f'Duplicate source ID {a.id}')
    shutil.copyfile(src, dest)
    register_source(w, profile, a.id, a.kind, dest.relative_to(w).as_posix(), a.notes or f'Imported {src.name}; sha256 {sha(dest)}')
    return dest

def add_interview(root, a):
    """Create (or reopen) a dated interview transcript and register it as a source. Idempotent: safe to call again for the same ID."""
    w = initialize(root); sid = a.id or f'interview-{today()}'; valid_id(sid)
    dest = w/'sources'/f'{sid}.md'
    if not dest.exists():
        dest.write_text(f'# Interview {sid}\n\nVerbatim candidate answers. Number each answer (A1, A2, ...) so claims can cite it as a locator.\n\n', encoding='utf-8')
    profile = read(w/'profile.json')
    if not any(x['id']==sid for x in profile['sources']):
        register_source(w, profile, sid, 'interview', dest.relative_to(w).as_posix(), f'Interview transcript started {today()}')
    return dest

def cv_reviewed(root):
    """Record that assemble-master-cv has completed a pass; readiness depends on it."""
    w = workspace(root); p = read(w/'profile.json'); p['inventory_reviewed_at'] = now(); write(w/'profile.json', p)
    return 'Career inventory marked reviewed '+p['inventory_reviewed_at']

def new_job(root, a):
    w = initialize(root)
    ident = slug(a.company)+'-'+slug(a.role)
    text = Path(a.description).read_text(encoding='utf-8') if a.description else 'Posting text pending; do not infer requirements from URL.'
    folder = w/'applications'/ident
    if folder.exists(): raise FileExistsError(f'An application folder named {ident} already exists; edit that packet or use a different role name')
    folder.mkdir()
    app = read(root/'templates/application.json')
    app.update(id=ident, company=a.company, role=a.role, url=a.url, captured_at=now(), profile_snapshot_sha256=sha(w/'profile.json'))
    write(folder/'application.json', app)
    (folder/'job.md').write_text(f'# {a.company} — {a.role}\n\nURL: {a.url or "not supplied"}\nCaptured: {app["captured_at"]}\n\n{text}\n', encoding='utf-8')
    for name in ['resume.md','cover-letter.md','review.md']: shutil.copyfile(root/'templates'/name, folder/name)
    return folder

def fmt_detail(key, value):
    if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
        return f'- {key}: {len(value)} items (full list in profile.json)'
    if isinstance(value, list): return f'- {key}: '+'; '.join(str(x) for x in value)
    if isinstance(value, dict): return f'- {key}: '+json.dumps(value, ensure_ascii=False)
    return f'- {key}: {value}'

def fmt_question(q):
    if isinstance(q, str): return q
    parts = [str(q.get('question', ''))]
    if q.get('related'): parts.append('related: '+', '.join(map(str, q['related'])))
    if q.get('resolution'): parts.append('resolution: '+str(q['resolution']))
    return parts[0] + ''.join(f' ({x})' for x in parts[1:])

def render_cv(root):
    w = initialize(root); p = read(w/'profile.json'); claims = {c['id']: c for c in p['claims']}
    order = {k: i for i, k in enumerate(ENTRY_KINDS)}
    entries = sorted(p['entries'], key=lambda e: (order.get(e['kind'], 99), str(e.get('start') or '0')), reverse=False)
    entries = sorted(entries, key=lambda e: order.get(e['kind'], 99))  # stable: kind order, then by start desc within kind
    grouped = {}
    for e in entries: grouped.setdefault(e['kind'], []).append(e)
    lines = ['# '+(p['candidate']['name'] or 'Candidate')+' — master CV', '', 'Exhaustive working inventory; claim status labels are not submission prose.', '']
    for kind in ENTRY_KINDS:
        if kind not in grouped: continue
        lines += [f'# {kind.capitalize()}', '']
        for e in sorted(grouped[kind], key=lambda e: str(e.get('start') or ''), reverse=True):
            dates = '' if kind=='statement' else f' | {e.get("start") or "unknown"} – {e.get("end") or "unknown"}'
            where = f' | {e["location"]}' if e.get('location') else ''
            head = e['title'] + (f' — {e["organization"]}' if e.get('organization') else '')
            lines += [f'## {head}', '', f'{e["id"]}{dates}{where}', '', e.get('narrative', ''), '']
            for cid in e['claim_ids']:
                c = claims[cid]; refs = '; '.join(f'{x["source_id"]}: {x["locator"]}' for x in c['source_refs'])
                lines += [f'- [{c["status"]}] {c["text"]} ({cid}; {refs})']
                if c.get('metrics'): lines += ['  Metrics: '+json.dumps(c['metrics'], ensure_ascii=False)]
            if e.get('details'):
                lines += ['', '### Details', ''] + [fmt_detail(k, v) for k, v in e['details'].items()]
            lines += ['']
    lines += ['# Sources', ''] + [f'- {s["id"]}: {s["kind"]}; {s["locator"]}' for s in p['sources']]
    lines += ['', '# Open questions', ''] + ([f'- {fmt_question(q)}' for q in p['open_questions']] or ['- none'])
    dest = w/'master-cv.md'; dest.write_text('\n'.join(lines)+'\n', encoding='utf-8'); return dest

def validate(root):
    w = workspace(root); errors = []; p = read(w/'profile.json')
    def check(ok, msg):
        if not ok: errors.append(msg)
    def index(items, label):
        ids = [x['id'] for x in items]; check(len(ids)==len(set(ids)), f'Duplicate {label} IDs')
        return {x['id']: x for x in items}
    check(p['schema_version']==1, 'Unsupported profile version')
    sources = index(p['sources'], 'source'); entries = index(p['entries'], 'entry'); claims = index(p['claims'], 'claim')
    for s in sources.values(): check(s['kind'] in SOURCE_KINDS, f'Unknown source kind: {s["id"]}')
    for e in entries.values():
        check(e['kind'] in ENTRY_KINDS, f'Unknown entry kind: {e["id"]}')
        for key in ['organization','title','start','end','narrative','details','claim_ids']: check(key in e, f'Entry {e["id"]} missing {key}')
        for cid in e['claim_ids']: check(cid in claims and claims[cid]['entry_id']==e['id'], f'Invalid entry claim: {cid}')
    for c in claims.values():
        check(c['status'] in {'proposed','confirmed','disputed','retired'}, f'Unknown claim status: {c["id"]}')
        check(bool(c['text'].strip()), f'Empty claim: {c["id"]}')
        check(c['entry_id'] in entries and c['id'] in entries[c['entry_id']]['claim_ids'], f'Orphan claim: {c["id"]}')
        check(c['status']!='confirmed' or bool(c['source_refs']), f'Confirmed claim lacks evidence: {c["id"]}')
        for ref in c['source_refs']: check(ref['source_id'] in sources and bool(ref['locator']), f'Invalid source: {c["id"]}')
    corpus = read(w/'corpus.json'); samples = index(corpus['samples'], 'sample')
    hashes = [s['sha256'] for s in samples.values()]; check(len(hashes)==len(set(hashes)), 'Duplicate sample content')
    for s in samples.values():
        path = (w/s['path']).resolve(); safe = path.is_relative_to(w.resolve()); check(safe, f'Unsafe sample path: {s["id"]}')
        if safe:
            check(path.is_file(), f'Missing sample: {s["id"]}')
            if path.is_file(): check(sha(path)==s['sha256'], f'Changed sample hash: {s["id"]}')
        check(not s['approved'] or s['authorship']=='candidate', f'Unattributed approved sample: {s["id"]}')
    voice = read(w/'voice/profile.json'); check(voice['status'] in {'unlearned','draft','approved'}, 'Unknown voice status')
    for sid in voice['sample_ids']: check(sid in samples and samples[sid]['approved'], f'Invalid voice sample: {sid}')
    for rule in voice['rules']:
        check(bool(rule['sample_ids']), 'Voice rule lacks evidence')
        for sid in rule['sample_ids']: check(sid in voice['sample_ids'], f'Invalid rule sample: {sid}')
    if voice['status']=='approved':
        check(bool(voice['sample_ids']) and bool(voice['rules']), 'Approved voice lacks samples or rules')
        check(bool(voice['calibration']['approved_by']) and bool(voice['calibration']['approved_at']), 'Voice approval missing attribution/date')
        check((w/'voice/SKILL.md').is_file(), 'Approved voice lacks generated skill')
    for path in sorted((w/'applications').glob('*/application.json')):
        a = read(path); prefix = a['id']+': '; mode = a.get('voice_mode', 'learned')
        check(a['schema_version']==1, prefix+'unsupported version')
        check(a['status'] in ALL_STATUSES, prefix+'unknown status')
        check(mode in VOICE_MODES, prefix+'unknown voice_mode')
        drafted = bool(a['requirements']) or bool(a['evidence'])
        if a['status'] in ACTIVE_STATUSES and drafted:
            check(a['profile_snapshot_sha256']==sha(w/'profile.json'), prefix+'profile changed since this draft; recheck its evidence, then run: uv run -q scripts/hunt.py refresh-snapshot '+a['id'])
        reqs = index(a['requirements'], prefix+'requirement')
        for q in reqs.values():
            check(q['priority'] in {'required','preferred','duty'}, prefix+'unknown requirement priority')
            check(bool(q['claim_ids']) or bool(q['gap']), prefix+'requirement lacks evidence or gap')
            for cid in q['claim_ids']: check(cid in claims and claims[cid]['status']=='confirmed', prefix+f'unsupported requirement claim {cid}')
        for e in a['evidence']:
            check(e['artifact'] in {'resume.md','cover-letter.md'}, prefix+'unknown artifact')
            check(bool(e['locator']) and bool(e['claim_ids']), prefix+'incomplete assertion evidence')
            for cid in e['claim_ids']: check(cid in claims and claims[cid]['status']=='confirmed', prefix+f'unsupported draft claim {cid}')
        if a['status']!='draft':
            for name in ['resume.md','cover-letter.md']: check('{{' not in (path.parent/name).read_text(encoding='utf-8'), prefix+f'unfilled template in {name}')
            check(bool(a['requirements']) and bool(a['evidence']), prefix+'missing requirement/evidence map')
            check(a['review']['facts_checked'] and a['review']['voice_checked'], prefix+'review incomplete')
            check(voice['status']=='approved' or mode=='neutral', prefix+'approved voice missing (or set voice_mode to neutral with the candidate\'s explicit permission)')
        if a['status']=='ready': check(bool(a['review']['approved_by']), prefix+'candidate approval missing')
    return errors

def refresh_snapshot(root, a):
    w = workspace(root); path = w/'applications'/a.job/'application.json'
    if not path.is_file(): raise ValueError(f'No application named {a.job}; run status to list them')
    app = read(path); app['profile_snapshot_sha256'] = sha(w/'profile.json'); write(path, app)
    return f'{a.job}: snapshot refreshed to current profile; evidence must already have been rechecked'

def readiness(p, corpus, voice):
    """Prerequisites for drafting an application, in the order skills should satisfy them. Voice is reported separately because a neutral draft is an allowed fallback."""
    missing = []
    if not p['candidate']['name']: missing.append('contact details are empty (start-job-search)')
    career = any(c['status']=='confirmed' and next((e for e in p['entries'] if e['id']==c['entry_id']), {}).get('kind') in CAREER_KINDS for c in p['claims'])
    if not career: missing.append('no confirmed claims on any job, project, or education entry (assemble-master-cv)')
    if not p.get('inventory_reviewed_at'): missing.append('career inventory not yet assembled and reviewed (assemble-master-cv; it ends with cv-reviewed)')
    return missing

def voice_line(corpus, voice):
    if voice['status']=='approved': return 'Voice: approved'
    samples = sum(1 for s in corpus['samples'] if s['approved'])
    step = 'learn-candidate-voice' if samples else 'build-writing-corpus, then learn-candidate-voice'
    return f'Voice: {voice["status"]} ({step}; or the candidate may choose a neutral draft per application)'

def status(root):
    created = not (root/'workspace'/'profile.json').is_file()
    w = initialize(root); p = read(w/'profile.json'); corpus = read(w/'corpus.json'); voice = read(w/'voice/profile.json')
    by_status = {}
    for c in p['claims']: by_status[c['status']] = by_status.get(c['status'], 0)+1
    missing = readiness(p, corpus, voice)
    lines = (['Workspace created (first run).', ''] if created else []) + [
        f"Candidate: {p['candidate']['name'] or '(name not set)'}",
        f"Master CV: {len(p['entries'])} entries, {len(p['claims'])} claims"+(' ('+', '.join(f'{k} {v}' for k, v in sorted(by_status.items()))+')' if by_status else ''),
        f"Writing samples: {sum(1 for s in corpus['samples'] if s['approved'])} approved of {len(corpus['samples'])}",
        voice_line(corpus, voice),
        'Ready to draft applications: '+('yes' if not missing else 'not yet'), *('  - missing: '+m for m in missing)]
    if p['open_questions']:
        lines += ['', f'Open questions ({len(p["open_questions"])}):'] + ['  - '+fmt_question(q)[:120] for q in p['open_questions'][:10]]
        if len(p['open_questions']) > 10: lines.append(f'  ... and {len(p["open_questions"])-10} more in profile.json')
    lines += ['', 'Applications:']
    apps = sorted((w/'applications').glob('*/application.json'))
    if not apps: lines.append('  (none yet)')
    for path in apps:
        a = read(path); drafted = bool(a['requirements']) or bool(a['evidence'])
        flags = []
        if a['status'] in ACTIVE_STATUSES and drafted and a['profile_snapshot_sha256']!=sha(w/'profile.json'): flags.append('profile changed')
        if a.get('voice_mode')=='neutral': flags.append('neutral voice')
        if a['review'].get('approved_by'): flags.append('approved by candidate')
        lines.append(f"  {a['id']:40} {a['status']:12} captured {str(a['captured_at'] or '')[:10]}"+(('  ['+'; '.join(flags)+']') if flags else ''))
    return '\n'.join(lines)

def backup(root, a):
    w = workspace(root); dest = Path(a.dest).expanduser().resolve() if a.dest else Path.home()/'Documents'/'job-hunt-kit-backups'
    if dest.is_relative_to(root.resolve()): raise ValueError('Choose a backup folder outside the repository')
    dest.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    archive = shutil.make_archive(str(dest/f'workspace-{stamp}'), 'zip', root_dir=root, base_dir='workspace')
    return f'{archive}\nThis zip holds all personal data; keep it somewhere private and delete old copies you no longer need.'

def export_file(root, a):
    source = Path(a.file).resolve()
    if not source.is_relative_to((root/'workspace').resolve()) or source.suffix!='.md': raise ValueError('Export Markdown inside workspace/')
    if not shutil.which('pandoc'): raise ValueError('Pandoc is not installed. Produce the DOCX/PDF from this Markdown with your own document tools and save it beside it; or install Pandoc (brew install pandoc) and retry')
    target = source.with_suffix('.'+a.format)
    if target.exists(): raise ValueError('Export exists; preserve or rename before exporting again')
    subprocess.run(['pandoc', str(source), '-o', str(target)], check=True)
    return target

def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('init', help='create an empty private workspace'); sub.add_parser('validate', help='check IDs, evidence links, and status rules')
    sub.add_parser('render-cv', help='write workspace/master-cv.md from profile.json'); sub.add_parser('status', help='summarize the workspace and applications (creates it on first run)')
    sub.add_parser('cv-reviewed', help='record that assemble-master-cv completed a pass')
    r = sub.add_parser('refresh-snapshot', help='re-pin an application to the current profile after rechecking evidence'); r.add_argument('job', help='application folder name, e.g. acme-coordinator')
    b = sub.add_parser('backup', help='zip workspace/ to a private folder'); b.add_argument('--dest', help='backup folder (default ~/Documents/job-hunt-kit-backups)')
    a = sub.add_parser('add-sample', help='register a candidate-authored writing excerpt'); a.add_argument('file')
    for f in ['id','genre','locator']: a.add_argument('--'+f, required=True)
    a.add_argument('--authorship', choices=['candidate','mixed','unknown'], required=True)
    so = sub.add_parser('add-source', help='import an old resume, transcript, or other career document as evidence'); so.add_argument('file')
    so.add_argument('--id', required=True); so.add_argument('--kind', choices=SOURCE_KINDS, default='document'); so.add_argument('--notes')
    ai = sub.add_parser('add-interview', help='start or reopen a dated interview transcript registered as a source'); ai.add_argument('--id', help='default interview-YYYY-MM-DD')
    j = sub.add_parser('new-job', help='scaffold an application folder'); j.add_argument('company'); j.add_argument('role'); j.add_argument('--url'); j.add_argument('--description', help='text file with the posting')
    e = sub.add_parser('export', help='convert a workspace Markdown file with Pandoc'); e.add_argument('file'); e.add_argument('--format', choices=['docx','pdf'], required=True)
    args = p.parse_args()
    try:
        if args.command=='validate':
            errors = validate(ROOT)
            if errors: print('\n'.join(errors), file=sys.stderr); return 1
            result = 'Data references valid; prose and layout still require review.'
        elif args.command=='init': result = initialize(ROOT)
        elif args.command=='render-cv': result = render_cv(ROOT)
        elif args.command=='add-sample': result = add_sample(ROOT, args)
        elif args.command=='add-source': result = add_source(ROOT, args)
        elif args.command=='add-interview': result = add_interview(ROOT, args)
        elif args.command=='cv-reviewed': result = cv_reviewed(ROOT)
        elif args.command=='new-job': result = new_job(ROOT, args)
        elif args.command=='status': result = status(ROOT)
        elif args.command=='refresh-snapshot': result = refresh_snapshot(ROOT, args)
        elif args.command=='backup': result = backup(ROOT, args)
        else: result = export_file(ROOT, args)
        print(result); return 0
    except FileExistsError as exc:
        print(f'Cannot complete: {exc.args[0] if exc.args else exc}', file=sys.stderr); return 1
    except FileNotFoundError as exc:
        print(f'Cannot complete: missing file {exc.filename}', file=sys.stderr); return 1
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as exc:
        print(f'Cannot complete: {exc}', file=sys.stderr); return 1
if __name__=='__main__': raise SystemExit(main())
