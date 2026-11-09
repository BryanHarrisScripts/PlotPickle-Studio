#!/usr/bin/env python3
"""Non-destructive PlotPickle: actual local fal MP4 bytes -> verified 24 fps shot batch.

No paid provider calls, network, PPF mutation, native Save/Lock, or editor app connection.
Requires current PPF, a private source-linked batch manifest, and real media files.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from fractions import Fraction
from urllib.parse import urlsplit

FPS = 24
FRAMES_PER_SHOT = 72
MAX_BYTES = 200 * 1024 * 1024


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def run(argv: list[str], timeout=300) -> str:
    p = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       text=True, timeout=timeout, check=False)
    if p.returncode:
        raise ValueError(f'{Path(argv[0]).name} failed: {p.stderr[-1000:]}')
    return p.stdout


def probe(path: Path) -> dict:
    d = json.loads(run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries',
        'stream=codec_type,codec_name,width,height,avg_frame_rate,nb_read_frames,nb_frames:'
        'format=duration,size', '-of', 'json', str(path)]))
    vids = [v for v in d.get('streams', []) if v.get('codec_type') == 'video']
    if len(vids) != 1:
        raise ValueError('ONE_VIDEO_STREAM_REQUIRED')
    v = vids[0]
    f = float(Fraction(v['avg_frame_rate']))
    n = next((int(v[k]) for k in ('nb_read_frames', 'nb_frames')
              if v.get(k) not in (None, 'N/A')), None)
    return {'width': int(v['width']), 'height': int(v['height']), 'fps': f,
            'frames': n, 'duration': float(d['format']['duration']),
            'bytes': int(d['format']['size']), 'codec': v.get('codec_name'),
            'audio': any(s.get('codec_type') == 'audio' for s in d.get('streams', []))}


def full_decode(path: Path) -> None:
    run(['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', str(path),
         '-map', '0:v:0', '-f', 'null', '-'], timeout=240)


def check_url(url: str) -> None:
    u = urlsplit(url)
    if (u.scheme != 'https' or u.hostname != 'v3b.fal.media'
        or u.port not in (None, 443) or u.username or u.password
        or u.query or u.fragment or not u.path.startswith('/files/')
        or not u.path.endswith('.mp4')):
        raise ValueError('UNTRUSTED_FAL_VIDEO_URL')


def checked_source(root: Path, filename: str) -> Path:
    if (not isinstance(filename, str) or not filename.endswith('.mp4')
        or Path(filename).name != filename or len(filename) > 120):
        raise ValueError('INPUT_MUST_BE_FLAT_MP4_FILENAME')
    p = (root / filename).resolve(strict=True)
    if not p.is_relative_to(root.resolve()) or not p.is_file():
        raise ValueError('FILE_OUTSIDE_ALLOWED_VIDEO_ROOT')
    if p.stat().st_size < 512 or p.stat().st_size > MAX_BYTES:
        raise ValueError('INVALID_VIDEO_BYTE_LENGTH')
    return p


def source_shot(project: dict, shot: int, block: int, mini: int) -> dict:
    maps = (((project.get('assetRegistry') or {}).get('extensions') or {})
            .get('storyWorkflow') or {}).get('imageMappings') or []
    addr = {'actNumber': 1, 'sequenceNumber': (block + 1) // 2,
            'blockNumber': block, 'miniBlockNumber': mini, 'shotNumber': shot}
    hits = [x for x in maps if isinstance(x, dict) and
            all((x.get('address') or {}).get(k) == v for k,v in addr.items())]
    if len(hits) != 1:
        raise ValueError('SOURCE_SHOT_MAPPING_UNVERIFIABLE')
    ids = {x.get('id') for x in ((project.get('sourceEvidence') or {}).get('screenplay')
                                  or {}).get('passages', []) if isinstance(x, dict)}
    passages = hits[0].get('passageIds') or []
    if not passages or any(i not in ids for i in passages):
        raise ValueError('SOURCE_PASSAGE_ID_UNVERIFIABLE')
    return {'address': addr, 'artifactId': hits[0].get('artifactId'),
            'mappedStillSha256': hits[0].get('sha256'), 'passageIds': passages,
            'stillSaved': hits[0].get('savedMarkerPresent') is True,
            'stillLocked': hits[0].get('locked') is True,
            'actualInputStillIdenticalToPPF': False}


def assemble(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', required=True, type=Path)
    ap.add_argument('--manifest', required=True, type=Path)
    ap.add_argument('--video-root', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ns = ap.parse_args(argv)
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise ValueError('FFMPEG_AND_FFPROBE_REQUIRED')
    source_bytes = ns.project.read_bytes()
    raw_sha = hashlib.sha256(source_bytes).hexdigest()
    project = json.loads(source_bytes)
    m = json.loads(ns.manifest.read_bytes())
    if m.get('schema') != 'plotpickle.fal-shot-batch.v1':
        raise ValueError('UNSUPPORTED_BATCH_MANIFEST')
    if (m.get('projectId') != project.get('id') or
        m.get('revision') != project.get('revision') or
        m.get('rawSha256') != raw_sha):
        raise ValueError('SOURCE_PROJECT_IDENTITY_OR_REVISION_CHANGED')
    block,mini = m.get('block'),m.get('miniBlock')
    if type(block) is not int or type(mini) is not int or not (1 <= block <= 24 and 1 <= mini <= 4):
        raise ValueError('INVALID_BLOCK_ADDRESS')
    shots = m.get('shots')
    if not isinstance(shots, list) or not (1 <= len(shots) <= 5):
        raise ValueError('EXPECTED_1_TO_5_SHOTS')
    numbers = [s.get('shot') for s in shots]
    if (any(type(x) is not int or not 1 <= x <= 25 for x in numbers) or
        numbers != list(range(numbers[0], numbers[0] + len(shots)))):
        raise ValueError('SHOTS_NOT_ORDERED_CONSECUTIVELY')
    sources = []
    for row in shots:
        if row.get('status') != 'completed-provider-video':
            raise ValueError('JOB_NOT_COMPLETED')
        if not row.get('endpointId') or not row.get('requestId'):
            raise ValueError('PROVIDER_IDENTITY_MISSING')
        check_url(row.get('url'))
        source_shot(project, row['shot'], block, mini)
        p = checked_source(ns.video_root, row.get('file'))
        if row.get('reportedBytes') is not None and p.stat().st_size != row['reportedBytes']:
            raise ValueError('MEDIA_BYTES_DIFFER_FROM_PROVIDER_REPORT')
        sources.append(p)
    dest = ns.out.resolve()
    dest.mkdir(parents=True, exist_ok=False)
    try:
        conform_paths, receipts = [], []
        dimensions = None
        for row,src in zip(shots,sources):
            original = dest / f'shot-{row["shot"]:02d}-original.mp4'
            shutil.copyfile(src, original)
            f = probe(original)
            full_decode(original)
            if f['duration'] < 2.99:
                raise ValueError('SOURCE_VIDEO_SHORTER_THAN_SHOT')
            if f['width'] <= 0 or f['height'] <= 0 or max(f['width'],f['height']) > 8192:
                raise ValueError('SOURCE_VIDEO_DIMENSIONS_INVALID')
            if dimensions is None:
                dimensions = (f['width'], f['height'])
            if dimensions != (f['width'], f['height']):
                raise ValueError('MIXED_SOURCE_DIMENSIONS')
            conform = dest / f'shot-{row["shot"]:02d}-24fps.mp4'
            run(['ffmpeg', '-nostdin', '-v','error','-xerror','-n', '-i',str(original),
                 '-map','0:v:0','-vf','fps=24,setsar=1','-frames:v','72','-an',
                 '-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','veryfast',
                 '-r','24','-movflags','+faststart',str(conform)])
            g=probe(conform)
            full_decode(conform)
            if (g['frames'] != FRAMES_PER_SHOT or abs(g['fps']-24) > 0.001
                or abs(g['duration']-3) > 0.04 or g['audio']
                or (g['width'],g['height']) != dimensions):
                raise ValueError('SHOT_CONFORM_FAILED')
            conform_paths.append(conform)
            receipts.append({'shot':row['shot'], 'source':source_shot(project,row['shot'],block,mini),
                'provider': {'endpointId':row['endpointId'],'requestId':row['requestId'],
                             'url':row['url']},
                'original': {'file':original.name,'sha256':sha(original),'facts':f,
                             'fullDecodeVerified':True},
                'conformed': {'file':conform.name,'sha256':sha(conform),'facts':g,
                              'fullDecodeVerified':True},
                'startFrame': (row['shot']-numbers[0])*72,'durationFrames':72,
                'humanReview':'pending', 'nativePpfImported':False})
        output = dest / 'draft-24fps.mp4'
        command=['ffmpeg','-nostdin','-v','error','-xerror','-n']
        for path in conform_paths:
            command += ['-i',str(path)]
        inputs=''.join(f'[{i}:v:0]' for i in range(len(conform_paths)))
        command += ['-filter_complex',f'{inputs}concat=n={len(conform_paths)}:v=1:a=0[v]',
                    '-map','[v]','-frames:v',str(len(shots)*72),'-r','24',
                    '-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-preset','veryfast',
                    '-an','-movflags','+faststart',str(output)]
        run(command, timeout=300)
        combined=probe(output)
        full_decode(output)
        if (combined['frames'] != 72*len(shots) or abs(combined['fps']-24) > 0.001
            or abs(combined['duration']-3*len(shots)) > 0.04
            or combined['audio'] or (combined['width'],combined['height']) != dimensions):
            raise ValueError('FINAL_BATCH_CONFORM_FAILED')
        receipt={'schema':'plotpickle.fal-batch-draft-receipt.v1',
                 'status':'verified-draft-sidecar','projectId':project['id'],
                 'revision':project['revision'],'rawSha256':raw_sha,
                 'address':{'block':block,'miniBlock':mini},'shots':receipts,
                 'combined':{'file':output.name,'sha256':sha(output),'facts':combined,
                             'fullDecodeVerified':True},
                 'review':{'creativeApproval':False,'nativePpfModified':False,
                           'nativePpfImported':False,'localEditorImported':False},
                 'notes':['Actual local video bytes verified; independent shot media integrity does not establish editorial creative acceptance.',
                          'Editor media import and PPF durable Save/Lock remain separate gates.']}
        (dest/'draft-receipt.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
        if hashlib.sha256(ns.project.read_bytes()).hexdigest() != raw_sha:
            raise ValueError('SOURCE_PPF_CHANGED_DURING_INTAKE')
        print(json.dumps({'status':'verified-draft-sidecar','output':str(output),
                          'receipt':str(dest/'draft-receipt.json'),
                          'frames':combined['frames'],'fps':combined['fps'],
                          'sha256':receipt['combined']['sha256'],
                          'nativePpfModified':False},indent=2))
    except BaseException:
        shutil.rmtree(dest, ignore_errors=True)
        raise

if __name__ == '__main__':
    try:
        assemble()
    except Exception as e:
        raise SystemExit(f'PLOTPICKLE_BATCH_INTAKE_BLOCKED: {e}')
