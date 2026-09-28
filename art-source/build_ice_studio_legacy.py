"""Author a real ice studio through Blender MCP; coordinates match the Three.js card."""
import bpy, bmesh, math, random, json
from pathlib import Path
from mathutils import Vector

ROOT=Path('C:/Users/socce/OneDrive/Documents/ClientWebsites/Practice Sites/frost-card-next')
random.seed(72)
for obj in list(bpy.context.scene.objects): bpy.data.objects.remove(obj,do_unlink=True)
FLOOR=-2.60

def material(name,color,roughness,metallic=.05):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=(*color,1)
    p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness;p.inputs['Metallic'].default_value=metallic
    p.inputs['Coat Weight'].default_value=.35;p.inputs['Coat Roughness'].default_value=.22
    return mat

deep=material('Ice blue depth',(.095,.22,.31),.21,.14)
ice=material('Ice pale faces',(.26,.40,.49),.25,.12)
frost=material('Ice frost crust',(.48,.64,.71),.62,.03)
floor_mat=material('Ice floor substrate',(.33,.47,.54),.21,.25)
crack_mat=material('Ice embedded fissures',(.13,.29,.38),.55,.03)
materials=[deep,ice,frost,floor_mat,crack_mat]

def mesh(name,verts,faces,mat,smooth=False):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);data.materials.append(mat)
    for p in data.polygons:p.use_smooth=smooth
    return obj

def cube(name,loc,scale,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);obj=bpy.context.object;obj.name=name;obj.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat)
    if bevel:
        mod=obj.modifiers.new('Soft frozen edge','BEVEL');mod.width=bevel;mod.segments=3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj

# A substantial slab extends beyond every camera crop. Its upper skin is the
# interactive planar ice reflection in the browser, above this actual mesh.
cube('Ice floor slab',(0,FLOOR-.22,-2),(36,.44,36),floor_mat,.08)

# Sculpted curved glacial wall: real shallow facets and vertical compressed strata.
verts=[];faces=[];nx=92;ny=46
for j in range(ny+1):
    y=FLOOR+j*15/ny
    for i in range(nx+1):
        x=-16+i*32/nx
        z=-6.4+.017*x*x+.26*math.sin(x*.7+y*.45)+.10*math.sin(x*2.5+y*.9)+.04*math.sin(x*6.1-y*1.6)
        z+=random.uniform(-.065,.065)
        verts.append((x,y,z))
for j in range(ny):
    for i in range(nx):
        a=j*(nx+1)+i
        faces.extend([(a,a+1,a+nx+1),(a+1,a+nx+2,a+nx+1)])
wall=mesh('Sculpted glacier backdrop',verts,faces,ice,True)

def ice_ridge(name,x,z,width,height,depth,lean):
    footprint=[(-.52,-.30),(-.28,-.55),(.35,-.48),(.55,-.06),(.38,.51),(-.39,.44)]
    verts=[]
    for level in [0,.37,.78,1]:
        for px,pz in footprint:
            taper=1-.42*level
            verts.append((x+px*width*taper+lean*level,FLOOR+height*level+(.14*math.sin(px*9) if level else 0),z+pz*depth*taper-.12*level))
    faces=[tuple(reversed(range(6))),tuple(range(18,24))]
    for level in range(3):
        for k in range(6):
            a=level*6+k;b=level*6+(k+1)%6
            faces.extend([(a,b,b+6),(a,b+6,a+6)])
    obj=mesh(name,verts,faces,deep)
    obj.data.materials.append(ice);obj.data.materials.append(frost)
    for p in obj.data.polygons:p.material_index=2 if p.normal.y>.35 else (1 if p.index%4 else 0)
    bevel=obj.modifiers.new('Weathered crystal arris','BEVEL');bevel.width=.035;bevel.segments=2
    bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=bevel.name)
    return obj

