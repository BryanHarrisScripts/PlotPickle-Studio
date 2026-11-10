#!/usr/bin/env python3
"""PlotPickle design kit: read-only, revision-bound character/world/layout sheet planning.

All media panels remain candidates until separately generated, verified and approved.
Never changes input project, performs network calls or stores user credentials.
"""
import argparse
import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path

CHAR_PANELS = [
    ('front', 'Full figure / front', 'Full-body neutral front view, consistent physical design.'),
    ('three-quarter-left', 'Three-quarter / left', 'Full-body three-quarter left view with same face, body and wardrobe.'),
    ('profile', 'Profile', 'Side-profile, consistent silhouette and facial features.'),
    ('back', 'Rear view', 'Full-body rear view with matching costume construction.'),
    ('three-quarter-right', 'Three-quarter / right', 'Full-body three-quarter right view.'),
    ('face', 'Expression study', 'Close study of expressions; expression choices are visual proposals.'),
    ('wardrobe', 'Wardrobe details', 'Outfit layers and textures; unspecified details remain proposals.'),
    ('hands-props', 'Hands and props', 'Hand scale and any screenplay-supported held props.'),
    ('silhouette', 'Silhouette and scale', 'Neutral silhouette with proportional reference.'),
]
WORLD_PANELS = [
    ('establishing', 'Establishing view', 'Place overview; stage only screenplay-supported geography.'),
    ('ground-plan', 'Ground plan', 'Spatial diagram: entrances, exits, paths; proposed where not scripted.'),
    ('reverse', 'Reverse / opposing view', 'Opposing camera direction preserving geography.'),
    ('details', 'Environmental details', 'Surfaces, objects and landmarks supported by source or marked proposed.'),
    ('lighting', 'Lighting key', 'Story-grounded time of day, proposed lighting choices.'),
    ('continuity', 'Continuity anchors', 'Repeatable spatial landmarks, axis and camera access.'),
]


def norm(s):
    return re.sub(r'\s+', ' ', str(s)).strip()


def char_name(text):
    text = re.sub(r'\s*\([^)]*\)\s*$', '', norm(text))
    return text.title()


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:90]


def read_project(path, ident):
    blob = Path(path).read_bytes()
    data = json.loads(blob)
    actual = {'id': data.get('id'), 'revision': data.get('revision'),
              'sha256': hashlib.sha256(blob).hexdigest()}
    if actual != ident or not actual['id'] or not isinstance(actual['revision'], int):
        raise ValueError('Project identity/revision/SHA mismatch; reopen current saved project')
    passage_list = data.get('sourceEvidence', {}).get('screenplay', {}).get('passages', [])
    if not isinstance(passage_list, list) or not passage_list:
        raise ValueError('No retained screenplay passages')
    if not all(isinstance(p, dict) and isinstance(p.get('id'), str) and isinstance(p.get('text'), str) for p in passage_list):
        raise ValueError('Invalid screenplay passage records')
    ids = [p['id'] for p in passage_list]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate screenplay passage ID')
    return data, actual, passage_list


def index_subjects(passages):
    characters = {}
    worlds = {}
    for i,p in enumerate(passages):
        if p.get('type') == 'character':
            name=char_name(p['text'])
            key=slug(name)
            if key:
                c=characters.setdefault(key, {'id':key,'name':name,'cuePassageIds':[]})
                c['cuePassageIds'].append(p['id'])
        if p.get('type') == 'scene-heading':
            name=norm(p['text'])
            key=slug(name)
            if key:
                w=worlds.setdefault(key, {'id':key,'heading':name,'scenePassageIds':[], 'headingIndices':[]})
                w['scenePassageIds'].append(p['id']);w['headingIndices'].append(i)
    return characters, worlds


def catalogue(project,ident,passages):
    chars, worlds=index_subjects(passages)
    return {'schema':'plotpickle.design-catalogue.v1','project':ident,'title':project.get('title'),
            'status':'source-index-only','projectModified':False,
            'characters':sorted(({'id':c['id'],'name':c['name'],'cueCount':len(c['cuePassageIds']),
                                 'examplePassageId':c['cuePassageIds'][0]} for c in chars.values()), key=lambda z:z['name']),
            'worlds':sorted(({'id':w['id'],'heading':w['heading'],'sceneCount':len(w['scenePassageIds']),
                              'examplePassageId':w['scenePassageIds'][0]} for w in worlds.values()), key=lambda z:z['heading'])}


