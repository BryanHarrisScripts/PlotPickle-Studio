#!/usr/bin/env python3
"""Build an offline, responsive read-only Story Explorer from a PPF and its portable image assets."""
import argparse, hashlib, html, json
from pathlib import Path

CSS='''
:root{color-scheme:dark;font:14px system-ui,-apple-system,sans-serif;background:#0e1110;color:#e5eae7}
*{box-sizing:border-box}body{margin:0}.page{max-width:1100px;margin:auto;padding:14px}
header,section{border:1px solid #465149;border-radius:12px;background:#151a17;padding:16px;margin-bottom:12px}
header{background:linear-gradient(125deg,#173222,#111615);display:flex;justify-content:space-between;gap:10px;align-items:center}
h1{font-size:clamp(22px,5vw,32px);margin:4px 0}h2{font-size:15px;letter-spacing:.06em;margin:0 0 12px;color:#c2dbc8}
.kicker{letter-spacing:.12em;font-size:12px;color:#91bd9c}.muted{color:#acb9af;font-size:12px}.titlebar{display:flex;justify-content:space-between;gap:10px}
.actrow{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}.sequences{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px}
.blocks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.minis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}
.shots{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:5px}.tabs{display:flex;gap:5px;overflow:auto;padding:10px 0}
button{font:inherit;cursor:pointer;border:1px solid #506153;color:#d9e5dc;background:#1c241f;border-radius:8px;padding:10px}
button.active{border-color:#89d6a1;background:#2a573b;color:white}button:focus-visible{outline:2px solid #b1e9c0}
.seq,.block{padding:12px;text-align:left;border:1px solid #4a5a50;border-radius:9px;background:#1a221c;min-width:0}
.seq{width:100%}.seqname{font-weight:700;display:block;overflow-wrap:anywhere}.seq small{display:block;margin-top:7px;color:#a9b6ad}
.block.active{border-color:#77c78f}.blocktitle{font-weight:700;margin-bottom:8px;overflow-wrap:anywhere}
.mini{padding:9px 4px}.shot{padding:9px 4px}.shot small{display:block;font-size:10px;color:#a3bca8}
.copy{white-space:pre-wrap;background:#1c2720;border-left:3px solid #76b98c;padding:12px;border-radius:5px;overflow-wrap:anywhere;margin:7px 0}
.card{background:#1b251e;padding:12px;border-radius:6px}.preview{width:100%;max-height:360px;object-fit:contain;background:#0d110e;border-radius:8px}
.warning{border:1px solid #86724a;background:#302819;color:#e4d4aa;border-radius:8px;padding:10px;margin-bottom:12px;font-size:12px}
@media(max-width:630px){.page{padding:8px}header,section{padding:12px}.sequences,.blocks{grid-template-columns:1fr}.seq{padding:11px}.seq small{margin-top:3px}.shot small{display:none}h1{font-size:27px}}
'''
JS=r'''
const D=JSON.parse(document.getElementById('model').textContent);let a=1,q=1,b=1,m=1,s=7,tab='Script';
const byId=id=>document.getElementById(id),pad=n=>String(n).padStart(2,'0');
const esc=x=>String(x??'').replace(/[&<>"']/g,k=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[k]));
const mini=(b,m)=>D.minis[b+'.'+m]||{passageIds:[],images:0,planned:0};
const candidates=()=>D.shotsByMini[b+'.'+m]||[];
const candidate=()=>candidates().find(x=>x.number===s)||null;
function A(n){a=n;q=(n-1)*3+1;b=(n-1)*6+1;m=1;s=1;draw()}
function Q(n){q=n;b=(n-1)*2+1;m=1;s=1;draw()}
function M(n,k){b=n;q=Math.floor((n-1)/2)+1;m=k;s=1;draw()}
function S(n){s=n;tab='Script';draw()}
function T(n){tab=n;drawDetail()}
function draw(){
 byId('acts').innerHTML=[1,2,3,4].map(n=>`<button class="${a===n?'active':''}" onclick="A(${n})">Act ${n}</button>`).join('');
 byId('acttitle').textContent=`ACT ${a} / SEQUENCES`;
 byId('seq').innerHTML=[1,2,3].map(k=>{let n=(a-1)*3+k,rec=D.sequences[n-1];return `<button class="seq ${q===n?'active':''}" onclick="Q(${n})"><span class="seqname">S${pad(n)} · ${esc(rec.name)}</span><small>Blocks ${pad((n-1)*2+1)}–${pad((n-1)*2+2)} · Draft source</small></button>`}).join('');
 byId('blocktitle').textContent=`SEQUENCE ${pad(q)} / BLOCKS`;
 byId('blocks').innerHTML=[1,2].map(k=>{let n=(q-1)*2+k,rec=D.blocks[n-1],total=[1,2,3,4].reduce((z,x)=>z+mini(n,x).passageIds.length,0);return `<div class="block ${b===n?'active':''}"><div class="blocktitle">Block ${pad(n)} · ${esc(rec.name)}</div><span class="muted">${total} screenplay passages</span><div class="minis">${[1,2,3,4].map(j=>`<button class="mini ${b===n&&m===j?'active':''}" onclick="M(${n},${j})">${j}</button>`).join('')}</div></div>`}).join('');
 let info=mini(b,m);byId('minititle').textContent=`BLOCK ${pad(b)} / MINI-BLOCK ${pad(m)}`;byId('ministats').textContent=`${info.passageIds.length} passages · ${info.planned} shots planned · ${info.images} images`;
 byId('shots').innerHTML=Array.from({length:25},(_,i)=>i+1).map(n=>`<button class="shot ${s===n?'active':''}" onclick="S(${n})">${pad(n)}<small>${candidates().find(c=>c.number===n)?.image?'Image':candidates().find(c=>c.number===n)?'Planned':'Gap'}</small></button>`).join('');
 byId('crumb').textContent=`${D.title} › Act ${a} › S${pad(q)} › B${pad(b)} › Mini ${m} › Shot ${pad(s)}`;
 byId('inspecttitle').textContent='Shot '+pad(s)+(candidate()?' · '+candidate().name:'');drawDetail();
}
function drawDetail(){
 byId('tabs').innerHTML=['Script','Beat','Prompt','Image','Continuity','Save/Lock'].map(n=>`<button class="${tab===n?'active':''}" onclick="T('${n}')">${n}</button>`).join('');
 const c=candidate(),ids=c?c.passageIds:mini(b,m).passageIds;let val='';
 if(tab==='Script'){let pp=D.passages.filter(p=>ids.includes(p.id));val=pp.length?pp.map(p=>`<div class="copy"><span class="muted">${esc(p.id)} · ${esc(p.type)}</span>\n${esc(p.text)}</div>`).join(''):'<p>Not mapped to an individual screenplay passage.</p>';}
 else if(tab==='Beat'){val=c?`<div class="copy">${esc(c.action)}</div><div class="muted">Planned shot purpose, not independently authored beat.</div>`:'<p>Not authored for this shot.</p>';}
 else if(tab==='Prompt'){val=c&&c.prompt?`<div class="warning">Prompt provenance: ${esc(c.promptOrigin||'not verified')}.</div><div class="copy">${esc(c.prompt)}</div>`:'<p>No stored prompt for this shot.</p>';}
 else if(tab==='Image'){val=c&&c.image?`<img class="preview" src="${esc(c.image)}" alt="Shot ${pad(s)} image candidate"><p class="muted">Portable asset hash checked. Image acceptance and pixel decoding are separate checks.</p>`:'<p>No registered image candidate.</p>';}
 else if(tab==='Continuity'){val=c?c.truths.map(x=>`<div class="copy">${esc(x)}</div>`).join('')||'<p>Not authored.</p>':'<p>No shot-specific continuity recorded.</p>';}
 else {val=c?`<div class="card">Candidate: ${c.image?'registered':'not registered'}<br>Visual approval: ${esc(c.visualApproval||'not recorded')}<br>Save marker: ${c.saved?'recorded':'not recorded'}<br>Lock: ${c.locked?'recorded':'not recorded'}</div>`:'<p>No verified Save or Lock records.</p>';}
 byId('detail').innerHTML=val;
}
draw();
'''

