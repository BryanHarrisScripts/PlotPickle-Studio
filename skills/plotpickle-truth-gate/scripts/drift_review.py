#!/usr/bin/env python3
"""Non-destructive visual DRIFTED label for explicitly inspected failed candidates."""
import argparse,hashlib,json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

def sha(data):return hashlib.sha256(data).hexdigest()
def stamp(args):
    if args.status != 'DRIFTED': raise ValueError('ONLY DRIFTED semantic state may be marked')
    if not args.reason.strip():raise ValueError('specific drift reason required')
    src=Path(args.image).resolve(); out=Path(args.out).resolve()
    if src==out:raise ValueError('never overwrite original image')
    if not src.is_file():raise ValueError('missing original image')
    if out.exists():raise ValueError('output already exists')
    if out.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):raise ValueError('unsupported output')
    raw=src.read_bytes();before=sha(raw)
    with Image.open(src) as loaded:
        loaded.load();im=loaded.convert('RGBA')
    w,h=im.size
    layer=Image.new('RGBA',(w,h),(0,0,0,0));d=ImageDraw.Draw(layer)
    size=max(18,round(min(w/6,h/3)))
    try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',size)
    except OSError:font=ImageFont.load_default()
    word='DRIFTED';b=d.textbbox((0,0),word,font=font,stroke_width=max(1,size//50));tw=b[2]-b[0];th=b[3]-b[1]
    d.rounded_rectangle((w//16,int(h*.37),w-w//16,int(h*.65)),radius=max(5,w//100),fill=(145,0,0,210))
    d.text(((w-tw)/2,(h-th)/2-b[1]),word,font=font,fill=(255,255,255,255),stroke_width=max(1,size//50),stroke_fill=(0,0,0,255))
    out.parent.mkdir(parents=True,exist_ok=True)
    result=Image.alpha_composite(im,layer)
    if out.suffix.lower() in ('.jpg','.jpeg'):result.convert('RGB').save(out,quality=93)
    else:result.save(out)
    if sha(src.read_bytes())!=before: raise ValueError('original bytes changed unexpectedly')
    receipt={'schema':'plotpickle.truth-gate.drift-mark.v1','semanticState':'DRIFTED','reason':args.reason,'originalFile':src.name,'originalSha256':before,'markedReviewFile':out.name,'markedReviewSha256':sha(out.read_bytes()),'usableForProduction':False,'originalPreserved':True}
    receipt_path=out.with_suffix(out.suffix+'.receipt.json')
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))

def gate(args):
    d=json.loads(Path(args.review).read_text());issues=[]
    for r in d.get('shots',[]):
        addr=r.get('productionAddress','?');state=r.get('semanticState','UNKNOWN')
        if state not in ('PASS','DRIFTED','REVIEW_REQUIRED','UNKNOWN'):issues.append([addr,'invalid state']);continue
        needed=('humanApproved','nativeSaved','nativeLocked','libraryReadbackVerified','sourceSha256','mediaSha256','scriptPassageIds','approvedVisualRefs')
        missing=[x for x in needed if not r.get(x)]
        ready=(state=='PASS' and not missing)
        if state=='DRIFTED' and not r.get('reason'):missing.append('drift reason')
        if r.get('usableForProduction',False)!=ready:issues.append([addr,'incorrect usability',state,missing])
    print(json.dumps({'schema':'plotpickle.truth-gate.audit.v1','shots':len(d.get('shots',[])),'issues':issues,'gatePassed':not issues},indent=2))
    if issues:sys.exit(2)

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
    s=sub.add_parser('stamp');s.add_argument('--image',required=True);s.add_argument('--out',required=True);s.add_argument('--status',required=True);s.add_argument('--reason',required=True)
    g=sub.add_parser('gate');g.add_argument('--review',required=True)
    a=p.parse_args()
    try:stamp(a) if a.cmd=='stamp' else gate(a)
    except (OSError,ValueError,KeyError) as e: print('ERROR:',e,file=sys.stderr);sys.exit(2)
