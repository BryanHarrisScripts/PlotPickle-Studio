#!/usr/bin/env python3
import copy
import json
import unittest
from release_lock import INDEX, load, validate, append, stamp, check_lock


class ReleaseLockTests(unittest.TestCase):
    def setUp(self):
        self.idx = load(INDEX)

    def test_index_valid(self):
        self.assertTrue(validate(self.idx))

    def test_no_archives_or_story_media(self):
        p = self.idx['storagePolicy']
        self.assertEqual(p['customArchivesPerRelease'], 0)
        self.assertFalse(p['bundlePrivateProjectAssets'])

    def test_locked_surface_reference_preserved(self):
        self.assertIn('PP-SKIN-V2-HOME-LOCK-2026-11-13-01', self.idx['releases'][0]['surfaceLockRefs'])

    def test_candidate_cannot_deploy(self):
        with self.assertRaises(ValueError):
            check_lock(self.idx['releases'][0])

    def test_changed_record_detected(self):
        x = copy.deepcopy(self.idx)
        x['releases'][0]['surfaceLockRefs'] = []
        with self.assertRaises(ValueError):
            validate(x)

    def test_duplicate_refused(self):
        with self.assertRaises(ValueError):
            append(self.idx, self.idx['releases'][0])

    def test_append_new_draft(self):
        x = {k:v for k,v in self.idx['releases'][0].items() if k != 'recordDigest'}
        major, minor, patch = map(int, self.idx['currentVersion'].split('.'))
        version = f'{major}.{minor}.{patch + 1}'
        x.update(version=version, state='DRAFT')
        updated = append(self.idx,x)
        self.assertEqual(updated['currentVersion'], version)
        self.assertEqual(updated['releases'][:-1], self.idx['releases'])
        self.assertEqual(updated['releases'][0], self.idx['releases'][0])
        self.assertTrue(validate(updated))

    def test_claimed_patent_filing_requires_evidence(self):
        x = copy.deepcopy(self.idx)
        x['releases'][0]['patentFilingRefs']=[{'id':'PAT-01'}]
        x['releases'][0]['recordDigest']=stamp(x['releases'][0])
        with self.assertRaises(ValueError):
            validate(x)


if __name__ == '__main__':
    unittest.main(verbosity=2)