def choose(index, subject):
    target=slug(subject)
    if target in index:
        return index[target]
    matches=[v for k,v in index.items() if target and target in k]
    if len(matches)==1:return matches[0]
    if len(matches)>1: raise ValueError('Ambiguous subject: choose an exact catalogue ID')
    raise ValueError('Subject not found in retained screenplay catalogue')


def evidence(p):
    full = p['text']
    excerpt = full[:540]
    return {'passageId':p['id'],'type':p.get('type'),
            'text':excerpt,
            'textSha256':hashlib.sha256(full.encode('utf-8')).hexdigest(),
            'excerptSha256':hashlib.sha256(excerpt.encode('utf-8')).hexdigest(),
            'excerptTruncated':len(full)>540}


def character_design(project,ident,passages,subject):
    chars,_=index_subjects(passages)
    target=choose(chars,subject)
    name=target['name']
    re_name=re.compile(r'(?<!\w)'+re.escape(name)+r'(?!\w)',re.I)
    selected=[]
    cue_indices=[i for i,p in enumerate(passages) if p['id'] in target['cuePassageIds']]
    for i,p in enumerate(passages):
        if p.get('type')=='action' and re_name.search(p['text']): selected.append(p)
    for i in cue_indices[:5]:
        selected.append(passages[i])
        if i+1 < len(passages) and passages[i+1].get('type') in ('dialogue','parenthetical'):
            selected.append(passages[i+1])
    dedup={p['id']:p for p in sorted(selected,key=lambda p:passages.index(p))}
    chosen=list(dedup.values())[:20]
    return {'schema':'plotpickle.design-brief.v1','kind':'character','status':'draft-proposal',
            'project':ident,'title':project.get('title'),
            'subject':{'id':target['id'],'name':name},
            'sourceEvidence':[evidence(p) for p in chosen],
            'identityAndAppearance':{'screenplayFacts':'Read cited passages; no physical attributes inferred automatically',
                                    'sourceSupported':[], 'unspecified':[], 'visualProposals':[]},
            'continuity':{'sourceReferencePolicy':'Use current saved source plus user-approved visual references',
                          'wardrobeVariants':[], 'ageVariants':[], 'referenceImages':[],
                          'approval':'not-requested'},
            'layoutTemplate':'character-turnaround-3x3','projectModified':False,'mediaGenerated':False}


def world_design(project,ident,passages,subject):
    _,worlds=index_subjects(passages)
    target=choose(worlds,subject)
    segments=[]
    for idx in target['headingIndices']:
        section=[passages[idx]]
        for p in passages[idx+1:]:
            if p.get('type')=='scene-heading': break
            if p.get('type') in ('action','dialogue'):
                section.append(p)
            if len(section)>=10: break
        segments.extend(section)
    chosen=list({p['id']:p for p in segments}.values())[:24]
    return {'schema':'plotpickle.design-brief.v1','kind':'world','status':'draft-proposal',
            'project':ident,'title':project.get('title'),
            'subject':{'id':target['id'],'name':target['heading']},
            'sourceEvidence':[evidence(p) for p in chosen],
            'settingAndGeography':{'screenplayFacts':'Read cited passages; no landmarks or geography invented automatically',
                                   'sourceSupported':[], 'unspecified':[], 'visualProposals':[]},
            'continuity':{'geography':[],'landmarks':[],'lightingVariants':[],
                          'referenceImages':[], 'approval':'not-requested'},
            'layoutTemplate':'world-layout-2x3','projectModified':False,'mediaGenerated':False}


def layout(design):
    if design.get('schema')!='plotpickle.design-brief.v1' or design.get('kind') not in ('character','world'):
        raise ValueError('Valid draft design brief required')
    if design.get('status')!='draft-proposal' or design.get('mediaGenerated') is not False:
        raise ValueError('Only ungenerated draft design briefs can be laid out')
    kind=design['kind']
    rows,cols,aspect,panels=(3,3,'1:1',CHAR_PANELS) if kind=='character' else (3,2,'16:9',WORLD_PANELS)
    return {'schema':'plotpickle.design-layout.v1', 'status':'empty-template', 'kind':kind,
            'project':design['project'], 'subject':design['subject'],
            'sourceEvidenceIds':[e['passageId'] for e in design['sourceEvidence']],
            'columns':cols,'rows':rows, 'cellAspectRatio':aspect,
            'panels':[{'id':i,'title':title,'promptGuidance':guide,'image':None,
                       'imageVerified':False,'visualApproval':'pending'} for i,title,guide in panels],
            'mediaGenerated':False,'projectModified':False,'designApproved':False,
            'notes':'Layout plan only. No generated images, accepted continuity, native Save/Lock or project edits.'}


