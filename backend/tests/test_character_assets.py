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
    # Retiring dense legacy crown guides reduces vertices; every active vertex still needs valid skinning.
    assert vertices>0
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
    original_head=next(item for item in face['mesh_inventory'] if 'Neutral aged skin blockout' in item['materials'])
    rig_head=next(item for item in rig['mesh_inventory'] if 'Neutral aged skin blockout' in item['materials'])
    assert rig_head['vertices']==original_head['vertices'] and rig_head['triangles']==original_head['triangles']
    for name,measured in original_head['morph_deformations'].items():
        assert rig_head['morph_deformations'][name]['affected_vertices']==measured['affected_vertices']
        assert rig_head['morph_deformations'][name]['max_displacement']==measured['max_displacement']
        # Oral lining splits the original head into two material primitives.
        assert rig_head['morph_deformations'][name]['primitive_count']==measured['primitive_count']+1
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
    rig=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-rig-study.glb',measure=True)
    original=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-face-study.glb',measure=True)
    rig_head=next(item for item in rig['mesh_inventory'] if 'Neutral aged skin blockout' in item['materials'])
    original_head=next(item for item in original['mesh_inventory'] if 'Neutral aged skin blockout' in item['materials'])
    assert rig_head['vertices']==original_head['vertices'] and rig_head['triangles']==original_head['triangles']
    assert evidence['binding_neutral_max_error_m']<.000001 and evidence['restored_max_error_m']<.000001


def test_baked_skin_maps_are_really_embedded_and_bound_to_the_runtime_material():
    import hashlib,json
    report=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-rig-study.glb')
    inventory=report['material_inventory']
    skin=next(material for material in inventory['materials'] if material['name']=='Neutral aged skin blockout')
    assert inventory['texture_count']==7 and len(inventory['images'])==7
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


def test_weighted_study_preserves_original_head_rest_positions_across_material_splits():
    import json
    def head_points(path):
        data=path.read_bytes();offset=12;document=None;binary=None
        while offset<len(data):
            size,kind=struct.unpack_from('<II',data,offset);offset+=8
            if kind==0x4e4f534a:document=json.loads(data[offset:offset+size])
            elif kind==0x004e4942:binary=data[offset:offset+size]
            offset+=size
        material=next(i for i,item in enumerate(document['materials']) if item.get('name')=='Neutral aged skin blockout')
        mesh=next(mesh for mesh in document['meshes'] if any(p.get('material')==material for p in mesh['primitives']))
        points=[]
        for primitive in mesh['primitives']:
            accessor=document['accessors'][primitive['attributes']['POSITION']]
            assert accessor['componentType']==5126 and accessor['type']=='VEC3'
            view=document['bufferViews'][accessor['bufferView']]
            start=view.get('byteOffset',0)+accessor.get('byteOffset',0);stride=view.get('byteStride',12)
            points.extend(tuple(round(value,6) for value in struct.unpack_from('<3f',binary,start+i*stride)) for i in range(accessor['count']))
        return sorted(points)
    assert head_points(ROOT/'frontend/public/character-lab/scholar-rig-study.glb')==head_points(ROOT/'frontend/public/character-lab/scholar-face-study.glb')


def test_fitted_facial_groom_has_actual_weighted_geometry_and_nonzero_mouth_targets():
    import json
    report=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-rig-study.glb',measure=True)
    groom=next(item for item in report['mesh_inventory'] if 'Scholar Fitted silver facial groom' in item['node_names'])
    evidence=json.loads((ROOT/'assets/character-production/groom-validation.json').read_text())
    assert groom['vertices']==evidence['added_vertices']==18000
    assert groom['triangles']==evidence['added_triangles']==12000
    assert set(groom['morph_deformations'])=={'jawOpen','mouthPucker','lipPress','mouthSmile'}
    for target in groom['morph_deformations'].values():
        assert target['affected_vertices']>1000 and .001<target['max_displacement']<.03
    assert evidence['clumps']=={'beard':2200,'moustache':800}
    assert evidence['scalp_or_crown_modified'] is False and evidence['existing_head_unchanged'] is True
    assert evidence['max_weight_sum_error']<.000001
    assert evidence['maximum_morph_correspondence_error_m']<.000001
    assert evidence['minimum_face_outward_dot']>0 and evidence['inverted_face_count']==0
    assert evidence['minimum_rest_lip_proxy_clearance_m']>.001
    assert len(evidence['pose_attachment'])==5
    for pose in evidence['pose_attachment'].values():
        assert pose['inward_vertices']==0 and pose['minimum_outward_offset_m']>0
        assert pose['maximum_correspondence_distance_m']<.001
    assert report['morph_target_count']==11 and report['joint_count']==64 and not report['external_resources']


