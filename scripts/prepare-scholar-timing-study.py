"""Package the verified same-inference Lewis proof for the isolated character lab.
No synthesis, downloads, live room access or provider calls. Run the timing probe first.
"""
from pathlib import Path
import hashlib,io,json,shutil,wave
ROOT=Path(__file__).resolve().parents[1]

def package():
    report=json.loads((ROOT/'assets/character-production/lewis-timing-proof.json').read_text(encoding='utf-8'))
    source=ROOT/'data/scholar-timing-proof/timed.wav';audio=source.read_bytes()
    digest=hashlib.sha256(audio).hexdigest()
    if digest!=report['timed_wav_sha256'] or not report['same_audio_object'] or not report['identical_pcm_wav']:
        raise ValueError('The local proof waveform does not match its model timing record. Rerun the timing probe.')
    if report['voice']!='bm_lewis' or report['generation_speed']!=.92 or report['approved_playback_rate']!=1.05:raise ValueError('Unapproved voice or pace')
    with wave.open(io.BytesIO(audio),'rb') as wav:
        if wav.getframerate()!=24000 or wav.getnchannels()!=1 or wav.getsampwidth()!=2 or wav.getnframes()!=report['frames']:raise ValueError('Unexpected proof WAV format')
        if abs(wav.getnframes()/wav.getframerate()-report['duration_seconds'])>0.000001:raise ValueError('Cue duration does not match waveform')
    manifest={'schema_version':1,'text':report['text'],'voice':'bm_lewis','generation_speed':.92,'playback_rate':1.05,
      'duration_seconds':report['duration_seconds'],'audio_sha256':digest,'timing_source':'kokoro-model-duration','phonemes':report['phonemes']}
    target=ROOT/'frontend/public/character-lab'
    shutil.copyfile(source,target/'lewis-study.wav')
    (target/'lewis-study.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Packaged verified fixed Lewis clip: {len(audio)} bytes, {len(manifest["phonemes"])} model timing spans.')

if __name__=='__main__':package()
