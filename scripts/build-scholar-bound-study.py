"""Bind a separate Scholar bust experiment to the real imported MPFB skeleton.
Run after build-scholar-face-controls.py with portable Blender. Never activates TV.
"""
from pathlib import Path
import hashlib,json,math,subprocess
import bpy
import addon_utils
from mathutils import Vector
from mathutils.kdtree import KDTree

ROOT=Path(__file__).resolve().parents[1]
source_path=ROOT/'assets/character-production/face-study.blend'
source_hash=hashlib.sha256(source_path.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source_path))
collection=bpy.data.collections['EDITABLE_MAKEHUMAN_SOURCE_CC0']
source=next(obj for obj in collection.objects if obj.type=='MESH')
rig=next(mod.object for mod in source.modifiers if mod.type=='ARMATURE')
collection.hide_viewport=False;collection.hide_render=False;source.hide_set(False)
for bone in rig.pose.bones:
    bone.rotation_mode='QUATERNION';bone.rotation_quaternion=(1,0,0,0)
    bone.location=(0,0,0);bone.scale=(1,1,1)
bpy.context.view_layer.update()
bone_names={bone.name for bone in rig.data.bones}
group_names={group.index:group.name for group in source.vertex_groups if group.name in bone_names}
source_weights=[]
for vertex in source.data.vertices:
    weights={group_names[g.group]:g.weight for g in vertex.groups if g.group in group_names and g.weight>1e-8}
    if not weights:raise RuntimeError('Unweighted anatomical source vertex')
    source_weights.append(weights)
tree=KDTree(len(source.data.vertices))
for vertex in source.data.vertices:tree.insert(source.matrix_world@vertex.co,vertex.index)
tree.balance()
objects=sorted([obj for obj in bpy.data.objects if obj.type=='MESH' and obj.name.startswith('Scholar ')],key=lambda obj:obj.name)

def positions(obj):
    bpy.context.view_layer.update()
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    try:return [evaluated.matrix_world@v.co for v in mesh.vertices]
    finally:evaluated.to_mesh_clear()

# Load real bundled expression-unit geometry; do not synthesize empty compatibility keys.
config=json.loads((ROOT/'assets/character-production/scholar.json').read_text(encoding='utf-8'))
mpfb=ROOT/config['mpfb']['source_path']
actual_commit=subprocess.check_output(['git','-C',str(mpfb),'rev-parse','HEAD'],text=True).strip()
if actual_commit!=config['mpfb']['commit']:raise RuntimeError('MPFB checkout differs from pinned authoring source')
bpy.context.preferences.extensions.repos.new(name='Scholar MPFB source',module='scholar_mpfb',custom_directory=str(mpfb/'src'))
if addon_utils.enable('bl_ext.scholar_mpfb.mpfb',default_set=True) is None:raise RuntimeError('Pinned MPFB unavailable')
from bl_ext.scholar_mpfb.mpfb.services.targetservice import TargetService
source_rest=positions(source);expression_tree=KDTree(len(source_rest))
for index,point in enumerate(source_rest):expression_tree.insert(point,index)
expression_tree.balance()
units=mpfb/'src/mpfb/data/targets/expression/units/caucasian'
expressions={'browInnerUp':['eyebrows-left-inner-up','eyebrows-right-inner-up'],
 'browOuterUpLeft':['eyebrows-left-extern-up'],'browOuterUpRight':['eyebrows-right-extern-up'],
 'browDownLeft':['eyebrows-left-down'],'browDownRight':['eyebrows-right-down'],
 'mouthPucker':['mouth-pursing'],'lipPress':['mouth-compression'],'mouthSmile':['mouth-corner-puller']}
