"""Offline validation of duration metadata; no neural runtime or provider calls."""
import importlib.util,json
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('timing_probe',ROOT/'scripts/probe-scholar-timing.py')
probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)

def test_actual_fixed_line_proof_uses_same_inference_audio_and_bounded_model_cues():
    proof=json.loads((ROOT/'assets/character-production/lewis-timing-proof.json').read_text(encoding='utf-8'))
    cues=probe.validate_timings(proof['phonemes'],proof['duration_seconds'])
    assert len(cues)==proof['phoneme_count']>20
    assert proof['same_audio_object'] and proof['identical_pcm_wav']
    assert proof['original_wav_sha256']==proof['timed_wav_sha256']
    assert proof['max_float_difference']==0
    assert proof['generation_speed']==0.92 and proof['approved_playback_rate']==1.05
    assert proof['game_worker_modified'] is False
    assert 'model duration output' in proof['timing_source']

def test_zero_duration_symbols_and_real_pause_gaps_are_preserved():
    cues=[{'phoneme':'a','start':0.1,'end':0.2},{'phoneme':' ','start':0.2,'end':0.2},{'phoneme':'b','start':0.4,'end':0.5}]
    assert probe.validate_timings(cues,1)==cues

@pytest.mark.parametrize('cues',[
    [],[{'phoneme':'a','start':-0.1,'end':0.2}],
    [{'phoneme':'a','start':0.1,'end':1.1}],
    [{'phoneme':'a','start':0.1,'end':0.5},{'phoneme':'b','start':0.4,'end':0.6}],
    [{'phoneme':'a','start':float('nan'),'end':0.2}],
    [{'phoneme':'a','start':True,'end':0.2}],
    [{'phoneme':'a','start':0.1,'end':0.2,'guessed':True}],
])
def test_invalid_or_invented_metadata_is_rejected(cues):
    with pytest.raises(ValueError):probe.validate_timings(cues,1)


def test_packaged_lab_clip_matches_its_own_model_cues_and_approved_voice():
    import hashlib,io,wave
    directory=ROOT/'frontend/public/character-lab'
    manifest=json.loads((directory/'lewis-study.json').read_text(encoding='utf-8'))
    audio=(directory/'lewis-study.wav').read_bytes()
    assert hashlib.sha256(audio).hexdigest()==manifest['audio_sha256']
    assert manifest['schema_version']==1 and manifest['voice']=='bm_lewis'
    assert manifest['generation_speed']==.92 and manifest['playback_rate']==1.05
    assert manifest['timing_source']=='kokoro-model-duration'
    with wave.open(io.BytesIO(audio),'rb') as wav:
        assert wav.getnchannels()==1 and wav.getframerate()==24000 and wav.getsampwidth()==2
        assert abs(wav.getnframes()/24000-manifest['duration_seconds'])<0.000001
    cues=probe.validate_timings(manifest['phonemes'],manifest['duration_seconds'])
    proof=json.loads((ROOT/'assets/character-production/lewis-timing-proof.json').read_text(encoding='utf-8'))
    assert cues==proof['phonemes'] and manifest['audio_sha256']==proof['timed_wav_sha256']


def test_longer_proof_is_tied_to_only_canonical_public_narration():
    import hashlib
    case_bytes=(ROOT/'backend/cases/blackthorn.json').read_bytes()
    case=json.loads(case_bytes)
    report=json.loads((ROOT/'assets/character-production/lewis-long-timing-proof.json').read_text(encoding='utf-8'))
    canonical=json.dumps(case,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    assert report['source_content_sha256']==hashlib.sha256(canonical).hexdigest()
    assert report['public_source_fields']==['narration.welcome','narration.start','narration.advance']
    assert report['text']==' '.join(case['narration'][name] for name in ['welcome','start','advance'])
    assert 40<=report['word_count']==len(report['text'].split())<=80
    assert report['voice']=='bm_lewis' and report['generation_speed']==.92 and report['approved_playback_rate']==1.05
    assert abs(report['duration_seconds']-report['frames']/report['sample_rate'])<.000001
    assert report['phoneme_count']>73 and report['out_of_bounds_cues']==report['overlapping_cues']==0
    assert report['sidecar_bytes']<512*1024 and report['worker_elapsed_seconds_observed']<report['worker_timeout_seconds']==40
    assert report['downloads'] is False and report['paid_calls'] is False and report['live_game_modified'] is False


def test_case_content_evidence_hash_is_portable_but_detects_changed_facts():
    spec=importlib.util.spec_from_file_location('long_timing_probe',ROOT/'scripts/probe-scholar-long-timing.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    lf=b'{\n  "narration": {"welcome": "Public line."}, "version": 1\n}\n'
    assert module.case_content_hash(lf)==module.case_content_hash(lf.replace(b'\n',b'\r\n'))
    changed=lf.replace(b'Public line.',b'Changed line.')
    assert module.case_content_hash(lf)!=module.case_content_hash(changed)


def test_cache_probe_reuses_one_validated_public_clip_within_memory_budget():
    import hashlib
    case_bytes=(ROOT/'backend/cases/blackthorn.json').read_bytes();case=json.loads(case_bytes)
    report=json.loads((ROOT/'assets/character-production/lewis-cache-proof.json').read_text(encoding='utf-8'))
    canonical=json.dumps(case,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    assert report['source_content_sha256']==hashlib.sha256(canonical).hexdigest()
    assert report['text']==' '.join(case['narration'][name] for name in ['welcome','start','advance'])
    assert report['worker_spawns_cold']==report['worker_spawns_total_after_warm']==1
    assert report['identical_result'] and report['fresh_warm_result_copy']
    assert report['cache_info_observed']['entries']==1
    assert 0<report['cache_info_observed']['payload_bytes']<=report['configured_cache_limits']['cache_max_bytes']
    assert report['generation_files_remaining'] is False and report['live_game_modified'] is False
    assert report['room_authorization_changed'] is False and report['http_cache_policy_changed'] is False
    assert report['voice']=='bm_lewis' and report['generation_speed']==.92 and report['playback_rate']==1.05
    assert report['phoneme_count']>73 and len(report['audio_sha256'])==len(report['matching_timing_sha256'])==64
