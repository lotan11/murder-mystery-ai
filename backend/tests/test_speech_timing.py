"""Offline boundaries for model-supplied timing; no optional runtime required."""
import json
import pytest
from backend.speech_timing import MAX_PHONEMES,MAX_TIMING_BYTES,validate_phoneme_timing

def timing():
    return {'source':'kokoro-model-duration','clock':'audio-seconds','phonemes':[
        {'phoneme':'ɡ','start':0.1,'end':0.2},{'phoneme':' ','start':0.2,'end':0.2},{'phoneme':'ə','start':0.4,'end':0.5}]}

def test_source_clock_zero_duration_and_real_pause_gap_are_preserved():
    value=timing();result=validate_phoneme_timing(value,1)
    assert result==value and result is not value and result['phonemes'] is not value['phonemes']

@pytest.mark.parametrize('field,value', [('source','guessed'),('clock','playback-seconds'),('phonemes',[]),('phonemes',None)])
def test_missing_or_guessed_metadata_is_rejected(field,value):
    data=timing();data[field]=value
    with pytest.raises(ValueError):validate_phoneme_timing(data,1)

@pytest.mark.parametrize('field,value', [('start',True),('start',float('nan')),('end',float('inf')),('start',-0.1),('end',1.01),('end',0.05),('phoneme',''),('phoneme','a'*9),('phoneme','\n'),('phoneme','\t'),('phoneme','\u200b'),('phoneme','\ud800')])
def test_bad_symbol_numbers_and_audio_bounds_fail(field,value):
    data=timing();data['phonemes'][0][field]=value
    with pytest.raises(ValueError):validate_phoneme_timing(data,1)

def test_overlapping_and_unknown_fields_are_rejected():
    data=timing();data['phonemes'][1]['start']=0.19
    with pytest.raises(ValueError):validate_phoneme_timing(data,1)
    data=timing();data['extra']='not forwarded'
    with pytest.raises(ValueError):validate_phoneme_timing(data,1)
    data=timing();data['phonemes'][0]['text']='not forwarded'
    with pytest.raises(ValueError):validate_phoneme_timing(data,1)

def test_excessive_cues_and_injected_dictionary_byte_limit_fail():
    data=timing();data['phonemes']=[{'phoneme':'a','start':0,'end':0}]*(MAX_PHONEMES+1)
    with pytest.raises(ValueError):validate_phoneme_timing(data,1)
    # Oversized injected strings are bounded before per-cue validation.
    data=timing();data['phonemes']=[{'phoneme':'😀'*64,'start':0.12345678901234567,'end':0.12345678901234567}]*MAX_PHONEMES
    assert len(json.dumps(data,ensure_ascii=False).encode('utf-8'))>MAX_TIMING_BYTES
    with pytest.raises(ValueError):validate_phoneme_timing(data,1)
