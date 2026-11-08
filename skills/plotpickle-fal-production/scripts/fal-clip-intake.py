#!/usr/bin/env python3
"""PlotPickle: source-pinned fal video -> verified 24-fps draft clip.

Operates on one completed fal job, saved source PPF, and real video bytes.
Does NOT submit fal jobs, spend credits, mutate PPF or mark the shot accepted.
A host with HTTPS access may fetch the fal CDN URL; otherwise use --video FILE.
Never silently substitute another source when its bytes are unavailable.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
from urllib.parse import urlsplit
from fractions import Fraction

TARGET_FPS = 24
MAX_VIDEO_BYTES = 200 * 1024 * 1024
FAL_DOMAINS = ('fal.media', 'fal.ai')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda: f.read(1024*1024), b''):
            h.update(c)
    return h.hexdigest()


def run(args):
    p = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f'{args[0]} exited {p.returncode}: {p.stderr[-1500:]}')
    return p.stdout


def probe(path: Path) -> dict:
    info = json.loads(run(['ffprobe', '-v', 'error', '-count_frames',
        '-show_entries', 'format=duration,size,format_name:stream=index,codec_type,codec_name,width,height,avg_frame_rate,nb_read_frames,nb_frames,duration',
        '-of', 'json', str(path)]))
    videos = [s for s in info.get('streams', []) if s.get('codec_type') == 'video']
    if len(videos) != 1:
        raise ValueError('EXPECTED_ONE_VIDEO_STREAM')
    video = videos[0]
    def numframes(v):
        for k in ('nb_read_frames','nb_frames'):
            try: return int(v[k])
            except (ValueError, TypeError, KeyError): pass
        return None
    try: fps = float(Fraction(video['avg_frame_rate']))
    except (KeyError, ZeroDivisionError): raise ValueError('VIDEO_FPS_UNREADABLE')
    return dict(width=video['width'], height=video['height'], fps=fps,
                frames=numframes(video), duration=float(info['format']['duration']),
                bytes=int(info['format']['size']), codec=video.get('codec_name'),
                audio=any(s.get('codec_type')=='audio' for s in info.get('streams',[])))


def check_fal_video_url(url: str) -> None:
    parsed = urlsplit(url)
    name = (parsed.hostname or '').lower()
    if parsed.scheme != 'https' or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError('UNSAFE_FAL_MEDIA_URL')
    if not any(name == d or name.endswith('.'+d) for d in FAL_DOMAINS):
        raise ValueError('UNRECOGNIZED_FAL_MEDIA_HOST')


def fetch(url: str, path: Path) -> None:
    check_fal_video_url(url)
    # Avoid a redirected request to unrelated hosts or internal network destinations.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise ValueError('REMOTE_REDIRECT_NOT_ACCEPTED')
    opener = urllib.request.build_opener(NoRedirect)
    request = urllib.request.Request(url, headers={'User-Agent':'PlotPickle-Fal-Clip-Intake/1.0'})
    total = 0
    with opener.open(request, timeout=45) as response, path.open('xb') as out:
        if response.status != 200:
            raise ValueError(f'FAL_MEDIA_HTTP_{response.status}')
        length = response.headers.get('Content-Length')
        if length and int(length) > MAX_VIDEO_BYTES:
            raise ValueError('MEDIA_TOO_LARGE')
        while True:
            part = response.read(1024 * 1024)
            if not part: break
            total += len(part)
            if total > MAX_VIDEO_BYTES:
                raise ValueError('MEDIA_TOO_LARGE')
            out.write(part)
    if total < 512:
        raise ValueError('MEDIA_TOO_SMALL_OR_EMPTY')


def source_mapping(project: dict, act: int, seq: int, block: int, mini: int, shot: int):
    all_maps = (((project.get('assetRegistry') or {}).get('extensions') or {}).get('storyWorkflow') or {}).get('imageMappings') or []
    addr = dict(actNumber=act, sequenceNumber=seq, blockNumber=block, miniBlockNumber=mini, shotNumber=shot)
    matched = [m for m in all_maps if isinstance(m, dict) and all((m.get('address') or {}).get(k)==v for k,v in addr.items())]
    if len(matched)!=1:
        raise ValueError(f'SOURCE_SHOT_MAPPING_COUNT_{len(matched)}')
    m = matched[0]
    ids = {x.get('id') for x in ((project.get('sourceEvidence') or {}).get('screenplay') or {}).get('passages',[]) if isinstance(x,dict)}
    passages = m.get('passageIds',[])
    if not passages or not all(s in ids for s in passages):
        raise ValueError('SCREENPLAY_PROVENANCE_MISSING')
    return m, addr


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', required=True, type=Path)
    ap.add_argument('--result', required=True, type=Path, help='Completed fal response JSON with request_id, result.video')
    ap.add_argument('--out', required=True, type=Path, help='New directory; existing directory is refused')
    ap.add_argument('--video', type=Path, help='Existing MP4 bytes; omit only when host permits fal CDN download')
    ap.add_argument('--allow-fal-download', action='store_true')
    ap.add_argument('--act', type=int, default=1); ap.add_argument('--sequence', type=int, default=1)
    ap.add_argument('--block', type=int, required=True); ap.add_argument('--mini', type=int, required=True)
    ap.add_argument('--shot', type=int, required=True)
    ap.add_argument('--frames-per-shot', type=int, default=72)
    ap.add_argument('--expected-project-sha', help='Fail on source revision drift')
    ns=ap.parse_args(argv)
    for x in ('ffmpeg','ffprobe'):
        if not shutil.which(x):
            raise RuntimeError(f'MISSING_{x.upper()}')
    if ns.frames_per_shot!=72:
        raise ValueError('CANONICAL_SHOT_MUST_BE_72_FRAMES')
    for v, a,b in [(ns.act,1,4),(ns.sequence,1,12),(ns.block,1,24),(ns.mini,1,4),(ns.shot,1,25)]:
        if not (a<=v<=b):raise ValueError('INVALID_SHOT_ADDRESS')
    if (ns.act-1)*3 != (ns.sequence-1)//3*3 or ns.block not in (2*ns.sequence-1,2*ns.sequence):
        raise ValueError('INCONSISTENT_CANONICAL_ADDRESS')
    ppf_bytes=ns.project.read_bytes()
    ppf_hash=hashlib.sha256(ppf_bytes).hexdigest()
    if ns.expected_project_sha and ppf_hash != ns.expected_project_sha:
        raise ValueError('SOURCE_PROJECT_SHA_MISMATCH')
    project=json.loads(ppf_bytes)
    if not isinstance(project.get('id'),str) or type(project.get('revision'))!=int:
        raise ValueError('INVALID_PPF_ID_OR_REVISION')
    mapping, address = source_mapping(project,ns.act,ns.sequence,ns.block,ns.mini,ns.shot)
    obj=json.loads(ns.result.read_text())
    if obj.get('status')!='COMPLETED' or obj.get('has_result') is False:
        raise ValueError('FAL_JOB_NOT_COMPLETED')
    model=obj.get('endpoint_id') or obj.get('provider',{}).get('endpoint_id')
    request=obj.get('request_id')
    video_info=(obj.get('result') or {}).get('video') or {}
    media_url=video_info.get('url')
    if not model or not request or not media_url:
        raise ValueError('FAL_RESULT_MISSING_JOB_OR_MEDIA')
    check_fal_video_url(media_url)
    dest=ns.out.resolve()
    dest.mkdir(parents=True,exist_ok=False)
    downloaded=False
    source=dest/'source-30fps.mp4'
    try:
        if ns.video:
            # Keep the original intact, and avoid mutating the caller's file.
            shutil.copyfile(ns.video,source)
        elif ns.allow_fal_download:
            fetch(media_url,source)
            downloaded=True
        else:
            raise ValueError('MEDIA_BYTES_UNAVAILABLE_USE_VIDEO_OR_ALLOW_FAL_DOWNLOAD')
        sourcefacts=probe(source)
        run(['ffmpeg','-v','error','-xerror','-i',str(source),'-map','0:v:0','-f','null','-'])
        if sourcefacts['duration'] < 2.99:
            raise ValueError('SOURCE_VIDEO_SHORTER_THAN_3_SECONDS')
        if video_info.get('file_size') and source.stat().st_size != int(video_info['file_size']):
            raise ValueError('FAL_VIDEO_FILE_SIZE_MISMATCH')
        if video_info.get('width') and sourcefacts['width'] != video_info['width']:
            raise ValueError('VIDEO_WIDTH_MISMATCH')
        if video_info.get('height') and sourcefacts['height'] != video_info['height']:
            raise ValueError('VIDEO_HEIGHT_MISMATCH')
        out=dest/'draft-24fps.mp4'
        run(['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-n','-i',str(source),
            '-map','0:v:0','-vf','fps=24,setsar=1','-frames:v','72',
            '-c:v','libx264','-pix_fmt','yuv420p','-preset','medium','-crf','18','-an',
            '-r','24','-movflags','+faststart',str(out)])
        outfacts=probe(out)
        if outfacts['frames']!=72 or abs(outfacts['fps']-24)>0.01 or abs(outfacts['duration']-3.0)>0.04:
            raise ValueError('CONFORM_DID_NOT_MEET_72_FRAME_GATE')
        if (outfacts['width'],outfacts['height'])!=(sourcefacts['width'],sourcefacts['height']):
            raise ValueError('CONFORM_DIMENSIONS_CHANGED')
        if outfacts['audio']:
            raise ValueError('CONFORM_HAS_UNEXPECTED_AUDIO')
        run(['ffmpeg','-v','error','-xerror','-i',str(out),'-map','0:v:0','-f','null','-'])
        receipt={
            'schema':'plotpickle.fal-draft-intake.v1',
            'registration':'verified-draft-sidecar',
            'source':{'projectId':project['id'],'revision':project['revision'],'rawSha256':ppf_hash,
                      'title':project.get('title'),'shot':address,'storyboardArtifactId':mapping.get('artifactId'),
                      'passageIds':mapping['passageIds'],'mappedStillSha256':mapping.get('sha256'),
                      'mappedStillBytesVerified':False,
                      'stillSaved':mapping.get('savedMarkerPresent') is True,
                      'stillLocked':mapping.get('locked') is True,
                      'sameFrameAsNativePPFMappingVerified':False},
            'provider':{'name':'fal','model':model,'requestId':request,'originalUrl':media_url,
                        'seed':(obj.get('result') or {}).get('seed')},
            'originalVideo':{'path':'source-30fps.mp4','sha256':sha256(source),'fullDecodePassed':True,
                             'downloadedByIntake':downloaded,**sourcefacts},
            'editorialVideo':{'path':'draft-24fps.mp4','sha256':sha256(out),'fullDecodePassed':True,**outfacts},
            'review':{'status':'draft-pending-creative-review','accepted':False,'nativePPFImported':False,
                      'nativePPFModified':False,'saveLocked':False},
            'notes':['Draft registration is a sidecar, not an accepted or locked native PPF video asset.',
                     'The generated first frame is not proven to equal the native mapped image; inspect visual continuity before acceptance.']
        }
        (dest/'draft-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'status':'verified-draft-sidecar','path':str(out),'receipt':str(dest/'draft-receipt.json'),
                          'sha256':sha256(out),'frames':outfacts['frames'],'fps':outfacts['fps'],
                          'nativePPFModified':False},indent=2))
        return 0
    except BaseException:
        # Don't leave a half-written directory that could be mistaken for a verified draft.
        shutil.rmtree(dest,ignore_errors=True)
        raise

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:
        print(f'PLOTPICKLE_FAL_INTAKE_BLOCKED: {e}',file=sys.stderr)
        sys.exit(1)
