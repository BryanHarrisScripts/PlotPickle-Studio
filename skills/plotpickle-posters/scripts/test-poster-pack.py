#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).with_name('poster-pack.py')
spec = importlib.util.spec_from_file_location('poster_pack', MODULE)
poster = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poster)

class PosterTests(unittest.TestCase):
    def test_four_formats_and_names(self):
        with tempfile.TemporaryDirectory() as d:
            brief = Path(d)/'brief.json'
            brief.write_text('{}')
            plan = poster.plan({'title':'Brotherly Love','tagline':'A test','posterType':'teaser'},brief)
            self.assertEqual([(x['id'],x['width'],x['height']) for x in plan['outputs']],
                [('theatrical',1620,2400),('square',1080,1080),('portrait-feed',1080,1350),('story-reel',1080,1920)])
            self.assertEqual(plan['source']['status'],'unbound-proposal')
            self.assertFalse(plan['exportsArePrintReady'])
            self.assertTrue(all(x['status']=='planned' for x in plan['outputs']))
            self.assertEqual(len(plan['curriculumReferences']),6)
            self.assertIn('1080x1920',plan['outputs'][-1]['filename'])

    def test_source_hash_and_identity(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)
            content=json.dumps({'id':'project-1','revision':5})
            p=folder/'story.ppf.json';p.write_text(content)
            b=folder/'brief.json';b.write_text('{}')
            source={'file':p.name,'sha256':hashlib.sha256(content.encode()).hexdigest(),'projectId':'project-1','revision':5}
            self.assertEqual(poster.plan({'title':'A','source':source},b)['source']['status'],'source-bytes-verified')
            source['revision']=6
            with self.assertRaises(poster.CampaignError):poster.plan({'title':'A','source':source},b)
            source['revision']=5;source['sha256']='0'*64
            with self.assertRaises(poster.CampaignError):poster.plan({'title':'A','source':source},b)

    def test_no_overwrite_and_missing_images(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);b=folder/'b.json';b.write_text('{}')
            data=poster.plan({'title':'Film'},b)
            out=folder/'p.json'
            poster.save_new_json(out,data)
            with self.assertRaises(FileExistsError): poster.save_new_json(out,data)
            audit=poster.inspect(data,folder)
            self.assertFalse(audit['allBytesVerified'])
            self.assertEqual([x['status'] for x in audit['outputs']],['missing']*4)

    def test_bad_media_fails_and_source_does_not_get_written(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);b=folder/'b.json';b.write_text('{}')
            data=poster.plan({'title':'Movie'},b)
            (folder/data['outputs'][0]['filename']).write_bytes(b'not a png')
            audit=poster.inspect(data,folder)
            self.assertEqual(audit['outputs'][0]['status'],'invalid')
            self.assertEqual(audit['outputs'][1]['status'],'missing')

    def test_bad_brief_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            b=Path(d)/'b.json';b.write_text('{}')
            for wrong in ({'title':''},{'title':'A','posterType':'fantasy'},{'title':'A','madeUpField':1}):
                with self.assertRaises(poster.CampaignError):poster.plan(wrong,b)

    def test_schema_and_lesson_map(self):
        for filename in ('poster-campaign.v1.schema.json','poster-pack.v1.schema.json'):
            d=json.loads((MODULE.parent.parent/'schemas'/filename).read_text())
            self.assertTrue(d['$schema'].endswith('/2020-12/schema'))
        refs=poster.lesson_refs()
        self.assertEqual([(x['topic'],x['number']) for x in refs],
                         [('foundations',1),('foundations',15),('theme',16),('visual-storytelling',17),('revision',42),('industry',46)])

if __name__ == '__main__':
    unittest.main()
