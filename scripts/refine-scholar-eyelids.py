"""Accepted conservative neutral eyelid correction for the derived Scholar only.
Call after binding-neutral verification, before skin baking/crown/facial-groom fitting.
Adds the same local offset to Basis and every existing shape; no new facial controls.
"""
from pathlib import Path
import gzip,hashlib,json,struct,subprocess
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

CONFIG_SHA256='5e08dc40308865d5d6dc3f794cbba19cc20e6a25fefb35cf398575d852fc8c67'
FACE_STUDY_SHA256='9824ffa51275815d3d7fe252e76dbd31d0fd992e40e02ecb2ec21f9110ee5153'
BEFORE_BASIS_SHA256='37267eb6ede4390571636ed4ef25f194cafee861883a1d207c72a8c7405962a1'
AFTER_BASIS_SHA256='bd8a821a61f8c7ff6118f0aed7912872233dcc34d84ca834a41f736e47173843'
TARGET_HASHES={
 'l-eye-height2-incr.target.gz':'2ad24113bdd67f07870cb0298d0b0732ab5185b11f890946212c4cbb19845e34',
 'r-eye-height2-incr.target.gz':'22fce2f25e349ab9f2beff8e3a4b54bda757535169afcfa0b4d022548f14494e'}


def refine_eyelids(head,source,root,rig):
    root=Path(root)
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    config_path=root/'assets/character-production/scholar.json'
    if sha(config_path)!=CONFIG_SHA256:raise RuntimeError('Eyelid correction requires the reviewed anatomical configuration')
    face_path=root/'assets/character-production/face-study.blend'
    if sha(face_path)!=FACE_STUDY_SHA256:raise RuntimeError('Face-study source changed; repeat eyelid visual/offset review')
    config=json.loads(config_path.read_text(encoding='utf-8'));mpfb=root/config['mpfb']['source_path']
    commit=subprocess.check_output(['git','-C',str(mpfb),'rev-parse','HEAD'],text=True).strip()
    if commit!=config['mpfb']['commit']:raise RuntimeError('Pinned MPFB source changed')
    if head.get('scholar_eyelid_refinement_applied'):raise RuntimeError('Eyelid correction already applied; rebuild original source')
    if head.data.shape_keys is None:raise RuntimeError('Expected the reviewed facial shape keys')
    keys=head.data.shape_keys.key_blocks;basis=keys.get('Basis')
    if basis is None or len(head.data.vertices)!=4353:raise RuntimeError('Reviewed head topology is missing')
    if any(abs(key.value)>1e-8 for key in keys if key.name!='Basis'):raise RuntimeError('Eyelid refinement requires neutral facial values')

    def coordinate_hash(obj):
        return hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in obj.data.vertices)).hexdigest()
    def basis_hash():
        return hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in basis.data)).hexdigest()
    def delta_hashes():
        return {key.name:hashlib.sha256(b''.join(struct.pack('<3f',*(key.data[i].co-basis.data[i].co)) for i in range(len(basis.data)))).hexdigest() for key in keys if key.name!='Basis'}
    def uv_hash():
        return hashlib.sha256(b''.join(struct.pack('<2f',*d.uv) for layer in head.data.uv_layers for d in layer.data)).hexdigest()
    def weights_hash():
        return hashlib.sha256(b''.join(struct.pack('<IIf',v.index,g.group,g.weight) for v in head.data.vertices for g in v.groups)).hexdigest()
    def rig_hash():
        return hashlib.sha256(b''.join(b.name.encode()+b''.join(struct.pack('<4f',*row) for row in b.matrix_local) for b in rig.data.bones)).hexdigest()
    def evaluated_points(obj):
        bpy.context.view_layer.update();evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        try:return [evaluated.matrix_world@v.co for v in mesh.vertices]
        finally:evaluated.to_mesh_clear()
    def smoothstep(low,high,value):
        t=max(0.,min(1.,(value-low)/(high-low)));return t*t*(3-2*t)
    def gltf(point):return [point.x,point.z,-point.y]

    before_hash=basis_hash()
    if before_hash!=BEFORE_BASIS_SHA256:raise RuntimeError('Head neutral differs from reviewed eyelid input')
    if coordinate_hash(head)!=before_hash:raise RuntimeError('Mesh neutral and Basis coordinates disagree')
    before_local=[v.co.copy() for v in basis.data];before_world=evaluated_points(head)
    protected={'uv_sha256':uv_hash(),'weights_sha256':weights_hash(),'rig_rest_sha256':rig_hash(),'morph_deltas_sha256':delta_hashes()}
    other_geometry={obj.name:coordinate_hash(obj) for obj in bpy.data.objects if obj.type=='MESH' and obj!=head}
    source_points=evaluated_points(source);tree=KDTree(len(source_points))
    for index,point in enumerate(source_points):tree.insert(point,index)
    tree.balance();mapping=[tree.find(head.matrix_world@point) for point in before_local]
    mapping_error=max(distance for _,_,distance in mapping)
    if mapping_error>.0000002:raise RuntimeError('Head/source correspondence no longer matches accepted eyelid preview')
    raw={};target_files={};source_key_errors={}
    source_basis=source.data.shape_keys.key_blocks['Basis']
    for filename,expected in TARGET_HASHES.items():
        path=mpfb/'src/mpfb/data/targets/eyes'/filename
        if sha(path)!=expected:raise RuntimeError('Anatomical eye target differs from reviewed bytes')
        target_files[path.relative_to(root).as_posix()]=expected;side_raw={}
        for line in gzip.decompress(path.read_bytes()).decode('utf-8').splitlines():
            if not line.strip() or line.startswith('#'):continue
            index,x,y,z=line.split();index=int(index)
            # Pinned TargetService._target_string_to_shape_key_info/_set_shape_key_coords_from_dict.
            delta=Vector((float(x),-float(z),float(y)))*.1
            side_raw[index]=delta;raw[index]=raw.get(index,Vector())+delta
        key=source.data.shape_keys.key_blocks.get(filename.removesuffix('.target.gz'))
        if key is None or abs(key.value-.65)>.000001:raise RuntimeError('Expected original0.65 eye-height source key')
        error=max((key.data[i].co-source_basis.data[i].co-side_raw.get(i,Vector())).length for i in range(len(source_basis.data)))
        if error>.0000001:raise RuntimeError('Raw target coordinate/scale does not match loaded source key')
        source_key_errors[key.name]=error
    inverse=head.matrix_world.inverted().to_3x3();moves=[];factors=[]
    for point,(_,index,distance) in zip(before_local,mapping):
        world=head.matrix_world@point
        factor=smoothstep(.018,.022,abs(world.x))*smoothstep(1.602,1.607,world.z);factors.append(factor)
        moves.append(inverse@(source.matrix_world.to_3x3()@raw.get(index,Vector())*.20*factor))
    # Equal offsets preserve relative morphs. Mesh neutral remains consistent with Basis.
    for key in keys:
        for index,move in enumerate(moves):key.data[index].co+=move
    for index,move in enumerate(moves):head.data.vertices[index].co+=move
    bpy.context.view_layer.update();after_world=evaluated_points(head);after_hash=basis_hash()
    if after_hash!=AFTER_BASIS_SHA256:raise RuntimeError('Eyelid neutral result differs from visually reviewed candidate')
    if coordinate_hash(head)!=after_hash:raise RuntimeError('Corrected mesh and Basis coordinates disagree')
    after_protected={'uv_sha256':uv_hash(),'weights_sha256':weights_hash(),'rig_rest_sha256':rig_hash(),'morph_deltas_sha256':delta_hashes()}
    if protected!=after_protected:raise RuntimeError('Eyelid correction altered protected weights/UV/rig/morph deltas')
    if any(coordinate_hash(bpy.data.objects[name])!=value for name,value in other_geometry.items()):raise RuntimeError('Eyelid correction changed another mesh')
    offsets=[];quantized={}
    for index,(before,after) in enumerate(zip(before_local,basis.data)):
        world=head.matrix_world@before;after_point=head.matrix_world@after.co
        a=tuple(round(value,6) for value in gltf(world));b=tuple(round(value,6) for value in gltf(after_point))
        quantized.setdefault(a,set()).add(b)
        delta=after.co-before
        if delta.length>0:
            offsets.append({'head_vertex_index':index,'source_vertex_index':mapping[index][1],'mapping_error_m':mapping[index][2],
              'localization_factor':factors[index],'local_before':list(before),'local_after_float32':list(after.co),
              'local_delta_float32':list(delta),'world_before':list(world),'world_after_float32':list(after_point),
              'gltf_world_before':gltf(world),'gltf_world_after':gltf(after_point)})
    ambiguous=sum(len(values)>1 for values in quantized.values())
    if ambiguous:raise RuntimeError('Declared six-decimal point mapping is ambiguous')
    deltas=[(a-b).length for a,b in zip(before_world,after_world)]
    protected_face=max(deltas[i] for i,point in enumerate(before_world) if abs(point.x)<.018 and point.z<1.605)
    if protected_face!=0 or max(deltas)>.000561:raise RuntimeError('Eyelid offset escaped reviewed eye-local bounds')
    min_dot=1.;area_ratios=[]
    for polygon in head.data.polygons:
        for j in range(1,len(polygon.vertices)-1):
            ids=[polygon.vertices[k] for k in [0,j,j+1]]
            a,b,c=[before_world[i] for i in ids];x,y,z=[after_world[i] for i in ids]
            old=(b-a).cross(c-a);new=(y-x).cross(z-x)
            if old.length<1e-12 or new.length<1e-12:raise RuntimeError('Degenerate eyelid/head triangle')
            min_dot=min(min_dot,old.normalized().dot(new.normalized()));area_ratios.append(new.length/old.length)
    if min_dot<.99 or min(area_ratios)<.85 or max(area_ratios)>1.08:raise RuntimeError('Eyelid correction exceeds reviewed face-integrity bounds')
    evidence={'version':1,'status':'Accepted localized neutral correction for separate development rig; no full likeness/eye-contact approval',
      'head_name':head.name,'head_vertex_count':len(before_local),'changed_vertex_count':len(offsets),
      'head_matrix_world':[list(row) for row in head.matrix_world],'source_matrix_world':[list(row) for row in source.matrix_world],
      'basis_local_before_sha256':before_hash,'basis_local_after_sha256':after_hash,
      'gltf_coordinate_rule':'Blender world(X,Y,Z) -> glTF world(X,Z,-Y); apply actual node/world transforms if exporter changes',
      'six_decimal_point_mapping_ambiguous_keys':ambiguous,'offsets':offsets}
    evidence_path=root/'assets/character-production/eyelid-neutral-offsets.json'
    evidence_path.write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    report={'version':1,'status':'Accepted modest alertness correction; unfinished development avatar',
      'invocation':'After original binding-neutral verification, before skin bake/crown/facial groom. Refresh head rest only after recording correction.',
      'source_face_study_sha256':FACE_STUDY_SHA256,'config_sha256':CONFIG_SHA256,'mpfb_commit':commit,'source_targets_sha256':target_files,
      'source_key_coordinate_scale_max_errors_m':source_key_errors,'source_head_mapping_max_error_m':mapping_error,
      'method':'Actual left/right eye-height2-incr anatomical deltas; raw(X,-Z,Y)*0.1*0.20; smooth world eye-local mask; equal offset to every key and mesh neutral',
      'localization':'smoothstep(absX0.018..0.022m)*smoothstep(Z1.602..1.607m)',
      'target_contribution_delta':.20,'peak_effective_original_weight':.85,
      'head_vertex_count':len(before_local),'changed_vertices':len(offsets),'significantly_changed_vertices':sum(value>1e-7 for value in deltas),
      'max_neutral_delta_m':max(deltas),'protected_lower_nose_lips_delta_m':protected_face,
      'basis_local_before_sha256':before_hash,'basis_local_after_sha256':after_hash,
      'morph_count':len(protected['morph_deltas_sha256']),'protected_data_before':protected,'protected_data_after':after_protected,
      'morph_deltas_unchanged':True,'uv_unchanged':True,'weights_unchanged':True,'rig_unchanged':True,'other_mesh_geometry_unchanged':True,
      'triangle_min_normal_dot':min_dot,'triangle_area_ratio_range':[min(area_ratios),max(area_ratios)],
      'neutral_offset_manifest':{'path':evidence_path.relative_to(root).as_posix(),'sha256':hashlib.sha256(evidence_path.read_bytes().replace(b'\r\n',b'\n')).hexdigest(),'hash_encoding':'UTF-8 LF','rows':len(offsets),'six_decimal_mapping_ambiguities':ambiguous},
      'limitations':['Neutral aperture correction only; existing expression deltas are unchanged, not reauthored.',
       'Closed blink was visually reviewed in preview; integration must recheck blink/head/combined poses and fitted groom.',
       'No physical eye collision, corneal volume, gaze control, final likeness or production rig approval.']}
    head['scholar_eyelid_refinement_applied']=True
    (root/'assets/character-production/eyelid-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report
