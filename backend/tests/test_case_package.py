import copy
import json

import pytest
from backend.case_package import CASE, load_case
from backend.legacy_tone import serious_saved_dialogue


def test_case_package_is_the_authoritative_source():
    from backend.mystery import EVIDENCE, SOLUTION, NARRATION
    from backend.characters import CHARACTERS
    assert EVIDENCE is CASE['evidence']
    assert CHARACTERS is CASE['characters']
    assert SOLUTION == CASE['solution']
    assert NARRATION == CASE['narration']


@pytest.mark.parametrize('mutation', ['duplicate_clue','missing_act','missing_private_card','unknown_format','missing_hint','unsupported_roster'])
def test_invalid_case_fails_before_game_can_start(tmp_path, mutation):
    case=copy.deepcopy(CASE)
    if mutation=='duplicate_clue': case['evidence'][1]['id']=case['evidence'][0]['id']
    elif mutation=='missing_act': case['evidence']=[e for e in case['evidence'] if e['act']!=3]
    elif mutation=='missing_private_card': del case['characters']['ada']
    elif mutation=='unknown_format': case['format_version']=2
    elif mutation=='missing_hint': del case['evidence'][0]['hint']
    elif mutation=='unsupported_roster': case['suspects'][0]['id']='other'
    path=tmp_path/'case.json'; path.write_text(json.dumps(case),encoding='utf-8')
    with pytest.raises(ValueError,match='Invalid case package'): load_case(path)


def test_duplicate_json_field_rejected(tmp_path):
    path=tmp_path/'case.json';path.write_text('{"id":"a","id":"b"}',encoding='utf-8')
    with pytest.raises(ValueError,match='Duplicate case field'):load_case(path)


def test_saved_tone_revision_preserves_facts_and_unrelated_text():
    assert serious_saved_dialogue('A clue. Do resist the urge to lick the evidence.')=='A clue.'
    text='The photograph is timestamped 9:20. Player-authored observation.'
    assert serious_saved_dialogue(text)==text
