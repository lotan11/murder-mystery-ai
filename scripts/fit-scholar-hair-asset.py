"""Fit the reviewed CC0 MakeHuman short02 hair to the retained Scholar source.
Retains the old fitted cap in the editable scene, excluding it from the active export.
"""
from pathlib import Path
import hashlib,json,math,struct
import bpy,bmesh,numpy as np
from mathutils.bvhtree import BVHTree
from mathutils import Vector


def _positions(obj):
    bpy.context.view_layer.update();value=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=value.to_mesh()
    try:return [value.matrix_world@vertex.co for vertex in mesh.vertices]
    finally:value.to_mesh_clear()


def _hash(obj):
    return hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in obj.data.vertices)).hexdigest()


def _deformation_hash(obj):
    digest=hashlib.sha256()
    if obj.data.shape_keys:
        for key in obj.data.shape_keys.key_blocks:
            digest.update(key.name.encode('utf-8'))
            digest.update(b''.join(struct.pack('<3f',*point.co) for point in key.data))
    for vertex in obj.data.vertices:
        for entry in sorted(vertex.groups,key=lambda value:value.group):digest.update(struct.pack('<If',entry.group,entry.weight))
    return digest.hexdigest()


def fit_hair_asset(head,source,objects,rig,root):
    from bl_ext.scholar_mpfb.mpfb.services.humanservice import HumanService
    root=Path(root);folder=root/'assets/character-production/source-assets/makehuman-system/hair/short02'
    for suffix in ['obj','mhclo','mhmat']:
        if 'explicitly released as CC0' not in (folder/f'short02.{suffix}').read_text(errors='replace')[:1500]:
            raise RuntimeError('Hair source lacks consistent individual CC0 release header: '+suffix)
    protected={obj.name:_hash(obj) for obj in objects}
    protected_deformation={obj.name:_deformation_hash(obj) for obj in objects}
    cap=next(obj for obj in objects if any(mat and 'Grey hair underlayer' in mat.name for mat in obj.data.materials))
    cap.hide_render=True;cap.hide_set(True)
    retired={}
    for obj in objects:
        if not any(mat and 'Grey strand' in mat.name for mat in obj.data.materials):continue
        mesh=bmesh.new();mesh.from_mesh(obj.data)
        selected=[]
        for face in mesh.faces:
            point=obj.matrix_world@face.calc_center_median()
            if point.z>1.643 or (point.z>1.598 and point.y>-.038):selected.append(face)
        retired[obj.name]={'retired_crown_polygons':len(selected),'original_polygons':len(mesh.faces),'retained_vertices':len(mesh.verts)}
        # Keep every original vertex, shape-key layer and weight. Only crown faces retire.
        bmesh.ops.delete(mesh,geom=selected,context='FACES_ONLY');mesh.to_mesh(obj.data);mesh.free()
        retired[obj.name]['active_polygons']=len(obj.data.polygons)
    hair=HumanService.add_mhclo_asset(str(folder/'short02.mhclo'),source,asset_type='Hair',subdiv_levels=0,material_type='MAKESKIN',set_up_rigging=False)
    matrix=hair.matrix_world.copy();hair.parent=None;hair.matrix_world=matrix;hair.name='Scholar short02 silver hair'
    hair.vertex_groups.clear();group=hair.vertex_groups.new(name='mixamorig:Head');group.add(list(range(len(hair.data.vertices))),1,'REPLACE')
    modifier=hair.modifiers.new('Existing Head bone short02 attachment','ARMATURE');modifier.object=rig
    original=next(node.image for material in hair.data.materials if material and material.use_nodes for node in material.node_tree.nodes if node.type=='TEX_IMAGE' and node.name=='diffuseTexture')
    rgba=np.array(original.pixels[:],dtype=np.float32).reshape((-1,4));alpha=rgba[:,3].copy()
    luminance=rgba[:,:3]@np.array([.2126,.7152,.0722],dtype=np.float32)
    value=.34+.48*np.sqrt(np.clip(luminance,0,1));rgba[:,:3]=value[:,None]*np.array([.96,.98,1.0])
    directory=root/'assets/character-production/hair-materials';directory.mkdir(exist_ok=True)
    image=bpy.data.images.new('Scholar short02 silver albedo alpha',width=original.size[0],height=original.size[1],alpha=True)
    image.pixels.foreach_set(rgba.reshape(-1));image.update();image.filepath_raw=str(directory/'short02-silver-albedo.png');image.file_format='PNG';image.save();image.pack()
    material=bpy.data.materials.new('Scholar short02 silver hair');material.use_nodes=True;material.surface_render_method='DITHERED';material.use_transparency_overlap=False
    nodes=material.node_tree.nodes;links=material.node_tree.links;shader=nodes.get('Principled BSDF')
    texture=nodes.new('ShaderNodeTexImage');texture.image=image
    links.new(texture.outputs['Color'],shader.inputs['Base Color']);links.new(texture.outputs['Alpha'],shader.inputs['Alpha'])
    shader.inputs['Roughness'].default_value=.8;shader.inputs['Specular IOR Level'].default_value=.15
    normal=bpy.data.images.load(str(folder/'short02_normal.png'),check_existing=True);normal.colorspace_settings.name='Non-Color';normal.pack()
    normal_texture=nodes.new('ShaderNodeTexImage');normal_texture.image=normal
    normal_map=nodes.new('ShaderNodeNormalMap');normal_map.space='TANGENT';normal_map.inputs['Strength'].default_value=.4
    links.new(normal_texture.outputs['Color'],normal_map.inputs['Color']);links.new(normal_map.outputs['Normal'],shader.inputs['Normal'])
    hair.data.materials.clear();hair.data.materials.append(material)
    for name,digest in protected.items():
        if _hash(bpy.data.objects[name])!=digest:raise RuntimeError('Hair fitting altered protected rest positions: '+name)
        if _deformation_hash(bpy.data.objects[name])!=protected_deformation[name]:raise RuntimeError('Hair fitting altered protected morphs/weights: '+name)
    head.data.calc_loop_triangles();triangles=[tuple(t.vertices) for t in head.data.loop_triangles if head.data.polygons[t.polygon_index].material_index==0]
    neutral_head=_positions(head);neutral_hair=_positions(hair)
    tree=BVHTree.FromPolygons(neutral_head,triangles,all_triangles=True)
    all_nearest=[tree.find_nearest(point)[3] for point in neutral_hair]
    proximal=[index for index,distance in enumerate(all_nearest) if distance<=.004]
    if not proximal:raise RuntimeError('Hair has no anatomical contact proxy within four millimetres')
    def fit():
        hp=_positions(head);hairp=_positions(hair);tree=BVHTree.FromPolygons(hp,triangles,all_triangles=True)
        distances=[];signed=[]
        for index in proximal:
            point=hairp[index];location,normal,_,distance=tree.find_nearest(point)
            distances.append(distance);signed.append((point-location).dot(normal))
        return {'minimum_nearest_head_distance_m':min(distances),'maximum_nearest_head_distance_m':max(distances),'minimum_triangle_signed_offset_m':min(signed),'triangle_inward_sign_count':sum(v<-.00001 for v in signed)}
    bone=rig.pose.bones['mixamorig:Head'];basis=bone.matrix_basis.copy();mode=bone.rotation_mode
    checks={'neutral':fit()};attachment={}
    for degrees in [-10,10]:
        bone.rotation_mode='XYZ';bone.rotation_euler=(0,math.radians(degrees),0);bpy.context.view_layer.update()
        actual=_positions(hair)
        transform=rig.matrix_world@bone.matrix@bone.bone.matrix_local.inverted()@rig.matrix_world.inverted()
        error=max((point-(transform@original)).length for point,original in zip(actual,neutral_hair))
        attachment[str(degrees)]={'maximum_rigid_head_correspondence_error_m':error};checks[str(degrees)]=fit()
        if error>.00001:raise RuntimeError('Imported hair does not follow actual Head bone')
    bone.rotation_mode=mode;bone.matrix_basis=basis;bpy.context.view_layer.update()
    report={'status':'Reviewed bounded development hair replacement; not finished loose Scholar waves','object':hair.name,'material':material.name,'method':'HumanService.add_mhclo_asset and actual retained MPFB full-source MHCLO barycentric/scale mapping','source_hashes':{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.iterdir()) if p.is_file()},'vertices':len(hair.data.vertices),'polygons':len(hair.data.polygons),'weight_method':'All real imported vertices normalized 1.0 to existing mixamorig:Head','min_weight_sum':1.0,'max_weight_sum':1.0,'new_bones':0,'new_morphs':0,'retired_node_names':[cap.name],'retained_editable_cap_vertices':len(cap.data.vertices),'retired_guide_polygons':retired,'protected_rest_position_sha256':protected,'protected_morph_weight_sha256':protected_deformation,'existing_rest_positions_unchanged':True,'cap_geometry_retained_in_source':True,'alpha_preserved_max_error':float(np.max(np.abs(rgba[:,3]-alpha))),'albedo_path':Path(image.filepath_raw).relative_to(root).as_posix(),'albedo_sha256':hashlib.sha256(Path(image.filepath_raw).read_bytes()).hexdigest(),'silver_transform':'0.34+0.48*sqrt(source diffuse luminance), RGB multipliers0.96/0.98/1.0; source alpha retained','roughness':.8,'blender_specular_ior_level':.15,'gltf_specular_factor':.3,'normal_strength':.4,'normal_caveat':'Source MHMAT normal False; supplied purple map explicitly trialled as tangent-space with actual UVs and reviewed after GLB export; no claim of original source intent','maximum_nearest_head_distance_m':max(all_nearest),'proximal_contact_proxy_vertex_count':len(proximal),'proximal_contact_proxy_threshold_m':.004,'contact_fit':checks,'head_attachment':attachment,'limitations':['Dense swept quiff remains a development likeness, not final loose premium hair.','Contact proxy uses nearby geometry vertices, not artist-authored follicle roots; signed triangle values are recorded without claiming watertight coverage or zero intersections.','Only crown polygons of original grey guides retire; all original guide vertex positions, morph data and weights remain in editable source.']}
    (root/'assets/character-production/hair-asset-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return hair,cap,report


def render_hair_comparison(root):
    """Matched neutral views of the final combined material/geometry state."""
    scene=bpy.context.scene;camera=scene.camera
    location=camera.location.copy();rotation=camera.rotation_euler.copy();scale=camera.data.ortho_scale
    resolution=(scene.render.resolution_x,scene.render.resolution_y);filepath=scene.render.filepath
    try:
        camera.data.ortho_scale=.37;scene.render.resolution_x=768;scene.render.resolution_y=900
        for name,point in [('front',(0,-3,1.63)),('threequarter',(2,-3,1.63)),('profile',(3,0,1.63))]:
            camera.location=point;camera.rotation_euler=(Vector((0,-.025,1.63))-camera.location).to_track_quat('-Z','Y').to_euler()
            scene.render.filepath=str(Path(root)/f'docs/assets/scholar-assets-{name}.png');bpy.ops.render.render(write_still=True)
    finally:
        camera.location=location;camera.rotation_euler=rotation;camera.data.ortho_scale=scale
        scene.render.resolution_x,scene.render.resolution_y=resolution;scene.render.filepath=filepath