expression_report={}
for name,files in expressions.items():
    keys=[];hashes={}
    for file in files:
        path=units/(file+'.target.gz');hashes[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
        keys.append(TargetService.load_target(source,str(path),weight=1,name='StudySource_'+file))
    changed_source=positions(source)
    delta=[point-base for point,base in zip(changed_source,source_rest)]
    for key in keys:key.value=0
    bpy.context.view_layer.update()
    affected=[point.z for point,move in zip(source_rest,delta) if move.length>1e-7]
    if not affected:raise RuntimeError('Empty source expression')
    measured={'source_affected_height_m':[min(affected),max(affected)],'source_targets_sha256':hashes,'changed_vertices':0,'max_delta_m':0,'meshes':[]}
    for obj in objects:
        skin='skin blockout' in obj.name
        groom=any('Grey strand' in mat.name for mat in obj.data.materials if mat)
        if not(skin or groom):continue
        inverse=obj.matrix_world.inverted().to_3x3();movements=[]
        for vertex in obj.data.vertices:
            neighbours=expression_tree.find_n(obj.matrix_world@vertex.co,1 if skin else 4)
            if neighbours[0][2]>(0.00002 if skin else .012):move=Vector((0,0,0))
            else:
                factors=[1/max(distance,.00001)**2 for _,_,distance in neighbours];total=sum(factors)
                move=sum((delta[index]*factor/total for (_,index,_),factor in zip(neighbours,factors)),Vector())
            movements.append(inverse@move)
        count=sum(move.length>1e-7 for move in movements)
        if not count:continue
        if obj.data.shape_keys is None:obj.shape_key_add(name='Basis')
        key=obj.shape_key_add(name=name)
        for index,move in enumerate(movements):key.data[index].co=obj.data.vertices[index].co+move
        key.value=0
        measured['changed_vertices']+=count;measured['max_delta_m']=max(measured['max_delta_m'],max(move.length for move in movements));measured['meshes'].append(obj.name)
    if measured['changed_vertices']<20 or measured['max_delta_m']<.0001:raise RuntimeError('Expression produced no meaningful geometry: '+name)
    expression_report[name]=measured

rest={obj.name:positions(obj) for obj in objects}
report={'expression_controls':expression_report,'source_face_study_sha256':source_hash,'bone_count':len(bone_names),'meshes':{},'speech_connected':False,
        'status':'Experimental weighted bust; not finished likeness, full facial rig or production speech avatar',
        'method':'Exact-nearest source weights for skin; inverse-distance four-neighbour transfer for groom; rigid Head accessories and Spine2 wardrobe. Normalized strongest four influences.'}
for obj in objects:
    materials=' '.join(mat.name for mat in obj.data.materials if mat)
    wardrobe=any(name in materials for name in ['tweed','waistcoat','Ivory shirt','patterned tie'])
    rigid_head=any(name in materials for name in ['spectacle','eye whites','iris','Pupils','hair underlayer'])
    method='rigid torso' if wardrobe else 'rigid head' if rigid_head else 'source-weight transfer'
    obj.vertex_groups.clear();groups={}
    max_distance=0;minimum_sum=1;maximum_sum=0
    for vertex in obj.data.vertices:
        point=obj.matrix_world@vertex.co
        if wardrobe:weights={'mixamorig:Spine2':1}
        elif rigid_head:weights={'mixamorig:Head':1}
        else:
            neighbours=tree.find_n(point,1 if 'skin blockout' in obj.name else 4)
            max_distance=max(max_distance,neighbours[0][2]);weights={}
            for _,index,distance in neighbours:
                contribution=1/max(distance,0.00001)**2
                for name,value in source_weights[index].items():weights[name]=weights.get(name,0)+value*contribution
            weights=dict(sorted(weights.items(),key=lambda item:item[1],reverse=True)[:4])
            total=sum(weights.values());weights={name:value/total for name,value in weights.items()}
        total=sum(weights.values());minimum_sum=min(minimum_sum,total);maximum_sum=max(maximum_sum,total)
        for name,weight in weights.items():
            if name not in groups:groups[name]=obj.vertex_groups.new(name=name)
            groups[name].add([vertex.index],weight,'REPLACE')
    modifier=obj.modifiers.new(name='Actual MPFB weighted skeleton',type='ARMATURE');modifier.object=rig
    obj.parent=rig;obj.matrix_parent_inverse=rig.matrix_world.inverted()
    report['meshes'][obj.name]={'vertices':len(obj.data.vertices),'weighted_vertices':len(obj.data.vertices),'method':method,
        'max_nearest_source_distance_m':max_distance,'min_weight_sum':minimum_sum,'max_weight_sum':maximum_sum}
neutral={obj.name:positions(obj) for obj in objects}
report['binding_neutral_max_error_m']=max((a-b).length for name in rest for a,b in zip(rest[name],neutral[name]))
if report['binding_neutral_max_error_m']>0.00001:raise RuntimeError('Binding changed neutral geometry')
head=rig.pose.bones['mixamorig:Head'];head.rotation_mode='XYZ';head.rotation_euler=(0,math.radians(10),0)
posed={obj.name:positions(obj) for obj in objects}
for obj in objects:
    deltas=[(a-b).length for a,b in zip(rest[obj.name],posed[obj.name])]
    item=report['meshes'][obj.name];item['head_turn_max_delta_m']=max(deltas)
    if item['method']=='rigid torso' and max(deltas)>0.00001:raise RuntimeError('Head turn moved torso wardrobe')
    if item['method']=='rigid head' and max(deltas)<0.001:raise RuntimeError('Head accessory did not follow actual skeleton')
scene=bpy.context.scene
scene.render.filepath=str(ROOT/'docs/assets/rig-study-head-turn.png');bpy.ops.render.render(write_still=True)
head.rotation_euler=(0,math.radians(-10),0)
negative={obj.name:positions(obj) for obj in objects}
report['negative_head_turn_max_delta_m']=max((a-b).length for name in rest for a,b in zip(rest[name],negative[name]))
# Exercise morphs and skeletal binding together, without exporting a posed default.
for obj in objects:
    if obj.data.shape_keys:
        for key in obj.data.shape_keys.key_blocks:
            if key.name=='jawOpen':key.value=.38
            elif key.name.startswith('eyeBlink'):key.value=1
            elif key.name in ['browInnerUp','browOuterUpLeft','browOuterUpRight']:key.value=.35
combined={obj.name:positions(obj) for obj in objects}
report['combined_pose_max_delta_m']=max((a-b).length for name in rest for a,b in zip(rest[name],combined[name]))
for values in combined.values():
    if any(not all(math.isfinite(c) for c in point) for point in values):raise RuntimeError('Non-finite combined pose')
for obj in objects:
    if obj.data.shape_keys:
        for key in obj.data.shape_keys.key_blocks:
            if key.name!='Basis':key.value=0
head.rotation_euler=(0,0,0)
for obj in objects:
    if obj.data.shape_keys:
        for key in obj.data.shape_keys.key_blocks:
            if key.name in ['browInnerUp','browOuterUpLeft','browOuterUpRight']:key.value=.35
scene.render.filepath=str(ROOT/'docs/assets/rig-study-brow-lift.png');bpy.ops.render.render(write_still=True)
for obj in objects:
    if obj.data.shape_keys:
        for key in obj.data.shape_keys.key_blocks:
            if key.name!='Basis':key.value=0
# Preview each mouth unit at the restrained lab limit, then restore neutral.
report['mouth_preview_limits']={'mouthPucker':.25,'lipPress':.25,'mouthSmile':.20}
for name,limit in report['mouth_preview_limits'].items():
    for obj in objects:
        if obj.data.shape_keys and name in obj.data.shape_keys.key_blocks:obj.data.shape_keys.key_blocks[name].value=limit
    scene.render.filepath=str(ROOT/f'docs/assets/rig-study-{name}.png');bpy.ops.render.render(write_still=True)
    for obj in objects:
        if obj.data.shape_keys and name in obj.data.shape_keys.key_blocks:obj.data.shape_keys.key_blocks[name].value=0

restored={obj.name:positions(obj) for obj in objects}
report['restored_max_error_m']=max((a-b).length for name in rest for a,b in zip(rest[name],restored[name]))
if report['restored_max_error_m']>0.00001:raise RuntimeError('Rig failed to restore rest pose')
source.hide_set(True);source.hide_render=True;rig.hide_render=True
for obj in bpy.context.selected_objects:obj.select_set(False)
for obj in objects+[rig]:obj.hide_set(False);obj.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.gltf(filepath=str(ROOT/'frontend/public/character-lab/scholar-rig-study.glb'),export_format='GLB',use_selection=True,
    export_animations=False,export_skins=True,export_morph=True,export_extras=True,export_all_influences=False)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'assets/character-production/rig-study.blend'),compress=True)
report['head_turn_degrees']=10
report['limitations']=['Head/neck binding proof only; eye gaze, jaw bone, shoulders and combined extreme poses are not approved.',
 'Eleven facial morphs only; full expressive/viseme set, speech alignment, mouth interior, groom and materials remain unfinished.',
 'Wardrobe intentionally rigid to Spine2; no cloth simulation or shoulder deformation claim.']
(ROOT/'assets/character-production/rig-study-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('RIG STUDY COMPLETE '+json.dumps(report))
