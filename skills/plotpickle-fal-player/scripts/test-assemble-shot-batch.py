"""Offline synthetic acceptance for verified 3-shot editorial export. No network, no spend."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
SCRIPT=HERE/'assemble-shot-batch.py'


class TestShotBatch(unittest.TestCase):
    def test_three_shots_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            ppf={'id':'synthetic-ppf','revision':3,'title':'Synthetic test',
                 'sourceEvidence':{'screenplay':{'passages':[{'id':f'passage-{n}'} for n in range(1,4)]}},
                 'assetRegistry':{'extensions':{'storyWorkflow':{'imageMappings':[
                   {'artifactId':f'still-{n}', 'address':{'actNumber':1,'sequenceNumber':1,'blockNumber':1,
                    'miniBlockNumber':1,'shotNumber':n},'passageIds':[f'passage-{n}'],
                    'sha256':'a'*64,'savedMarkerPresent':n==1,'locked':n==1}
                   for n in range(1,4)]}}}}
            p=root/'project.ppf.json';p.write_text(json.dumps(ppf));raw=hashlib.sha256(p.read_bytes()).hexdigest()
            rows=[]
            for n in range(1,4):
                fn=f'input-{n:02d}.mp4';target=root/fn
                subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi',
                    '-i',f'testsrc2=size=160x90:rate=30:duration=3',
                    '-c:v','libx264','-pix_fmt','yuv420p','-an',str(target)],check=True)
                rows.append({'shot':n,'status':'completed-provider-video',
                             'endpointId':'test-fal-ivt','requestId':f'synth-{n}',
                             'url':f'https://v3b.fal.media/files/testing/{n}.mp4',
                             'file':fn,'reportedBytes':target.stat().st_size})
            m={'schema':'plotpickle.fal-shot-batch.v1','projectId':'synthetic-ppf',
               'revision':3,'rawSha256':raw,'block':1,'miniBlock':1,'shots':rows}
            mp=root/'manifest.json';mp.write_text(json.dumps(m))
            args=[sys.executable,str(SCRIPT),'--project',str(p),'--manifest',str(mp),
                  '--video-root',str(root),'--out',str(root/'output')]
            r=subprocess.run(args,text=True,capture_output=True)
            self.assertEqual(r.returncode,0,r.stderr)
            receipt=json.loads((root/'output'/'draft-receipt.json').read_text())
            self.assertEqual(receipt['combined']['facts']['frames'],216)
            self.assertEqual(receipt['combined']['facts']['fps'],24)
            self.assertEqual([x['startFrame'] for x in receipt['shots']],[0,72,144])
            self.assertEqual([x['source']['stillLocked'] for x in receipt['shots']],[True,False,False])
            self.assertFalse(receipt['review']['nativePpfModified'])
            self.assertFalse(receipt['review']['localEditorImported'])
            self.assertEqual(raw,hashlib.sha256(p.read_bytes()).hexdigest())
            # Refuse overwrite and stale source, without changing previous verified outputs.
            r=subprocess.run(args,text=True,capture_output=True)
            self.assertNotEqual(r.returncode,0)
            m['rawSha256']='0'*64;mp.write_text(json.dumps(m));
            r=subprocess.run(args[:-1]+[str(root/'rejected')],text=True,capture_output=True)
            self.assertNotEqual(r.returncode,0)
            self.assertFalse((root/'rejected').exists())
            # No endpoint submission or direct network transfer belongs to the offline helper.
            script=SCRIPT.read_text()
            self.assertNotIn('fal_client',script)
            self.assertNotIn('urllib.request',script)

if __name__=='__main__':unittest.main(verbosity=2)
