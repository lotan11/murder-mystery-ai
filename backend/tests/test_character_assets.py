import importlib.util
import struct
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('character_inspector',ROOT/'scripts'/'inspect-character.py')
inspector=importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspector)


def test_existing_sample_inventory_distinguishes_silence_target_from_full_approval():
    report=inspector.inspect(ROOT/'frontend/public/audition/mpfb.glb')
    assert report['vertices']>10000 and report['joint_count']==67
    assert report['missing_bones']==[] and report['missing_expressions']==[]
    assert report['missing_visemes']==['viseme_sil']
    assert report['external_resources']==[]
    assert 'separate review' in report['approval']


def test_scholar_blockout_contains_actual_embedded_geometry():
    report=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-blockout.glb')
    assert report['vertices']>1000 and report['triangles']>1000
    assert report['mesh_count']>0 and report['external_resources']==[]
    assert report['approval'].startswith('Structural inventory only')


@pytest.mark.parametrize('data',[b'bad asset file bytes!!',struct.pack('<4sII',b'glTF',2,999)+b'\0'*20])
def test_malformed_model_is_not_presented_as_a_valid_inventory(tmp_path,data):
    path=tmp_path/'bad.glb';path.write_bytes(data)
    with pytest.raises(ValueError):inspector.inspect(path)


def test_face_study_has_real_local_deformations_and_preserves_neutral():
    import json
    report=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-face-study.glb',measure=True)
    assert report['joint_count']==0 and report['external_resources']==[]
    assert report['morph_target_count']==3
    assert set(report['morph_deformations'])=={'jawOpen','eyeBlinkLeft','eyeBlinkRight'}
    for target in report['morph_deformations'].values():
        assert target['affected_vertices']>100
        assert 0.001<target['max_displacement']<0.05
    evidence=json.loads((ROOT/'assets/character-production/face-study-validation.json').read_text())
    assert evidence['neutral_max_error_m']==0
    assert evidence['head_max_mapping_error_m']<0.000001
    assert evidence['speech_connected'] is False


def test_bound_study_exports_real_normalized_skin_weights_and_joint_references():
    import json
    data=(ROOT/'frontend/public/character-lab/scholar-rig-study.glb').read_bytes()
    offset=12;document=None;binary=None
    while offset<len(data):
        size,kind=struct.unpack_from('<II',data,offset);offset+=8
        if kind==0x4e4f534a:document=json.loads(data[offset:offset+size])
        elif kind==0x004e4942:binary=data[offset:offset+size]
        offset+=size
    assert len(document['skins'])==1
    skin=document['skins'][0]
    assert len(skin['joints'])==64
    assert any(document['nodes'][index]['name'].endswith('Head') for index in skin['joints'])
    def accessor(index):
        item=document['accessors'][index];view=document['bufferViews'][item['bufferView']]
        assert item['type']=='VEC4'
        fmt={5126:'<4f',5123:'<4H',5121:'<4B'}[item['componentType']]
        width=struct.calcsize(fmt);stride=view.get('byteStride',width)
        start=view.get('byteOffset',0)+item.get('byteOffset',0)
        return [struct.unpack_from(fmt,binary,start+i*stride) for i in range(item['count'])]
    vertices=0
    for node in document['nodes']:
        if 'mesh' not in node:continue
        assert node['skin']==0
        for primitive in document['meshes'][node['mesh']]['primitives']:
            attributes=primitive['attributes']
            weights=accessor(attributes['WEIGHTS_0']);joints=accessor(attributes['JOINTS_0'])
            assert len(weights)==len(joints)==document['accessors'][attributes['POSITION']]['count']
            vertices+=len(weights)
            for values,indices in zip(weights,joints):
                assert all(0<=value<=1 for value in values)
                assert abs(sum(values)-1)<0.00001
                assert all(0<=index<len(skin['joints']) for index,value in zip(indices,values) if value>0)
    assert vertices>100000
    report=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-rig-study.glb',measure=True)
    assert report['missing_bones']==[] and report['morph_target_count']==3
    assert report['external_resources']==[] and not report['talkinghead_inventory_complete']
    for target in report['morph_deformations'].values():assert target['affected_vertices']>100
    evidence=json.loads((ROOT/'assets/character-production/rig-study-validation.json').read_text())
    assert evidence['binding_neutral_max_error_m']<0.00001
    assert evidence['restored_max_error_m']<0.00001
    for item in evidence['meshes'].values():
        if item['method']=='rigid torso':assert item['head_turn_max_delta_m']<0.00001
        if item['method']=='rigid head':assert item['head_turn_max_delta_m']>0.001
