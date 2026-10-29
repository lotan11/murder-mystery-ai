"""Derive three experimental face shapes from actual imported MPFB bone weights.

Run probe-scholar-skeleton.py first, then this script with portable Blender.
Canonical blockout and game presentation are never modified.
"""
from pathlib import Path
import hashlib,json,math
import bpy
from mathutils import Vector,Quaternion
from mathutils.kdtree import KDTree

ROOT=Path(__file__).resolve().parents[1]
proof=json.loads((ROOT/'assets/character-production/skeleton-proof.json').read_text(encoding='utf-8'))
canonical=ROOT/'assets/character-production/scholar-blockout.blend'
if hashlib.sha256(canonical.read_bytes()).hexdigest()!=proof['source_blend_sha256']:
    raise RuntimeError('Canonical source changed; rerun weighted skeleton proof before deriving shapes.')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/proof['diagnostic_blend']))
collection=bpy.data.collections['EDITABLE_MAKEHUMAN_SOURCE_CC0']
source=next(obj for obj in collection.objects if obj.type=='MESH')
rig=next(mod.object for mod in source.modifiers if mod.type=='ARMATURE')
collection.hide_viewport=False;collection.hide_render=False;source.hide_set(False)

def positions():
    bpy.context.view_layer.update()
    evaluated=source.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    try:return [evaluated.matrix_world@vertex.co for vertex in mesh.vertices]
    finally:evaluated.to_mesh_clear()

def clear_pose():
    for bone in rig.pose.bones:bone.rotation_mode='QUATERNION';bone.rotation_quaternion=Quaternion();bone.location=(0,0,0);bone.scale=(1,1,1)
    bpy.context.view_layer.update()

def world_x_rotation(name,angle):
    bone=rig.pose.bones[name]
    axis=(rig.matrix_world.to_3x3()@bone.bone.matrix_local.to_3x3()).inverted()@Vector((1,0,0))
    bone.rotation_quaternion=Quaternion(axis.normalized(),angle)

clear_pose();rest=positions();tree=KDTree(len(rest))
for i,point in enumerate(rest):tree.insert(point,i)
tree.balance()
poses={}
world_x_rotation('mixamorig:Jaw',math.radians(20));poses['jawOpen']=positions();clear_pose()
blink_angles={}
for side in ['Left','Right']:
    for suffix in ['Top','Bottom']:
        name='mixamorig:'+side+'Orbicularis'+suffix;bone=rig.data.bones[name]
        direction=rig.matrix_world.to_3x3()@(bone.tail_local-bone.head_local)
        angle=(math.atan2(direction.z,-direction.y)+.015)*(1.9 if suffix=='Top' else 1.5)
        blink_angles[name]=angle
        world_x_rotation(name,angle)
    poses['eyeBlink'+side]=positions();clear_pose()

deltas={name:[point-base for point,base in zip(points,rest)] for name,points in poses.items()}
objects=[obj for obj in bpy.data.objects if obj.type=='MESH' and obj.name.startswith('Scholar ')]
head=next(obj for obj in objects if 'skin blockout' in obj.name)
report={'source_blend_sha256':proof['source_blend_sha256'],'source':'Imported MPFB mixamo_unity real bone weights; pose snapshots transferred to exact head vertices and nearby beard guides','controls':{},'canonical_modified':False,'skeleton_in_export':False,'speech_connected':False,'limitations':['Experimental jaw/eyelid studies only; no full expression/viseme set or production deformation approval.','Mouth interior, teeth/tongue, facial hair deformation and complete blink quality require visual review.']}
for obj in objects:
    is_head=obj==head;is_groom=any('Grey strand' in mat.name for mat in obj.data.materials if mat)
    if not(is_head or is_groom):continue
    world=obj.matrix_world;inverse=world.inverted().to_3x3()
    mapping=[tree.find(world@vertex.co) for vertex in obj.data.vertices]
    for name,delta in deltas.items():
        if not is_head and name!='jawOpen':continue
        movements=[]
        for vertex,(_,index,distance) in zip(obj.data.vertices,mapping):
            movements.append(inverse@delta[index] if distance<(.00002 if is_head else .012) else Vector((0,0,0)))
        changed=sum(move.length>1e-7 for move in movements)
        if not changed:continue
        if obj.data.shape_keys is None:obj.shape_key_add(name='Basis')
        key=obj.shape_key_add(name=name)
        for i,move in enumerate(movements):key.data[i].co=obj.data.vertices[i].co+move
        key.value=0
        measured=report['controls'].setdefault(name,{'changed_vertices':0,'max_delta_m':0,'meshes':[]})
        measured['changed_vertices']+=changed;measured['max_delta_m']=max(measured['max_delta_m'],max(move.length for move in movements));measured['meshes'].append(obj.name)
    if is_head:
        report['head_vertex_count']=len(obj.data.vertices)
        report['head_max_mapping_error_m']=max(distance for _,_,distance in mapping)
        report['neutral_max_error_m']=max((obj.data.shape_keys.key_blocks['Basis'].data[i].co-vertex.co).length for i,vertex in enumerate(obj.data.vertices))
if set(report['controls'])!={'jawOpen','eyeBlinkLeft','eyeBlinkRight'}:raise RuntimeError('Missing meaningful experimental face deformation.')
if report['head_max_mapping_error_m']>.00002 or report['neutral_max_error_m']>1e-7:raise RuntimeError('Neutral head topology did not match the weighted source.')
collection.hide_render=True;source.hide_set(True);source.hide_render=True;rig.hide_render=True
for obj in bpy.context.selected_objects:obj.select_set(False)
for obj in objects:obj.hide_set(False);obj.select_set(True)
bpy.context.view_layer.objects.active=head
out=ROOT/'frontend/public/character-lab/scholar-face-study.glb'
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',use_selection=True,export_animations=False,export_skins=False,export_morph=True,export_extras=True)
scene=bpy.context.scene;scene['face_study']='Three actual weighted-pose-derived morph studies; no live speech or production rig'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/character-production/face-study.blend'),compress=True)
scene.render.resolution_x=768;scene.render.resolution_y=1024;scene.render.resolution_percentage=100;scene.cycles.samples=20
scene.camera.data.ortho_scale=.32
scene.camera.location=Vector((0,-3,1.605))
scene.camera.rotation_euler=(Vector((0,-.03,1.605))-scene.camera.location).to_track_quat('-Z','Y').to_euler()

def values(jaw=0,blink=0):
    for obj in objects:
        if obj.data.shape_keys:
            for key in obj.data.shape_keys.key_blocks:
                if key.name=='jawOpen':key.value=jaw
                elif key.name.startswith('eyeBlink'):key.value=blink
    bpy.context.view_layer.update()
for label,jaw,blink in [('rest',0,0),('jaw',.38,0),('blink',0,1)]:
    values(jaw,blink);scene.render.filepath=str(ROOT/f'docs/assets/face-study-{label}.png');bpy.ops.render.render(write_still=True)
values();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/character-production/face-study.blend'),compress=True)
report['blink_angles_radians']=blink_angles
report['preview_jaw_weight']=.38;report['preview_blink_weight']=1
(ROOT/'assets/character-production/face-study-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('FACE STUDY COMPLETE '+json.dumps(report))