def test_crown_repair_preserves_topology_and_reports_sharp_edge_limits():
    import json
    evidence=json.loads((ROOT/'assets/character-production/crown-validation.json').read_text(encoding='utf-8'))
    assert evidence['existing_head_unchanged'] and not evidence['material_changed']
    assert evidence['new_vertices']==evidence['new_polygons']==0
    assert evidence['referenced_vertices']==9113 and evidence['unused_loose_vertices_ignored']==3730
    assert .002 <= evidence['surface_offset_m'] <= .003
    assert evidence['maximum_vertex_adjustment_m'] < .007
    assert evidence['before_fit']['closest_triangle_inward_vertex_count'] > 0
    for name in ['after_fit','head_turn_10_degrees_fit']:
        fit=evidence[name]
        assert fit['inward_vertex_count']==0 and fit['minimum_signed_outward_offset_m']>.001
        # Smooth surface fitting does not erase sharp ear-edge triangle disagreements.
        assert fit['closest_triangle_inward_vertex_count'] > 0
        assert fit['triangle_vs_interpolated_normal_ambiguity_count']==fit['closest_triangle_inward_vertex_count']
        assert len(fit['triangle_vs_interpolated_normal_ambiguous_world_positions'])==fit['triangle_vs_interpolated_normal_ambiguity_count']
    report=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-rig-study.glb',measure=True)
    original=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-face-study.glb',measure=True)
    assert not any(item['name']=='Anatomical scalp shell' for item in report['mesh_inventory'])
    baseline=next(item for item in original['mesh_inventory'] if item['name']=='Anatomical scalp shell')
    assert baseline['vertices']==evidence['referenced_vertices']
    hair=json.loads((ROOT/'assets/character-production/hair-asset-validation.json').read_text(encoding='utf-8'))
    assert hair['cap_geometry_retained_in_source']
    assert hair['retained_editable_cap_vertices']==evidence['referenced_vertices']+evidence['unused_loose_vertices_ignored']
    assert evidence['object'] in hair['retired_node_names']
    rig=json.loads((ROOT/'assets/character-production/rig-study-validation.json').read_text(encoding='utf-8'))
    assert rig['crown']['active_in_export'] is False and rig['crown']['replacement_object']==hair['object']


