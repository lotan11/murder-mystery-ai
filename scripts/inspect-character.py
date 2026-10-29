"""Inspect local GLB structure and TalkingHead inventories without claiming visual approval."""
from pathlib import Path
import argparse
import json
import struct
import math
import hashlib

CORE=['Hips','Spine','Spine1','Spine2','Neck','Head']
SIDE=['Shoulder','Arm','ForeArm','Hand','UpLeg','Leg','Foot','ToeBase']
FINGERS=[f'Hand{finger}{joint}' for finger in ['Thumb','Index','Middle','Ring','Pinky'] for joint in range(1,4)]
BONES=set(CORE+[side+name for side in ['Left','Right'] for name in SIDE+FINGERS]+['LeftEye','RightEye'])
VISEMES={'viseme_'+name for name in ['sil','PP','FF','TH','DD','kk','CH','SS','nn','RR','aa','E','I','O','U']}
EXPRESSIONS=set('eyeBlinkLeft eyeBlinkRight eyeLookDownLeft eyeLookDownRight eyeLookInLeft eyeLookInRight eyeLookOutLeft eyeLookOutRight eyeLookUpLeft eyeLookUpRight eyeSquintLeft eyeSquintRight eyeWideLeft eyeWideRight jawForward jawLeft jawRight jawOpen mouthClose mouthFunnel mouthPucker mouthLeft mouthRight mouthSmileLeft mouthSmileRight mouthFrownLeft mouthFrownRight mouthDimpleLeft mouthDimpleRight mouthStretchLeft mouthStretchRight mouthRollLower mouthRollUpper mouthShrugLower mouthShrugUpper mouthPressLeft mouthPressRight mouthLowerDownLeft mouthLowerDownRight mouthUpperUpLeft mouthUpperUpRight browDownLeft browDownRight browInnerUp browOuterUpLeft browOuterUpRight cheekPuff cheekSquintLeft cheekSquintRight noseSneerLeft noseSneerRight tongueOut'.split())


def measure_morphs(document, binary):
    """Measure actual embedded float32 POSITION deltas, including sparse accessors."""
    accessors=document.get('accessors',[]);views=document.get('bufferViews',[])
    def entries(view_index, offset, count, fmt, stride=None):
        if type(view_index) is not int or not 0<=view_index<len(views):raise ValueError('Invalid morph buffer view')
        view=views[view_index]
        if view.get('buffer',0)!=0 or binary is None:raise ValueError('Morph data is not embedded')
        width=struct.calcsize(fmt);step=stride or width
        if step<width or offset<0 or count<0:raise ValueError('Invalid morph stride or offset')
        end=offset+(count-1)*step+width if count else offset
        begin=view.get('byteOffset',0)
        if end>view.get('byteLength',0) or begin<0 or begin+end>len(binary):raise ValueError('Truncated morph data')
        return [struct.unpack_from(fmt,binary,begin+offset+i*step) for i in range(count)]
    def deltas(index, expected_count):
        if type(index) is not int or not 0<=index<len(accessors):raise ValueError('Invalid morph accessor')
        accessor=accessors[index];count=accessor.get('count')
        if accessor.get('componentType')!=5126 or accessor.get('type')!='VEC3' or count!=expected_count:raise ValueError('Unsupported morph position accessor')
        if 'bufferView' in accessor:
            view=views[accessor['bufferView']]
            values=entries(accessor['bufferView'],accessor.get('byteOffset',0),count,'<fff',view.get('byteStride'))
        else:values=[(0.0,0.0,0.0)]*count
        sparse=accessor.get('sparse')
        if sparse:
            size=sparse.get('count',0);indices=sparse['indices'];data=sparse['values']
            if not 0<=size<=count:raise ValueError('Invalid sparse morph count')
            fmt={5121:'<B',5123:'<H',5125:'<I'}.get(indices.get('componentType'))
            if fmt is None:raise ValueError('Unsupported sparse morph index')
            positions=[v[0] for v in entries(indices['bufferView'],indices.get('byteOffset',0),size,fmt)]
            if positions!=sorted(set(positions)) or any(i>=count for i in positions):raise ValueError('Invalid sparse morph indices')
            updates=entries(data['bufferView'],data.get('byteOffset',0),size,'<fff')
            values=list(values)
            for position,value in zip(positions,updates):values[position]=value
        if any(not all(math.isfinite(c) for c in value) for value in values):raise ValueError('Non-finite morph displacement')
        return values
    report={}
    for mesh in document.get('meshes',[]):
        names=mesh.get('extras',{}).get('targetNames',[])
        for primitive in mesh.get('primitives',[]):
            expected=accessors[primitive['attributes']['POSITION']]['count']
            for i,target in enumerate(primitive.get('targets',[])):
                if 'POSITION' not in target:continue
                name=names[i] if i<len(names) else str(i)
                values=deltas(target['POSITION'],expected)
                magnitudes=[math.sqrt(sum(c*c for c in value)) for value in values]
                measured=report.setdefault(name,{'affected_vertices':0,'max_displacement':0.0,'primitive_count':0})
                measured['affected_vertices']+=sum(value>1e-8 for value in magnitudes)
                measured['max_displacement']=max(measured['max_displacement'],max(magnitudes,default=0.0))
                measured['primitive_count']+=1
    return report


