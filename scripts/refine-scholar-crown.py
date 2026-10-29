"""Conservative same-topology anatomical crown fit repair for the derived rig study.
Projects referenced cap vertices outside actual head skin; no angular crown cards.
"""
from pathlib import Path
import hashlib,json,math,struct
import bpy
from mathutils import Vector
from mathutils.geometry import barycentric_transform
from mathutils.bvhtree import BVHTree


def refine_crown(head,objects,root,rig,offset=.0025):
    cap=next(obj for obj in objects if obj.type=='MESH' and any('Grey hair underlayer' in mat.name for mat in obj.data.materials if mat))
    head.data.calc_loop_triangles()
    points=[head.matrix_world@vertex.co for vertex in head.data.vertices]
    triangles=[tuple(tri.vertices) for tri in head.data.loop_triangles if head.data.polygons[tri.polygon_index].material_index==0]
    bvh=BVHTree.FromPolygons(points,triangles,all_triangles=True)
    referenced=sorted({index for polygon in cap.data.polygons for index in polygon.vertices})
    head_hash=lambda:hashlib.sha256(b''.join(struct.pack('<3f',*vertex.co) for vertex in head.data.vertices)).hexdigest()
    before_head=head_hash();before=[cap.matrix_world@cap.data.vertices[index].co for index in referenced]
    def vertex_normals(values):
        normals=[Vector((0,0,0)) for _ in values]
        for ids in triangles:
            n=(values[ids[1]]-values[ids[0]]).cross(values[ids[2]]-values[ids[0]])
            for index in ids:normals[index]+=n
        return [n.normalized() for n in normals]
    normals=vertex_normals(points)
    def nearest(point,tree,values,normals):
        location,_,index,distance=tree.find_nearest(point)
        ids=triangles[index]
        bary=barycentric_transform(location,*(values[i] for i in ids),Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
        normal=sum((normals[i]*factor for i,factor in zip(ids,bary)),Vector()).normalized()
        return location,normal,index,distance
    def fit(values,tree,surface,normal_values):
        signed=[];distances=[];triangle_signed=[];ambiguous=[]
        for point in values:
            location,normal,_,distance=nearest(point,tree,surface,normal_values)
            signed.append((point-location).dot(normal));distances.append(distance)
            raw_location,raw_normal,_,_=tree.find_nearest(point)
            raw=(point-raw_location).dot(raw_normal);triangle_signed.append(raw)
            if raw<-.00001 and signed[-1]>=0:ambiguous.append(list(point))
        return {'minimum_signed_outward_offset_m':min(signed),'maximum_nearest_distance_m':max(distances),
          'inward_vertex_count':sum(value<-.00001 for value in signed),'closest_triangle_minimum_signed_offset_m':min(triangle_signed),'closest_triangle_inward_vertex_count':sum(value<-.00001 for value in triangle_signed),'triangle_vs_interpolated_normal_ambiguity_count':len(ambiguous),'triangle_vs_interpolated_normal_ambiguous_world_positions':ambiguous}
    prior=fit(before,bvh,points,normals)
    inverse=cap.matrix_world.inverted()
    for index,point in zip(referenced,before):
        location,normal,_,_=nearest(point,bvh,points,normals)
        cap.data.vertices[index].co=inverse@(location+normal*offset)
    # At sharp triangle boundaries the first face normal can point toward a neighbouring face.
    # Recheck the actual nearest surface and resolve those points conservatively.
    for _ in range(12):
        corrected=0
        for index in referenced:
            point=cap.matrix_world@cap.data.vertices[index].co
            location,normal,_,_=nearest(point,bvh,points,normals)
            if (point-location).dot(normal)<offset*.8:
                cap.data.vertices[index].co=inverse@(point+normal*(offset-(point-location).dot(normal)));corrected+=1
        if not corrected:break
    cap.data.update()
    # Existing empty facial targets still hold their own coordinates; move every target
    # by the same cap-only displacement so evaluation retains the repaired neutral surface.
    if cap.data.shape_keys:
        for index,old in zip(referenced,before):
            delta=cap.data.vertices[index].co-(inverse@old)
            for key in cap.data.shape_keys.key_blocks:key.data[index].co+=delta
    # Match the cap to the anatomical triangle skinning, including neck blend at the nape.
    groups={group.index:group.name for group in head.vertex_groups}
    for index in referenced:
        point=cap.matrix_world@cap.data.vertices[index].co
        location,_,triangle,_=nearest(point,bvh,points,normals)
        ids=triangles[triangle]
        bary=barycentric_transform(location,*(points[i] for i in ids),Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
        weights={}
        for vertex_index,factor in zip(ids,bary):
            for item in head.data.vertices[vertex_index].groups:
                name=groups[item.group]
                if name in rig.data.bones:
                    weights[name]=weights.get(name,0)+max(0,factor)*item.weight
        total=sum(weights.values())
        if total<=0:raise RuntimeError('No anatomical skin weights for crown vertex')
        for group in cap.vertex_groups:group.remove([index])
        for name,weight in weights.items():
            group=cap.vertex_groups.get(name) or cap.vertex_groups.new(name=name)
            group.add([index],weight/total,'REPLACE')
    after=[cap.matrix_world@cap.data.vertices[index].co for index in referenced]
    result=fit(after,bvh,points,normals)
    if result['inward_vertex_count'] or result['minimum_signed_outward_offset_m']<.001:
        raise RuntimeError(f'Repaired cap still penetrates head: {result}')
    if head_hash()!=before_head:raise RuntimeError('Crown repair changed head geometry')
    def evaluated(obj):
        bpy.context.view_layer.update();value=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=value.to_mesh()
        try:return [value.matrix_world@vertex.co for vertex in mesh.vertices]
        finally:value.to_mesh_clear()
    cap.data.update();cap.update_tag(refresh={'DATA'})
    bone=rig.pose.bones['mixamorig:Head'];original_mode=bone.rotation_mode;original=bone.matrix_basis.copy()
    bone.rotation_mode='XYZ';bone.rotation_euler=(0,math.radians(10),0)
    head_pose=evaluated(head);cap_pose=evaluated(cap)
    posed_tree=BVHTree.FromPolygons(head_pose,triangles,all_triangles=True)
    posed=fit([cap_pose[index] for index in referenced],posed_tree,head_pose,vertex_normals(head_pose))
    bone.rotation_mode=original_mode;bone.matrix_basis=original
    bpy.context.view_layer.update()
    if posed['inward_vertex_count'] or posed['minimum_signed_outward_offset_m']<.001:raise RuntimeError(f'Cap attachment failed restrained head turn: {posed}')
    report={'status':'Same-topology crown surface fit development repair; not finished hair silhouette or likeness',
      'object':cap.name,'method':'Project referenced cap vertices to actual anatomical skin BVH plus positive normal offset',
      'weight_method':'Barycentric actual head-triangle weights, normalized on existing bones; cap only','clearance_normal_method':'Area-weighted anatomical vertex normals interpolated barycentrically; raw closest triangle signed counts also retained','surface_offset_m':offset,'referenced_vertices':len(referenced),'unused_loose_vertices_ignored':len(cap.data.vertices)-len(referenced),
      'polygons':len(cap.data.polygons),'before_fit':prior,'after_fit':result,'head_turn_10_degrees_fit':posed,
      'maximum_vertex_adjustment_m':max((a-b).length for a,b in zip(before,after)),
      'head_position_sha256':before_head,'existing_head_unchanged':True,'new_vertices':0,'new_polygons':0,'material_changed':False,
      'limitations':['Closest-triangle normal checks retain ear-edge signed ambiguities; interpolated-normal zero-inward results do not prove every triangle is outside the head.',
       'Helmet-like hairline, coarse strands, and cap coverage over the ear remain unfinished.',
       'Existing cap topology, scalp tone, guide strands and hairline contour retained; no final strand grooming or premium hair claim.',
       'Nearest-surface fit is a vertex-level check, not certification of all triangle coverage, camera angles or complex deformation.']}
    (Path(root)/'assets/character-production/crown-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report

