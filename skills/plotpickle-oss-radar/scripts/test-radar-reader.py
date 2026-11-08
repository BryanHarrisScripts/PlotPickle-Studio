#!/usr/bin/env python3
import datetime as dt
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

mod_path=Path(__file__).parent/'radar-reader.py'
spec=importlib.util.spec_from_file_location('radar_reader',mod_path)
radar=importlib.util.module_from_spec(spec)
spec.loader.exec_module(radar)

class ReadTests(unittest.TestCase):
    def issue(self,num=3364):
        return {'title':'[OSS RADAR] November 2026','number':num,'html_url':f'https://github.com/BryanHarrisScripts/PlotPickle/issues/{num}'}
    def comment(self,day,url=None):
        return {'html_url':url or 'https://github.com/BryanHarrisScripts/PlotPickle/issues/3364#issuecomment-42',
                'body':f'<!-- PLOTPICKLE-OSS-RADAR-DAY:{day} -->\n## OSS Radar — {day}\n## Findings\nResearch only'}
    def test_latest_not_comment_order(self):
        result=radar.latest_from_bundles([(self.issue(),[self.comment('2026-11-06'),self.comment('2026-11-04')])],dt.date(2026,11,7))
        self.assertEqual(result['reportDate'],'2026-11-06')
        self.assertEqual(result['ageDays'],1)
        self.assertEqual(result['workflowHealth'],'not-checked')
    def test_future_and_foreign_rejected(self):
        comments=[self.comment('2026-11-09'), self.comment('2026-11-06','https://example.com/fake')]
        result=radar.latest_from_bundles([(self.issue(),comments)],dt.date(2026,11,7))
        self.assertEqual(result['status'],'unavailable')
    def test_mismatched_header_rejected(self):
        bad=self.comment('2026-11-06');bad['body']=bad['body'].replace('## OSS Radar — 2026-11-06','## OSS Radar — 2026-11-05')
        self.assertEqual(radar.latest_from_bundles([(self.issue(),[bad])],dt.date(2026,11,7))['status'],'unavailable')
    def test_other_project_rejected(self):
        bad=self.issue();bad['html_url']='https://github.com/Someone/Other/issues/3364'
        self.assertEqual(radar.latest_from_bundles([(bad,[self.comment('2026-11-06')])],dt.date(2026,11,7))['status'],'unavailable')

if __name__=='__main__': unittest.main()