def test_iris_detail_is_embedded_on_actual_second_uv_without_changing_eyes():
    import hashlib,json
    evidence=json.loads((ROOT/'assets/character-production/eye-material-validation.json').read_text(encoding='utf-8'))
    assert evidence['geometry_unchanged'] and evidence['eye_geometry_unchanged']
    assert evidence['pupil_and_sclera_materials_unchanged'] and not evidence['pupil_diameter_changed']
    assert not evidence['new_geometry'] and not evidence['new_bones_or_morphs']
    assert evidence['original_uv0_preserved'] and evidence['uv_index']==1
    assert len(evidence['islands'])==2
    for island in evidence['islands']:
        assert island['vertices']==610
        assert all(.0048<radius<.005 for radius in island['radii_xz_m'])
    texture=evidence['texture'];data=(ROOT/texture['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest()==texture['sha256']
    assert texture['width']==texture['height']==512 and texture['lighting_painted'] is False
    report=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-rig-study.glb')
    inventory=report['material_inventory']
    iris=next(item for item in inventory['materials'] if item['name']==evidence['material_name'])
    binding=iris['base_color_texture'];assert binding['tex_coord']==1
    image=inventory['images'][binding['image_index']]
    assert image['embedded'] and image['width']==image['height']==512 and image['sha256']==texture['sha256']
    def eye_components(path):
        raw=path.read_bytes();offset=12;document=binary=None
        while offset<len(raw):
            size,kind=struct.unpack_from('<II',raw,offset);offset+=8
            if kind==0x4e4f534a:document=json.loads(raw[offset:offset+size])
            elif kind==0x004e4942:binary=raw[offset:offset+size]
            offset+=size
        result={}
        for name in ['Slate blue grey iris','Pupils','Natural eye whites']:
            index=next(i for i,item in enumerate(document['materials']) if item.get('name')==name)
            points=[]
            for mesh_index,mesh in enumerate(document['meshes']):
                if not any(primitive.get('material')==index for primitive in mesh['primitives']):continue
                node_index=next(i for i,node in enumerate(document['nodes']) if node.get('mesh')==mesh_index)
                translation=[0.,0.,0.]
                while True:
                    node=document['nodes'][node_index]
                    assert 'matrix' not in node and 'rotation' not in node and 'scale' not in node
                    translation=[a+b for a,b in zip(translation,node.get('translation',[0,0,0]))]
                    parents=[i for i,parent in enumerate(document['nodes']) if node_index in parent.get('children',[])]
                    if not parents:break
                    node_index=parents[0]
                for primitive in mesh['primitives']:
                    if primitive.get('material')!=index:continue
                    if name=='Slate blue grey iris' and path.name=='scholar-rig-study.glb':
                        assert 'TEXCOORD_1' in primitive['attributes'] and 'TEXCOORD_0' in primitive['attributes']
                    accessor=document['accessors'][primitive['attributes']['POSITION']]
                    view=document['bufferViews'][accessor['bufferView']]
                    start=view.get('byteOffset',0)+accessor.get('byteOffset',0);stride=view.get('byteStride',12)
                    points.extend(tuple(x+t for x,t in zip(struct.unpack_from('<3f',binary,start+i*stride),translation)) for i in range(accessor['count']))
            result[name]=points
        return result
    # Static eyes retain node translations; skinning bakes those into positions.
    # Compare world-space geometry with a two-micrometre float-export tolerance.
    import itertools,math
    from collections import defaultdict
    current=eye_components(ROOT/'frontend/public/character-lab/scholar-rig-study.glb')
    original=eye_components(ROOT/'frontend/public/character-lab/scholar-face-study.glb')
    tolerance=.000002
    for name,points in current.items():
        expected=original[name];assert len(points)==len(expected)>0
        bins=defaultdict(list)
        key=lambda point:tuple(math.floor(x/tolerance) for x in point)
        for point in expected:bins[key(point)].append(point)
        for point in points:
            cell=key(point)
            candidates=(old for offset in itertools.product((-1,0,1),repeat=3) for old in bins[tuple(a+b for a,b in zip(cell,offset))])
            assert any(sum((a-b)**2 for a,b in zip(point,old))<tolerance**2 for old in candidates)


def test_real_hair_asset_has_supported_maps_and_no_invented_rig_controls():
    import hashlib,json
    evidence=json.loads((ROOT/'assets/character-production/hair-asset-validation.json').read_text(encoding='utf-8'))
    assert evidence['vertices']==1755 and evidence['polygons']==1672
    assert evidence['new_bones']==evidence['new_morphs']==0
    assert evidence['min_weight_sum']==evidence['max_weight_sum']==1
    assert evidence['existing_rest_positions_unchanged'] and evidence['cap_geometry_retained_in_source']
    assert evidence['alpha_preserved_max_error']==0
    for path,digest in evidence['source_hashes'].items():
        data=(ROOT/path).read_bytes();assert hashlib.sha256(data).hexdigest()==digest
        if path.endswith(('.obj','.mhclo','.mhmat')):assert 'released as cc0 in september 2020' in data.decode('utf-8').lower()
    for pose in evidence['head_attachment'].values():assert pose['maximum_rigid_head_correspondence_error_m']<.000001
    for pose in evidence['contact_fit'].values():
        assert pose['maximum_nearest_head_distance_m']<.005
        assert -.005<pose['minimum_triangle_signed_offset_m']<0 and pose['triangle_inward_sign_count']>0
    report=inspector.inspect(ROOT/'frontend/public/character-lab/scholar-rig-study.glb',measure=True)
    mesh=next(item for item in report['mesh_inventory'] if evidence['object'] in item['node_names'])
    assert mesh['vertices']>=evidence['vertices'] and not mesh['morph_deformations']
    inventory=report['material_inventory'];mat=next(m for m in inventory['materials'] if m['name']==evidence['material'])
    image=inventory['images'][mat['base_color_texture']['image_index']]
    assert image['width']==image['height']==2048 and image['embedded'] and image['sha256']==evidence['albedo_sha256']
    assert hashlib.sha256((ROOT/evidence['albedo_path']).read_bytes()).hexdigest()==image['sha256']
    normal=inventory['images'][mat['normal_texture']['image_index']]
    assert normal['width']==normal['height']==2048 and normal['embedded']
    assert normal['sha256']==next(value for name,value in evidence['source_hashes'].items() if name.endswith('short02_normal.png'))
    raw=(ROOT/'frontend/public/character-lab/scholar-rig-study.glb').read_bytes();length=struct.unpack_from('<I',raw,12)[0];document=json.loads(raw[20:20+length])
    runtime=next(m for m in document['materials'] if m.get('name')==evidence['material'])
    assert runtime['alphaMode']=='BLEND' and runtime['doubleSided']
    assert runtime['normalTexture']['scale']==pytest.approx(.4) and runtime['pbrMetallicRoughness']['roughnessFactor']==pytest.approx(.8)
    assert runtime['extensions']['KHR_materials_specular']['specularFactor']==pytest.approx(.3)


def test_skin_age_blend_retains_inputs_and_binds_the_actual_color_bake():
    import hashlib,json
    evidence=json.loads((ROOT/'assets/character-production/skin-color-validation.json').read_text(encoding='utf-8'))
    assert evidence['geometry_unchanged'] and evidence['uv_mapping_unchanged']
    assert evidence['weights_morphs_material_assignments_unchanged'] and evidence['normal_roughness_preserved']
    assert evidence['source_image_unchanged'] and evidence['procedural_input_preserved']
    assert evidence['geometry_uv_weights_morph_sha256_before']==evidence['geometry_uv_weights_morph_sha256_after']
    assert evidence['uv_index']==0 and evidence['recipe']['source_mix_weight']==.45
    assert evidence['recipe']['source_tint_linear']==[.78,.82,.9]
    assert evidence['source']['license']=='CC0-1.0' and evidence['source']['width']==evidence['source']['height']==2048
    assert 'released as cc0 in september 2020' in (ROOT/evidence['source']['material_path']).read_text(encoding='utf-8').lower()
    for item in [evidence['source'],evidence['texture'],evidence['input_color']]:
        assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
    validation=json.loads((ROOT/'assets/character-production/skin-material-validation.json').read_text(encoding='utf-8'))
    assert validation['maps']['base_color']['sha256']==evidence['texture']['sha256']
    assert evidence['texture']['sha256']!=evidence['input_color']['sha256']
    assert evidence['texture']['width']==evidence['texture']['height']==1024
    manifest=json.loads((ROOT/'assets/character-production/source-assets/makehuman-system/SOURCE.json').read_text(encoding='utf-8'))
    assert manifest['license']=='CC0-1.0' and len(manifest['files'])==7
    for item in manifest['files']:
        data=(ROOT/'assets/character-production/source-assets/makehuman-system'/item['path']).read_bytes()
        assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
