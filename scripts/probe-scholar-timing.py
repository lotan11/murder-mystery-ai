"""Offline proof of model-supplied Lewis phoneme timing; never changes game speech.
Run with data/casting-runtime/Scripts/python.exe. No downloads or paid providers.
"""
from pathlib import Path
import argparse,hashlib,importlib.metadata,importlib.util,json,math
ROOT=Path(__file__).resolve().parents[1]
TEXT='Good evening. I am Detective Wobblebottom. Let us examine the evidence.'

def validate_timings(items,duration_seconds):
    if not isinstance(items,list) or not items or len(items)>10000:raise ValueError('Missing or excessive phoneme timings')
    if type(duration_seconds) not in (int,float) or not math.isfinite(duration_seconds) or not 0<duration_seconds<=170:raise ValueError('Invalid audio duration')
    result=[];previous=0
    for item in items:
        if not isinstance(item,dict) or set(item)!={'phoneme','start','end'}:raise ValueError('Invalid timing entry')
        phoneme,start,end=item['phoneme'],item['start'],item['end']
        if not isinstance(phoneme,str) or not 1<=len(phoneme)<=8:raise ValueError('Invalid phoneme')
        if any(type(value) not in (int,float) or not math.isfinite(value) for value in [start,end]):raise ValueError('Invalid timing number')
        if start<previous-0.000001 or not 0<=start<=end<=duration_seconds+0.000001:raise ValueError('Timing outside audio or overlapping')
        result.append({'phoneme':phoneme,'start':start,'end':end});previous=end
    return result

def main(output):
    if importlib.metadata.version('kokoro-onnx')!='0.6.1':raise RuntimeError('Use approved pinned optional runtime')
    spec=importlib.util.spec_from_file_location('casting',ROOT/'scripts/prepare-casting.py')
    preparation=importlib.util.module_from_spec(spec);spec.loader.exec_module(preparation)
    models=ROOT/'data/casting-models';preparation.ensure_models(models,allow_download=False)
    import numpy as np
    import soundfile as sf
    from kokoro_onnx import Kokoro
    engine=Kokoro(str(models/'kokoro-v1.0.onnx'),str(models/'voices-v1.0.bin'))
    if not engine.has_timings:raise RuntimeError('Approved model has no duration output; do not invent timings')
    # create() already delegates to create_timed() and discards its timing result.
    # Capture that SAME inference, since separate neural renders need not be byte-identical.
    original_timed=engine.create_timed;captured={}
    def capture(*args,**kwargs):
        result=original_timed(*args,**kwargs)
        captured['result']=result
        return result
    engine.create_timed=capture
    original,rate=engine.create(TEXT,voice='bm_lewis',speed=.92,lang='en-gb')
    timed,timed_rate,spans=captured['result']
    if rate!=24000 or timed_rate!=rate or len(original)!=len(timed):raise RuntimeError('Timed path changed audio format')
    output.mkdir(parents=True,exist_ok=True)
    original_path=output/'original.wav';timed_path=output/'timed.wav'
    sf.write(str(original_path),original,rate,subtype='PCM_16');sf.write(str(timed_path),timed,rate,subtype='PCM_16')
    original_hash=hashlib.sha256(original_path.read_bytes()).hexdigest();timed_hash=hashlib.sha256(timed_path.read_bytes()).hexdigest()
    if original_hash!=timed_hash:raise RuntimeError('Timed path changed PCM audio; review before any adoption')
    duration=len(timed)/rate
    cues=validate_timings([{'phoneme':span.phoneme,'start':float(span.start),'end':float(span.end)} for span in spans],duration)
    report={'text':TEXT,'provider':'kokoro-onnx','version':'0.6.1','voice':'bm_lewis','generation_speed':.92,
      'approved_playback_rate':1.05,'timing_clock':'seconds on original WAV; use audio.currentTime at 1.05 playback',
      'timing_source':'model duration output mapped by kokoro-onnx to emitted audio samples; not text-proportional estimates or external forced alignment',
      'sample_rate':rate,'frames':len(timed),'duration_seconds':duration,'phoneme_count':len(cues),
      'capture_method':'Timing captured from the same inference inside existing create(); no second synthesis or audio alteration',
      'same_audio_object':original is timed,'identical_pcm_wav':True,'original_wav_sha256':original_hash,'timed_wav_sha256':timed_hash,
      'max_float_difference':float(np.max(np.abs(np.asarray(original)-np.asarray(timed)))),
      'models_sha256':{name:metadata['sha256'] for name,metadata in preparation.MODEL_FILES.items()},
      'phonemes':cues,'game_worker_modified':False,'limitations':['Short fixed-line proof only; long-line boundaries, perception and runtime bounds still require review.',
      'Separate neural renders are not byte-deterministic; retain timestamps from the same inference as their waveform.',
      'Model-predicted durations are not manually annotated ground truth. No viseme mapping, facial playback or production activation.']}
    path=ROOT/'assets/character-production/lewis-timing-proof.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:report[key] for key in ['phoneme_count','duration_seconds','identical_pcm_wav','max_float_difference']}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'data/scholar-timing-proof');args=parser.parse_args();main(args.output)
