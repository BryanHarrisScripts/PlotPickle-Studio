"""PlotPickle draft editing truth, independent of UI and transport.

This module never changes native PPF Save/Lock/approval.
"""
from __future__ import annotations
import copy
import hashlib
import ipaddress
import json
import pathlib
import socket
from urllib.parse import urlsplit

FPS=24
TRACKS=("video","dialogue","action","foley","ambience","music")
MAX_FRAME=24*60*60*4

class EditError(ValueError):
    pass

def fal_media_url(url: str, resolve=False) -> str:
    if not isinstance(url,str) or len(url)>2048:
        raise EditError('Expected a short fal HTTPS media URL')
    x=urlsplit(url)
    if (x.scheme!="https" or x.hostname!="v3b.fal.media" or x.port not in (None,443)
            or x.username or x.password or x.query or x.fragment or not x.path.startswith('/files/')
            or not x.path.lower().endswith('.mp4')):
        raise EditError('Only direct https://v3b.fal.media/files/*.mp4 URLs are supported')
    if resolve:
        results=socket.getaddrinfo(x.hostname,443,proto=socket.IPPROTO_TCP)
        if not results: raise EditError('fal CDN name could not be resolved')
        for result in results:
            ip=ipaddress.ip_address(result[4][0]);
            if not ip.is_global: raise EditError('fal CDN did not resolve to a public IP')
    return url

def sha(path: pathlib.Path) -> str:
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def initial(seed=None):
    p={"schema":"plotpickle.editor-draft.v1","title":"Untitled Film","source":{"projectId":None,"revision":None,"rawSha256":None,"nativePpfModified":False},"revision":0,"fps":FPS,"media":{},"audioAssets":{},"tracks":{t:[] for t in TRACKS},"script":[],"job":{"state":"idle"},"draftApproved":False}
    if seed:
        if not isinstance(seed,dict) or seed.get('schema')!='plotpickle.editor-seed.v1': raise EditError('Invalid seed')
        p['title']=str(seed.get('title','Untitled Film'))[:150]
        src=seed.get('source',{})
        p['source']={"projectId":src.get('projectId'),"revision":src.get('revision'),"rawSha256":src.get('rawSha256'),"nativePpfModified":False}
        p['script']=[{"id":str(x['id'])[:100],"text":str(x['text'])[:1000],"shot":int(x.get('shot',1))} for x in seed.get('script',[])[:500]]
        for m in seed.get('media',[]):
            mid=str(m['id']);url=fal_media_url(m['url']);
            p['media'][mid]={"id":mid,"status":"pending-transfer","originUrl":url,"sourceProvider":"fal","requestId":str(m.get('requestId',''))[:200],"path":None,"sha256":None,"fps":None,"frames":None}
        for item in seed.get('clips',[]):
            track=item['track'];
            if track not in TRACKS:raise EditError('Unknown seed track')
            clip={"id":str(item['id'])[:80],"label":str(item.get('label',''))[:150],"startFrame":int(item['startFrame']),"durationFrames":int(item['durationFrames']),"mediaId":item.get('mediaId'),"gainDb":float(item.get('gainDb',0)),"note":str(item.get('note',''))[:500],"sourceShot":item.get('sourceShot'),"audioId":item.get('audioId'),"muted":bool(item.get('muted',False))}
            validate_clip(clip)
            p['tracks'][track].append(clip)
    return p

def validate_clip(c):
    if not isinstance(c.get('id'),str) or not c['id'] or len(c['id'])>80:raise EditError('Invalid clip ID')
    for key in ('startFrame','durationFrames'):
        if type(c.get(key)) is not int:raise EditError(key+' must be an integer')
    if c['startFrame']<0 or c['durationFrames']<1 or c['startFrame']+c['durationFrames']>MAX_FRAME:raise EditError('Invalid frame bounds')
    if type(c.get('gainDb')) not in (int,float) or not -80 <= c['gainDb'] <= 12:raise EditError('Invalid gain')
    if c.get('audioId') is not None and (not isinstance(c['audioId'],str) or len(c['audioId'])>64):raise EditError('Invalid audio asset reference')
    if type(c.get('muted',False)) is not bool:raise EditError('Muted must be a boolean')
    return c

def apply_edit(p, edit):
    if type(edit.get('expectedRevision')) is not int or edit['expectedRevision']!=p['revision']:raise EditError('Revision conflict; reload current timeline')
    track=edit.get('track')
    if track not in TRACKS:raise EditError('Unknown track')
    op=edit.get('operation')
    result=copy.deepcopy(p)
    arr=result['tracks'][track]
    if op=='add':
        raw=edit.get('clip',{})
        if not isinstance(raw,dict):raise EditError('Clip required')
        clip={"id":str(raw.get('id','')),"label":str(raw.get('label',''))[:150],"startFrame":raw.get('startFrame'),"durationFrames":raw.get('durationFrames'),"mediaId":raw.get('mediaId'),"gainDb":raw.get('gainDb',0),"note":str(raw.get('note',''))[:500],"sourceShot":raw.get('sourceShot'),"audioId":raw.get('audioId'),"muted":raw.get('muted',False)}
        validate_clip(clip)
        if any(clip['id']==c['id'] for tr in result['tracks'].values() for c in tr):raise EditError('Duplicate clip ID')
        if clip['mediaId'] is not None and clip['mediaId'] not in result['media']:raise EditError('Unknown media reference')
        if clip.get('audioId') is not None and clip['audioId'] not in result.get('audioAssets',{}):raise EditError('Unknown audio reference')
        if track in ('video','action') and clip.get('audioId') is not None:raise EditError('Not an audio lane')
        arr.append(clip)
    else:
        c=next((x for x in arr if x['id']==edit.get('id')),None)
        if c is None:raise EditError('Clip not found in requested track')
        if op=='remove':
            arr.remove(c)
        elif op=='change':
            for key in ('startFrame','durationFrames','gainDb','label','note','muted','audioId'):
                if key in edit:
                    v=edit[key]
                    if key in ('label','note'):
                        if not isinstance(v,str):raise EditError('Invalid text')
                        v=v[:500 if key=='note' else 150]
                    c[key]=v
            validate_clip(c)
            if c.get('audioId') is not None and c['audioId'] not in result.get('audioAssets',{}):raise EditError('Unknown audio reference')
            if track in ('video','action') and c.get('audioId') is not None:raise EditError('Not an audio lane')
        else:raise EditError('Unknown operation')
    result['revision']+=1
    result['job']={'state':'draft-edited'}
    result['draftApproved']=False
    return result

def total_frames(p):
    return max([72]+[c['startFrame']+c['durationFrames'] for tr in p['tracks'].values() for c in tr])

def public_state(p):
    s=copy.deepcopy(p)
    for a in s.get('audioAssets',{}).values():
        a.pop('path',None)
    for m in s['media'].values():
        # Never expose Windows paths or the provider transport URL to the browser.
        # The server explicitly grants a same-origin previewUrl for verified local bytes.
        for key in ('originUrl','path','originalPath'):
            m.pop(key,None)
    return s
