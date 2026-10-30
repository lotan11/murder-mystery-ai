"""Behavioral cache boundaries; no audio provider, clock sleeping or room data."""
import json
import pytest
from backend.speech_cache import SpeechCache


def test_cache_returns_fresh_nested_copy_and_no_sensitive_inspection():
    cache=SpeechCache()
    value={'text':'Public detective line','phoneme_timing':{'phonemes':[{'phoneme':'ə','start':0,'end':1}]}}
    assert cache.put('hashed identity',value)
    value['phoneme_timing']['phonemes'][0]['end']=999
    first=cache.get('hashed identity')
    assert first['phoneme_timing']['phonemes'][0]['end']==1
    first['phoneme_timing']['phonemes'].clear()
    assert len(cache.get('hashed identity')['phoneme_timing']['phonemes'])==1
    assert 'Public detective line' not in json.dumps(cache.info())
    assert 'hashed identity' not in json.dumps(cache.info())


def test_ttl_expires_at_boundary_and_hits_do_not_extend_it():
    now=[10.0];cache=SpeechCache(ttl=5,clock=lambda:now[0])
    cache.put('a',{'value':1});now[0]=14.9
    assert cache.get('a')=={'value':1}
    now[0]=15
    assert cache.get('a') is None and cache.info()['payload_bytes']==0


def test_lru_count_and_exact_utf8_payload_budget_evict_without_disk():
    cache=SpeechCache(max_entries=2)
    cache.put('a',{'text':'one'});cache.put('b',{'text':'two'})
    assert cache.get('a')=={'text':'one'}
    cache.put('c',{'text':'three'})
    assert cache.get('b') is None and cache.get('a') is not None and cache.get('c') is not None
    data={'text':'ə'};encoded=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    bounded=SpeechCache(max_bytes=len(encoded),max_entries=4)
    bounded.put('a',data);bounded.put('b',data)
    assert bounded.get('a') is None and bounded.get('b')==data
    assert bounded.info()['payload_bytes']==len(encoded)


def test_oversized_or_disabled_cache_never_evicts_a_valid_entry_or_stores_payload():
    cache=SpeechCache(max_bytes=25)
    cache.put('small',{'v':1})
    assert not cache.put('large',{'v':'x'*100})
    assert cache.get('small')=={'v':1} and cache.get('large') is None
    for kwargs in [{'max_entries':0},{'max_bytes':0},{'ttl':0}]:
        disabled=SpeechCache(**kwargs)
        assert not disabled.put('a',{'v':1}) and disabled.get('a') is None


@pytest.mark.parametrize('kwargs',[{'max_entries':True},{'max_bytes':-1},{'ttl':float('nan')},{'ttl':-1},{'clock':None}])
def test_invalid_policy_is_rejected(kwargs):
    with pytest.raises(ValueError):SpeechCache(**kwargs)
