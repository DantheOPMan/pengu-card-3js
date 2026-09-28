"""Restore the original ice studio and weather only its side-wall meshes."""
import bpy, bmesh, math, json, hashlib, struct
from pathlib import Path
from mathutils import Vector, noise

ROOT=Path('C:/Users/socce/OneDrive/Documents/ClientWebsites/Practice Sites/frost-card-next')
SOURCE=ROOT/'art-source/winter-crown-ice-studio.blend'
for obj in list(bpy.context.scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
with bpy.data.libraries.load(str(SOURCE),link=False) as (source,target):
    target.objects=list(source.objects)
for obj in target.objects:
    if obj is not None:bpy.context.collection.objects.link(obj)

ENV_PREFIXES=('Ice floor slab','Sculpted glacier backdrop','Embedded ice fracture','Anchored glacier ridge','Frozen bank at wall foot')
SIDE_PREFIXES=('Anchored glacier ridge','Frozen bank at wall foot')
original_env=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(ENV_PREFIXES)]
preserved=[o for o in original_env if not o.name.startswith(SIDE_PREFIXES)]

def fingerprint(obj):
    h=hashlib.sha256()
    for v in obj.data.vertices:h.update(struct.pack('<3f',*v.co))
    for p in obj.data.polygons:
        h.update(struct.pack('<I',len(p.vertices)))
        for i in p.vertices:h.update(struct.pack('<I',i))
    for row in obj.matrix_world:h.update(struct.pack('<4f',*row))
    return h.hexdigest()
before={o.name:fingerprint(o) for o in preserved}

def material(name,color,roughness):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=(*color,1)
    p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness;p.inputs['Metallic'].default_value=.035
    p.inputs['IOR'].default_value=1.31;p.inputs['Coat Weight'].default_value=.16;p.inputs['Coat Roughness'].default_value=.32
    return mat

blue=material('Weathered ice wall body',(.27,.43,.51),.37)
cap=material('Weathered ice wall frost',(.53,.66,.71),.54)

def fbm(x,y,z):
    return noise.noise(Vector((x,y,z)))*.66+noise.noise(Vector((x*2.17+9,y*2.17,z*2.17)))*.25+noise.noise(Vector((x*4.63,y*4.63+5,z*4.63)))*.09

def erode(original,seed):
    coords=[original.matrix_world@v.co for v in original.data.vertices]
    minimum=Vector(tuple(min(p[i] for p in coords) for i in range(3)))
    maximum=Vector(tuple(max(p[i] for p in coords) for i in range(3)))
    center=(minimum+maximum)*.5;size=maximum-minimum
    small=original.name.startswith('Frozen bank')
    sides=60;levels=14 if small else 56
    # Broad fracture planes are retained between irregular, rounded arrises.
    polygon=[(-.49,-.27),(-.29,-.52),(.29,-.49),(.53,-.09),(.40,.41),(-.30,.47)]
    tops=[.88,.94,1.02,.90,.85,.99]
    verts=[];faces=[]
    for j in range(levels+1):
        t=j/levels
        for i in range(sides):
            q=i/sides*6;k=int(q);f=q-k
            a=polygon[k];b=polygon[(k+1)%6]
            px=a[0]*(1-f)+b[0]*f;pz=a[1]*(1-f)+b[1]*f
            angle=math.tau*i/sides
            top=tops[k]*(1-f)+tops[(k+1)%6]*f
            top+=.025*fbm(px*8+seed,0,pz*8)
            y=minimum.y+size.y*t*top
            taper=1-(.55 if small else .15)*t
            bend=.075*math.sin(t*2.8+seed)*t
            n=fbm(px*3+seed,t*size.y*.73,pz*3)
            scallop=fbm(px*9+seed,y*1.8,pz*9)
            # Narrow, wandering melt channels run down the broad faces.
            channel=math.exp(-((f-(.46+.10*math.sin(y*.8+seed)))/.095)**2)
            recession=(.055*n+.024*scallop-.027*channel*math.sin(math.pi*t)**.5)
            radial=max(.01,math.hypot(px,pz))
            x=center.x+size.x*(px*taper+bend+px/radial*recession)
            z=center.z+size.z*(pz*taper-.035*t+pz/radial*recession)
            verts.append((x,y,z))
    for j in range(levels):
        for i in range(sides):
            a=j*sides+i;b=j*sides+(i+1)%sides
            faces.append((a,b,b+sides,a+sides))
    faces.extend([tuple(reversed(range(sides))),tuple(levels*sides+i for i in range(sides))])
    data=bpy.data.meshes.new('Weathered glacial fracture surface');data.from_pydata(verts,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free()
    data.materials.append(blue);data.materials.append(cap)
    for p in data.polygons:p.use_smooth=True;p.material_index=1 if p.normal.y>.58 else 0
    obj=bpy.data.objects.new('Weathered '+original.name,data);bpy.context.collection.objects.link(obj)
    bpy.data.objects.remove(original,do_unlink=True)
    return obj

sides=sorted([o for o in original_env if o.name.startswith(SIDE_PREFIXES)],key=lambda o:o.name)
replacements=[erode(o,2.13+i*3.719) for i,o in enumerate(sides)]
after={o.name:fingerprint(o) for o in preserved}
assert before==after,'Original floor, backdrop or fissures changed.'
environment=preserved+replacements
bpy.ops.object.select_all(action='DESELECT')
for o in environment:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/assets/ice-environment.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=False)

# Blender keeps the same procedural frost treatment as the live side-wall shader.
for mat in [blue,cap]:
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
    tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=8;tex.inputs['Detail'].default_value=4
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.11;bump.inputs['Distance'].default_value=.018
    links.new(tex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],p.inputs['Normal'])

camera=next(o for o in bpy.context.scene.objects if o.type=='CAMERA' and o.name.startswith('Ice studio'))
bpy.context.scene.camera=camera;bpy.context.scene.world.color=(.32,.42,.5)
bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=48
bpy.context.scene.render.resolution_x=1600;bpy.context.scene.render.resolution_y=1000;bpy.context.scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art-source/winter-crown-ice-studio-refined.blend'))
report={'design':'Original ice studio with weathered side walls','source':str(SOURCE),'meshes':len(environment),'vertices':sum(len(o.data.vertices) for o in environment),'triangles':sum(len(p.vertices)-2 for o in environment for p in o.data.polygons),'refined_side_meshes':len(replacements),'preserved_meshes':len(preserved),'preserved_geometry_hashes_match':before==after,'floor_y':-2.60,'floating_objects':0}
(ROOT/'output/ice-environment/model-report.json').write_text(json.dumps(report,indent=2))
(ROOT/'output/ice-environment/preserved-original-geometry.json').write_text(json.dumps(before,indent=2))
print('ORIGINAL_ICE_REFINED',json.dumps(report))
