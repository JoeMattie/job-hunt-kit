import argparse
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('hunt',Path(__file__).resolve().parents[1]/'scripts/hunt.py')
h=importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
class HuntTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); shutil.copytree(h.ROOT/'templates',self.root/'templates'); self.w=h.initialize(self.root)
    def job(self): return h.new_job(self.root,argparse.Namespace(company='Example',role='Coordinator',url=None,description=None))
    def test_init_preserves_candidate_edits(self):
        p=h.read(self.w/'profile.json'); p['candidate']['name']='Synthetic Candidate'; h.write(self.w/'profile.json',p)
        h.initialize(self.root); self.assertEqual(h.read(self.w/'profile.json')['candidate']['name'],'Synthetic Candidate')
    def test_empty_workspace_valid(self): self.assertEqual(h.validate(self.root),[])
    def test_packet_no_overwrite_and_stale_snapshot(self):
        self.job()
        with self.assertRaises(FileExistsError): self.job()
        p=h.read(self.w/'profile.json'); p['candidate']['name']='Changed'; h.write(self.w/'profile.json',p)
        self.assertFalse(any('profile changed' in e for e in h.validate(self.root)),'undrafted packet must not be pinned')
        folder=self.w/'applications/example-coordinator'; a=h.read(folder/'application.json')
        a['requirements']=[dict(id='r1',text='x',priority='duty',source_locator='l',claim_ids=[],gap='none yet')]; h.write(folder/'application.json',a)
        self.assertTrue(any('profile changed' in e for e in h.validate(self.root)))
    def test_sample_dedup_and_tamper(self):
        sample=self.root/'sample.txt'; sample.write_text('A synthetic professional sample.')
        a=argparse.Namespace(file=str(sample),id='one',genre='email',locator='test fixture',authorship='candidate')
        dest=h.add_sample(self.root,a)
        a.id='two'
        with self.assertRaises(ValueError): h.add_sample(self.root,a)
        dest.write_text('Changed'); self.assertTrue(any('hash' in e for e in h.validate(self.root)))
    def test_missing_evidence_and_orphan_claim(self):
        p=h.read(self.w/'profile.json'); p['claims']=[dict(id='c1',entry_id='absent',text='Synthetic claim',status='confirmed',source_refs=[])]
        h.write(self.w/'profile.json',p); errors=h.validate(self.root)
        self.assertTrue(any('Orphan' in e for e in errors)); self.assertTrue(any('lacks evidence' in e for e in errors))
    def test_ready_blocks_placeholder_and_unapproved_voice(self):
        folder=self.job(); a=h.read(folder/'application.json'); a['status']='ready'; h.write(folder/'application.json',a)
        errors=h.validate(self.root)
        for text in ['unfilled template','approved voice missing','candidate approval missing']:
            self.assertTrue(any(text in e for e in errors),errors)
    def test_cv_keeps_exhaustive_details(self):
        p=h.read(self.w/'profile.json'); p['sources']=[dict(id='s1',kind='interview',locator='answer 1')]
        p['entries']=[dict(id='e1',kind='project',organization='Personal',title='Fixture',start='2020',end=None,narrative='Long story',details={'methods':['A','B']},claim_ids=['c1'])]
        p['claims']=[dict(id='c1',entry_id='e1',text='Built a fixture',status='confirmed',source_refs=[dict(source_id='s1',locator='answer 1')])]
        h.write(self.w/'profile.json',p); self.assertEqual(h.validate(self.root),[])
        text=h.render_cv(self.root).read_text()
        for value in ['Long story','methods','Built a fixture','answer 1']: self.assertIn(value,text)
    def test_closed_packet_ignores_profile_changes_and_refresh_clears_active(self):
        folder=self.job(); a=h.read(folder/'application.json'); a['status']='closed'
        a['requirements']=[dict(id='r1',text='x',priority='required',source_locator='l',claim_ids=[],gap='g')]; h.write(folder/'application.json',a)
        p=h.read(self.w/'profile.json'); p['candidate']['name']='Changed'; h.write(self.w/'profile.json',p)
        self.assertFalse(any('profile changed' in e for e in h.validate(self.root)))
        a['status']='draft'; h.write(folder/'application.json',a)
        self.assertTrue(any('refresh-snapshot' in e for e in h.validate(self.root)))
        h.refresh_snapshot(self.root,argparse.Namespace(job=a['id'])); self.assertEqual(h.validate(self.root),[])
        with self.assertRaises(ValueError): h.refresh_snapshot(self.root,argparse.Namespace(job='nope'))
        outside=self.root/'outside'; outside.mkdir(); h.write(outside/'application.json',{'x':1})
        with self.assertRaises(ValueError): h.refresh_snapshot(self.root,argparse.Namespace(job='../../outside'))
        self.assertNotIn('profile_snapshot_sha256',h.read(outside/'application.json'))
    def test_status_and_backup(self):
        self.job(); text=h.status(self.root)
        self.assertIn('example-coordinator',text); self.assertIn('draft',text); self.assertIn('Voice: unlearned',text)
        self.assertIn('not yet',text); self.assertIn('assemble-master-cv',text); self.assertIn('build-writing-corpus',text); self.assertIn('Master CV: 1 entries',text)
        dest=self.root.parent/(self.root.name+'-backups')
        archive=Path(h.backup(self.root,argparse.Namespace(dest=str(dest))).split('\n')[0]); self.addCleanup(shutil.rmtree,dest)
        self.assertTrue(archive.is_file())
        import zipfile
        with zipfile.ZipFile(archive) as z: self.assertIn('workspace/profile.json',z.namelist())
        with self.assertRaises(ValueError): h.backup(self.root,argparse.Namespace(dest=str(self.root/'inside')))
    def test_add_source_registers_and_rejects_duplicates(self):
        doc=self.root/'old-resume.md'; doc.write_text('# Synthetic resume')
        a=argparse.Namespace(file=str(doc),id='resume-2019',kind='document',notes=None)
        dest=h.add_source(self.root,a); self.assertTrue(dest.is_file()); self.assertEqual(dest.name,'resume-2019.md')
        src=h.read(self.w/'profile.json')['sources'][0]
        self.assertEqual(src['id'],'resume-2019'); self.assertEqual(src['locator'],'sources/resume-2019.md'); self.assertEqual(h.validate(self.root),[])
        with self.assertRaises(ValueError): h.add_source(self.root,a)
    def test_neutral_voice_mode_allows_reviewed(self):
        folder=self.job(); a=h.read(folder/'application.json')
        for name in ['resume.md','cover-letter.md']: (folder/name).write_text('filled')
        p=h.read(self.w/'profile.json'); p['sources']=[dict(id='interview-2026-01-01',kind='interview',locator='sources/interview-2026-01-01.md',captured_at='x',notes='')]
        p['entries'][0]['claim_ids']=['candidate-statements-01']
        p['claims']=[dict(id='candidate-statements-01',entry_id='candidate-statements',text='Holds a driver licence',status='confirmed',source_refs=[dict(source_id='interview-2026-01-01',locator='A1')])]
        h.write(self.w/'profile.json',p)
        a.update(status='reviewed',requirements=[dict(id='r1',text='licence',priority='required',source_locator='l',claim_ids=['candidate-statements-01'],gap='')],
                 evidence=[dict(artifact='resume.md',locator='skills',claim_ids=['candidate-statements-01'])],profile_snapshot_sha256=h.sha(self.w/'profile.json'))
        a['review'].update(facts_checked=True,voice_checked=True); h.write(folder/'application.json',a)
        self.assertTrue(any('approved voice missing' in e for e in h.validate(self.root)))
        a['voice_mode']='neutral'; h.write(folder/'application.json',a); self.assertEqual(h.validate(self.root),[])
        self.assertIn('neutral voice',h.status(self.root))
    def test_readiness_requires_career_entry_and_cv_reviewed(self):
        p=h.read(self.w/'profile.json'); p['candidate']['name']='Synthetic'
        p['sources']=[dict(id='interview-2026-01-01',kind='interview',locator='sources/interview-2026-01-01.md',captured_at='x',notes='')]
        p['entries'][0]['claim_ids']=['candidate-statements-01']
        p['claims']=[dict(id='candidate-statements-01',entry_id='candidate-statements',text='Licence',status='confirmed',source_refs=[dict(source_id='interview-2026-01-01',locator='A1')])]
        h.write(self.w/'profile.json',p); self.assertEqual(h.validate(self.root),[])
        missing=h.readiness(p,h.read(self.w/'corpus.json'),h.read(self.w/'voice/profile.json'))
        self.assertTrue(any('job, project, or education' in m for m in missing)); self.assertTrue(any('cv-reviewed' in m for m in missing))
        p['entries'].append(dict(id='work-acme',kind='work',organization='Acme',title='Clerk',start='2019-fall',end='2020',location='',narrative='',details={},claim_ids=['work-acme-01']))
        p['claims'].append(dict(id='work-acme-01',entry_id='work-acme',text='Filed',status='confirmed',source_refs=[dict(source_id='interview-2026-01-01',locator='A2')]))
        h.write(self.w/'profile.json',p); h.cv_reviewed(self.root)
        self.assertEqual(h.readiness(h.read(self.w/'profile.json'),h.read(self.w/'corpus.json'),h.read(self.w/'voice/profile.json')),[])
        self.assertIn('Ready to draft applications: yes',h.status(self.root))
    def test_add_interview_idempotent(self):
        a=argparse.Namespace(id='interview-2026-01-01'); dest=h.add_interview(self.root,a); self.assertTrue(dest.is_file())
        dest.write_text(dest.read_text()+'A1: yes\n'); h.add_interview(self.root,a)
        self.assertIn('A1: yes',dest.read_text()); self.assertEqual(len(h.read(self.w/'profile.json')['sources']),1); self.assertEqual(h.validate(self.root),[])
    def test_status_creates_workspace_on_first_run(self):
        shutil.rmtree(self.w); text=h.status(self.root); self.assertIn('Workspace created',text); self.assertTrue((self.w/'profile.json').is_file())
    def test_render_cv_groups_and_collapses(self):
        p=h.read(self.w/'profile.json'); p['sources']=[dict(id='s1',kind='interview',locator='a',captured_at='x',notes='')]
        p['entries']+=[dict(id='edu-u',kind='education',organization='U',title='BS',start='2008',end='2012',location='',narrative='',details={'courses':[{'code':'A'},{'code':'B'}],'honors':['cum laude']},claim_ids=[]),
                       dict(id='work-a',kind='work',organization='A',title='Clerk',start='2016',end='2019',location='',narrative='n',details={},claim_ids=[])]
        p['open_questions']=[{'question':'Start month?','related':['work-a']}]; h.write(self.w/'profile.json',p)
        text=h.render_cv(self.root).read_text()
        self.assertLess(text.index('# Work'),text.index('# Education')); self.assertIn('courses: 2 items',text); self.assertIn('Start month? (related: work-a)',text); self.assertNotIn('"courses"',text)
        self.assertEqual(h.fmt_question({'question':'Q?','related':['a'],'resolution':'done'}),'Q? (related: a) (resolution: done)')
    def test_init_creates_inbox_and_render_names_dangling_claim(self):
        self.assertTrue((self.w/'inbox').is_dir())
        p=h.read(self.w/'profile.json'); p['entries'][0]['claim_ids']=['candidate-statements-99']; h.write(self.w/'profile.json',p)
        with self.assertRaises(ValueError) as ctx: h.render_cv(self.root)
        self.assertIn('candidate-statements lists unknown claim candidate-statements-99',str(ctx.exception))
    def test_corpus_and_voice_versions_checked(self):
        c=h.read(self.w/'corpus.json'); c['schema_version']=2; h.write(self.w/'corpus.json',c)
        v=h.read(self.w/'voice/profile.json'); del v['schema_version']; h.write(self.w/'voice/profile.json',v)
        errors=h.validate(self.root); self.assertTrue(any('corpus version' in e for e in errors)); self.assertTrue(any('voice profile version' in e for e in errors))
    def test_uninitialized_workspace_message(self):
        shutil.rmtree(self.w)
        with self.assertRaises(ValueError) as ctx: h.validate(self.root)
        self.assertIn('init',str(ctx.exception))
    def test_corpus_path_escape_rejected(self):
        h.write(self.w/'corpus.json',{'samples':[dict(id='escape',path='../outside.txt',sha256='x',approved=False,authorship='unknown')]})
        self.assertTrue(any('Unsafe' in e for e in h.validate(self.root)))
if __name__=='__main__': unittest.main()
