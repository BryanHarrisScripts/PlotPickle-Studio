import copy, json, os, pathlib, shutil, subprocess, tempfile, time, unittest, threading, urllib.request, urllib.error, http.server
from unittest.mock import patch
import editor_core as core
import editor_server as server

class TestEditing(unittest.TestCase):
    def seed(self):
        return {'schema':'plotpickle.editor-seed.v1','title':'Sample Film','source':{'projectId':'test','revision':0,'rawSha256':'0'*64},'script':[{'id':'scene-1','text':'Sea mist at dawn.','shot':1}], 'media':[{'id':'shot01','url':'https://v3b.fal.media/files/b/a/sample.mp4','requestId':'demo'}], 'clips':[{'id':'video-1','label':'Shot 01','track':'video','startFrame':0,'durationFrames':72,'mediaId':'shot01','sourceShot':1}]}
    def test_default_root_uses_localappdata_instead_of_missing_videos(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.dict(os.environ, {'LOCALAPPDATA':td}, clear=False):
                os.environ.pop('PLOTPICKLE_EDITOR_ROOT',None)
                root=server.default_media_root()
                # The default must not rely on creating a Windows Videos folder.
                if not (pathlib.Path.home()/'Videos'/'PlotPickle'/'The Third Bell'/'Editor'/'editor-draft.json').exists():
                    self.assertEqual(root, pathlib.Path(td)/'PlotPickle'/'Projects'/'The Third Bell'/'Editor')
                ed=server.Editor(root)
                self.assertTrue(ed.project_path.exists())
    def test_custom_root_override(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.dict(os.environ, {'PLOTPICKLE_EDITOR_ROOT':td, 'LOCALAPPDATA':'X:/irrelevant'}, clear=False):
                self.assertEqual(server.default_media_root(),pathlib.Path(td))
    def test_launcher_checks_supported_python_before_start(self):
        cmd=(pathlib.Path(__file__).with_name('Start-PlotPickle-Editor.cmd')).read_text()
        self.assertIn('py -%%V -c',cmd)
        self.assertNotIn('py -3 "%~dp0editor_server.py"',cmd)
        self.assertIn('LOCALAPPDATA',cmd)
        self.assertIn('PLOTPICKLE_EDITOR_ROOT',cmd)
    def test_seed(self):
        p=core.initial(self.seed()); self.assertEqual(p['revision'],0);self.assertEqual(p['tracks']['video'][0]['durationFrames'],72);self.assertFalse(p['source']['nativePpfModified'])
    def test_provider_url_security(self):
        for url in ['http://v3b.fal.media/files/b/a.mp4','https://evil.test/files/a.mp4','https://v3b.fal.media.evil.test/files/a.mp4','https://v3b.fal.media@evil.test/files/a.mp4','https://v3b.fal.media/files/a.mov','https://v3b.fal.media/files/a.mp4?q=abc','file:///C:/stuff.mp4','https://127.0.0.1/files/a.mp4']:
            with self.subTest(url=url),self.assertRaises(core.EditError):core.fal_media_url(url)
        self.assertEqual(core.fal_media_url('https://v3b.fal.media/files/b/a.mp4'),'https://v3b.fal.media/files/b/a.mp4')
    def test_revisions_undo_and_native_truth(self):
        with tempfile.TemporaryDirectory() as td:
            seed=pathlib.Path(td)/'seed.json';seed.write_text(json.dumps(self.seed()));e=server.Editor(pathlib.Path(td)/'vault',seed)
            r=e.edit({'expectedRevision':0,'track':'video','id':'video-1','operation':'change','startFrame':12,'durationFrames':48})
            self.assertEqual(r['revision'],1);self.assertEqual(r['tracks']['video'][0]['startFrame'],12)
            self.assertFalse(r['draftApproved']);self.assertFalse(r['source']['nativePpfModified'])
            with self.assertRaises(core.EditError):e.edit({'expectedRevision':0,'track':'video','id':'video-1','operation':'change','startFrame':10})
            old=e.undo(1);self.assertEqual(old['tracks']['video'][0]['startFrame'],0);self.assertEqual(old['revision'],2)
            e2=server.Editor(pathlib.Path(td)/'vault');self.assertEqual(e2.state()['revision'],2)
    def test_verified_media_preview_is_private_and_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            folder=pathlib.Path(td)
            seed=folder/'seed.json';seed.write_text(json.dumps(self.seed()))
            app=server.Editor(folder/'vault',seed)
            original=app.media/'shot01-original.mp4'
            original.write_bytes(b'ORIGINAL_PLACEHOLDER')
            video=app.media/'shot01-24fps.mp4'
            video.write_bytes(b'LOCAL_PREVIEW_PLACEHOLDER')
            app.p['media']['shot01'].update({
                'status':'verified-draft', 'path':'media/shot01-24fps.mp4',
                'originalPath':'media/shot01-original.mp4', 'sha256':core.sha(video),
                'fps':24, 'frames':72
            })
            app.p['job']={'state':'complete','mediaId':'shot01','verified':True}
            app._save()
            p=app.state(); m=p['media']['shot01']
            self.assertEqual(p['revision'],0)
            self.assertTrue(m['previewAvailable'])
            self.assertEqual(m['previewUrl'],'/media/shot01-24fps.mp4')
            for key in ('path','originalPath','originUrl'):
                self.assertNotIn(key,m)
            reopened=server.Editor(folder/'vault')
            self.assertEqual(reopened.state()['media']['shot01']['previewUrl'],'/media/shot01-24fps.mp4')
            self.assertFalse(reopened.state()['source']['nativePpfModified'])
            httpd=http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
            httpd.editor=reopened
            thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start()
            try:
                base=f'http://127.0.0.1:{httpd.server_port}'
                with urllib.request.urlopen(base+'/api/project') as response:
                    http_state=json.loads(response.read())
                self.assertEqual(http_state['media']['shot01']['previewUrl'],'/media/shot01-24fps.mp4')
                with urllib.request.urlopen(base+'/media/shot01-24fps.mp4') as response:
                    self.assertEqual(response.read(),b'LOCAL_PREVIEW_PLACEHOLDER')
                    self.assertEqual(response.headers['Content-Type'],'video/mp4')
            finally:
                httpd.shutdown();httpd.server_close()
            video.unlink()
            missing=reopened.state()['media']['shot01']
            self.assertFalse(missing['previewAvailable'])
            self.assertNotIn('previewUrl',missing)
            self.assertEqual(reopened.state()['revision'],0)

    def test_browser_script_must_not_depend_on_private_media_paths(self):
        script=pathlib.Path(__file__).with_name('app.js').read_text(encoding='utf-8')
        self.assertNotIn('.path.split(',script)
        self.assertIn('previewUrl',script)
        self.assertIn('previewAvailable',script)
    def test_edits_validate(self):
        p=core.initial(self.seed())
        for event in [{'operation':'change','id':'video-1','startFrame':-1},{'operation':'change','id':'video-1','durationFrames':0},{'operation':'change','id':'video-1','gainDb':-90},{'operation':'add','clip':{'id':'video-1','startFrame':1,'durationFrames':1}},{'operation':'remove','id':'nope'}]:
            with self.subTest(event=event),self.assertRaises(core.EditError):core.apply_edit(p,dict(event,expectedRevision=0,track='video'))
        self.assertEqual(p['revision'],0)
    def test_local_api_and_origin_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            td=pathlib.Path(td);seed=td/'seed.json';seed.write_text(json.dumps(self.seed()))
            app=server.Editor(td/'vault',seed)
            httpd=http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);httpd.editor=app
            thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start()
            try:
                base=f'http://127.0.0.1:{httpd.server_port}'
                with urllib.request.urlopen(base+'/api/health') as res:
                    self.assertEqual(json.loads(res.read())['status'],'local-only')
                body=json.dumps({'expectedRevision':0,'track':'video','operation':'change','id':'video-1','startFrame':3}).encode()
                good=urllib.request.Request(base+'/api/edit',data=body,headers={'Content-Type':'application/json','Origin':base,'X-PlotPickle-Local':'editor-v1'})
                with urllib.request.urlopen(good) as res:self.assertEqual(json.loads(res.read())['revision'],1)
                bad=urllib.request.Request(base+'/api/edit',data=body,headers={'Content-Type':'application/json','Origin':'https://unrelated.example','X-PlotPickle-Local':'editor-v1'})
                with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(bad)
                self.assertEqual(app.state()['revision'],1)
            finally:httpd.shutdown();httpd.server_close()
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'No FFmpeg')
    def test_real_conform_and_silent_render(self):
        with tempfile.TemporaryDirectory() as td:
            td=pathlib.Path(td)
            src=td/'source.mp4';out=td/'target.mp4'
            server.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','testsrc2=s=320x180:r=30:d=3', '-c:v','libx264','-pix_fmt','yuv420p',str(src)])
            fact=server.conform(src,out,72)
            self.assertEqual((fact['fps'],fact['frames'],fact['durationSeconds']),(24,72,3.0));self.assertTrue(fact['fullDecodeVerified'])
            seed=td/'seed.json';seed.write_text(json.dumps(self.seed()))
            app=server.Editor(td/'vault',seed)
            m=app.p['media']['shot01'];target=app.media/'shot01-24fps.mp4';shutil.copyfile(out,target)
            m.update({'path':'media/shot01-24fps.mp4','status':'verified-draft','sha256':core.sha(target)})
            app._save();job=app.render(0);self.assertEqual(job['state'],'rendering')
            for _ in range(200):
                if not app.busy:break
                time.sleep(.05)
            self.assertEqual(app.p['job']['state'],'render-complete',app.p['job']);self.assertEqual(app.p['job']['verification']['frames'],72)
            self.assertEqual((td/'vault'/app.p['job']['resultPath']).stat().st_size>1000,True)

if __name__=='__main__':unittest.main(verbosity=2)
