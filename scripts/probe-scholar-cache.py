"""Measure real cold/warm approved Lewis rendering in an isolated process.
No downloads, paid provider calls or live room access; no waveform is persisted.
"""
from pathlib import Path
import asyncio,base64,hashlib,importlib.util,json,sys,time
ROOT=Path(__file__).resolve().parents[1]

async def main():
    sys.path.insert(0,str(ROOT))
    from backend.scholar_speech import ScholarSpeechRenderer,PROCESS_TIMEOUT
    spec=importlib.util.spec_from_file_location('public_long_probe',ROOT/'scripts/probe-scholar-long-timing.py')
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    case_bytes=(ROOT/'backend/cases/blackthorn.json').read_bytes();case=json.loads(case_bytes)
    text=' '.join(case['narration'][name] for name in source.PUBLIC_FIELDS)
    limits={'cache_max_entries':4,'cache_max_bytes':32*1024*1024,'cache_ttl':900.0}
    base=ROOT/'data/scholar-cache-proof'
    renderer=ScholarSpeechRenderer(base_dir=base,**limits)
    if not renderer.available:raise RuntimeError('Prepare the approved optional runtime/models first; this probe never installs or downloads them')
    original_spawn=asyncio.create_subprocess_exec;spawns=0
    async def counted_spawn(*args,**kwargs):
        nonlocal spawns
        spawns+=1
        return await original_spawn(*args,**kwargs)
    asyncio.create_subprocess_exec=counted_spawn
    try:
        started=time.monotonic();cold=await renderer.render(text);cold_seconds=time.monotonic()-started
        after_cold=spawns
        started=time.monotonic();warm=await renderer.render(text);warm_seconds=time.monotonic()-started
    finally:asyncio.create_subprocess_exec=original_spawn
    if after_cold!=1 or spawns!=1 or cold!=warm or cold is warm:raise RuntimeError('Warm rendering did not reuse an isolated copy of the validated clip')
    if cold.get('voice')!='bm_lewis' or cold.get('playback_rate')!=1.05 or cold.get('text')!=text:raise RuntimeError('Approved identity or public text changed')
    cue=cold.get('phoneme_timing')
    if not cue or cue.get('source')!='kokoro-model-duration' or cue.get('clock')!='audio-seconds':raise RuntimeError('The matching model cue set was not retained')
    waveform=base64.b64decode(cold['audio_base64'],validate=True)
    if base.exists() and any(base.iterdir()):raise RuntimeError('Generation files remain after renderer cleanup')
    cache_info=renderer._cache.info()
    if cache_info['entries']!=1 or not 0<cache_info['payload_bytes']<=cache_info['max_bytes']:raise RuntimeError('Cache budget observation invalid')
    report={'cache_info_observed':cache_info,'probe':'real isolated approved Lewis renderer cold/warm cache','source':'backend/cases/blackthorn.json',
      'source_content_sha256':source.case_content_hash(case_bytes),'public_source_fields':['narration.'+name for name in source.PUBLIC_FIELDS],
      'text':text,'word_count':len(text.split()),'character_count':len(text),'voice':'bm_lewis','generation_speed':.92,'playback_rate':1.05,
      'duration_ms':cold['duration_ms'],'phoneme_count':len(cue['phonemes']),
      'cold_seconds_observed':round(cold_seconds,6),'warm_seconds_observed':round(warm_seconds,6),
      'worker_spawns_cold':after_cold,'worker_spawns_total_after_warm':spawns,'identical_result':True,'fresh_warm_result_copy':True,
      'audio_sha256':hashlib.sha256(waveform).hexdigest(),
      'matching_timing_sha256':hashlib.sha256(json.dumps(cue,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest(),
      'configured_cache_limits':limits,'worker_timeout_seconds':PROCESS_TIMEOUT,'generation_files_remaining':False,
      'http_cache_policy_changed':False,'room_authorization_changed':False,'paid_calls':False,'downloads':False,'live_game_modified':False,
      'limitations':['One local cold/warm observation, not an interactive or cross-device performance guarantee.',
        'A warm cache helps repeated identical public dialogue only; first generation, misses and expired/evicted entries remain cold.',
        'This does not change avatar quality, model timing accuracy, voice identity, pace or live-game activation.']}
    (ROOT/'assets/character-production/lewis-cache-proof.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({name:report[name] for name in ['cold_seconds_observed','warm_seconds_observed','worker_spawns_total_after_warm','phoneme_count']}))

if __name__=='__main__':asyncio.run(main())
