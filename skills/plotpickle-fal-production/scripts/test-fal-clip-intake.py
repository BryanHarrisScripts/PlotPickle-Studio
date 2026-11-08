#!/usr/bin/env python3
"""Executable integration tests for offline intake; uses synthetic media, no fal charges."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
SCRIPT=HERE/'fal-clip-intake.py'

class TestIntake(unittest.TestCase):
  def test_one_shot_success_and_fail_closed(self):
    with tempfile.TemporaryDirectory() as td:
      root=Path(td)
      project={'id':'test-project','title':'Test Story','revision':3,
               'sourceEvidence':{'screenplay':{'passages':[{'id':'p1','text':'EXT. SEA - DAWN'}]}},
               'assetRegistry':{'extensions':{'storyWorkflow':{'imageMappings':[
                 {'artifactId':'still1','address':{'actNumber':1,'sequenceNumber':1,'blockNumber':1,
                    'miniBlockNumber':1,'shotNumber':1},'passageIds':['p1'],'sha256':'a'*64,
                  'portablePath':'assets/frame.webp','savedMarkerPresent':False,'locked':False}]}}}}
      project_path=root/'project.json';project_path.write_text(json.dumps(project))
      project_sha=hashlib.sha256(project_path.read_bytes()).hexdigest()
      src=root/'test-video.mp4'
      subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i',
           'testsrc2=size=320x180:rate=30:duration=3', '-an','-c:v','libx264','-pix_fmt','yuv420p',str(src)],check=True)
      result={'status':'COMPLETED','endpoint_id':'alibaba/wan-3.0-prime/image-to-video',
              'request_id':'test-job','result':{'video':{'url':'https://v3b.fal.media/files/abc/def.mp4',
                'width':320,'height':180,'file_size':src.stat().st_size},'seed':123}}
      result_path=root/'fal-result.json';result_path.write_text(json.dumps(result))
      out=root/'draft'
      base=['python3',str(SCRIPT),'--project',str(project_path),'--result',str(result_path),
            '--out',str(out),'--video',str(src),'--block','1','--mini','1','--shot','1',
            '--expected-project-sha',project_sha]
      p=subprocess.run(base,text=True,capture_output=True)
      self.assertEqual(p.returncode,0,p.stderr)
      r=json.loads((out/'draft-receipt.json').read_text())
      self.assertEqual(r['editorialVideo']['frames'],72)
      self.assertEqual(r['editorialVideo']['fps'],24)
      self.assertEqual(r['registration'],'verified-draft-sidecar')
      self.assertTrue(r['editorialVideo']['fullDecodePassed'])
      self.assertFalse(r['review']['nativePPFModified'])
      self.assertFalse(r['review']['accepted'])
      self.assertFalse(r['source']['sameFrameAsNativePPFMappingVerified'])
      self.assertEqual(hashlib.sha256(project_path.read_bytes()).hexdigest(),project_sha)
      self.assertNotEqual(hashlib.sha256((out/'draft-24fps.mp4').read_bytes()).hexdigest(),hashlib.sha256(src.read_bytes()).hexdigest())
      p=subprocess.run(base,text=True,capture_output=True)
      self.assertNotEqual(p.returncode,0,'must refuse overwrite')
      self.assertTrue((out/'draft-receipt.json').exists())
      p=subprocess.run(base[:-2]+['--expected-project-sha','f'*64],text=True,capture_output=True)
      self.assertNotEqual(p.returncode,0)
  def test_no_spend_no_external_submissions(self):
    s=SCRIPT.read_text()
    self.assertNotIn('fal_client.submit',s)
    self.assertNotIn('api_key',s)
    self.assertIn('nativePPFModified',s)
    self.assertIn('UNRECOGNIZED_FAL_MEDIA_HOST',s)

if __name__=='__main__': unittest.main(verbosity=2)
