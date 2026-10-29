"""Reproducible anatomical Scholar blockout; run with portable Blender 4.5.

blender --background --factory-startup --python-exit-code 1 --python scripts/build-scholar.py
Set BLENDER_USER_RESOURCES to data/character-tools/blender-user before launching.
Requires the exact pinned MPFB checkout in scholar.json; no downloads or paid services.
This is a review bust, not approved likeness or a production facial rig.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
ARGS = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
parser = argparse.ArgumentParser()
parser.add_argument('--config', type=Path, default=ROOT/'assets/character-production/scholar.json')
parser.add_argument('--skip-renders', action='store_true')
args = parser.parse_args(ARGS)
config = json.loads(args.config.read_text(encoding='utf-8'))
random.seed(config['procedural']['seed'])
mpfb_root = ROOT/config['mpfb']['source_path']
commit = subprocess.check_output(['git','-C',str(mpfb_root),'rev-parse','HEAD'],text=True).strip()
if commit != config['mpfb']['commit']:
    raise RuntimeError('Use the pinned MPFB checkout from scholar.json, without substituting another base mesh.')
base_path = mpfb_root/'src/mpfb/data/3dobjs/base.obj'
if hashlib.sha256(base_path.read_bytes()).hexdigest()!=config['mpfb']['base_obj_sha256']:
    raise RuntimeError('The pinned anatomical base mesh checksum does not match.')

# Blender extension namespace is required by MPFB >= 2.0.18.
import addon_utils
bpy.context.preferences.extensions.repos.new(name='Scholar MPFB source',module='scholar_mpfb',custom_directory=str(mpfb_root/'src'))
module = addon_utils.enable('bl_ext.scholar_mpfb.mpfb',default_set=True)
if module is None:
    raise RuntimeError('MPFB could not be enabled in Blender extension mode.')
from bl_ext.scholar_mpfb.mpfb.services.humanservice import HumanService
from bl_ext.scholar_mpfb.mpfb.services.targetservice import TargetService
from bl_ext.scholar_mpfb.mpfb.services.locationservice import LocationService

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
source = HumanService.create_human(scale=0.1,feet_on_ground=True,macro_detail_dict=config['macro'])
source.name='MPFB_Parametric_Source_67_Approx'
for relative,weight in config['targets'].items():
    TargetService.load_target(source,str(Path(LocationService.get_mpfb_data('targets'))/relative),weight=weight)
bpy.context.view_layer.update()

# Joint helpers provide anatomical eye anchors before helper geometry is masked.
for modifier in source.modifiers: modifier.show_viewport=False
bpy.context.view_layer.update()
full_eval=source.evaluated_get(bpy.context.evaluated_depsgraph_get())
full=full_eval.to_mesh()
def group_center(name):
    group=source.vertex_groups[name].index
    points=[full.vertices[v.index].co.copy() for v in source.data.vertices if any(g.group==group for g in v.groups)]
    return sum(points,Vector())/len(points)
left_eye,right_eye=group_center('joint-l-eye'),group_center('joint-r-eye')
eye_z=(left_eye.z+right_eye.z)/2
full_eval.to_mesh_clear()
for modifier in source.modifiers: modifier.show_viewport=True
bpy.context.view_layer.update()
mesh=bpy.data.meshes.new_from_object(source.evaluated_get(bpy.context.evaluated_depsgraph_get()))
bust=bpy.data.objects.new('Scholar_Anatomical_Head_Neck',mesh);bpy.context.collection.objects.link(bust)
bm=bmesh.new();bm.from_mesh(mesh)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<config['procedural']['bust_skin_cutoff']],context='VERTS')
bm.to_mesh(mesh);bm.free()
for polygon in mesh.polygons:polygon.use_smooth=True
source.hide_render=True;source.hide_set(True)
source_collection=bpy.data.collections.new('EDITABLE_MAKEHUMAN_SOURCE_CC0');bpy.context.scene.collection.children.link(source_collection)
for collection in list(source.users_collection):collection.objects.unlink(source)
source_collection.objects.link(source)
source_collection.hide_render=True
bust['stage']='Anatomical work-in-progress; no facial rig or visemes'
bust['base_asset_license']='MakeHuman/MPFB bundled assets CC0-1.0'
bust['mpfb_source_commit']=commit
bust['authoring_config']='assets/character-production/scholar.json'

character=[bust]
def mat(name,color,roughness=.6,metallic=0):
    material=bpy.data.materials.new(name);material.use_nodes=True
    principled=material.node_tree.nodes.get('Principled BSDF')
    principled.inputs['Base Color'].default_value=(*color,1)
    principled.inputs['Roughness'].default_value=roughness
    principled.inputs['Metallic'].default_value=metallic
    material.diffuse_color=(*color,1)
    return material
skin=mat('Neutral aged skin blockout',(.37,.225,.155),.60)
skin.node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.06
bust.data.materials.clear();bust.data.materials.append(skin)
# Very shallow skin breakup is a render aid, not a claimed texture likeness.
noise=skin.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=165
bump=skin.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.0009
skin.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
skin.node_tree.links.new(bump.outputs['Normal'],skin.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
coat=mat('Brown tweed blocking',(.055,.032,.018),.86)
vest=mat('Forest wool waistcoat',(.027,.049,.038),.88)
shirt=mat('Ivory shirt',(.72,.69,.59),.8)
tie=mat('Muted patterned tie blocking',(.105,.060,.027),.78)
metal=mat('Thin dark bronze spectacle rims',(.075,.062,.046),.28,.72)
white=mat('Natural eye whites',(.77,.78,.71),.24)
iris=mat('Slate blue grey iris',(.075,.13,.16),.32)
pupil=mat('Pupils',(.006,.008,.009),.19)
hairmat=mat('Grey hair underlayer',(.055,.055,.051),.9)
hairmaterials=[mat('Grey strand '+str(i),(v*1.03,v*1.01,v*.95),.74) for i,v in enumerate([.10,.16,.22,.29,.36])]

# Anatomy is MakeHuman geometry. Small eyeballs and clothing/accessories are standard mesh additions.
def sphere(name,location,scale,material,segments=32,rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=location)
    obj=bpy.context.object;obj.name=name;obj.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(material)
    for face in obj.data.polygons:face.use_smooth=True
    character.append(obj);return obj
for side,center in [('Left',left_eye),('Right',right_eye)]:
    sphere(side+' anatomical eyeball',center,(.0116,.0116,.0116),white)
    sphere(side+' iris',(center.x,center.y-.01115,center.z),(.0049,.00065,.0049),iris)
    sphere(side+' pupil',(center.x,center.y-.01180,center.z),(.00225,.0003,.00225),pupil,24,12)

# BVH lets hair follow the actual anatomical scalp/jaw rather than floating primitive blobs.
bvh=BVHTree.FromPolygons([v.co for v in mesh.vertices],[list(p.vertices) for p in mesh.polygons])
def surface(x,z):
    hit,normal,index,distance=bvh.ray_cast(Vector((x,-.7,z)),Vector((0,1,0)))
    return (hit,normal) if hit is not None else (None,None)
def curve(name,points,radius,material):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=3;data.bevel_depth=radius;data.bevel_resolution=1
    spline=data.splines.new('BEZIER');spline.bezier_points.add(len(points)-1)
    for point,coordinate in zip(spline.bezier_points,points):
        point.co=coordinate;point.handle_left_type='AUTO';point.handle_right_type='AUTO'
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);data.materials.append(material);character.append(obj);return obj
for side,center in [('Left',left_eye),('Right',right_eye)]:
    radius=config['procedural']['glasses_radius']
    cy=center.y-.026;cz=center.z+.001
    points=[Vector((center.x+radius*math.cos(t),cy,cz+radius*math.sin(t))) for t in [2*math.pi*i/48 for i in range(49)]]
    curve(side+' round spectacle rim',points,.00095,metal)
    sign=1 if center.x>0 else -1
    curve(side+' spectacle temple',[Vector((center.x+sign*radius,cy,cz+.003)),Vector((sign*.077,-.092,cz+.002)),Vector((sign*.084,-.025,cz-.004)),Vector((sign*.080,.001,cz-.017))],.0008,metal)
curve('Spectacle bridge',[Vector((-.008,-.151,eye_z+.004)),Vector((0,-.164,eye_z+.009)),Vector((.008,-.151,eye_z+.004))],.00085,metal)

# A fitted scalp shell and individually curved grey guide strands, intentionally a first blockout.
scalp_faces=[]
for face in mesh.polygons:
    center=face.center
    if center.z>eye_z+.048 or (center.z>eye_z-.014 and center.y>-.078):scalp_faces.append(list(face.vertices))
scalp_mesh=bpy.data.meshes.new('Anatomical scalp shell')
scalp_mesh.from_pydata([tuple(v.co+v.normal*.0018) for v in mesh.vertices],[],scalp_faces)
scalp_mesh.update();scalp=bpy.data.objects.new('Grey scalp blocking',scalp_mesh);bpy.context.collection.objects.link(scalp);scalp.data.materials.append(hairmat);character.append(scalp)
scalp_sub=scalp.modifiers.new('Soft scalp mass','SUBSURF');scalp_sub.levels=2
for p in scalp.data.polygons:p.use_smooth=True
candidates=[v for v in mesh.vertices if v.co.z>eye_z+.05 or (v.co.z>eye_z+.005 and v.co.y>-.065)]
for i in range(config['procedural']['hair_strands']):
    vertex=random.choice(candidates);start=vertex.co.copy();normal=vertex.normal.copy()
    direction=Vector((random.uniform(.45,1),random.uniform(.2,.9),random.uniform(-.15,.2))).normalized()
    distance=random.uniform(.028,.055)
    lift=random.uniform(.002,.006)
    projected,endnormal,_,_=bvh.find_nearest(start+direction*distance)
    if projected is None:continue
    points=[]
    for j in range(7):
        t=j/6;point=start.lerp(projected,t);n=normal.lerp(endnormal,t).normalized()
        point+=n*(.0015+math.sin(math.pi*t)*lift)
        point.z+=math.sin(math.pi*t)*.002
        points.append(point)
    curve('Grey swept hair guide %03d'%i,points,random.uniform(.00025,.00048),random.choice(hairmaterials))
# Short facial hair follows the chin and cheeks; mouth opening stays unobscured.
for i in range(config['procedural']['beard_strands']):
    x=random.uniform(-.058,.058);z=random.uniform(eye_z-.116,eye_z-.044)
    if abs(x)<.025 and eye_z-.077<z<eye_z-.058:continue
    point,normal=surface(x,z)
    if point is None or normal.y>-.22:continue
    length=random.uniform(.002,.0055)
    curve('Short grey beard %03d'%i,[point+normal*.001,point+normal*.003+Vector((0,0,-length*.55)),point+normal*.002+Vector((0,0,-length))],random.uniform(.00012,.00022),random.choice(hairmaterials))
for sign in [-1,1]:
    for i in range(32):
        x=sign*random.uniform(.010,.047);z=eye_z+.019-(abs(x)-.010)*.15
        point,normal=surface(x,z)
        if point is not None:curve('Grey eyebrow',[point+normal*.001,point+normal*.002+Vector((sign*.005,0,.001)),point+normal*.001+Vector((sign*.009,0,-.001))],.0004,random.choice(hairmaterials))

# Neutral stage bust wardrobe: no third-party clothing license or hidden full-body nudity.
def mesh_object(name,vertices,faces,material):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
    uv=data.uv_layers.new(name='UVMap')
    for face in data.polygons:
        for loop_index in face.loop_indices:
            co=data.vertices[data.loops[loop_index].vertex_index].co
            uv.data[loop_index].uv=(co.x*4+.5,co.z*4)
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);data.materials.append(material);character.append(obj)
    return obj
rings=[(1.10,.245,.120),(1.20,.265,.136),(1.32,.265,.136),(1.41,.225,.116),(1.46,.150,.085),(1.49,.065,.063)]
vertices=[];faces=[];steps=72
for z,rx,ry in rings:
    vertices.extend([(rx*math.sin(2*math.pi*i/steps),.014-ry*math.cos(2*math.pi*i/steps),z) for i in range(steps)])
for j in range(len(rings)-1):
    for i in range(steps):faces.append((j*steps+i,j*steps+(i+1)%steps,(j+1)*steps+(i+1)%steps,(j+1)*steps+i))
clothes=mesh_object('Tailored brown jacket blockout',vertices,faces,coat)
for face in clothes.data.polygons:face.use_smooth=True
sub=clothes.modifiers.new('Soft cloth silhouette','SUBSURF');sub.levels=1
mesh_object('Dark green waistcoat', [(-.105,-.127,1.10),(.105,-.127,1.10),(.10,-.129,1.33),(.044,-.093,1.475),(0,-.108,1.395),(-.044,-.093,1.475),(-.10,-.129,1.33)],[(0,1,2,3,4,5,6)],vest)
mesh_object('Ivory shirt front',[(-.048,-.083,1.49),(.048,-.083,1.49),(.030,-.113,1.395),(0,-.126,1.355),(-.030,-.113,1.395)],[(0,1,2,3,4)],shirt)
for sign in [-1,1]:
    mesh_object('Notched jacket lapel',[(sign*.057,-.080,1.49),(sign*.172,-.082,1.42),(sign*.116,-.126,1.335),(sign*.044,-.135,1.235),(sign*.024,-.121,1.39)],[(0,1,2,3,4)],coat)
    mesh_object('Shirt collar',[(0,-.098,1.47),(sign*.048,-.083,1.49),(sign*.042,-.114,1.418),(sign*.016,-.121,1.435)],[(0,1,2,3)],shirt)
mesh_object('Tie blade',[(-.010,-.123,1.44),(.010,-.123,1.44),(.020,-.141,1.31),(0,-.142,1.275),(-.020,-.141,1.31)],[(0,1,2,3,4)],tie)
mesh_object('Tie knot',[(-.012,-.125,1.454),(.012,-.125,1.454),(.008,-.132,1.430),(-.008,-.132,1.430)],[(0,1,2,3)],tie)
for z in [1.34,1.265,1.19]:sphere('Antique waistcoat button',(0,-.141,z),(.005,.0028,.005),metal,16,10)

# A small packed project-authored weave tile is embedded in the GLB, not fetched remotely.
import numpy as np
size=256;yy,xx=np.mgrid[0:size,0:size]
weave=((xx+yy)%9<2).astype(float)*.014+((xx-yy)%11<2).astype(float)*.009
rng=np.random.default_rng(config['procedural']['seed'])
noise=rng.normal(0,.004,(size,size))
rgba=np.ones((size,size,4),dtype=np.float32)
for channel,base in enumerate([.073,.045,.026]):rgba[:,:,channel]=np.clip(base+weave+noise,.005,1)
image=bpy.data.images.new('Project authored tweed weave',width=size,height=size)
image.pixels=rgba.reshape(-1).tolist();image.pack()
texture=coat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image;texture.extension='REPEAT'
coat.node_tree.links.new(texture.outputs['Color'],coat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])

# Camera and lighting are review aids, excluded from the runtime GLB.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
bpy.context.preferences.filepaths.save_version=0
scene.cycles.use_denoising=True
scene.world.color=(.10,.10,.10)
scene.render.resolution_x=768;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
def area(name,location,energy,size):
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=location
    obj.rotation_euler=(Vector((0,-.02,1.56))-obj.location).to_track_quat('-Z','Y').to_euler()
area('Large soft key',(-1.2,-1.9,2.5),75,1.5)
area('Gentle fill',(1.3,-1.0,1.7),30,1.3)
area('Hair separation',(0,1.1,2.2),95,1.0)
camdata=bpy.data.cameras.new('Neutral review camera');camera=bpy.data.objects.new('Neutral review camera',camdata);scene.collection.objects.link(camera);scene.camera=camera
camdata.type='ORTHO';camdata.ortho_scale=.79
look=Vector((0,-.025,1.425))
def point_camera(location):
    camera.location=location;camera.rotation_euler=(look-camera.location).to_track_quat('-Z','Y').to_euler()
point_camera(Vector((0,-3,1.425)))

# Export only the review bust. Convert curve strands and apply cloth modifiers, no fake joints/visemes.
for obj in character:
    obj.hide_set(False);obj.select_set(False)
export_objects=[]
for obj in character:
    if obj.type=='CURVE':
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH');obj=bpy.context.object
    export_objects.append(obj)
for obj in export_objects:
    if obj.type=='MESH':
        for face in obj.data.polygons:face.use_smooth=True
for obj in export_objects:
    if obj.modifiers:
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
groups={}
for obj in export_objects:
    key=obj.data.materials[0].name if len(obj.data.materials)==1 else obj.name
    groups.setdefault(key,[]).append(obj)
merged=[]
for name,items in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for item in items:item.select_set(True)
    bpy.context.view_layer.objects.active=items[0]
    if len(items)>1:bpy.ops.object.join()
    obj=bpy.context.view_layer.objects.active;obj.name='Scholar '+name;merged.append(obj)
export_objects=merged
bust=next(obj for obj in export_objects if 'skin blockout' in obj.name)
bpy.ops.object.select_all(action='DESELECT')
for obj in export_objects:obj.select_set(True)
bpy.context.view_layer.objects.active=bust
outputs={key:ROOT/value for key,value in config['outputs'].items()}
for path in outputs.values():path.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(outputs['glb']),export_format='GLB',use_selection=True,export_animations=False,export_extras=True,export_apply=True)
scene['character_stage']='MPFB anatomical blockout; likeness and production facial rig not approved'
scene['source_config']='assets/character-production/scholar.json'
scene['mpfb_commit']=commit
bpy.ops.wm.save_as_mainfile(filepath=str(outputs['blend']),compress=True)
if not args.skip_renders:
    point_camera(Vector((0,-3,1.425)));scene.render.filepath=str(outputs['front']);bpy.ops.render.render(write_still=True)
    point_camera(Vector((3,-.025,1.425)));scene.render.filepath=str(outputs['profile']);bpy.ops.render.render(write_still=True)
    point_camera(Vector((0,-3,1.425)))
    bpy.ops.wm.save_as_mainfile(filepath=str(outputs['blend']),compress=True)
inventory={'status':config['status'],'base_vertices':len(source.data.vertices),'runtime_objects':len(export_objects),'runtime_vertices':sum(len(o.data.vertices) for o in export_objects if o.type=='MESH'),'joints':0,'facial_morphs':0,'mpfb_commit':commit,'source_asset_license':'CC0-1.0','procedural_accessories':'Project-authored mesh blocking','orientation':'Blender -Y forward; glTF +Z forward','source_config':'assets/character-production/scholar.json'}
outputs['inventory'].write_text(json.dumps(inventory,indent=2),encoding='utf-8')
print('SCHOLAR BLOCKOUT COMPLETE',json.dumps(inventory))
