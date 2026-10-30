"""Project-authored iris albedo/UV detail for the separate weighted Scholar study.
No anatomy, pupil diameter, eye scale, bone, morph or production presentation edits.
"""
from pathlib import Path
import hashlib,json,math,struct,zlib
import bpy


def _png(path,size=512):
    """Deterministic sRGB radial fibers; color only, never painted illumination."""
    rows=bytearray()
    def smooth(a,b,x):
        t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
    for y in range(size):
        rows.append(0)
        for x in range(size):
            u=(x+.5)/size*2-1;v=(y+.5)/size*2-1
            r=math.hypot(u,v);theta=math.atan2(v,u)
            # Multiple continuous spatial scales avoid identical spokes or large flat wedges.
            fibers=(math.sin(theta*83+2.1*math.sin(theta*11)+r*21)*.025
                    +math.sin(theta*173+r*35+math.sin(theta*29))*.013
                    +math.sin(theta*41-r*17)*.018)
            collarette=math.exp(-((r-.56)/.09)**2)*.026
            value=.225+fibers+collarette
            limb=smooth(.84,1.0,r)
            value=value*(1-limb)+.075*limb
            # The existing real pupil geometry remains in front of this color field.
            pupil=smooth(.40,.49,r)
            value=.035*(1-pupil)+value*pupil
            channels=(value*.83,value*1.03,value*1.10)
            rows.extend(max(0,min(255,round(channel*255))) for channel in channels)
    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    raw=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',size,size,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(rows),9))+chunk(b'IEND',b'')
    path.write_bytes(raw)
    return {'path':str(path).replace('\\','/'),'width':size,'height':size,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'color_space':'sRGB','lighting_painted':False}


def refine_eyes(objects,root):
    root=Path(root)
    iris=next(o for o in objects if o.type=='MESH' and any(m and m.name=='Slate blue grey iris' for m in o.data.materials))
    eye_objects=[o for o in objects if o.type=='MESH' and any(m and m.name in {'Slate blue grey iris','Natural eye whites','Pupils'} for m in o.data.materials)]
    def geometry_hash(items):
        digest=hashlib.sha256()
        for o in sorted(items,key=lambda value:value.name):
            digest.update(o.name.encode())
            for vertex in o.data.vertices:digest.update(struct.pack('<3f',*vertex.co))
            for polygon in o.data.polygons:
                for index in polygon.vertices:digest.update(struct.pack('<I',index))
        return digest.hexdigest()
    before_all=geometry_hash([o for o in objects if o.type=='MESH']);before_eyes=geometry_hash(eye_objects)
    mesh=iris.data
    neighbours=[set() for _ in mesh.vertices]
    for edge in mesh.edges:
        a,b=edge.vertices;neighbours[a].add(b);neighbours[b].add(a)
    remaining=set(range(len(mesh.vertices)));islands=[]
    while remaining:
        todo=[min(remaining)];remaining.remove(todo[0]);island=[]
        while todo:
            index=todo.pop();island.append(index)
            for neighbour in neighbours[index]:
                if neighbour in remaining:remaining.remove(neighbour);todo.append(neighbour)
        islands.append(sorted(island))
    if len(islands)!=2:raise RuntimeError('Expected exactly two existing anatomical iris islands')
    layer=mesh.uv_layers.get('IrisFrontProjection') or mesh.uv_layers.new(name='IrisFrontProjection')
    # Preserve original UV0, including its seam splits; the explicit UVMap node uses UV1.
    layer.active_render=False;mesh.uv_layers[0].active_render=True
    bounds=[];coordinates={}
    for island in islands:
        low=[min(mesh.vertices[i].co[axis] for i in island) for axis in range(3)]
        high=[max(mesh.vertices[i].co[axis] for i in island) for axis in range(3)]
        center=[(a+b)/2 for a,b in zip(low,high)]
        rx=(high[0]-low[0])/2;rz=(high[2]-low[2])/2
        for index in island:
            p=mesh.vertices[index].co
            coordinates[index]=((p.x-center[0])/(2*rx)+.5,(p.z-center[2])/(2*rz)+.5)
        bounds.append({'vertices':len(island),'local_min_m':low,'local_max_m':high,'local_center_m':center,'radii_xz_m':[rx,rz]})
    for loop in mesh.loops:layer.data[loop.index].uv=coordinates[loop.vertex_index]
    folder=root/'assets/character-production/eye-materials';folder.mkdir(parents=True,exist_ok=True)
    path=folder/'iris-base-color.png';image_report=_png(path)
    image_report['path']=path.relative_to(root).as_posix()
    image=bpy.data.images.load(str(path),check_existing=False);image.name='Scholar procedural slate iris color';image.colorspace_settings.name='sRGB';image.pack()
    material=next(m for m in mesh.materials if m.name=='Slate blue grey iris');material.use_nodes=True
    nodes=material.node_tree.nodes;links=material.node_tree.links
    shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    texture=nodes.new('ShaderNodeTexImage');texture.name='Project-authored iris albedo';texture.image=image;texture.interpolation='Linear';texture.extension='EXTEND'
    uv=nodes.new('ShaderNodeUVMap');uv.uv_map=layer.name
    links.new(uv.outputs['UV'],texture.inputs['Vector']);links.new(texture.outputs['Color'],shader.inputs['Base Color'])
    before_roughness=shader.inputs['Roughness'].default_value
    shader.inputs['Roughness'].default_value=.26
    after_all=geometry_hash([o for o in objects if o.type=='MESH']);after_eyes=geometry_hash(eye_objects)
    if before_all!=after_all or before_eyes!=after_eyes:raise RuntimeError('Iris material refinement changed geometry')
    report={'status':'Development iris albedo detail; not finished eyes, gaze rig, corneal refraction or likeness approval',
      'object':iris.name,'mesh':mesh.name,'material':material.name,'material_name':material.name,'method':'Two existing connected iris sphere islands, front-projected X/Z UV coordinates and project-authored radial color fibers',
      'uv_layer':layer.name,'uv_index':list(mesh.uv_layers).index(layer),'original_uv0_preserved':True,'islands':bounds,'texture':image_report,
      'all_object_geometry_sha256':after_all,'eye_component_geometry_sha256':after_eyes,
      'all_geometry_unchanged':True,'geometry_unchanged':True,'eye_geometry_unchanged':True,'pupil_and_sclera_materials_unchanged':True,
      'pupil_diameter_changed':False,'new_geometry':False,'new_bones_or_morphs':False,
      'iris_roughness_before':before_roughness,'iris_roughness_after':.26,
      'limitations':['No corneal volume/refraction, eye tracking, anatomical eyelid refinement or new gaze controls.',
       'Supported albedo detail only; existing pupil/iris size, eye positions and white materials remain development geometry.',
       'Radial color detail does not constitute finished portrait likeness or premium eye approval.']}
    (root/'assets/character-production/eye-material-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report
