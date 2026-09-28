"""Carve an ordered ice sanctuary through Blender MCP; Y is up for Three.js."""
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

ice=material('Sanctuary blue ice',(.16,.27,.33),.38,.02)
frost=material('Sanctuary carved frost',(.43,.57,.62),.28,.07)
trim=material('Sanctuary silver inlay',(.51,.58,.60),.28,.48)
floor_mat=material('Ice floor substrate',(.34,.45,.49),.25,.15)
window=material('Sanctuary luminous apse',(.65,.75,.74),.48,0)
window.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(.65,.76,.72,1)
window.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.45
materials=[ice,frost,trim,floor_mat,window]

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

# A continuous, gently vaulted enclosure gives the arches a real background.
verts=[];faces=[];nx=60;ny=36
for j in range(ny+1):
    y=FLOOR+j*15/ny
    for i in range(nx+1):
        x=-16+i*32/nx
        z=-10.3+.025*x*x+.03*math.sin(x*.8+y*.3)
        verts.append((x,y,z))
for j in range(ny):
    for i in range(nx):
        a=j*(nx+1)+i
        faces.extend([(a,a+1,a+nx+1),(a+1,a+nx+2,a+nx+1)])
wall=mesh('Continuous vaulted ice enclosure',verts,faces,ice,True)

def arch_path(width,apex,z,steps=100):
    # Vertical at its foot, each continuous half curves toward a pointed crown.
    left=[(-width*(1-(i/steps)**2.65),FLOOR+(apex-FLOOR)*i/steps,z) for i in range(steps+1)]
    return left+[(-x,y,z) for x,y,z in reversed(left[:-1])]

def moulding(name,points,radius,mat,depth_ratio=1,cyclic=False,carved=False):
    section=[(-.72,-1),(.72,-1),(1,-.72),(1,.72),(.72,1),(-.72,1),(-1,.72),(-1,-.72)] if carved else [(math.cos(math.tau*j/12),math.sin(math.tau*j/12)) for j in range(12)]
    verts=[];faces=[];sides=len(section);count=len(points)
    for i,point in enumerate(points):
        before=Vector(points[(i-1)%count] if cyclic else points[max(0,i-1)])
        after=Vector(points[(i+1)%count] if cyclic else points[min(count-1,i+1)])
        tangent=(after-before).normalized()
        axis=Vector((0,0,1)) if abs(tangent.z)<.8 else Vector((0,1,0))
        u=tangent.cross(axis).normalized();v=tangent.cross(u).normalized()
        for su,sv in section:
            p=Vector(point)+u*(radius*su)+v*(radius*depth_ratio*sv)
            verts.append(tuple(p))
    for i in range(count if cyclic else count-1):
        for j in range(sides):
            faces.append((i*sides+j,i*sides+(j+1)%sides,((i+1)%count)*sides+(j+1)%sides,((i+1)%count)*sides+j))
    if not cyclic:faces.extend([tuple(reversed(range(sides))),tuple((count-1)*sides+j for j in range(sides))])
    obj=mesh(name,verts,faces,mat,not carved)
    return obj

# Three complete architectural ribs establish symmetry and receding depth.
for index,z in enumerate([-3.8,-6.2,-8.6]):
    moulding(f'Carved pointed arch {index+1}',arch_path(5.25,3.55,z),.19,frost,1.65,carved=True)
    moulding(f'Outer silver fillet {index+1}',arch_path(5.58,3.91,z-.03),.035,trim,1.2)
    moulding(f'Inner ice fillet {index+1}',arch_path(4.98,3.26,z+.03),.046,frost)
    for side in [-1,1]:
        cube('Integrated arch foot',(side*5.25,FLOOR+.095,z),(.68,.19,.85),frost,.065)

