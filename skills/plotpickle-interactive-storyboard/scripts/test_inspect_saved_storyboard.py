#!/usr/bin/env python3
"""No private stories or media are included in this plugin test."""
import hashlib
import json
import unittest
from inspect_saved_storyboard import extract_source_snapshot, ReviewSourceError


def fixture():
    return json.dumps({
        'title':'FICTIONAL TEST','id':'TEST-ONLY','revision':1,
        'assetRegistry':{'assets':[{'id':f'asset-{i}','kind':'image','label':f'Block 1 Mini 1 Shot {i:02d}: Frame {i}'} for i in range(1,26)],
        'extensions':{'storyWorkflow':{
            'plans':[{'address':{'blockNumber':1,'miniBlockNumber':1},'shots':[{'shotNumber':i,'passageIds':[f'fictional-{i}'],'narrativePurpose':f'Beat {i}','composition':'Wide'} for i in range(1,26)]}],
            'imageMappings':[{'artifactId':str(i),'address':{'blockNumber':1,'miniBlockNumber':1,'shotNumber':i},'savedMarkerPresent':True,'locked':True,'visualApproval':{'state':'approved' if i == 1 else 'pending-user-review'}, 'passageIds':[f'fictional-{i}']} for i in range(1,26)],
            'authoredBeats':[]
        }}}
    },separators=(',',':')).encode()


class TestSourceInspector(unittest.TestCase):
    def test_verified_25_slots_and_approval_distinction(self):
        b=fixture()
        x=extract_source_snapshot(b, expected_sha256=hashlib.sha256(b).hexdigest())
        self.assertEqual(len(x['shots']),25)
        self.assertEqual(x['summary']['sourcePpfSaved'],25)
        self.assertEqual(x['summary']['sourcePpfLocked'],25)
        self.assertEqual(x['summary']['explicitHumanVisualApproval'],1)
        self.assertEqual(x['summary']['pendingVisualReview'],24)
        self.assertEqual(x['shots'][24]['page'],5)
        self.assertTrue(x['readOnly'])
    def test_hash_mismatch_rejected(self):
        with self.assertRaisesRegex(ReviewSourceError,'SHA-256 mismatch'):
            extract_source_snapshot(fixture(),expected_sha256='0'*64)
    def test_duplicate_mapping_rejected(self):
        x=json.loads(fixture())
        x['assetRegistry']['extensions']['storyWorkflow']['imageMappings'].append(x['assetRegistry']['extensions']['storyWorkflow']['imageMappings'][0])
        b=json.dumps(x).encode()
        with self.assertRaisesRegex(ReviewSourceError,'duplicate'):
            extract_source_snapshot(b,expected_sha256=hashlib.sha256(b).hexdigest())

if __name__ == '__main__': unittest.main()
