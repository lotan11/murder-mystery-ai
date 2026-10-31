"""Bake the accepted restrained CC0 diffuse blend into the separate Scholar study.
Requires a fresh procedural skin bake. Source assets, anatomy and UVs are immutable.
"""
from pathlib import Path
import copy,hashlib,json,struct
import bpy

SOURCE_SHA256='dfb2310ed3e0ad024ea7a3ad321215e2e9e2994cca64043d9f3d07c6543ec847'
MATERIAL_SHA256='001eccec34180d4eb7369933360116a7ea1022c72674c1b012b988af65002600'


def refine_skin_color(head,root):
    root=Path(root);source=root/'assets/character-production/source-assets/makehuman-system/skins/old_caucasian_male'
    diffuse=source/'old_lightskinned_male_diffuse.png';mhmat=source/'old_caucasian_male.mhmat'
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    if sha(diffuse)!=SOURCE_SHA256 or sha(mhmat)!=MATERIAL_SHA256:raise RuntimeError('Skin candidate differs from the audited CC0 files')
    header=mhmat.read_text(encoding='utf-8')
    if 'explicitly released as CC0 in september 2020' not in header:raise RuntimeError('Audited explicit CC0 material declaration missing')
    validation_path=root/'assets/character-production/skin-material-validation.json'
    material_report=json.loads(validation_path.read_text(encoding='utf-8'))
    input_color=copy.deepcopy(material_report['maps']['base_color'])
    if input_color['path']!='assets/character-production/skin-materials/skin-base-color.png':raise RuntimeError('Skin color refinement requires a fresh procedural base-color bake')
    if sha(root/input_color['path'])!=input_color['sha256']:raise RuntimeError('Fresh procedural skin-color bytes do not match bake evidence')
    skin=next(m for m in head.data.materials if m and m.name=='Neutral aged skin blockout')
    shader=next(n for n in skin.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    base_socket=shader.inputs['Base Color'].links[0].from_socket
    input_image=getattr(base_socket.node,'image',None)
    if input_image is None or not input_image.packed_file or hashlib.sha256(bytes(input_image.packed_file.data)).hexdigest()!=input_color['sha256']:
        raise RuntimeError('Active skin color binding is not the verified fresh procedural bake')
    def geometry_hash():
        h=hashlib.sha256()
        for row in head.matrix_world:
            h.update(struct.pack('<4f',*row))
        for vertex in head.data.vertices:
            h.update(struct.pack('<3f',*vertex.co))
            for entry in vertex.groups:h.update(struct.pack('<If',entry.group,entry.weight))
        for polygon in head.data.polygons:
            h.update(struct.pack('<I',polygon.material_index))
            for index in polygon.vertices:h.update(struct.pack('<I',index))
        for layer in head.data.uv_layers:
            h.update(layer.name.encode())
            for item in layer.data:h.update(struct.pack('<2f',*item.uv))
        if head.data.shape_keys:
            for key in head.data.shape_keys.key_blocks:
                h.update(key.name.encode());h.update(struct.pack('<f',key.value))
                for point in key.data:h.update(struct.pack('<3f',*point.co))
        return h.hexdigest()
    def binding(name):
        socket=shader.inputs[name]
        return {'default':list(socket.default_value) if hasattr(socket.default_value,'__len__') else socket.default_value,
                'links':[{'node':l.from_node.name,'socket':l.from_socket.name,'image':getattr(getattr(l.from_node,'image',None),'name',None)} for l in socket.links]}
    before_geometry=geometry_hash();normal_before=binding('Normal');rough_before=binding('Roughness')
    untouched_maps={name:copy.deepcopy(material_report['maps'][name]) for name in ['normal','roughness']}
    before_source=sha(diffuse)
    uv0=head.data.uv_layers[0]
    nodes=skin.node_tree.nodes;links=skin.node_tree.links
    image=bpy.data.images.load(str(diffuse),check_existing=False);image.name='CC0 MakeHuman old male diffuse source';image.colorspace_settings.name='sRGB';image.filepath=bpy.path.relpath(str(diffuse));image.pack()
    texture=nodes.new('ShaderNodeTexImage');texture.name='Scholar audited CC0 age-color source';texture.image=image;texture.interpolation='Linear';texture.extension='EXTEND'
    uv=nodes.new('ShaderNodeUVMap');uv.uv_map=uv0.name;links.new(uv.outputs['UV'],texture.inputs['Vector'])
    tint=nodes.new('ShaderNodeMixRGB');tint.name='Scholar restrained age-source tint';tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.78,.82,.90,1);links.new(texture.outputs['Color'],tint.inputs[1])
    geometry=nodes.new('ShaderNodeNewGeometry');split=nodes.new('ShaderNodeSeparateXYZ');links.new(geometry.outputs['Position'],split.inputs[0])
    rear=nodes.new('ShaderNodeMapRange');rear.name='Scholar age-color rear mask';rear.interpolation_type='SMOOTHSTEP';rear.clamp=True
    rear.inputs['From Min'].default_value=-.075;rear.inputs['From Max'].default_value=-.045;rear.inputs['To Min'].default_value=0;rear.inputs['To Max'].default_value=1;links.new(split.outputs['Y'],rear.inputs['Value'])
    low=nodes.new('ShaderNodeMapRange');low.name='Scholar age-color nape mask';low.interpolation_type='SMOOTHSTEP';low.clamp=True
    low.inputs['From Min'].default_value=1.63;low.inputs['From Max'].default_value=1.67;low.inputs['To Min'].default_value=1;low.inputs['To Max'].default_value=0;links.new(split.outputs['Z'],low.inputs['Value'])
    suppress=nodes.new('ShaderNodeMath');suppress.operation='MULTIPLY';links.new(rear.outputs['Result'],suppress.inputs[0]);links.new(low.outputs['Result'],suppress.inputs[1])
    keep=nodes.new('ShaderNodeMath');keep.operation='SUBTRACT';keep.inputs[0].default_value=1;links.new(suppress.outputs[0],keep.inputs[1])
    weight=nodes.new('ShaderNodeMath');weight.operation='MULTIPLY';weight.inputs[1].default_value=.45;links.new(keep.outputs[0],weight.inputs[0])
    blend=nodes.new('ShaderNodeMixRGB');blend.name='Scholar restrained age-color blend';blend.blend_type='MIX';links.new(weight.outputs[0],blend.inputs[0]);links.new(base_socket,blend.inputs[1]);links.new(tint.outputs['Color'],blend.inputs[2]);links.new(blend.outputs['Color'],shader.inputs['Base Color'])
    # Bake only color; UV0 carries the mask result in the runtime material, not unsupported nodes.
    scene=bpy.context.scene
    previous={'engine':scene.render.engine,'device':scene.cycles.device,'samples':scene.cycles.samples}
    targets=[]
    for obj in bpy.context.selected_objects:obj.select_set(False)
    head.hide_set(False);head.select_set(True);bpy.context.view_layer.objects.active=head
    baked=bpy.data.images.new('Scholar restrained age-blended skin color',width=1024,height=1024,alpha=True,float_buffer=False);baked.colorspace_settings.name='sRGB';baked.file_format='PNG'
    for material in head.data.materials:
        if material and material.use_nodes:
            for old in material.node_tree.nodes:old.select=False
            target=material.node_tree.nodes.new('ShaderNodeTexImage');target.name='Scholar age-color bake target';target.image=baked;target.select=True;material.node_tree.nodes.active=target;targets.append((material,target))
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8
    scene.render.bake.use_selected_to_active=False;scene.render.bake.use_clear=True;scene.render.bake.margin=8
    bpy.ops.object.bake(type='DIFFUSE',pass_filter={'COLOR'})
    path=root/'assets/character-production/skin-materials/skin-age-blend-color.png';baked.filepath_raw=str(path);baked.save();baked.pack()
    for material,target in targets:material.node_tree.nodes.remove(target)
    baked_node=nodes.new('ShaderNodeTexImage');baked_node.name='Scholar baked age-blended Base Color';baked_node.image=baked;baked_node.interpolation='Linear';links.new(uv.outputs['UV'],baked_node.inputs['Vector']);links.new(baked_node.outputs['Color'],shader.inputs['Base Color'])
    scene.render.engine=previous['engine'];scene.cycles.device=previous['device'];scene.cycles.samples=previous['samples']
    texture_report={'path':path.relative_to(root).as_posix(),'sha256':sha(path),'bytes':path.stat().st_size,'width':1024,'height':1024,'colorspace':'sRGB'}
    after_geometry=geometry_hash()
    if before_geometry!=after_geometry:raise RuntimeError('Skin color refinement changed geometry/UV/weights/morphs or material assignments')
    if binding('Normal')!=normal_before or binding('Roughness')!=rough_before:raise RuntimeError('Skin color refinement changed normal or roughness binding')
    if sha(diffuse)!=before_source or sha(root/input_color['path'])!=input_color['sha256']:raise RuntimeError('Skin source/procedural input image was altered')
    for name,evidence in untouched_maps.items():
        if sha(root/evidence['path'])!=evidence['sha256']:raise RuntimeError('Skin normal/roughness bytes changed')
    report={'status':'Restrained CC0 diffuse color blend for development Scholar; not clean/de-lit scan or finished likeness',
      'source':{'path':diffuse.relative_to(root).as_posix(),'sha256':before_source,'width':image.size[0],'height':image.size[1],'license':'CC0-1.0','material_path':mhmat.relative_to(root).as_posix(),'material_sha256':sha(mhmat),'license_evidence':'MHMat explicitly released as CC0 in September2020'},
      'material_name':skin.name,'head_object':head.name,'input_color':input_color,'texture':texture_report,'uv_layer':uv0.name,'uv_index':0,
      'recipe':{'source_mix_weight':.45,'source_tint_linear':[.78,.82,.90],'mask_coordinate_space':'Geometry Position world meters at rest; baked into UV0',
        'rear_y_transition_m':[-.075,-.045],'below_z_transition_m':[1.63,1.67],'mask_interpolation':'SMOOTHSTEP','weight_formula':'.45*(1-rearY*belowZ)'},
      'bake':{'type':'DIFFUSE COLOR only','engine':'Cycles CPU','samples':8,'margin_pixels':8,'resolution':1024,'additional_lighting_baked':False},
      'geometry_uv_weights_morph_sha256_before':before_geometry,'geometry_uv_weights_morph_sha256_after':after_geometry,
      'geometry_unchanged':True,'uv_mapping_unchanged':True,'weights_morphs_material_assignments_unchanged':True,
      'source_image_unchanged':True,'procedural_input_preserved':True,'normal_roughness_preserved':True,
      'limitations':['Existing diffuse appearance retained; no clean/de-lit scan claim and original MHMat litsphere/emission/subsurface behavior not recreated.',
       'Adds color variation only; does not sculpt age anatomy or finish portrait likeness, eyelids, groom or skin artistry.',
       'Normal/roughness and oral material assignments unchanged; only the active supported base-color image is replaced.']}
    material_report['input_color']=input_color
    material_report['maps']['base_color']=texture_report
    material_report['color_refinement']={'validation_path':'assets/character-production/skin-color-validation.json','source_sha256':before_source,'additional_lighting_baked':False,'source_is_clean_scan_claimed':False}
    material_report['limitations']=['Procedural grain/normal proof retained; restrained CC0 diffuse blend adds color variation only, not sculpted age anatomy or final skin/likeness approval.',
      'Existing diffuse is not established as a clean/de-lit scan; no additional light was baked by the COLOR-only pass.',
      'Subsurface response is not baked into PBR maps; final browser appearance still requires review.']
    validation_path.write_text(json.dumps(material_report,indent=2)+'\n',encoding='utf-8')
    (root/'assets/character-production/skin-color-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report