# Quiet recessed light at the end of the nave, with restrained window tracery.
outline=arch_path(4.74,3.30,-9.12)
panel=mesh('Recessed luminous ice apse',outline,[tuple(range(len(outline)))],window)
moulding('Apse reveal',arch_path(4.79,3.36,-9.04),.075,trim)
for side in [-1,1]:
    points=[(side*2.24,FLOOR,-9.00),(side*2.24,.65,-9.00),(side*2.07,1.57,-9.00),(side*1.6,2.24,-9.00)]
    moulding('Slender apse tracery',points,.023,frost)
oculus=[(.60*math.cos(math.tau*i/144),2.55+.60*math.sin(math.tau*i/144),-8.99) for i in range(144)]
moulding('Crown light oculus',oculus,.027,trim,cyclic=True)

# Inlaid arcs and a clear aisle replace scattered rocks and broken floor seams.
for radius in [3.10,3.19,5.65]:
    points=[(radius*math.cos(math.tau*i/220),FLOOR+.009,radius*math.sin(math.tau*i/220)-.25) for i in range(220)]
    moulding('Sanctuary floor inlay',points,.005,trim,cyclic=True)
for side in [-1,1]:
    moulding('Longitudinal aisle seam',[(side*3.70,FLOOR+.010,-12),(side*3.70,FLOOR+.010,15)],.004,trim)

environment_objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in environment_objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/assets/ice-environment.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=False)
report={'meshes':len(environment_objects),'vertices':sum(len(o.data.vertices) for o in environment_objects),'triangles':sum(len(p.vertices)-2 for o in environment_objects for p in o.data.polygons),'floor_y':FLOOR,'bounds':'36-unit ice floor, three symmetric continuous pointed arches, recessed luminous apse','floating_objects':0,'loose_rocks':0,'design':'Carved ice sanctuary'}
(ROOT/'output/ice-environment/model-report.json').write_text(json.dumps(report,indent=2))

# Complete editable scene includes the approved card and packed original artwork.
with bpy.data.libraries.load(str(ROOT/'art-source/winter-crown.blend'),link=False) as (source,target):
    target.objects=[name for name in source.objects if not name.startswith(('Crystal_','Cold key','Silver rim','Winter Crown preview'))]
card_assembly=bpy.data.objects.new('Grounded Winter Crown assembly',None);bpy.context.collection.objects.link(card_assembly)
for obj in target.objects:
    if obj is not None and obj.type=='MESH':
        bpy.context.collection.objects.link(obj)
        transform=obj.matrix_world.copy();obj.parent=card_assembly;obj.matrix_world=transform
card_assembly.location.y=-.22
relief=bpy.data.objects.get('Preview original penguin relief')
if relief:
    for v in relief.data.vertices:
        uv_y=(v.co.y-.10)/2.79+.5
        t=max(0,min(1,uv_y/.08));edge=t*t*(3-2*t)
        v.co.x*=2.94/2.79;v.co.y=(v.co.y-.10)*2.94/2.79+.10
        v.co.z=.183+(v.co.z-.183)*edge

for mat in materials:
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
    noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=9;noise.inputs['Detail'].default_value=2
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.055;bump.inputs['Distance'].default_value=.008
    links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],p.inputs['Normal'])

bpy.ops.object.camera_add(location=(0,1.8,11.5));camera=bpy.context.object;camera.name='Ice sanctuary preview'
camera.rotation_euler=(Vector((0,-.10,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=42;bpy.context.scene.camera=camera
for name,loc,power,size in [('Sanctuary skylight',(-3,7,3),1350,8),('Apse light',(0,3,-7),1700,5),('Quiet ice fill',(4,2,3),550,7)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.name=name;light.data.energy=power;light.data.size=size
    light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.world.color=(.32,.42,.5)
bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=48
bpy.context.scene.render.resolution_x=1600;bpy.context.scene.render.resolution_y=1000;bpy.context.scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art-source/winter-crown-ice-sanctuary.blend'))
print('ICE_ENVIRONMENT_COMPLETE',json.dumps(report))
