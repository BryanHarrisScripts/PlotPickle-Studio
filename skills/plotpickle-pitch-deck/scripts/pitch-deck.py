#!/usr/bin/env python3
"""Build evidence-bound pitch outlines or 96-panel proposals from a saved PPF."""
import argparse,hashlib,json,pathlib,sys

def source(p,sha):
    if not isinstance(p,dict) or not isinstance(p.get('id'),str) or not isinstance(p.get('revision'),int):raise ValueError('PPF identity missing')
    return {'projectId':p['id'],'revision':p['revision'],'sha256':sha,'storyTitle':p.get('title') or (p.get('metadata') or {}).get('title') or 'Untitled'}

def screenplay(p):return [x for x in ((p.get('sourceEvidence') or {}).get('screenplay') or {}).get('passages',[]) if isinstance(x,dict)]

def presentation(p,sha):
    src=source(p,sha);story=p.get('story') or {}; review=p.get('review') or {};pitch=review.get('pitchPackage') or {}
    if not isinstance(pitch,dict):pitch={}
    passages=screenplay(p);headings=[x for x in passages if str(x.get('type','')).lower() in ('scene-heading','scene_heading')]
    speaker_names=[]
    for x in passages:
        if str(x.get('type','')).lower()=='character':
            name=str(x.get('text','')).strip()
            if name and name not in speaker_names:speaker_names.append(name)
    def entry(title,detail,truth,source_field=None):return {'title':title,'content':detail,'truth':truth,'sourceField':source_field}
    logline=pitch.get('logline') or story.get('logline')
    synopsis=pitch.get('synopsis') or story.get('synopsis')
    slides=[
      entry('Title',pitch.get('title') or src['storyTitle'],'project-record','title'),
      entry('Logline',logline if logline else '[Draft logline needed — protagonist, disruption, stakes]','recorded-candidate-unapproved' if logline else 'placeholder','review.pitchPackage.logline or story.logline'),
      entry('Story / synopsis',synopsis if synopsis else '[Author-approved synopsis needed]','recorded-candidate-unapproved' if synopsis else 'placeholder','review.pitchPackage.synopsis or story.synopsis'),
      entry('Genre and tone',{'genre':story.get('genre'),'tone':story.get('tone')},'project-record-if-present','story.genre/story.tone'),
      entry('Characters',{'screenplayCueNames':speaker_names[:12],'caveat':'Screenplay cue detection alone does not establish protagonists or character arcs.'},'source-extracted','sourceEvidence.screenplay.passages'),
      entry('World and locations',{'recordedSceneHeadings':[x.get('text') for x in headings[:12]]},'source-extracted','sourceEvidence.screenplay.passages'),
      entry('Conflict and stakes','[Draft: establish protagonist, opposition, central stakes]','placeholder'),
      entry('Visual language',pitch.get('visualStatement') or '[Select approved visual references, mood and layout]', 'recorded-candidate-unapproved' if pitch.get('visualStatement') else 'placeholder','review.pitchPackage.visualStatement'),
      entry('Structure and audience',{'canonicalStructure':'4 Acts / 12 Sequences / 24 Blocks / 96 Mini-Blocks (planning scaffold)','audience':pitch.get('audience') or '[Define audience]'},'planned-scaffold-plus-draft','review.pitchPackage.audience'),
      entry('Positioning and comparables',pitch.get('comparableTitles') or '[Research and verify comparable titles, no automatic claims]','recorded-candidate-unapproved' if pitch.get('comparableTitles') else 'placeholder','review.pitchPackage.comparableTitles'),
      entry('Creator statement',pitch.get('creatorStatement') or '[Author-supplied statement]', 'recorded-candidate-unapproved' if pitch.get('creatorStatement') else 'placeholder','review.pitchPackage.creatorStatement'),
      entry('Rights / production / ask',{'rights':(p.get('rights') or {}).get('copyrightNotice') or '[Rights status requires review]','production':'[Development status and intended production approach]','ask':'[Specific requested next step, finance, distribution or collaborators]'},'mixed-verified-fields-and-placeholders')]
    return {'schema':'plotpickle.pitch.presentation.v1','source':src,'slides':slides,'status':'editable-draft-not-approved','spend':False,'mediaGenerated':False}

def comic(p,sha):
    src=source(p,sha);wf=((p.get('assetRegistry') or {}).get('extensions') or {}).get('storyWorkflow') or {}
    mapping={}
    for x in wf.get('imageMappings',[]) or []:
        if not isinstance(x,dict):continue
        addr=x.get('address') or {};k=(addr.get('blockNumber'),addr.get('miniBlockNumber'))
        if all(isinstance(v,int) for v in k):mapping.setdefault(k,[]).append(x)
    pages=[]
    for block in range(1,25):
        panels=[]
        for mini in range(1,5):
            shots=mapping.get((block,mini),[])
            passages=[]
            for x in shots:
                for v in x.get('passageIds',[]) or []:
                    if v not in passages:passages.append(v)
            panels.append({'blockNumber':block,'miniBlockNumber':mini,'sourcePassageIds':passages,
                           'mappedShotCount':len(shots),'status':'source-linked-proposal' if passages else 'unmapped',
                           'imageGenerated':False,'identityApproved':None,'dialogue':'[Editable screenplay dialogue when sourced and approved]'})
        pages.append({'pageNumber':block,'blockNumber':block,'panels':panels})
    return {'schema':'plotpickle.pitch.comic-plan.v1','source':src,'pageCount':24,'panelCount':96,'pages':pages,
            'status':'planning-only-no-generated-comic-art','spend':False,'mediaGenerated':False}

def render_md(data):
    src=data['source'];lines=[f"# {src['storyTitle']} — PlotPickle Pitch",f"Project {src['projectId']} · rev {src['revision']}",f"SHA-256: {src['sha256']}", 'Status: draft, not approved or exported as slides.']
    if 'slides' in data:
        for i,x in enumerate(data['slides'],1):lines.extend(['', '---',f"## Slide {i} — {x['title']}",str(x['content']),f"Truth: {x['truth']}"])
    else:
        for page in data['pages']:
            lines.extend(['',f"## Page {page['pageNumber']} — Block {page['blockNumber']}"])
            for panel in page['panels']:lines.append(f"- Mini-Block {panel['miniBlockNumber']}: {panel['status']}; mapped shots {panel['mappedShotCount']} — source passages: {', '.join(panel['sourcePassageIds']) or 'none'}")
    return '\n'.join(lines)+'\n'

def main():
    a=argparse.ArgumentParser();a.add_argument('--project',type=pathlib.Path,required=True);a.add_argument('--mode',choices=['presentation','comic'],default='presentation');a.add_argument('--format',choices=['json','markdown'],default='json');a.add_argument('--out',type=pathlib.Path);v=a.parse_args()
    raw=v.project.read_bytes();p=json.loads(raw);sha=hashlib.sha256(raw).hexdigest();data=presentation(p,sha) if v.mode=='presentation' else comic(p,sha)
    out=json.dumps(data,indent=2,ensure_ascii=False)+'\n' if v.format=='json' else render_md(data)
    if v.out:
        with v.out.open('x',encoding='utf-8') as f:f.write(out)
    else:sys.stdout.write(out)
if __name__=='__main__':main()
