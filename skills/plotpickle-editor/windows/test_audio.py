import json
import math
import http.server
import threading
import urllib.request
import urllib.error
import pathlib
import shutil
import struct
import tempfile
import time
import unittest
import wave
from unittest.mock import patch
import editor_audio as aud
import editor_core as core
import editor_server as server

HERE=pathlib.Path(__file__).resolve().parent
SEED=HERE/'the-third-bell-seed.json'

def wait(app):
    for _ in range(200):
        if not app.busy:return
        time.sleep(.07)
    raise AssertionError('Timed out waiting for local render')

def levels(path):
    raw=server.subprocess.run(['ffmpeg','-v','error','-i',str(path),'-vn','-ac','1','-ar','8000',
      '-f','s16le','pipe:1'],check=True,capture_output=True).stdout
    vals=struct.unpack('<'+'h'*(len(raw)//2),raw)
    if not vals:return 0.0
    return math.sqrt(sum((x/32768)**2 for x in vals)/len(vals))

class TestAudio(unittest.TestCase):
    def new_editor(self):
        td=tempfile.TemporaryDirectory();folder=pathlib.Path(td.name)
        e=server.Editor(folder/'vault',SEED)
        return td, e
    def test_upgrade_preserves_existing_draft_and_seed_state(self):
        td,e=self.new_editor()
        try:
            self.assertEqual(e.p['revision'],0)
            self.assertFalse(e.p['source']['nativePpfModified'])
            self.assertEqual(e.p['tracks']['ambience'][0]['audioId'],'demo-ocean')
            self.assertEqual(e.p['tracks']['foley'][0]['audioId'],'demo-gulls')
            self.assertEqual(set(e.p['audioAssets']),{'demo-ocean','demo-gulls'})
            for aid in e.p['audioAssets']:
                with wave.open(str(e._audio_path(aid))) as f:
                    self.assertEqual((f.getframerate(),f.getnchannels()),(48000,2))
            before=e.p['revision']; e2=server.Editor(e.root)
            self.assertEqual(e2.p['revision'],before)
            e2.edit({'operation':'remove','track':'foley','id':'foley-01','expectedRevision':before})
            e3=server.Editor(e.root)
            self.assertEqual(e3.p['tracks']['foley'],[])
            self.assertEqual(e3.p['revision'],1)
        finally:td.cleanup()
    def test_path_not_in_public_state(self):
        td,e=self.new_editor()
        try:
            pub=e.state()
            self.assertFalse(pub['source']['nativePpfModified'])
            self.assertTrue(pub['audioAssets']['demo-ocean']['demo'])
            self.assertNotIn('path',pub['audioAssets']['demo-ocean'])
        finally:td.cleanup()
    def test_audio_filter_math_frame_alignment(self):
        c=[{'input_index':1,'startFrame':24,'durationFrames':48,'gainDb':-6},
           {'input_index':2,'startFrame':0,'durationFrames':72,'gainDb':-12}]
        spec=aud.audio_filter_spec(c,72)
        self.assertIn('adelay=48000S|48000S',spec)
        self.assertIn('atrim=end_sample=96000',spec)
        self.assertIn('whole_len=144000',spec)
        self.assertIsNone(aud.audio_filter_spec([],72))
    def test_unknown_audio_asset_rejected(self):
        td,e=self.new_editor()
        try:
            with self.assertRaises(core.EditError): e.edit({'expectedRevision':0,'track':'foley','id':'foley-01','operation':'change','audioId':'not-real'})
            with self.assertRaises(core.EditError): e.edit({'expectedRevision':0,'track':'video','id':'video-01','operation':'change','audioId':'demo-gulls'})
            with self.assertRaises(core.EditError): e.edit({'expectedRevision':0,'track':'foley','id':'foley-01','operation':'change','muted':'no'})
        finally:td.cleanup()
    def test_audio_upload_revisioned_and_private(self):
        td,e=self.new_editor()
        try:
            inputfile=e._audio_path('demo-gulls')
            raw=inputfile.read_bytes()
            pub=e.attach_audio('foley','foley-01',0,raw)
            self.assertEqual(pub['revision'],1)
            asset_id=e.p['tracks']['foley'][0]['audioId']
            self.assertTrue(asset_id.startswith('user-'))
            self.assertFalse(e.p['audioAssets'][asset_id]['demo'])
            self.assertTrue(e._audio_path(asset_id).is_file())
            with self.assertRaises(core.EditError): e.attach_audio('foley','foley-01',0,raw)
            with self.assertRaises(core.EditError): e.attach_audio('foley','foley-01',1,b'NOT_A_WAV')
            self.assertFalse(e.p['source']['nativePpfModified'])
        finally:td.cleanup()
    def test_localhost_audio_upload_requires_correct_origin_and_revision(self):
        td,e=self.new_editor()
        httpd=http.server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);httpd.editor=e
        worker=threading.Thread(target=httpd.serve_forever,daemon=True);worker.start()
        try:
            base=f'http://127.0.0.1:{httpd.server_port}'
            payload=e._audio_path('demo-gulls').read_bytes()
            headers={'Content-Type':'audio/wav','Origin':base,'X-PlotPickle-Local':'editor-v1',
                'X-PlotPickle-Track':'foley','X-PlotPickle-Clip':'foley-01','X-PlotPickle-Revision':'0'}
            req=urllib.request.Request(base+'/api/audio-upload',data=payload,headers=headers)
            with urllib.request.urlopen(req) as res:
                state=json.loads(res.read())
            self.assertEqual(state['revision'],1)
            self.assertTrue(state['tracks']['foley'][0]['audioId'].startswith('user-'))
            with self.assertRaises(urllib.error.HTTPError):
                urllib.request.urlopen(urllib.request.Request(base+'/api/audio-upload',data=payload,headers=headers))
            headers['X-PlotPickle-Revision']='1';headers['Origin']='https://evil.invalid'
            with self.assertRaises(urllib.error.HTTPError):
                urllib.request.urlopen(urllib.request.Request(base+'/api/audio-upload',data=payload,headers=headers))
            self.assertEqual(e.state()['revision'],1)
        finally:
            httpd.shutdown();httpd.server_close();td.cleanup()

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'ffmpeg required')
    def test_real_mixed_render_revisions_and_mute(self):
        td,e=self.new_editor()
        try:
            source=pathlib.Path(td.name)/'sample30.mp4';conformed=e.media/'shot01-24fps.mp4'
            server.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','testsrc2=s=320x180:r=30:d=3',
                        '-c:v','libx264','-pix_fmt','yuv420p',str(source)])
            server.conform(source,conformed,72)
            e.p['media']['shot01'].update({'path':'media/shot01-24fps.mp4','status':'verified-draft',
                                             'sha256':core.sha(conformed),'fps':24,'frames':72})
            e._save()
            self.assertEqual(e.render(0)['state'],'rendering');wait(e)
            self.assertEqual(e.p['job']['state'],'render-complete',e.p['job'])
            result=e.root/e.p['job']['resultPath']
            self.assertTrue(result.is_file())
            stat=server.framecheck(result,72)
            self.assertEqual((stat['frames'],stat['fps']),(72,24))
            metadata,_=server.probe(result)
            audio=next(x for x in metadata['streams'] if x.get('codec_type')=='audio')
            self.assertEqual(audio['sample_rate'],'48000')
            self.assertEqual(e.p['job']['verification']['audio']['mixedCueCount'],2)
            self.assertGreater(levels(result),.003)
            preview=e.state()['job']['previewUrl']
            self.assertTrue(preview.startswith('/render/draft-revision-'))
            e.edit({'operation':'change','track':'foley','id':'foley-01','expectedRevision':0,'muted':True})
            self.assertNotIn('previewUrl',e.state()['job'])
            e.edit({'operation':'change','track':'ambience','id':'ambience-01','expectedRevision':1,'muted':True})
            self.assertEqual(e.render(2)['state'],'rendering');wait(e)
            self.assertEqual(e.p['job']['state'],'render-complete',e.p['job'])
            self.assertEqual(e.p['job']['verification']['audio']['mixedCueCount'],0)
            self.assertLess(levels(e.root/e.p['job']['resultPath']),.0002)
            self.assertTrue((e.renders/'draft-revision-0000.mp4').exists())
            self.assertTrue((e.renders/'draft-revision-0002.mp4').exists())
        finally:td.cleanup()
    def test_unbound_audio_cue_not_claimed_as_mixed(self):
        td,e=self.new_editor()
        try:
            e.edit({'operation':'add','track':'music','expectedRevision':0,'clip':{'id':'music-test','label':'No source yet','startFrame':0,'durationFrames':72,'gainDb':0,'audioId':None}})
            self.assertIsNone(e.p['tracks']['music'][0]['audioId'])
        finally:td.cleanup()

if __name__=='__main__':unittest.main(verbosity=2)
