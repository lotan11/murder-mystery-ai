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
    assert report['missing_bones']==[] and report['morph_target_count']==11
    assert report['external_resources']==[] and not report['talkinghead_inventory_complete']
    for target in report['morph_deformations'].values():assert target['affected_vertices']>100
    evidence=json.loads((ROOT/'assets/character-production/rig-study-validation.json').read_text())
    assert evidence['binding_neutral_max_error_m']<0.00001
    assert evidence['restored_max_error_m']<0.00001
    for item in evidence['meshes'].values():
        if item['method']=='rigid torso':assert item['head_turn_max_delta_m']<0.00001
        if item['method']=='rigid head':assert item['head_turn_max_delta_m']>0.001


def test_brow_controls_are_local_real_targets_and_preserve_existing_face_study():
    import json
    rig=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-rig-study.glb',measure=True)
    face=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-face-study.glb',measure=True)
    for name,measured in face['morph_deformations'].items():
        assert rig['morph_deformations'][name]['affected_vertices']==measured['affected_vertices']
        assert rig['morph_deformations'][name]['max_displacement']==measured['max_displacement']
        # Oral lining splits the head into two material primitives, not new deformation geometry.
        assert rig['morph_deformations'][name]['primitive_count']==measured['primitive_count']+1
    expected={'browInnerUp','browOuterUpLeft','browOuterUpRight','browDownLeft','browDownRight'}
    assert {name for name in rig['morph_deformations'] if name.startswith('brow')}==expected
    evidence=json.loads((ROOT/'assets/character-production/rig-study-validation.json').read_text())
    assert {name for name in evidence['expression_controls'] if name.startswith('brow')}==expected
    for name in expected:
        measured=rig['morph_deformations'][name]
        assert measured['affected_vertices']>100
        assert 0.001<measured['max_displacement']<0.015
        control=evidence['expression_controls'][name]
        assert control['source_affected_height_m'][0]>1.5
        assert all(len(digest)==64 for digest in control['source_targets_sha256'].values())
        assert any('skin blockout' in mesh for mesh in control['meshes'])
        assert any('Grey strand' in mesh for mesh in control['meshes'])
    assert evidence['binding_neutral_max_error_m']<0.000001
    assert evidence['restored_max_error_m']<0.000001


def test_mouth_units_have_real_local_deformation_and_restrained_preview_limits():
    import json
    rig=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-rig-study.glb',measure=True)
    expected={'mouthPucker':0.25,'lipPress':0.25,'mouthSmile':0.20}
    evidence=json.loads((ROOT/'assets/character-production/rig-study-validation.json').read_text())
    assert evidence['mouth_preview_limits']==expected
    hashes=[]
    for name,limit in expected.items():
        measured=rig['morph_deformations'][name]
        assert measured['affected_vertices']>100
        assert 0.0001<measured['max_displacement']<0.04
        assert measured['max_displacement']*limit<0.01
        control=evidence['expression_controls'][name]
        assert 1.4<control['source_affected_height_m'][0]<control['source_affected_height_m'][1]<1.7
        assert any('skin blockout' in mesh for mesh in control['meshes'])
        assert any('Grey strand' in mesh for mesh in control['meshes'])
        hashes.extend(control['source_targets_sha256'].values())
    assert len(hashes)==len(set(hashes))==3
    assert evidence['speech_connected'] is False
    assert not rig['talkinghead_inventory_complete'] and rig['missing_visemes']


def test_oral_lining_uses_existing_anatomical_cavity_without_new_geometry():
    import json
    data=(ROOT/'frontend/public/character-lab/scholar-rig-study.glb').read_bytes()
    size,kind=struct.unpack_from('<II',data,12)
    assert kind==0x4e4f534a
    document=json.loads(data[20:20+size])
    materials=document['materials']
    indexes=[i for i,material in enumerate(materials) if material.get('name')=='Scholar anatomical oral lining study']
    assert len(indexes)==1
    lining=materials[indexes[0]]['pbrMetallicRoughness']
    assert max(lining['baseColorFactor'][:3])<.05 and lining['roughnessFactor']>.8
    primitives=[primitive for mesh in document['meshes'] for primitive in mesh['primitives'] if primitive.get('material')==indexes[0]]
    assert len(primitives)==1
    assert 'JOINTS_0' in primitives[0]['attributes'] and 'WEIGHTS_0' in primitives[0]['attributes']
    evidence=json.loads((ROOT/'assets/character-production/rig-study-validation.json').read_text())
    mouth=evidence['mouth_lining']
    assert mouth['polygons']==398 and mouth['vertices']==418
    assert mouth['new_geometry'] is False and mouth['teeth_or_tongue_added'] is False
    assert len(mouth['mask_sha256'])==64
    assert mouth['world_bounds_m']['min'][2]>1.5 and mouth['world_bounds_m']['max'][2]<1.6
    rig=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-rig-study.glb')
    original=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-face-study.glb')
    assert rig['vertices']==original['vertices'] and rig['triangles']==original['triangles']
    assert evidence['binding_neutral_max_error_m']<.000001 and evidence['restored_max_error_m']<.000001


def test_baked_skin_maps_are_really_embedded_and_bound_to_the_runtime_material():
    import hashlib,json
    report=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-rig-study.glb')
    inventory=report['material_inventory']
    skin=next(material for material in inventory['materials'] if material['name']=='Neutral aged skin blockout')
    assert inventory['texture_count']==4 and len(inventory['images'])==4
    for slot in ['base_color_texture','normal_texture','metallic_roughness_texture']:
        reference=skin[slot]
        assert reference is not None and reference['tex_coord']==0
        image=inventory['images'][reference['image_index']]
        assert image['embedded'] and image['mime_type']=='image/png'
        assert image['width']==image['height']==1024 and image['bytes']>1000
    evidence=json.loads((ROOT/'assets/character-production/skin-material-validation.json').read_text())
    assert evidence['geometry_modified'] is False and evidence['light_baked_into_color'] is False
    assert evidence['normal_vs_bump_disabled_rms_xy']>.0005
    assert evidence['baked_surface_pixels_including_margin']>10000
    for channel in ['0','1']:
        low,high=evidence['normal_channel_ranges'][channel]
        assert .3<low<high<.7 and high-low>.01
    for name,source in evidence['maps'].items():
        data=(ROOT/source['path']).read_bytes()
        assert hashlib.sha256(data).hexdigest()==source['sha256'] and len(data)==source['bytes']
        assert data[:8]==b'\x89PNG\r\n\x1a\n'
        assert struct.unpack_from('>II',data,16)==(1024,1024)
    normal=inventory['images'][skin['normal_texture']['image_index']]
    assert normal['sha256']==evidence['maps']['normal']['sha256']
    base=inventory['images'][skin['base_color_texture']['image_index']]
    assert base['sha256']==evidence['maps']['base_color']['sha256']
    assert report['external_resources']==[] and report['joint_count']==64 and report['morph_target_count']==11