# Rooted ice formations flank the open presentation area; nothing floats.
for side in [-1,1]:
    for i in range(7):
        x=side*(4.1+i*.75+random.uniform(-.18,.18));z=-2.8-i*.35
        ice_ridge('Anchored glacier ridge',x,z,1.25+random.random()*.65,4.8+random.random()*3.7,1.5+random.random(),side*.30)
    for i in range(5):
        x=side*(3.65+i*.63);z=-1.0-random.random()*2
        ice_ridge('Frozen bank at wall foot',x,z,.9,random.uniform(.30,.75),1.3,side*.08)

def crack(points,width):
    data=bpy.data.curves.new('Embedded ice fracture','CURVE');data.dimensions='3D';data.bevel_depth=width;data.bevel_resolution=0
    spline=data.splines.new('POLY');spline.points.add(len(points)-1)
    for p,(x,z) in zip(spline.points,points):p.co=(x,FLOOR+.009,z,1)
    obj=bpy.data.objects.new('Embedded ice fracture',data);bpy.context.collection.objects.link(obj);data.materials.append(crack_mat)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH')

# Meandering fracture seams are fixed into the floor geometry.
for i in range(18):
    x=random.uniform(-14,14);z=random.uniform(-12,8);heading=random.random()*math.tau
    points=[(x,z)]
    for j in range(random.randint(4,8)):
        heading+=random.uniform(-.8,.8);step=random.uniform(.35,1.0)
        x+=math.cos(heading)*step;z+=math.sin(heading)*step;points.append((x,z))
    crack(points,random.uniform(.002,.006))
    mid=len(points)//2;branch=[points[mid],(points[mid][0]+.48,points[mid][1]+.6),(points[mid][0]+.92,points[mid][1]+.82)]
    crack(branch,.002)

environment_objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in environment_objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/assets/ice-environment.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=False)
report={'meshes':len(environment_objects),'vertices':sum(len(o.data.vertices) for o in environment_objects),'triangles':sum(len(p.vertices)-2 for o in environment_objects for p in o.data.polygons),'floor_y':FLOOR,'bounds':'36-unit ice slab, curved glacier wall, rooted flank formations','floating_objects':0}
(ROOT/'output/ice-environment/model-report.json').write_text(json.dumps(report,indent=2))

# Complete editable scene includes the approved card and packed original artwork.
with bpy.data.libraries.load(str(ROOT/'art-source/winter-crown.blend'),link=False) as (source,target):
    target.objects=[name for name in source.objects if not name.startswith(('Crystal_','Cold key','Silver rim','Winter Crown preview'))]
for obj in target.objects:
    if obj is not None and obj.type=='MESH':bpy.context.collection.objects.link(obj)
relief=bpy.data.objects.get('Preview original penguin relief')
if relief:
    for v in relief.data.vertices:
        uv_y=(v.co.y-.10)/2.79+.5
        t=max(0,min(1,uv_y/.08));edge=t*t*(3-2*t)
        v.co.x*=2.94/2.79;v.co.y=(v.co.y-.10)*2.94/2.79+.10
        v.co.z=.183+(v.co.z-.183)*edge

for mat in materials:
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
    noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=13;noise.inputs['Detail'].default_value=4
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.035
    links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],p.inputs['Normal'])

bpy.ops.object.camera_add(location=(0,1.8,11.5));camera=bpy.context.object;camera.name='Ice studio preview'
camera.rotation_euler=(Vector((0,-.10,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=42;bpy.context.scene.camera=camera
for name,loc,power,size in [('Soft window light',(-4,7,5),1600,6),('Blue ice bounce',(5,3,1),950,5)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.name=name;light.data.energy=power;light.data.size=size
    light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.world.color=(.32,.42,.5)
bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=48
bpy.context.scene.render.resolution_x=1600;bpy.context.scene.render.resolution_y=1000;bpy.context.scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art-source/winter-crown-ice-studio.blend'))
print('ICE_ENVIRONMENT_COMPLETE',json.dumps(report))
