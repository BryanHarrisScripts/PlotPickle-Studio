#!/usr/bin/env python3
"""Offline tests for approval reconciliation truth gate."""
import copy,hashlib,importlib.util,json,tempfile
from pathlib import Path

def load():
    p=Path(__file__).with_name('reconcile.py')
    spec=importlib.util.spec_from_file_location('reconcile',p)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def test():
    a=load()
    base={'project':{'id':'test-project'}, 'scope':{'blocks':[1], 'miniBlocksEach':1,'shotsPerMiniBlock':2},
          'creatorInstruction':'All approved',
          'positions':[{'block':1,'miniBlock':1,'shot':1,'creatorApproval':'approved',
                        'originalStatus':'hash_and_decode_verified_in_prior_byte_audit',
                        'originalFilename':'one.png','originalSha256':'a'*64},
                       {'block':1,'miniBlock':1,'shot':2,'creatorApproval':'approved',
                        'originalStatus':'MISSING','originalFilename':None,'originalSha256':None}]}
    r=a.validate(base)
    assert r['counts']['target']==2 and r['counts']['creatorAuthorized']==2
    assert r['counts']['historicalImageEvidence']==1 and r['counts']['nativeLocksFullyVerified']==0
    assert r['status']=='BLOCKED' and r['groups'][0]['unresolved']==[1,2]
    bad=copy.deepcopy(base);bad['positions'][1]=bad['positions'][0]
    try:a.validate(bad);raise AssertionError('duplicate not rejected')
    except ValueError:pass
    bad=copy.deepcopy(base);bad['positions'][0]['originalStatus']='DRIFTED'
    assert a.validate(bad)['positions'][0]['issue']=='DRIFTED_OR_REJECTED'
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        ppf={'id':'test-project','build':{'foundations':{'visualArtifacts':[],'acceptedVisualArtifactIds':[]}},
             'assetRegistry':{'extensions':{'storyWorkflow':{'imageMappings':[]}}}}
        file=root/'project.ppf.json';file.write_text(json.dumps(ppf))
        assert a.validate(base,file)['counts']['nativeLocksFullyVerified']==0
        # Even fake coherent marker without a readable image does not equal native lock.
        artifact={'id':'x','sourceDecisionKeys':['storyboard-local-save:v1'],'reviewState':'accepted'}
        mapping={'artifactId':'x','address':{'blockNumber':1,'miniBlockNumber':1,'shotNumber':1},
                 'savedMarkerPresent':True,'locked':True,'sha256':'a'*64}
        ppf['build']['foundations']['visualArtifacts']=[artifact]
        ppf['build']['foundations']['acceptedVisualArtifactIds']=['x']
        ppf['assetRegistry']['extensions']['storyWorkflow']['imageMappings']=[mapping]
        file.write_text(json.dumps(ppf))
        t=a.validate(base,file,root)
        assert t['positions'][0]['nativePpfLockMarkerCoherent']
        assert t['counts']['nativeLocksFullyVerified']==0
        # A mismatched source identity fails closed.
        wrong=copy.deepcopy(base);wrong['project']['id']='other'
        try:a.validate(wrong,file);raise AssertionError('source conflict ignored')
        except ValueError:pass
    print('PASS: 5 truth-gate cases; no fictional locks or silent missing shots')

if __name__=='__main__':test()
