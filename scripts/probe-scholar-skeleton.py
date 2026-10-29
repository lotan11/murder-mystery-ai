"""Blender-only weighted skeleton experiment; never modifies the canonical Scholar.
Run portable Blender --background --factory-startup --python-exit-code 1
--python scripts/probe-scholar-skeleton.py. Diagnostics remain in ignored data/.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil
import subprocess
import bpy
import addon_utils

ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'assets/character-production/scholar.json').read_text(encoding='utf-8'))
MPFB=ROOT/CONFIG['mpfb']['source_path']
OUT=ROOT/'data/character-tools/skeleton-proof'
OUT.mkdir(parents=True,exist_ok=True)
CANONICAL=ROOT/CONFIG['outputs']['blend']
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
source_hash=sha(CANONICAL)
snapshot=OUT/'scholar-input.blend'
shutil.copy2(CANONICAL,snapshot)
if sha(snapshot)!=source_hash:raise RuntimeError('Canonical source changed while being copied; rerun the proof.')
commit=subprocess.check_output(['git','-C',str(MPFB),'rev-parse','HEAD'],text=True).strip()
if commit!=CONFIG['mpfb']['commit']:raise RuntimeError('MPFB checkout does not match pinned source.')
bpy.ops.wm.open_mainfile(filepath=str(snapshot))
bpy.context.preferences.extensions.repos.new(name='Scholar MPFB source',module='scholar_mpfb',custom_directory=str(MPFB/'src'))
if addon_utils.enable('bl_ext.scholar_mpfb.mpfb',default_set=True) is None:raise RuntimeError('Could not enable pinned MPFB.')
from bl_ext.scholar_mpfb.mpfb.services.humanservice import HumanService
collection=bpy.data.collections.get('EDITABLE_MAKEHUMAN_SOURCE_CC0')
if collection is None:raise RuntimeError('Canonical editable anatomical source collection missing.')
meshes=[o for o in collection.objects if o.type=='MESH']
if len(meshes)!=1:raise RuntimeError('Expected exactly one preserved anatomical source mesh.')
source=meshes[0]
collection.hide_viewport=False
collection.hide_render=False
source.hide_set(False)
source.hide_viewport=False
source.hide_render=False
for mod in source.modifiers:mod.show_viewport=False;mod.show_render=False
bpy.context.view_layer.objects.active=source
source.select_set(True)
rig=HumanService.add_builtin_rig(source,'mixamo_unity',import_weights=True)
if rig is None:raise RuntimeError('MPFB did not create an armature.')
mods=[m for m in source.modifiers if m.type=='ARMATURE' and m.object==rig]
if len(mods)!=1:raise RuntimeError('No unique bound armature modifier found.')
mods[0].show_viewport=True
mods[0].show_render=True
bones=sorted(b.name for b in rig.data.bones)
head=rig.pose.bones.get('mixamorig:Head')
if head is None:raise RuntimeError('Imported skeleton does not contain Head.')

def positions():
 bpy.context.view_layer.update()
 evaluated=source.evaluated_get(bpy.context.evaluated_depsgraph_get())
 mesh=evaluated.to_mesh()
 try:return [evaluated.matrix_world@v.co for v in mesh.vertices]
 finally:evaluated.to_mesh_clear()

rest=positions()
head_group=source.vertex_groups.get('mixamorig:Head')
if head_group is None:raise RuntimeError('Imported Head weights are missing.')
head_indices=[v.index for v in source.data.vertices if any(g.group==head_group.index and g.weight>.5 for g in v.groups)]
body_indices=[i for i,v in enumerate(rest) if v.z<1.0]
if len(head_indices)<20 or len(body_indices)<100:raise RuntimeError('Insufficient head or stable-body vertices for proof.')
head.rotation_mode='XYZ'
head.rotation_euler=(0,math.radians(12),0)
posed=positions()
if len(rest)!=len(posed):raise RuntimeError('Unexpected topology change during armature evaluation.')
head_deltas=[(posed[i]-rest[i]).length for i in head_indices]
body_deltas=[(posed[i]-rest[i]).length for i in body_indices]
head.rotation_euler=(0,0,0)
restored=positions()
restore_max=max((a-b).length for a,b in zip(rest,restored))
if max(head_deltas)<.005:raise RuntimeError('Head did not meaningfully deform under imported weights.')
if max(body_deltas)>.00001 or restore_max>.00001:raise RuntimeError('Body moved unexpectedly or rest pose was not restored.')
weighted_groups={g.name:g.index for g in source.vertex_groups if g.name in bones}
weighted_count=sum(any(g.group in weighted_groups.values() and g.weight>0 for g in v.groups) for v in source.data.vertices)
required=['Hips','Spine','Spine1','Spine2','Neck','Head','LeftShoulder','RightShoulder','LeftArm','RightArm','LeftForeArm','RightForeArm','LeftHand','RightHand','LeftUpLeg','RightUpLeg','LeftLeg','RightLeg','LeftFoot','RightFoot','LeftEye','RightEye']
rig_dir=MPFB/'src/mpfb/data/rigs/standard'
report={
 'version':1,'status':'Isolated anatomical source skeleton proof; canonical review bust remains unrigged',
 'source_blend_sha256':source_hash,'mpfb_commit':commit,'rig':'mixamo_unity',
 'rig_sha256':sha(rig_dir/'rig.mixamo_unity.json'),'weights_sha256':sha(rig_dir/'weights.mixamo_unity.json'),
 'source_vertex_count':len(rest),'weighted_vertex_count':weighted_count,
 'bone_count':len(bones),'bones':bones,'bone_name_prefix':'mixamorig:', 'missing_required_bones':[n for n in required if 'mixamorig:'+n not in bones],
 'armature_modifier_count':len(mods),'bound_armature_matches':mods[0].object==rig,
 'head_rotation_degrees':12,'rotation_axis':'local Y','head_test_vertices':len(head_indices),
 'head_max_displacement_m':max(head_deltas),'head_mean_displacement_m':sum(head_deltas)/len(head_deltas),
 'stable_body_vertices':len(body_indices),'stable_body_max_displacement_m':max(body_deltas),
 'rest_pose_max_error_m':restore_max,'rest_pose_restored':True,
 'canonical_modified':False,'facial_morphs_added':0,'imported_eye_bones':[n for n in bones if n.endswith('Eye')],
 'eye_deformation_tested':False,'jaw_deformation_tested':False,
 'limitations':['Source body only; runtime cropped bust and accessories are not bound.', 'Imported eye/jaw bones are inventoried only; their deformation is not tested. No facial expressions, visemes, lip sync or animation quality approval.'],
 'diagnostic_blend':'data/character-tools/skeleton-proof/scholar-skeleton-proof.blend'}
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scholar-skeleton-proof.blend'))
(ROOT/'assets/character-production/skeleton-proof.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('SCHOLAR_SKELETON_PROOF '+json.dumps(report))
