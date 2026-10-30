"""Bake supported UV skin maps from the existing Scholar material in Blender.
No sculpting, generated images, painted lighting or geometry modification.
"""
from array import array
from pathlib import Path
import hashlib,json,math
import bpy


def bake_skin_materials(head, root, resolution=1024):
    root=Path(root);out=root/'assets/character-production/skin-materials';out.mkdir(parents=True,exist_ok=True)
    if head.data.uv_layers.active is None:raise RuntimeError('Skin baking requires the existing anatomical UV map')
    skin=next(material for material in head.data.materials if material and material.name=='Neutral aged skin blockout')
    principled=skin.node_tree.nodes.get('Principled BSDF')
    source_color=list(principled.inputs['Base Color'].default_value)
    source_roughness=float(principled.inputs['Roughness'].default_value)
    source_normal=principled.inputs['Normal'].links[0].from_socket if principled.inputs['Normal'].is_linked else None
    if source_normal is None:raise RuntimeError('Expected existing procedural bump to bake')
    scene=bpy.context.scene
    previous_samples=scene.cycles.samples;previous_device=scene.cycles.device;previous_engine=scene.render.engine
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8
    scene.render.bake.use_selected_to_active=False;scene.render.bake.use_clear=True;scene.render.bake.margin=8
    scene.render.bake.normal_space='TANGENT';scene.render.bake.normal_r='POS_X';scene.render.bake.normal_g='POS_Y';scene.render.bake.normal_b='POS_Z'
    for obj in bpy.context.selected_objects:obj.select_set(False)
    head.hide_set(False);head.select_set(True);bpy.context.view_layer.objects.active=head
    targets=[]
    for material in head.data.materials:
        if material and material.use_nodes:
            node=material.node_tree.nodes.new('ShaderNodeTexImage');node.name='Scholar bake target';targets.append((material,node))
    def new_image(name,color=False):
        image=bpy.data.images.new(name,width=resolution,height=resolution,alpha=True,float_buffer=False)
        image.colorspace_settings.name='sRGB' if color else 'Non-Color'
        image.file_format='PNG';return image
    def bake(image,kind):
        for material,node in targets:
            for candidate in material.node_tree.nodes:candidate.select=False
            node.image=image;node.select=True;material.node_tree.nodes.active=node
        if kind=='DIFFUSE':bpy.ops.object.bake(type=kind,pass_filter={'COLOR'})
        else:bpy.ops.object.bake(type=kind)
        pixels=array('f',[0])*len(image.pixels);image.pixels.foreach_get(pixels)
        return pixels
    def save(image,filename):
        path=out/filename;image.filepath_raw=str(path);image.save();image.pack()
        return {'path':path.relative_to(root).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'bytes':path.stat().st_size,'width':resolution,'height':resolution,'colorspace':image.colorspace_settings.name}
    base=new_image('Scholar baked skin base color',True);base_pixels=bake(base,'DIFFUSE')
    roughness=new_image('Scholar baked skin roughness');rough_pixels=bake(roughness,'ROUGHNESS')
    normal=new_image('Scholar baked skin tangent normal');normal_pixels=bake(normal,'NORMAL')
    # Compare with an actual bump-disabled bake on the same UVs to prove the source detail survived.
    for link in list(principled.inputs['Normal'].links):skin.node_tree.links.remove(link)
    baseline=new_image('Scholar normal validation baseline');baseline_pixels=bake(baseline,'NORMAL')
    skin.node_tree.links.new(source_normal,principled.inputs['Normal'])
    coverage=new_image('Scholar UV coverage validation')
    outputs=[]
    for material,_ in targets:
        output=next(node for node in material.node_tree.nodes if node.type=='OUTPUT_MATERIAL' and node.is_active_output)
        surface=output.inputs['Surface'];prior=surface.links[0].from_socket
        emission=material.node_tree.nodes.new('ShaderNodeEmission');emission.inputs['Color'].default_value=(1,1,1,1)
        material.node_tree.links.new(emission.outputs['Emission'],surface);outputs.append((material,output,prior,emission))
    coverage_pixels=bake(coverage,'EMIT')
    for material,output,prior,emission in outputs:
        material.node_tree.links.new(prior,output.inputs['Surface']);material.node_tree.nodes.remove(emission)
    valid=[offset for offset in range(0,len(normal_pixels),4) if coverage_pixels[offset]>.9]
    if len(valid)<1000:raise RuntimeError('Insufficient valid UV bake pixels')
    difference=math.sqrt(sum((normal_pixels[offset+channel]-baseline_pixels[offset+channel])**2 for offset in valid for channel in (0,1))/(len(valid)*2))
    ranges={str(channel):[min(normal_pixels[offset+channel] for offset in valid),max(normal_pixels[offset+channel] for offset in valid)] for channel in (0,1,2)}
    if not difference>.0005:raise RuntimeError('Normal bake did not capture meaningful procedural bump detail: '+str(difference))
    report={'resolution':resolution,'engine':'Cycles CPU','samples':8,'margin_pixels':8,'normal_space':'TANGENT +X +Y +Z',
      'source_material':skin.name,'source_base_color_linear':source_color,'source_roughness':source_roughness,
      'baked_surface_pixels_including_margin':len(valid),'coverage_method':'White emission surface coverage bake, including eight-pixel bake margin','normal_vs_bump_disabled_rms_xy':difference,'normal_channel_ranges':ranges,
      'geometry_modified':False,'light_baked_into_color':False,'limitations':['Existing shallow procedural grain only; no authored wrinkles, pores, photographic skin scan or final likeness approval.',
        'Subsurface response is not baked into PBR maps; final browser appearance still needs review.']}
    report['maps']={'base_color':save(base,'skin-base-color.png'),'roughness':save(roughness,'skin-roughness.png'),'normal':save(normal,'skin-normal.png')}
    # Remove temporary bake targets and bind explicit glTF-supported material inputs.
    for material,node in targets:material.node_tree.nodes.remove(node)
    bpy.data.images.remove(baseline);bpy.data.images.remove(coverage)
    for label,image in [('Base Color',base),('Roughness',roughness)]:
        node=skin.node_tree.nodes.new('ShaderNodeTexImage');node.name='Scholar baked '+label;node.image=image
        skin.node_tree.links.new(node.outputs['Color'],principled.inputs[label])
    principled.inputs['Base Color'].default_value=(1,1,1,1);principled.inputs['Roughness'].default_value=1
    normal_texture=skin.node_tree.nodes.new('ShaderNodeTexImage');normal_texture.name='Scholar baked tangent normal';normal_texture.image=normal
    normal_map=skin.node_tree.nodes.new('ShaderNodeNormalMap');normal_map.space='TANGENT';normal_map.inputs['Strength'].default_value=1
    skin.node_tree.links.new(normal_texture.outputs['Color'],normal_map.inputs['Color']);skin.node_tree.links.new(normal_map.outputs['Normal'],principled.inputs['Normal'])
    # The old source nodes remain disconnected for editable provenance; avoid claiming runtime subsurface support.
    principled.inputs['Subsurface Weight'].default_value=0
    scene.cycles.samples=previous_samples;scene.cycles.device=previous_device;scene.render.engine=previous_engine
    report['restored_render_samples']=previous_samples
    (root/'assets/character-production/skin-material-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report