def render_html(spec):
    if spec.get('schema')!='plotpickle.design-layout.v1':raise ValueError('Valid layout spec required')
    if len(spec.get('panels',[])) not in (6,9):raise ValueError('Unsupported panel count')
    cols=int(spec['columns'])
    ratio='1/1' if spec['cellAspectRatio']=='1:1' else '16/9'
    heading=html.escape(spec['subject']['name'])
    panels=''.join(f'<section class="panel"><div class="photo">IMAGE PENDING</div><h2>{html.escape(p["title"])}</h2><small>{html.escape(p["promptGuidance"])}</small></section>' for p in spec['panels'])
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>PlotPickle Design Layout — '+heading+'</title><style>'
            'body{font:14px system-ui,Arial,sans-serif;color:#eee;background:#16171b;max-width:1100px;margin:0 auto;padding:22px}'
            'header{margin-bottom:22px}h1{font-size:26px;margin:0 0 4px}h2{font-size:14px;margin:8px 0 4px}'
            '.subtitle,small{color:#aaa}.grid{display:grid;grid-template-columns:repeat('+str(cols)+',minmax(0,1fr));gap:12px}'
            '.panel{background:#25262c;border:1px solid #444;border-radius:8px;padding:10px;min-width:0}'
            '.photo{aspect-ratio:'+ratio+';border:1px dashed #777;background:#1b1c21;display:flex;align-items:center;justify-content:center;color:#888;letter-spacing:.12em;font-size:10px}'
            'small{display:block;line-height:1.4;font-size:11px}.footer{margin-top:20px;color:#aaa;font-size:12px}'
            '@media(max-width:620px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}'
            '@media print{body{background:white;color:#111}.panel{background:white;border-color:#bbb}.photo{background:#fafafa;color:#777}.subtitle,small,.footer{color:#555}}'
            '</style><header><h1>'+heading+'</h1><div class="subtitle">PlotPickle · '+html.escape(spec['kind']).title()+' design layout · '+html.escape(spec['cellAspectRatio'])+' cells · Draft</div></header>'
            '<main class="grid">'+panels+'</main><div class="footer">Source-bound candidate sheet. No artwork generated or approved. Source project unchanged.</div></html>')


def output(path,obj,as_html=False):
    p=Path(path)
    if p.exists():raise ValueError('Output exists; refusing to overwrite')
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(obj if as_html else json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def cli():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest='command',required=True)
    for k in ('catalogue','character','world'):
        x=sub.add_parser(k)
        x.add_argument('--project',required=True)
        x.add_argument('--project-id',required=True)
        x.add_argument('--revision',required=True,type=int)
        x.add_argument('--sha256',required=True)
        if k!='catalogue':x.add_argument('--subject',required=True)
        x.add_argument('--out')
    for k in ('layout','sheet'):
        x=sub.add_parser(k)
        x.add_argument('--design',required=True) if k=='layout' else x.add_argument('--layout',required=True)
        x.add_argument('--out',required=True)
    args=ap.parse_args()
    try:
        if args.command in ('catalogue','character','world'):
            project,ident,passages=read_project(args.project,{'id':args.project_id,'revision':args.revision,'sha256':args.sha256})
            result = catalogue(project,ident,passages) if args.command=='catalogue' else (character_design(project,ident,passages,args.subject) if args.command=='character' else world_design(project,ident,passages,args.subject))
            if args.out:output(args.out,result)
            else:print(json.dumps(result,ensure_ascii=False,indent=2))
        elif args.command=='layout':
            result=layout(json.loads(Path(args.design).read_text(encoding='utf-8')))
            output(args.out,result)
        else:
            result=render_html(json.loads(Path(args.layout).read_text(encoding='utf-8')))
            output(args.out,result,as_html=True)
        if args.out:print(json.dumps({'ok':True,'readOnly':True,'path':args.out,'projectModified':False}))
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError) as e:
        print(json.dumps({'ok':False,'failClosed':True,'error':str(e)}));return 2
    return 0

if __name__=='__main__':raise SystemExit(cli())
