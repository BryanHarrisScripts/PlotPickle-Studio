#!/usr/bin/env python3
import json, unittest
from pathlib import Path
from resolve_surface import resolve
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'references/registry.v1.json').read_text(encoding='utf-8'))
class TestSurfaceLibrary(unittest.TestCase):
    def test_release(self):
        self.assertEqual(DATA['pluginRelease'],'2.0.40')
        self.assertEqual(DATA['libraryVersion'],'1.0.0')
        self.assertFalse(DATA['privateUserDataBundled'])
    def test_five_main_cards_order(self):
        self.assertEqual(DATA['lockedHomeOrder'],['MEET_ELARA','LEARN','STORYBOARD','LIBRARY_YOUR_STORIES','CONNECTED_SERVICES'])
        self.assertEqual(DATA['lockedHomeOrder'].index('LIBRARY_YOUR_STORIES'),3)
    def test_home_skin_v2_authority(self):
        self.assertEqual(DATA['surfaces']['HOME']['authority'],'PP-SKIN-V2-HOME-LOCK-2026-11-13-01')
        self.assertEqual(DATA['surfaces']['HOME']['approval'],'owner-locked')
    def test_alias_parity(self):
        for alias in ['Home','Studio','Open Studio','Open Studio HOME','/home']:
            self.assertEqual(resolve(alias)['surfaceId'],'HOME')
    def test_five_named_surface_templates(self):
        self.assertEqual(set(DATA['surfaces']),{'HOME','STORYBOARD','LIBRARY_YOUR_STORIES','REVIEW','EDITOR'})
        for sid,s in DATA['surfaces'].items():
            with self.subTest(surface=sid):
                self.assertTrue((ROOT/s['template']).is_file())
                self.assertTrue((ROOT/s['spec']).is_file())
                self.assertTrue(s['readOnlyEntry'])
                self.assertIn('studio', ' '.join(s['dataSources']).lower())
    def test_editor_not_locked(self):
        self.assertEqual(DATA['surfaces']['EDITOR']['approval'],'registered-draft-not-visually-locked')
        self.assertIsNone(DATA['surfaces']['EDITOR']['authority'])
    def test_no_unintended_data(self):
        for sid,s in DATA['surfaces'].items():
            template=(ROOT/s['template']).read_text(encoding='utf-8')
            self.assertNotIn('The Third Bell',template)
            self.assertNotIn('fa34674',template)
            self.assertNotIn('app://',template)
            self.assertIn('```jsx',template)
            self.assertIn('GenUI.issueNewTurn(',template)
    def test_real_backend_gating(self):
        self.assertIn('studio_list_projects',DATA['surfaces']['LIBRARY_YOUR_STORIES']['dataSources'])
        self.assertIn('studio_get_image',DATA['surfaces']['REVIEW']['dataSources'])
        self.assertIn('studio_get_state',DATA['surfaces']['EDITOR']['dataSources'])
    def test_no_parallel_engine(self):
        self.assertIn('one plugin',DATA['identity'])
        self.assertEqual(DATA['transport'],'existing authenticated PlotPickle Studio MCP; no new backend')
    def test_resolver(self):
        self.assertEqual(resolve('REVIEW')['route'],'HOME/STORYBOARD/REVIEW')
        self.assertTrue(resolve('HOME')['readOnlyEntry'])
if __name__=='__main__':unittest.main(verbosity=2)
