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
        folder=self.job(); a=h.read(folder/'application.json'); a['status']='closed'; h.write(folder/'application.json',a)
        p=h.read(self.w/'profile.json'); p['candidate']['name']='Changed'; h.write(self.w/'profile.json',p)
        self.assertFalse(any('profile changed' in e for e in h.validate(self.root)))
        a['status']='draft'; h.write(folder/'application.json',a)
        self.assertTrue(any('refresh-snapshot' in e for e in h.validate(self.root)))
        h.refresh_snapshot(self.root,argparse.Namespace(job=a['id'])); self.assertEqual(h.validate(self.root),[])
        with self.assertRaises(ValueError): h.refresh_snapshot(self.root,argparse.Namespace(job='nope'))
    def test_status_and_backup(self):
        self.job(); text=h.status(self.root)
        self.assertIn('example-coordinator',text); self.assertIn('draft',text); self.assertIn('Voice: unlearned',text)
        self.assertIn('not yet',text); self.assertIn('assemble-master-cv',text); self.assertIn('learn-candidate-voice',text)
        dest=self.root.parent/(self.root.name+'-backups')
        archive=Path(h.backup(self.root,argparse.Namespace(dest=str(dest))).split('\n')[0]); self.addCleanup(shutil.rmtree,dest)
        self.assertTrue(archive.is_file())
        import zipfile
        with zipfile.ZipFile(archive) as z: self.assertIn('workspace/profile.json',z.namelist())
        with self.assertRaises(ValueError): h.backup(self.root,argparse.Namespace(dest=str(self.root/'inside')))
    def test_uninitialized_workspace_message(self):
        shutil.rmtree(self.w)
        with self.assertRaises(ValueError) as ctx: h.validate(self.root)
        self.assertIn('init',str(ctx.exception))
    def test_corpus_path_escape_rejected(self):
        h.write(self.w/'corpus.json',{'samples':[dict(id='escape',path='../outside.txt',sha256='x',approved=False,authorship='unknown')]})
        self.assertTrue(any('Unsafe' in e for e in h.validate(self.root)))
if __name__=='__main__': unittest.main()
