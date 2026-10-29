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
