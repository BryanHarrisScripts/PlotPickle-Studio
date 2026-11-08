"""Read-only, revision-pinned storyboard view data. No application or file-service writes."""
import argparse, hashlib, importlib.util, io, json, sys
from pathlib import Path
S=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('workflow',S/'story-workflow.py')
wf=importlib.util.module_from_spec(spec);spec.loader.exec_module(wf)

def verify(base, record):
    if not record:return {'state':'unmapped','bytesVerified':False}
    rel=Path(record.get('portablePath',''))
    if not str(rel) or rel.is_absolute() or '..' in rel.parts:return {'state':'unsafe-path','bytesVerified':False}
    path=(base/rel).resolve()
    if not path.is_relative_to(base):return {'state':'unsafe-path','bytesVerified':False}
    if not path.is_file():return {'state':'missing','bytesVerified':False}
    data=wf.read_bytes(path);actual=wf.digest(data)
    if actual!=record.get('sha256'):return {'state':'hash-mismatch','bytesVerified':False,'actualSha256':actual}
    try:
        from PIL import Image
        with Image.open(io.BytesIO(data)) as im:
            if im.width*im.height>40000000:raise ValueError('IMAGE_TOO_LARGE')
            im.load();width,height=im.size
    except ImportError:return {'state':'hash-verified-decoder-unavailable','bytesVerified':True,'sha256':actual}
    except (OSError,ValueError):return {'state':'decode-failed','bytesVerified':False,'sha256':actual}
    return {'state':'verified','bytesVerified':True,'sha256':actual,'width':width,'height':height}

def review(args):
    p,ident=wf.pinned(args);base=Path(args.project).resolve().parent
    observed=wf.call_node('inspect-project.mjs','--file',args.project,'--operation','shots','--project-id',ident['id'],'--revision',ident['revision'],'--sha256',ident['sha256'],'--block',args.block,'--mini',args.mini)
    ext=p.get('assetRegistry',{}).get('extensions',{})
    maps=ext.get('artworkMapping',{}).get('entries',[])+ext.get('storyWorkflow',{}).get('imageMappings',[])
    index={}
    for r in maps:
        aid=r['artifactId']
        if aid in index and index[aid]!=r:wf.fail('CONFLICTING_IMAGE_MAPPINGS')
        index[aid]=r
    source={s['id']:s for s in p.get('sourceEvidence',{}).get('screenplay',{}).get('passages',[])}
    log=ext.get('imageChanges',{});counts={'verified':0,'missing':0,'changedOrInvalid':0,'unmapped':0,'savedRecords':0,'lockedRecords':0}
    slots=[]
    for shot in observed['shots']:
        row={'address':shot['address'],'shotStatus':shot['shotStatus'],'miniBlockEvidence':shot['sourceEvidence'],'candidates':[]}
        for candidate in shot['candidates']:
            rec=index.get(candidate['id']);media=verify(base,rec);warnings=[]
            if rec and rec.get('address')!=shot['address']:warnings.append('MAPPING_ADDRESS_DIFFERS_FROM_CANONICAL_RECORD')
            refs=rec.get('passageIds',[]) if rec else []
            if any(x not in source for x in refs):warnings.append('UNRESOLVED_SOURCE_PASSAGE')
            state=media['state'];counts['verified' if state=='verified' else 'missing' if state=='missing' else 'unmapped' if state=='unmapped' else 'changedOrInvalid']+=1
            counts['savedRecords']+=int(candidate['savedMarkerPresent']);counts['lockedRecords']+=int(candidate['locked'])
            row['candidates'].append({**candidate,'mediaBytesVerified':media['bytesVerified'],'fileObservation':media,'portablePath':rec.get('portablePath') if rec else None,
              'passageIds':refs,'passages':[{'id':x,'text':source[x]['text']} for x in refs if x in source],
              'mappingProvenance':rec.get('mappingStatus','recorded-assignment') if rec else 'unknown','semanticMatchVerified':False,
              'visualApproval':rec.get('visualApproval',{'state':'unknown'}) if rec else {'state':'unknown'},'promptOrigin':rec.get('promptOrigin','not-captured') if rec else 'unknown',
              'pendingReplacements':[r for r in log.get('pending',[]) if r['artifactId']==candidate['id']], 'warnings':warnings})
        slots.append(row)
    return {'version':1,'project':ident,'scope':'EXPORTED_PROJECT_AND_AVAILABLE_PORTABLE_FILES','canonMutated':False,'liveApplicationUpdated':False,'connectedUiPersistenceVerified':False,
       'slotCount':len(slots),'candidateCount':sum(len(s['candidates']) for s in slots),'fileAndRecordCounts':counts,'shots':slots,
       'projectActiveImageCount':sum(a.get('workflow')=='storyboard-frame-webp-v2' and a.get('reviewState')!='rejected' for a in p.get('build',{}).get('foundations',{}).get('visualArtifacts',[])),
       'pendingReplacementCount':len(log.get('pending',[])), 'historyEventCount':len(log.get('events',[]))}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('project','project-id','sha256'):parser.add_argument('--'+name,required=True)
    for name in ('revision','block','mini'):parser.add_argument('--'+name,type=int,required=True)
    try:print(json.dumps(review(parser.parse_args()),ensure_ascii=False))
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({'status':'blocked','code':str(e)[:600],'inputFileMutated':False}),file=sys.stderr);sys.exit(1)
