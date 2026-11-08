"""Local original demo-audio generation and frame-exact FFmpeg mix helpers.

No network requests, external audio assets, or paid service calls.
The generated assets are clearly NON-PRODUCTION placeholders.
"""
from __future__ import annotations
import math
import pathlib
import random
import struct
import wave

SAMPLE_RATE=48000
DEMO_SECONDS=4

def create_demo_wav(path: pathlib.Path, kind: str) -> None:
    if kind not in ('ocean', 'gulls'):
        raise ValueError('Unknown demo sound')
    if path.exists():
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    rng=random.Random(20261108 if kind=='ocean' else 20261109)
    tmp=path.with_suffix('.tmp.wav')
    with wave.open(str(tmp),'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        smoothed=0.0
        chunk=bytearray()
        for i in range(SAMPLE_RATE*DEMO_SECONDS):
            t=i/SAMPLE_RATE
            if kind=='ocean':
                # Synthetic pink-ish surf hiss, slowly modulated to suggest gentle wash.
                smoothed=0.92*smoothed+0.08*rng.uniform(-1,1)
                swell=0.55+0.3*math.sin(2*math.pi*.34*t)
                signal=smoothed*swell*.28 + rng.uniform(-1,1)*.014
            else:
                # Quiet, stylized gull-like sweeps. NOT field-recorded wildlife.
                signal=0.0
                for start,duration,base in ((.6,.65,830),(2.15,.55,670)):
                    u=(t-start)/duration
                    if 0<=u<=1:
                        env=math.sin(math.pi*u)**2
                        phase=2*math.pi*(base*(t-start)+240*(t-start)**2)
                        signal+=.13*env*(math.sin(phase)+.2*math.sin(phase*2))
                signal+=rng.uniform(-1,1)*.001
            n=max(-32767,min(32767,round(signal*32767)))
            chunk+=struct.pack('<hh',n,n)
            if len(chunk)>=32768:
                w.writeframesraw(chunk)
                chunk.clear()
        if chunk:w.writeframesraw(chunk)
    tmp.replace(path)


def audio_filter_spec(cues, frames):
    """Produces independent, precisely timed 48k sample tracks for audio mix.

    Each cue dict supplies ffmpeg input_index and independently verified media.
    No text is inserted into FFmpeg's filter expression from user fields.
    """
    if not cues:
        # Proper silent reference for a picture-only draft.
        return None
    if len(cues)>24:
        raise ValueError('Too many audio cues')
    filters=[]
    for idx,c in enumerate(cues):
        start=c['startFrame']*2000
        length=c['durationFrames']*2000
        gain=10**(c['gainDb']/20)
        inp=c['input_index']
        # Trim before delay, so offsets are exact multiples of audio samples.
        filters.append(f'[{inp}:a:0]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,atrim=end_sample={length},asetpts=PTS-STARTPTS,volume={gain:.9f},adelay={start}S|{start}S[a{idx}]')
    tags=''.join(f'[a{idx}]' for idx in range(len(cues)))
    total=frames*2000
    filters.append(f'{tags}amix=inputs={len(cues)}:duration=longest:normalize=0:dropout_transition=0,alimiter=limit=0.95,apad=whole_len={total},atrim=end_sample={total}[mix]')
    return ';'.join(filters)
