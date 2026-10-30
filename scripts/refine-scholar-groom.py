"""Deterministic fitted silver ribbon-clump development groom for the weighted study.
Uses explicit triangle/barycentric head correspondence for both real weights and morphs.
No canonical model edits, photographs, paid assets or empty compatibility targets.
"""
from pathlib import Path
import hashlib,json,math,random,struct
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def refine_groom(head,objects,root,rig):
    if bpy.data.objects.get('Scholar Fitted silver facial groom') is not None:raise RuntimeError('Groom already exists; rebuild from the original face-study input')
    random.seed(271828)
    head.data.calc_loop_triangles()
    triangles=[tuple(tri.vertices) for tri in head.data.loop_triangles if head.data.polygons[tri.polygon_index].material_index==0]
    world=head.matrix_world;inverse=world.inverted()
    points=[world@vertex.co for vertex in head.data.vertices]
    bvh=BVHTree.FromPolygons(points,triangles,all_triangles=True)
    baseline_hash=hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in head.data.vertices)).hexdigest()
    # Match original anatomical eye anchors from the actual fitted eye geometry.
    eyes=next(obj for obj in objects if 'Natural eye whites' in obj.name)
    eye_z=sum((eyes.matrix_world@v.co).z for v in eyes.data.vertices)/len(eyes.data.vertices)
    vertices=[];faces=[];correspondence=[];face_materials=[];regions={};fit=[];minimum_lip_clearance=1

    def mapping(point):
        location,normal,index,distance=bvh.find_nearest(point)
        if location is None:return None
        a,b,c=(points[i] for i in triangles[index]);v0=b-a;v1=c-a;v2=location-a
        d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1)
        denominator=d00*d11-d01*d01
        if abs(denominator)<1e-16:return None
        v=(d11*d20-d01*d21)/denominator;w=(d00*d21-d01*d20)/denominator;u=1-v-w
        weights=[max(0,value) for value in (u,v,w)];total=sum(weights)
        return location,normal,[(i,weight/total) for i,weight in zip(triangles[index],weights)]

    def permitted(point,region):
        x,y,z=point;relative=z-eye_z
        if y>-.075 or abs(x)>.069:return False
        if region=='moustache':
            return -.057<relative<-.039 and abs(x)<.036
        if not -.122<relative<-.033:return False
        # Bare lips/philtrum, with cheek boundary rising toward the sideburn.
        if abs(x)<.032 and -.083<relative<-.057:return False
        if relative>-.084 and abs(x)<.026:return False
        return True

    def ribbon(start,normal,region):
        if region=='moustache':
            direction=Vector((math.copysign(.65,start.x or 1),0,-.55)).normalized();length=random.uniform(.004,.0075);width=random.uniform(.0004,.0008);offset=.0004
        else:
            direction=Vector((random.uniform(-.16,.16),.03,-1)).normalized();length=random.uniform(.004,.008);width=random.uniform(.0004,.0008);offset=.0004
        endpoint=bvh.find_nearest(start+direction*length)
        if endpoint[0] is None or not permitted(endpoint[0],region):return False
        end=endpoint[0];tangent=(end-start).normalized()
        built=[]
        for t,scale in [(0,.44),(.5,.5),(1,.025)]:
            center=start.lerp(end,t)
            found=mapping(center)
            if not found:return False
            center,n,_=found
            if not permitted(center,region):return False
            side=n.cross(tangent).normalized()
            bulge=.00010*math.sin(math.pi*t)
            for sign in [-1,1]:
                found=mapping(center+side*sign*width*scale)
                if not found:return False
                location,n,weights=found
                if not permitted(location,region):return False
                point=location+n*(offset+bulge)
                built.append((inverse@point,weights,offset+bulge))
        candidate_faces=[(0,3,1),(0,2,3),(2,5,3),(2,4,5)]
        for ids in candidate_faces:
            a,b,c=(built[i][0] for i in ids)
            geometric=(b-a).cross(c-a)
            if geometric.length<1e-12:return False
            reference=sum((sum((head.data.vertices[source].normal*weight for source,weight in built[i][1]),Vector()) for i in ids),Vector()).normalized()
            if geometric.normalized().dot(reference)<.10:return False
        base=len(vertices)
        vertices.extend(item[0] for item in built);correspondence.extend(item[1] for item in built);fit.extend(item[2] for item in built)
        material_index=random.choices([0,1,2],[.22,.53,.25])[0]
        for ids in [(0,3,1),(0,2,3),(2,5,3),(2,4,5)]:faces.append(tuple(base+i for i in ids));face_materials.append(material_index)
        regions[region]=regions.get(region,0)+1
        return True

    for region,target in [('beard',2200),('moustache',800)]:
        attempts=0
        while regions.get(region,0)<target and attempts<target*40:
            attempts+=1
            x=random.uniform(-.065,.065) if region=='beard' else random.uniform(-.033,.033)
            z=eye_z+random.uniform(-.120,-.035) if region=='beard' else eye_z+random.uniform(-.055,-.040)
            point,normal,_,_=bvh.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
            if point is None or normal.y>-.20:continue
            if not permitted(point,region):continue
            relative=point.z-eye_z
            if region=='beard':
                top=-.065+.025*(abs(point.x)/.065)
                density=max(0,min(1,(top-relative)/.009,(.069-abs(point.x))/.012,(relative+.122)/.012))
            elif region=='moustache':density=max(0,min(1,(.036-abs(point.x))/.008,(relative+.057)/.004,(-.039-relative)/.004))
            if random.random()<density:ribbon(point,normal,region)
        if regions.get(region,0)<target*.75:raise RuntimeError('Insufficient fitted '+region+' clumps: '+str(regions.get(region,0)))

    mesh=bpy.data.meshes.new('Scholar fitted silver ribbon clumps');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new('Scholar Fitted silver facial groom',mesh);bpy.context.collection.objects.link(obj)
    obj.parent=rig;obj.matrix_parent_inverse=head.matrix_parent_inverse.copy();obj.matrix_world=head.matrix_world.copy()
    for value in [.16,.22,.30]:
        material=bpy.data.materials.new('Scholar Silver facial hair '+str(value));material.use_nodes=True
        color=(value*1.02,value*1.01,value*.98,1);material.diffuse_color=color
        shader=material.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=color;shader.inputs['Roughness'].default_value=.9
        mesh.materials.append(material)
    for polygon,index in zip(mesh.polygons,face_materials):polygon.material_index=index;polygon.use_smooth=True
    # Smooth normals follow actual anatomical surface, not sharp ribbon-card edges.
    normals=[]
    for polygon in mesh.polygons:
        for index in polygon.vertices:
            weights=correspondence[index]
            normal=sum((head.data.vertices[source].normal*weight for source,weight in weights),Vector()).normalized()
            normals.append(tuple(normal))
    mesh.normals_split_custom_set(normals)
    names={group.index:group.name for group in head.vertex_groups}
    groups={}
    for index,weights in enumerate(correspondence):
        blended={}
        for source,blend in weights:
            for entry in head.data.vertices[source].groups:
                name=names[entry.group];blended[name]=blended.get(name,0)+entry.weight*blend
        blended=dict(sorted(blended.items(),key=lambda item:item[1],reverse=True)[:4]);total=sum(blended.values())
        if total<=0:raise RuntimeError('Unweighted groom vertex')
        for name,weight in blended.items():
            if name not in groups:groups[name]=obj.vertex_groups.new(name=name)
            groups[name].add([index],weight/total,'REPLACE')
    modifier=obj.modifiers.new('Actual fitted head weights','ARMATURE');modifier.object=rig
    morphs={};maximum_morph_correspondence_error=0
    if head.data.shape_keys:
        basis=head.data.shape_keys.key_blocks['Basis']
        for source_key in head.data.shape_keys.key_blocks:
            if source_key.name=='Basis':continue
            moves=[sum(((source_key.data[source].co-basis.data[source].co)*weight for source,weight in weights),Vector()) for weights in correspondence]
            affected=sum(move.length>1e-7 for move in moves)
            if not affected:continue
            if obj.data.shape_keys is None:obj.shape_key_add(name='Basis')
            key=obj.shape_key_add(name=source_key.name)
            for index,move in enumerate(moves):key.data[index].co=mesh.vertices[index].co+move
            key.value=0
            maximum_morph_correspondence_error=max(maximum_morph_correspondence_error,max(((key.data[index].co-mesh.vertices[index].co)-move).length for index,move in enumerate(moves)))
            morphs[key.name]={'affected_vertices':affected,'max_delta_m':max(move.length for move in moves)}
    outward=[]
    for face in faces:
        a,b,c=(vertices[index] for index in face)
        reference=sum((sum((head.data.vertices[source].normal*weight for source,weight in correspondence[index]),Vector()) for index in face),Vector()).normalized()
        outward.append((b-a).cross(c-a).normalized().dot(reference))
    if min(outward)<=0:raise RuntimeError('Inverted facial groom coverage')
    actual_fit=[bvh.find_nearest(world@point)[3] for point in vertices]
    # Conservative rest proxy for the bare lips, not a finished intersection certification.
    lip_bounds=(-.029,.029,eye_z-.081,eye_z-.059)
    def proxy_distance(point):
        dx=max(lip_bounds[0]-point.x,0,point.x-lip_bounds[1]);dz=max(lip_bounds[2]-point.z,0,point.z-lip_bounds[3])
        return math.hypot(dx,dz)
    lip_clearance=min(proxy_distance(world@point) for point in vertices)
    if lip_clearance<.001:raise RuntimeError('Facial groom enters protected bare-lip proxy')
    # Validate actual evaluated binding against the same head triangles under restrained poses.
    def evaluated_points(item):
        bpy.context.view_layer.update();evaluated=item.evaluated_get(bpy.context.evaluated_depsgraph_get());result=evaluated.to_mesh()
        try:return [evaluated.matrix_world@vertex.co for vertex in result.vertices]
        finally:evaluated.to_mesh_clear()
    bone=rig.pose.bones['mixamorig:Head'];bone_mode=bone.rotation_mode;bone_basis=bone.matrix_basis.copy()
    pose_metrics={}
    checks={'jaw_open':{'jawOpen':.38},'rounding':{'mouthPucker':.25},'compression':{'lipPress':.25},'slight_smile':{'mouthSmile':.20},'head_turn':{}}
    for pose,values in checks.items():
        bone.rotation_mode='XYZ';bone.rotation_euler=(0,math.radians(10) if pose=='head_turn' else 0,0)
        for item in [head,obj]:
            if item.data.shape_keys:
                for key in item.data.shape_keys.key_blocks:
                    if key.name!='Basis':key.value=values.get(key.name,0)
        head_points=evaluated_points(head);groom_points=evaluated_points(obj)
        offsets=[];distances=[]
        for index,weights in enumerate(correspondence):
            a,b,c=(head_points[source] for source,_ in weights)
            normal=(b-a).cross(c-a).normalized()
            attached=sum((head_points[source]*weight for source,weight in weights),Vector())
            delta=groom_points[index]-attached
            offsets.append(delta.dot(normal));distances.append(delta.length)
        pose_metrics[pose]={'minimum_outward_offset_m':min(offsets),'maximum_correspondence_distance_m':max(distances),'inward_vertices':sum(value<0 for value in offsets)}
        if min(offsets)<-.00001 or max(distances)>.0015:raise RuntimeError('Facial groom lost attachment under '+pose)
    bone.rotation_mode=bone_mode;bone.matrix_basis=bone_basis
    for item in [head,obj]:
        if item.data.shape_keys:
            for key in item.data.shape_keys.key_blocks:
                if key.name!='Basis':key.value=0
    bpy.context.view_layer.update()
    after_hash=hashlib.sha256(b''.join(struct.pack('<3f',*v.co) for v in head.data.vertices)).hexdigest()
    if after_hash!=baseline_hash:raise RuntimeError('Groom changed existing head geometry')
    report={'status':'Fitted ribbon-clump groom development study; not final hair or likeness approval','seed':271828,
      'object':obj.name,'materials':[material.name for material in mesh.materials],
      'added_vertices':len(vertices),'added_triangles':len(faces),'clumps':regions,'morphs':morphs,
      'weight_method':'Exact stored head-triangle barycentric interpolation, strongest four normalized bone influences',
      'pose_attachment':pose_metrics,'maximum_morph_correspondence_error_m':maximum_morph_correspondence_error,'vertex_correspondence_count':len(correspondence),'max_weight_sum_error':max(abs(sum(entry.weight for entry in vertex.groups)-1) for vertex in mesh.vertices),
      'surface_offset_range_m':[min(fit),max(fit)],'measured_neutral_fit_range_m':[min(actual_fit),max(actual_fit)],'minimum_face_outward_dot':min(outward),'inverted_face_count':sum(value<0 for value in outward),'protected_lip_proxy_xz_m':list(lip_bounds),'minimum_rest_lip_proxy_clearance_m':lip_clearance,'existing_head_unchanged':True,'existing_head_position_sha256':baseline_hash,
      'scalp_or_crown_modified':False,
      'limitations':['Development facial ribbon clumps and guide accents, not production hair cards/anisotropic shading; crown remains unchanged.',
      'Lip region excluded at rest; combined speech/intersection quality still requires visual review.']}
    scene=bpy.context.scene;camera=scene.camera
    original_camera=camera.matrix_world.copy();original_scale=camera.data.ortho_scale
    original_path=scene.render.filepath
    camera.data.ortho_scale=.34
    report['comparison_renders']={}
    for name,position in [('front',(0,-3,1.607)),('profile',(3,0,1.607))]:
        camera.location=Vector(position);camera.rotation_euler=(Vector((0,-.03,1.607))-camera.location).to_track_quat('-Z','Y').to_euler()
        relative='docs/assets/groom-study-'+name+'.png';scene.render.filepath=str(Path(root)/relative)
        bpy.ops.render.render(write_still=True);report['comparison_renders'][name]=relative
    camera.matrix_world=original_camera;camera.data.ortho_scale=original_scale;scene.render.filepath=original_path
    (Path(root)/'assets/character-production/groom-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return obj,report
