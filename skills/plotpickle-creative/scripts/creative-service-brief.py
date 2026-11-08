#!/usr/bin/env python3
"""Prepare an evidence-linked, nonexecuting creative-service request.

A brief is not a provider call, a credit authorization, a generated song,
or a saved PlotPickle project change. Intended for Suno connected through ChatGPT.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

DATA = Path(__file__).resolve().parents[1] / 'data'


def verify_project(blob, expected):
    project = json.loads(blob)
    actual = {'id':project.get('id'), 'revision':project.get('revision'),
              'sha256':hashlib.sha256(blob).hexdigest()}
    if actual != expected or not actual['id'] or not isinstance(actual['revision'],int):
        raise ValueError('Project identity/revision/SHA mismatch')
    passages = project.get('sourceEvidence',{}).get('screenplay',{}).get('passages',[])
    return project,actual,{p['id']:p for p in passages if isinstance(p,dict) and p.get('id')}


def prepare(project_bytes, request, registry):
    project,ident,passages=verify_project(project_bytes,request.get('project',{}))
    service_id=request.get('service')
    reg={s['id']:s for s in registry['services']}
    if service_id not in reg:
        raise ValueError('Unknown or unauthorized provider')
    spec=reg[service_id]
    if spec.get('status') != 'not-confirmed-connected':
        raise ValueError('Registry must not assert an unobserved connection')
    purpose=request.get('purpose');text=request.get('brief')
    if not isinstance(purpose,str) or not purpose.strip() or len(purpose)>240:
        raise ValueError('A bounded creative purpose is required')
    if not isinstance(text,str) or len(text.strip())<12 or len(text)>5000:
        raise ValueError('A substantive bounded creative brief is required')
    links=request.get('passageIds')
    if not isinstance(links,list) or not links or len(set(links))!=len(links) or any(i not in passages for i in links):
        raise ValueError('Explicit, valid screenplay source passage IDs required')
    if request.get('creditAuthorization') not in (None,'pending'):
        raise ValueError('This offline preview may not record credit authorization')
    if request.get('status') not in (None,'draft'):
        raise ValueError('Cannot mark a request as submitted or generated')
    action=request.get('action')
    if action not in ('create','extend','cover','mashup','speech'):
        raise ValueError('Requested action is not supported by the brief contract')
    if action!='create' and not request.get('sourceAssetId'):
        raise ValueError('Non-create action requires a source asset ID')
    return {
      'schemaVersion':'1.0','status':'draft-unsubmitted','providerConnectedVerified':False,
      'creditsAuthorized':False,'mediaGenerated':False,'mediaImported':False,
      'projectModified':False,'project':ident,'title':project.get('title'),
      'service':service_id,'serviceEndpoint':spec['mcpServerUrl'],
      'action':action,'purpose':purpose.strip(),'brief':text.strip(),
      'sourceAssetId':request.get('sourceAssetId'),
      'sourceEvidence':[{'passageId':i,'textSha256':hashlib.sha256(passages[i].get('text','').encode()).hexdigest()} for i in links],
      'intendedUse':request.get('intendedUse','temp creative exploration'),
      'proposedCreditsPolicy':'Require user-approved Suno connection and permission before generation',
      'resultPolicy':'Provider track IDs/URLs are references, not verified file bytes or accepted PlotPickle media',
      'nextAction':'User connects and authorizes Suno in ChatGPT; then approve a specific provider call'
    }


def record_reference(draft, reported):
    if draft.get('status')!='draft-unsubmitted' or draft.get('mediaGenerated') is not False:
        raise ValueError('Source must be an unsubmitted draft')
    if reported.get('service')!=draft.get('service') or not isinstance(reported.get('providerAssetId'),str) or not reported['providerAssetId'].strip():
        raise ValueError('Provider result must identify the matching service and asset')
    url=reported.get('providerAssetUrl')
    if not isinstance(url,str):raise ValueError('Missing provider URL')
    parsed=urlparse(url)
    if parsed.scheme!='https' or not parsed.hostname or parsed.hostname not in ('suno.com','www.suno.com'):
        raise ValueError('Unrecognized result host; never trust a callback URL blindly')
    return {'status':'externally-reported-unverified','project':draft['project'],
            'service':draft['service'],'providerAssetId':reported['providerAssetId'].strip(),
            'providerAssetUrl':url,'mediaGeneratedVerified':False,
            'mediaImported':False,'mediaApproved':False,'projectModified':False,
            'verificationNeeded':'Check connected-provider receipt; download permitted media, hash bytes, request creative approval, attach through project workflow'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=('preview','record-reference'))
    p.add_argument('--project',type=Path)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--draft',type=Path)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    try:
        if a.out.exists():raise ValueError('Refuse to overwrite existing output')
        req=json.loads(a.input.read_text())
        if a.action=='preview':
            if not a.project:raise ValueError('Project is required')
            before=a.project.read_bytes()
            registry=json.loads((DATA/'creative-services.json').read_text())
            result=prepare(before,req,registry)
            if a.project.read_bytes()!=before:raise ValueError('Project changed during preview')
        else:
            if not a.draft:raise ValueError('Prior draft is required')
            result=record_reference(json.loads(a.draft.read_text()),req)
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
        print(json.dumps({'ok':True,'status':result['status'],'projectModified':False,'path':str(a.out)}))
    except (ValueError,OSError,TypeError,KeyError,json.JSONDecodeError) as e:
        print(json.dumps({'ok':False,'failClosed':True,'error':str(e)}));return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
