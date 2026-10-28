"""Server-only case package loading. Never mount this directory as browser assets."""
import json
from pathlib import Path

DEFAULT_CASE = Path(__file__).with_name('cases') / 'blackthorn.json'


def load_case(path=DEFAULT_CASE):
    path = Path(path)
    if path.stat().st_size > 512 * 1024:
        raise ValueError('Case package exceeds the size limit.')
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate case field: ' + key)
            result[key] = value
        return result
    case = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_keys)
    def require(condition, message):
        if not condition:
            raise ValueError('Invalid case package: ' + message)
    def text(value, limit=3000):
        return isinstance(value, str) and bool(value.strip()) and len(value) <= limit
    require(isinstance(case, dict), 'expected an object')
    require(case.get('format_version') == 1 and type(case.get('format_version')) is int, 'format_version must be 1')
    require(text(case.get('id'), 80) and all(c.islower() or c.isdigit() or c == '-' for c in case['id']), 'invalid id')
    require(type(case.get('version')) is int and case['version'] > 0, 'positive version required')
    require(text(case.get('title'), 160) and text(case.get('solution')), 'title and solution required')
    suspects, evidence, characters = case.get('suspects'), case.get('evidence'), case.get('characters')
    require(isinstance(suspects, list) and 1 <= len(suspects) <= 12, 'suspects required')
    require(all(isinstance(s, dict) and all(text(s.get(k), 160 if k != 'description' else 1600) for k in ('id','name','description')) for s in suspects), 'invalid suspect')
    require(all(isinstance(s.get('topics'), list) and s['topics'] and all(text(t,80) for t in s['topics']) for s in suspects), 'suspect topics required')
    ids = [s['id'] for s in suspects]
    require(len(set(ids)) == len(ids), 'duplicate suspect ids')
    # Current game/client supports this roster; alternative roster sizes/IDs need engine work.
    require(set(ids) == {'ada','felix','margot'}, 'current prototype requires Ada/Felix/Margot stable role ids')
    require(isinstance(evidence, list) and 3 <= len(evidence) <= 20, 'evidence required')
    require(all(isinstance(e, dict) and all(text(e.get(k), 1600) for k in ('id','title','description','summary')) and type(e.get('act')) is int and 1 <= e['act'] <= 3 for e in evidence), 'invalid evidence')
    require(all(isinstance(e.get('topics'), list) and e['topics'] and all(text(t,80) for t in e['topics']) and text(e.get('hint'),1000) for e in evidence), 'evidence topics and hint required')
    require(len({e['id'] for e in evidence}) == len(evidence), 'duplicate evidence ids')
    require({e['act'] for e in evidence} == {1,2,3}, 'each investigation act needs evidence')
    require([e['act'] for e in evidence] == sorted(e['act'] for e in evidence), 'evidence must follow act order')
    require(isinstance(characters, dict) and set(characters) == set(ids) | {'investigator'}, 'character ids must match suspects plus investigator')
    for key, card in characters.items():
        require(isinstance(card, dict) and card.get('id') == key, 'invalid character id')
        require(all(text(card.get(k)) for k in ('name','public_intro','private_brief','performance_notes')), 'incomplete character card')
        require(isinstance(card.get('objectives'), list) and 1 <= len(card['objectives']) <= 8 and all(text(o,500) for o in card['objectives']), 'invalid objectives')
    narration = case.get('narration')
    require(isinstance(narration, dict) and set(narration) == {'welcome','reset','start','advance'} and all(text(v,1500) for v in narration.values()), 'invalid narration')
    return case


CASE = load_case()