def render(project,out):
    pth=Path(project).resolve();root=pth.parent;p=json.loads(pth.read_text())
    ext=p.get('assetRegistry',{}).get('extensions',{});nav=ext.get('storyNavigator',{});work=ext.get('storyWorkflow',{})
    # A vanilla saved PPF may have no named Story Navigator extension yet.
    nav.setdefault('acts',[{'number':x,'name':f'Act {x}'} for x in range(1,5)])
    nav.setdefault('sequences',[{'number':x,'name':f'Sequence {x:02}'} for x in range(1,13)])
    nav.setdefault('blocks',[{'number':x,'name':f'Block {x:02}'} for x in range(1,25)])
    if len(nav['acts'])!=4 or len(nav['sequences'])!=12 or len(nav['blocks'])!=24:raise ValueError('INVALID_CANONICAL_STRUCTURE')
    passes=p.get('sourceEvidence',{}).get('screenplay',{}).get('passages',[]);plans=work.get('plans',[])
    mappings=work.get('imageMappings',[])

    mini_map={}
    for b in range(1,25):
        for m in range(1,5):
            match=[x for x in plans if x['address']['blockNumber']==b and x['address']['miniBlockNumber']==m]
            mini_map[f'{b}.{m}']={'passageIds':[x['id'] for x in passes if (x['blockNumber'],x['miniBlockNumber'])==(b,m)],
                'planned':sum(s.get('state')=='PLANNED' for q in match for s in q['shots']),
                'images':sum((x['address']['blockNumber'],x['address']['miniBlockNumber'])==(b,m) for x in mappings)}
    truths={x['id']:x['text'] for x in work.get('truths',[])}
    shots_by_mini={}
    used_mappings=set()
    for plan in plans:
        addr=plan.get('address',{})
        b,m=addr.get('blockNumber'),addr.get('miniBlockNumber')
        if not (type(b) is int and 1 <= b <= 24 and type(m) is int and 1 <= m <= 4):
            raise ValueError('INVALID_PLAN_ADDRESS')
        key=f'{b}.{m}'
        if key in shots_by_mini:
            raise ValueError('DUPLICATE_MINI_PLAN')
        rows=[]
        for row in plan.get('shots',[]):
            n=row.get('shotNumber')
            if not (type(n) is int and 1 <= n <= 25):raise ValueError('INVALID_SHOT_NUMBER')
            if row.get('state') != 'PLANNED':continue
            mapped=[x for x in mappings if x.get('address',{}).get('blockNumber')==b and x.get('address',{}).get('miniBlockNumber')==m and x.get('address',{}).get('shotNumber')==n]
            if len(mapped)>1:raise ValueError('AMBIGUOUS_IMAGE_MAPPING')
            rec=mapped[0] if mapped else None
            image=None
            if rec:
                rel=Path(rec['portablePath']);file=(root/rel).resolve()
                if rel.is_absolute() or '..' in rel.parts or not file.is_relative_to(root):raise ValueError('UNSAFE_MEDIA_PATH')
                if not file.exists() or hashlib.sha256(file.read_bytes()).hexdigest()!=rec['sha256']:
                    raise ValueError('INVALID_MEDIA_HASH')
                image=rec['portablePath']
                used_mappings.add((b,m,n))
            purpose=row.get('narrativePurpose','')
            rows.append({'number':n,'name':purpose.split(': ',1)[0],
              'action':purpose,'prompt':row.get('prompt'), 'promptOrigin':rec.get('promptOrigin') if rec else 'not recorded',
              'passageIds':row.get('passageIds',[]), 'image':image,
              'visualApproval':rec.get('visualApproval',{}).get('state','not recorded') if rec else 'not recorded',
              'saved':bool(rec.get('savedMarkerPresent')) if rec else False,
              'locked':bool(rec.get('locked')) if rec else False,
              'truths':[truths[t] for t in row.get('truthIds',[]) if t in truths]})
        if len({x['number'] for x in rows})!=len(rows):raise ValueError('DUPLICATE_SHOT_NUMBER')
        shots_by_mini[key]=rows
    if any((x.get('address',{}).get('blockNumber'),x.get('address',{}).get('miniBlockNumber'),x.get('address',{}).get('shotNumber')) not in used_mappings for x in mappings):
        raise ValueError('IMAGE_MAPPING_WITHOUT_PLANNED_SHOT')
    data={'title':p['title'],'acts':nav['acts'],'sequences':nav['sequences'],'blocks':nav['blocks'],
          'minis':mini_map,'passages':passes,'shotsByMini':shots_by_mini}
    body=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    title=html.escape(p['title'])
    markup=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · PlotPickle</title><style>{CSS}</style></head>
