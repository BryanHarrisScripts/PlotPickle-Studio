#!/usr/bin/env python3
"""Synthetic tests, zero user story assets, no web/network/provider calls."""
import copy,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image
SCRIPT=Path(__file__).with_name('production_guard.py')

def call(command, root, packet, review=None):
    (root/'packet.json').write_text(json.dumps(packet))
    args=[sys.executable,str(SCRIPT),command,'--packet',str(root/'packet.json'),'--assets-root',str(root)]
    if review is not None:
        (root/'review.json').write_text(json.dumps(review));args+=['--results',str(root/'review.json')]
    p=subprocess.run(args,capture_output=True,text=True)
    return p.returncode,json.loads(p.stdout) if p.stdout.lstrip().startswith('{') else p.stderr

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def img(p,color):Image.new('RGB',(1280,720),color).save(p)

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    img(root/'approved.png','orange');img(root/'previous.png','green');img(root/'candidate.png','purple');img(root/'candidate2.png','red')
    (root/'synthetic.fdx').write_text('<FinalDraft><Paragraph>A person wakes when music suddenly plays. A person asks the vehicle what happened.</Paragraph></FinalDraft>')
    packet={'schema':'plotpickle.image-production-context.v1','projectId':'fictional-project-id', 'sourceTitle':'Synthetic Test Screenplay',
        'sourceFormat':'FDX','sourceRevision':5,'sourceFile':'synthetic.fdx','sourceSha256':sha(root/'synthetic.fdx'),
        'passages':[{'id':'passage-01','scene':'INT. CABIN - DAY','text':'A person wakes when music suddenly plays.'},
                    {'id':'passage-02','scene':'INT. CABIN - DAY','text':'A person asks the vehicle what happened.'}],
        'approvedReferences':[{'id':'character-test','role':'character', 'approval':'CREATOR_APPROVED','path':'approved.png','sha256':sha(root/'approved.png')}],
        'continuityAnchor':{'type':'PREVIOUS_SHOT','shotId':'B01-M01-S01','path':'previous.png','sha256':sha(root/'previous.png')},
        'continuation':{'block':1,'miniBlock':1,'shot':2},
        'shots':[{'productionAddress':{'block':1,'miniBlock':1,'shot':2},'scriptPassageIds':['passage-01'],
                  'scene':'INT. CABIN - DAY','subjects':['PERSON'], 'action':'Person jolts awake to sudden music',
                  'camera':'Close-up, eyes abruptly open', 'mustShow':['startled open eyes'],
                  'mustNotShow':['new characters','caption'], 'referenceIds':['character-test'],
                  'imagePrompt':'One uninterrupted cinematic wide frame of a person suddenly jolting awake in the car.'},
                 {'productionAddress':{'block':1,'miniBlock':1,'shot':3},'scriptPassageIds':['passage-02'],
                  'scene':'INT. CABIN - DAY','subjects':['PERSON'], 'action':'Person asks the vehicle why the music played',
                  'camera':'Medium view of person facing interface','mustShow':['questioning expression'],
                  'mustNotShow':['extra passenger','caption'], 'referenceIds':['character-test'],
                  'imagePrompt':'One uninterrupted cinematic wide frame of a passenger questioning a dark interface.'}]}
    rc,report=call('preflight',root,packet)
    assert rc==0, report
    assert len(report['requiredHostImageAttachments'])==2
    valid={ 'schema':'plotpickle.image-production-review.v1', 'packetSha256':report['packetSha256'], 'projectId':packet['projectId'], 'sourceSha256':packet['sourceSha256'],
      'shots':[{'productionAddress':s['productionAddress'], 'image':{'path':p,'sha256':sha(root/p)},'semanticState':'PASS',
      'visualInspectionPerformed':True,'inspector':'reviewer-1','referenceImagesProvidedToModel':True,
      'creatorApproved':False,'nativePpfSavedReadback':False,'nativePpfLockedReadback':False,'libraryMediaReadback':False,
      'usableForProduction':False} for s,p in zip(packet['shots'],('candidate.png','candidate2.png'))]}
    rc,out=call('review',root,packet,valid);assert rc==0,out
    assert all(x['candidateInspectable'] and not x['productionReady'] for x in out['shots'])
    accepted=copy.deepcopy(valid)
    for x in accepted['shots']:
        for k in ('creatorApproved','nativePpfSavedReadback','nativePpfLockedReadback','libraryMediaReadback'):x[k]=True
    rc,out=call('review',root,packet,accepted);assert rc==0,out
    assert all(not x['productionReady'] for x in out['shots'])
    forged=copy.deepcopy(accepted); forged['shots'][0]['usableForProduction']=True
    assert call('review',root,packet,forged)[0]!=0
    # A forged lock as string, missing actual media proof, or an unknown source version cannot pass.
    fake=copy.deepcopy(accepted);fake['shots'][0]['nativePpfLockedReadback']='true'
    rc,out=call('review',root,packet,fake);assert rc==0 and not out['shots'][0]['productionReady'],out
    bad=copy.deepcopy(packet);bad['sourceSha256']='a'*64;assert call('preflight',root,bad)[0]!=0
    bad=copy.deepcopy(packet);bad['approvedReferences'][0]['sha256']='0'*64;assert call('preflight',root,bad)[0]!=0
    bad=copy.deepcopy(packet);bad['shots'][0]['scriptPassageIds']=['passage-not-in-script'];assert call('preflight',root,bad)[0]!=0
    bad=copy.deepcopy(packet);bad['shots'][0]['imagePrompt']='Five panel storyboard collage of many events';assert call('preflight',root,bad)[0]!=0
    bad=copy.deepcopy(packet);bad['shots'][1]['productionAddress']['shot']=12;assert call('preflight',root,bad)[0]!=0
    bad=copy.deepcopy(packet);bad['continuation']['shot']=9;assert call('preflight',root,bad)[0]!=0
    bad=copy.deepcopy(packet);bad['approvedReferences'][0]['path']='../outside.png';assert call('preflight',root,bad)[0]!=0
    bad=copy.deepcopy(valid);bad['shots'][1]['image']=copy.deepcopy(bad['shots'][0]['image']);assert call('review',root,packet,bad)[0]!=0
    bad=copy.deepcopy(valid);bad['shots'][0]['referenceImagesProvidedToModel']=False;assert call('review',root,packet,bad)[0]!=0
    bad=copy.deepcopy(valid);bad['shots'][0]['semanticState']='DRIFTED';assert call('review',root,packet,bad)[0]!=0
    bad=copy.deepcopy(valid);bad['shots'][0]['semanticState']='DRIFTED';bad['shots'][0]['reason']='Wrong person in the actual rendered image';bad['shots'][0]['usableForProduction']=False
    rc,out=call('review',root,packet,bad);assert rc==0,out
    assert out['shots'][0]['candidateInspectable'] is False
    bad=copy.deepcopy(valid);bad['shots'][0]['usableForProduction']=True;assert call('review',root,packet,bad)[0]!=0
    bad=copy.deepcopy(valid);bad['sourceSha256']='a'*64;assert call('review',root,packet,bad)[0]!=0
    print('PASS: 15 guarded preflight/postflight tests, correct pending vs production-ready states, no private data')