def material_inventory(document, binary):
    """Inspect actual glTF texture bindings and embedded image bytes, not source nodes."""
    images=[];views=document.get('bufferViews',[])
    for index,item in enumerate(document.get('images',[])):
        entry={'index':index,'name':item.get('name',''),'mime_type':item.get('mimeType'), 'embedded':False}
        view_index=item.get('bufferView')
        if type(view_index) is int and 0<=view_index<len(views) and binary is not None:
            view=views[view_index];begin=view.get('byteOffset',0);size=view.get('byteLength',0)
            if view.get('buffer',0)!=0 or begin<0 or size<0 or begin+size>len(binary):raise ValueError('Invalid embedded image buffer')
            data=binary[begin:begin+size]
            entry.update({'embedded':True,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
            if data.startswith(b'\x89PNG\r\n\x1a\n') and len(data)>=33 and data[12:16]==b'IHDR':
                width,height=struct.unpack_from('>II',data,16)
                if not 0<width<=16384 or not 0<height<=16384:raise ValueError('Invalid PNG dimensions')
                entry.update({'width':width,'height':height,'bit_depth':data[24],'color_type':data[25]})
        images.append(entry)
    textures=document.get('textures',[])
    def binding(value):
        if value is None:return None
        index=value.get('index') if isinstance(value,dict) else None
        if type(index) is not int or not 0<=index<len(textures):raise ValueError('Invalid material texture reference')
        source=textures[index].get('source')
        if type(source) is not int or not 0<=source<len(images):raise ValueError('Invalid texture image reference')
        return {'texture_index':index,'image_index':source,'tex_coord':value.get('texCoord',0)}
    materials=[]
    for index,item in enumerate(document.get('materials',[])):
        pbr=item.get('pbrMetallicRoughness',{})
        materials.append({'index':index,'name':item.get('name',''),
          'base_color_texture':binding(pbr.get('baseColorTexture')),
          'normal_texture':binding(item.get('normalTexture')),
          'metallic_roughness_texture':binding(pbr.get('metallicRoughnessTexture'))})
    return {'materials':materials,'images':images,'texture_count':len(textures)}


def inspect(path, measure=False):
    path=Path(path)
    if not 20<=path.stat().st_size<=128*1024*1024:raise ValueError('GLB size outside inspection limit')
    data=path.read_bytes()
    magic,version,length=struct.unpack_from('<4sII',data)
    if magic!=b'glTF' or version!=2 or length!=len(data):raise ValueError('Invalid GLB header or length')
    offset=12;document=None;binary=None
    while offset<len(data):
        if offset+8>len(data):raise ValueError('Truncated GLB chunk header')
        size,kind=struct.unpack_from('<II',data,offset);offset+=8
        if offset+size>len(data):raise ValueError('Truncated GLB chunk')
        if kind==0x4e4f534a:
            if document is not None:raise ValueError('Duplicate GLB JSON chunk')
            document=json.loads(data[offset:offset+size].decode('utf-8'))
        elif kind==0x004e4942:
            binary=data[offset:offset+size]
        offset+=size
    if not isinstance(document,dict) or document.get('asset',{}).get('version')!='2.0':raise ValueError('Missing glTF 2.0 document')
    meshes=document.get('meshes',[]);accessors=document.get('accessors',[])
    if not meshes:raise ValueError('No mesh geometry to inspect')
    vertices=0;triangles=0;targets=set()
    for mesh in meshes:
        targets.update(mesh.get('extras',{}).get('targetNames',[]))
        for primitive in mesh.get('primitives',[]):
            material_index=primitive.get('material')
            if 'material' in primitive and (type(material_index) is not int or not 0<=material_index<len(document.get('materials',[]))):raise ValueError('Invalid primitive material reference')
            index=primitive.get('attributes',{}).get('POSITION')
            if type(index) is not int or not 0<=index<len(accessors):raise ValueError('Invalid position accessor')
            count=accessors[index].get('count',0)
            if type(count) is not int or count<=0:raise ValueError('Empty position data')
            vertices+=count
            if primitive.get('mode',4)==4:
                indices=primitive.get('indices')
                triangles+=(accessors[indices]['count'] if type(indices) is int and 0<=indices<len(accessors) else count)//3
    names={node.get('name','').replace('mixamorig:','').replace('mixamorig','') for node in document.get('nodes',[])}
    missing_bones=sorted(BONES-names);missing_expressions=sorted(EXPRESSIONS-targets);missing_visemes=sorted(VISEMES-targets)
    external=[item['uri'] for key in ['buffers','images'] for item in document.get(key,[]) if isinstance(item.get('uri'),str) and not item['uri'].startswith('data:')]
    report={'file':path.name,'bytes':len(data),'mesh_count':len(meshes),'vertices':vertices,'triangles':triangles,
            'skin_count':len(document.get('skins',[])),'joint_count':len({joint for skin in document.get('skins',[]) for joint in skin.get('joints',[])}),
            'morph_target_count':len(targets),'missing_bones':missing_bones,'missing_expressions':missing_expressions,'missing_visemes':missing_visemes,
            'external_resources':external,'talkinghead_inventory_complete':not(missing_bones or missing_expressions or missing_visemes),
            'approval':'Structural inventory only; likeness, deformations and runtime performance require separate review.'}
    report['material_inventory']=material_inventory(document,binary)
    if measure:
        # Component checks distinguish intentional groom additions from head deformation changes.
        inventory=[]
        for mesh_index,mesh in enumerate(meshes):
            item={'index':mesh_index,'node_names':[node.get('name','') for node in document.get('nodes',[]) if type(node.get('mesh')) is int and node.get('mesh')==mesh_index],
                  'materials':sorted({document['materials'][primitive['material']].get('name','') for primitive in mesh.get('primitives',[]) if 'material' in primitive}),
                  'name':mesh.get('name',''),'primitive_count':len(mesh.get('primitives',[])),
                  'vertices':0,'triangles':0,'morph_deformations':measure_morphs({**document,'meshes':[mesh]},binary)}
            for primitive in mesh.get('primitives',[]):
                count=accessors[primitive['attributes']['POSITION']]['count'];item['vertices']+=count
                index=primitive.get('indices')
                if primitive.get('mode',4)==4:item['triangles']+=(accessors[index]['count'] if type(index) is int and 0<=index<len(accessors) else count)//3
            inventory.append(item)
        report['mesh_inventory']=inventory
        combined={}
        for item in inventory:
            for name,measurement in item['morph_deformations'].items():
                total=combined.setdefault(name,{'affected_vertices':0,'max_displacement':0.0,'primitive_count':0})
                total['affected_vertices']+=measurement['affected_vertices']
                total['primitive_count']+=measurement['primitive_count']
                total['max_displacement']=max(total['max_displacement'],measurement['max_displacement'])
        report['morph_deformations']=combined
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('path',type=Path);parser.add_argument('--output',type=Path);parser.add_argument('--measure-morphs',action='store_true');args=parser.parse_args()
    result=inspect(args.path,measure=args.measure_morphs);text=json.dumps(result,indent=2)
    if args.output:args.output.write_text(text+'\n',encoding='utf-8')
    print(text)