<body><main class="page"><header><div><div class="kicker">PLOTPICKLE / STORY EXPLORER</div><h1>{title}</h1><span class="muted">Source-backed navigation · Draft revision {p['revision']}</span></div><button onclick="A(1)">Reset</button></header>
<div class="warning">Read-only portable project viewer. Navigation does not save or approve changes. Image state reflects the saved records; ChatGPT Project membership is separate.</div>
<section><div class="titlebar"><h2>Select Act</h2><span class="muted">4 Acts</span></div><div id="acts" class="actrow"></div></section>
<section><div class="titlebar"><h2 id="acttitle">Act 1 / Sequences</h2><span class="muted">3 per Act</span></div><div id="seq" class="sequences"></div></section>
<section><div class="titlebar"><h2 id="blocktitle">Sequence / Blocks</h2><span class="muted">4 Minis per Block</span></div><div id="blocks" class="blocks"></div></section>
<section><div class="titlebar"><div><h2 id="minititle">Block 1 / Mini 1</h2><span class="muted" id="ministats"></span></div><span class="muted">25 positions</span></div><div id="shots" class="shots"></div></section>
<section><div class="muted" id="crumb"></div><h2 id="inspecttitle" style="margin-top:10px">Shot</h2><div class="tabs" id="tabs"></div><div id="detail"></div></section>
<footer class="muted">Portable snapshot of .ppf data. Changes to the project require a new render; navigation does not change story truth.</footer></main>
<script type="application/json" id="model">{body}</script><script>{JS}</script></body></html>'''
    Path(out).write_text(markup,encoding='utf-8')
    return {'bytes':Path(out).stat().st_size,'screenplayPassages':len(passes), 'images':sum(bool(c['image']) for v in shots_by_mini.values() for c in v),'shots':sum(len(v) for v in shots_by_mini.values()), 'sourceWrite':False}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--project',required=True);a.add_argument('--out',required=True)
    args=a.parse_args();print(json.dumps(render(args.project,args.out),indent=2))
