#!/usr/bin/env python3
"""Read-only PlotPickle creative service catalogue with direct official provider links."""
import argparse
import json
from pathlib import Path
REGISTRY = Path(__file__).resolve().parents[1] / 'data' / 'creative-services.json'
OFFICIAL_LINKS = {'suno':'https://suno.com/','fal':'https://fal.ai/dashboard'}

def load_registry(path=REGISTRY):
    reg=json.loads(Path(path).read_text(encoding='utf-8'))
    assert reg.get('schemaVersion')=='1.1','Unsupported service catalogue schema'
    services=reg.get('services',[])
    assert services and len({s['id'] for s in services})==len(services),'Invalid service IDs'
    for s in services:
        assert s['credentialsStoredByPlotPickle'] is False,'Never store credentials in PlotPickle'
        assert s['status'] in ('not-confirmed-connected','planned-unavailable'),'A static registry cannot assert connection'
        assert s['catalogState'] in ('setup-available','planned'),'Unexpected catalog state'
        for a in s.get('actions',[]):
            assert isinstance(a.get('usesCredits'),bool) and isinstance(a.get('requiresProvider'),bool)
            assert a.get('prompt')
            if a['usesCredits']:assert a['requiresProvider'],'Credit actions require a provider'
            if a['kind']=='external-link':
                assert s['id'] in OFFICIAL_LINKS,'Unexpected external link service'
                assert a.get('url')==OFFICIAL_LINKS[s['id']],'External link not approved'
                assert a['id']=='open-'+s['id'] and not a['usesCredits'] and not a['requiresProvider'],'External link must be noncredit browser action'
    return reg

def catalog(reg):
    rows=[]
    for s in reg['services']:
        planned=s['catalogState']=='planned'
        rows.append({'id':s['id'],'name':s['name'],'category':s['category'],'summary':s['summary'],
          'status':'Planned · unavailable' if planned else 'Connection not verified',
          'statusEvidence':'catalogue-only-not-live','setupUrl':None if planned else s.get('officialSetupUrl'),
          'secureSignIn':s.get('secureSignIn'),'credentialsStoredByPlotPickle':False,
          'actions':[{'id':a['id'],'label':a['label'],'requiresProvider':a['requiresProvider'],
            'usesCredits':a['usesCredits'],'openUrl':a.get('url') if a['kind']=='external-link' else None,
            'conversationRequired':a['kind']!='external-link'} for a in s['actions']]})
    return {'schemaVersion':reg['schemaVersion'],'status':'catalogue-read-only',
      'liveConnectionChecked':False,'services':rows,
      'hostInstructions':'Only a live authorized provider response proves connection. Open Suno and Open fal are direct browser links, not new conversations.'}

def intent(reg,service_id,action_id):
    s=next((s for s in reg['services'] if s['id']==service_id),None)
    if s is None:raise ValueError('Unknown service')
    a=next((a for a in s['actions'] if a['id']==action_id),None)
    if a is None:raise ValueError('Unknown action')
    if s['catalogState']=='planned' and a['kind']!='local-concept':raise ValueError('Planned services cannot launch external actions')
    if a['kind']=='external-link':
        return {'status':'external-link-intent','service':service_id,'action':action_id,'label':a['label'],
          'openUrl':OFFICIAL_LINKS[service_id],'conversationRequired':False,'providerInvoked':False,
          'creditsAuthorized':False,'creditsSpent':False,'credentialPromptAllowed':False,'projectModified':False}
    return {'status':'intent-only-not-executed','service':service_id,'action':action_id,
      'label':a['label'],'suggestedPrompt':a['prompt'],
      'hostConnectionVerificationRequired':a['requiresProvider'],
      'requiresExplicitCreditApproval':a['usesCredits'],'providerInvoked':False,
      'creditsAuthorized':False,'creditsSpent':False,'credentialPromptAllowed':False,'projectModified':False,
      'setupUrl':s.get('officialSetupUrl') if a['requiresProvider'] else None}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['catalog','intent']);p.add_argument('--service');p.add_argument('--action')
    args=p.parse_args()
    try:
        reg=load_registry()
        if args.command=='intent':
            if not args.service or not args.action:p.error('intent requires --service and --action')
            result=intent(reg,args.service,args.action)
        else:result=catalog(reg)
        print(json.dumps(result,indent=2,ensure_ascii=False))
    except (ValueError,AssertionError,KeyError,OSError,json.JSONDecodeError) as exc:
        print(json.dumps({'status':'fail-closed','error':str(exc)}));return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
