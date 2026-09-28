"""Reproducible card hardware. Sent to the isolated Blender session over MCP.
Coordinates intentionally match Three.js: XY face, +Z front, 1 unit = card width/3.2.
"""
import bpy
import math
from mathutils import Vector

ROOT = 'C:/Users/socce/OneDrive/Documents/ClientWebsites/Practice Sites/frost-card-next'
for obj in list(bpy.context.scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

def material(name, color, metallic, roughness):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    node = mat.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value = (*color, 1)
    node.inputs['Metallic'].default_value = metallic
    node.inputs['Roughness'].default_value = roughness
    return mat

silver = material('Weathered bronze', (.16,.10,.045), .87, .47)
dark = material('Forged black iron', (.024,.025,.025), .74, .48)
gold = material('Worn gilding', (.36,.23,.095), .90, .39)
ice = material('Moonstone', (.17,.31,.34), .65, .24)

def outline(w,h,r,steps=14):
    points=[]
    for cx,cy,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for i in range(steps+1):
            angle=math.radians(start+i*90/steps)
            points.append((cx+r*math.cos(angle),cy+r*math.sin(angle)))
    return points

def ring(name,w,h,r,width,z,depth,mat):
    outer=outline(w,h,r)
    inner=outline(w-2*width,h-2*width,max(.02,r-width))
    n=len(outer)
    verts=[(x,y,z+d) for d in [-depth/2,depth/2] for loop in [outer,inner] for x,y in loop]
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],[tuple(reversed(face)) for face in faces]); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(obj); obj.data.materials.append(mat)
    bevel=obj.modifiers.new('Machined soft edges','BEVEL'); bevel.width=min(width*.2,.009); bevel.segments=3
    normal=obj.modifiers.new('Weighted reflections','WEIGHTED_NORMAL')
    return obj

def box(name,location,scale,mat,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=location)
    obj=bpy.context.object; obj.name=name; obj.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(mat)
    mod=obj.modifiers.new('Precision bevel','BEVEL'); mod.width=bevel; mod.segments=5
    obj.modifiers.new('Weighted reflections','WEIGHTED_NORMAL')
    return obj

box('Card core',(0,0,0),(3.15,4.55,.115),dark,.105)
ring('Heavy bronze bezel',3.20,4.60,.10,.075,.035,.19,silver)
ring('Front worn fillet',3.09,4.49,.08,.026,.143,.03,gold)
ring('Front gold hairline',3.025,4.425,.115,.010,.147,.012,gold)
ring('Reverse polished fillet',3.09,4.49,.14,.022,-.084,.023,silver)
ring('Artwork window',2.88,2.89,.095,.019,.163,.028,silver).location.y=.18
ring('Artwork gold inlay',2.825,2.835,.075,.009,.175,.015,gold).location.y=.18

for side in [-1,1]:
    for i in range(29):
        y=-1.82+i*.13
        box('Forged edge %s %02d'%(side,i),(side*1.578,y,.0),(.022,.034,.12),dark,.005)
    for y in [-2.12,2.12]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.036,location=(side*1.44,y,.156))
        obj=bpy.context.object; obj.name='Rivet'; obj.scale.z=.4; obj.data.materials.append(gold)

def rod(name,a,b,radius,mat):
    delta=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=radius,depth=delta.length,location=(Vector(a)+Vector(b))/2)
    obj=bpy.context.object; obj.name=name
    obj.rotation_euler=delta.to_track_quat('Z','Y').to_euler(); obj.data.materials.append(mat)
    return obj

def flourish(name, points, radius=.012, mat=gold):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D'
    curve.resolution_u=12;curve.bevel_depth=radius;curve.bevel_resolution=3
    spline=curve.splines.new('BEZIER');spline.bezier_points.add(len(points)-1)
    for p,co in zip(spline.bezier_points,points):
        p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    obj=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.object.convert(target='MESH')
    return obj

def jewel(name,x,y,z,size=.07):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,z))
    obj=bpy.context.object;obj.name=name;obj.scale=(size,size*1.5,size*.58);obj.data.materials.append(ice)
    for sign in [-1,1]:
        flourish('Gem setting',[(x,y+size*1.75,z-.01),(x+sign*size*1.4,y,z-.01),(x,y-size*1.75,z-.01)],.013,silver)

# Cast acanthus corners and tapering spires: actual relief, visible from the side.
for sx in [-1,1]:
    for sy in [-1,1]:
        def corner(points): return [(sx*x,sy*y,z) for x,y,z in points]
        flourish('Corner thorn',corner([(1.20,2.24,.19),(1.49,2.20,.22),(1.62,2.35,.20),(1.65,2.43,.15)]),.022,silver)
        flourish('Corner acanthus',corner([(1.56,1.86,.20),(1.46,1.96,.24),(1.39,2.17,.26),(1.17,2.18,.22),(1.10,2.10,.23),(1.17,2.06,.23),(1.20,2.12,.23)]),.018,gold)
        flourish('Corner curl',corner([(1.55,2.23,.20),(1.37,2.04,.25),(1.48,1.96,.23),(1.53,2.02,.23)]),.014,gold)
        jewel('Corner moonstone',sx*1.48,sy*2.21,.24,.049)
    # Narrow vines run beside the portrait without covering the character.
    for y in [-1.13,-.59,-.05,.49,1.03]:
        flourish('Border vine',[(sx*1.49,y-.28,.20),(sx*1.53,y-.08,.23),(sx*1.48,y+.14,.23),(sx*1.50,y+.28,.20)],.012,gold)
        flourish('Border leaf',[(sx*1.5,y,.22),(sx*1.42,y+.13,.24),(sx*1.46,y+.22,.20)],.010,silver)
    # Scrollwork rests below the image, framing the nameplate and lore.
    flourish('Lower scroll',[(sx*.12,-1.40,.19),(sx*.47,-1.44,.22),(sx*.91,-1.39,.23),(sx*1.16,-1.49,.22),(sx*1.08,-1.57,.23),(sx*.99,-1.51,.22)],.014,gold)
    flourish('Foot scroll',[(sx*.08,-2.17,.21),(sx*.41,-2.12,.22),(sx*.79,-2.18,.22),(sx*1.07,-2.08,.23)],.014,gold)

# A crowned crest breaks the otherwise rectangular silhouette.
flourish('Crown rim',[(-.31,2.28,.18),(0,2.25,.22),(.31,2.28,.18)],.023,silver)
for sx in [-1,1]:
    flourish('Crown peak',[(sx*.30,2.28,.20),(sx*.31,2.48,.19),(sx*.16,2.38,.21),(0,2.61,.17)],.018,gold)
    flourish('Crest shoulder',[(sx*.09,2.30,.22),(sx*.55,2.31,.22),(sx*.69,2.40,.18),(sx*.58,2.44,.18),(sx*.51,2.38,.18)],.012,silver)
jewel('Crown moonstone',0,2.38,.23,.065)

# Circular heraldic seal on the reverse with twelve small spear points.
for radius in [.76,.82,1.03]:
    flourish('Reverse seal',[(math.cos(i*math.tau/72)*radius,math.sin(i*math.tau/72)*radius,-.14) for i in range(73)],.013,gold)
for i in range(12):
    a=i*math.tau/12
    flourish('Seal spear',[(math.cos(a-.08)*.85,math.sin(a-.08)*.85,-.16),(math.cos(a)*.97,math.sin(a)*.97,-.19),(math.cos(a+.08)*.85,math.sin(a+.08)*.85,-.16)],.011,silver)

# An actual raised snowflake seal, used on the reverse face.
for i in range(6):
    angle=i*math.pi/3
    def polar(radius, offset=0):
        return (radius*math.cos(angle+offset),radius*math.sin(angle+offset),-.15)
    rod('Snowflake main',polar(.0),polar(.55),.018,silver)
    for radius in [.27,.42]:
        anchor=Vector(polar(radius))
        for direction in [-1,1]:
            end=anchor+Vector((math.cos(angle+direction*.85)*.15,math.sin(angle+direction*.85)*.15,0))
            rod('Snowflake branch',anchor,end,.012,gold)

# Detachable facets: the frontend animates these independently of the card.
for i in range(7):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(0,0,0))
    obj=bpy.context.object; obj.name='Crystal_%02d'%i
    obj.scale=(.045+(i%2)*.02,.12+(i%3)*.025,.05)
    obj.data.materials.append(ice)
    obj.location=(2.2*math.cos(i*2.4),2.4*math.sin(i*2.4),.1)

# Consolidate the static casting by material to keep browser draw calls low.
for mat in [silver,dark,gold,ice]:
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('Crystal_') and o.active_material==mat]
    for obj in objects:
        bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
    if objects:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects: obj.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        bpy.ops.object.join();bpy.context.object.name=mat.name+' casting'

# Source presentation camera; runtime lighting is owned by Three.js.
bpy.ops.object.camera_add(location=(0,0,9))
camera=bpy.context.object; camera.name='Source preview camera'
camera.rotation_euler=(0,0,0); bpy.context.scene.camera=camera
camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler()
for name,location,energy,size in [('Key',(-3,4,5),650,5),('Rim',(3,0,3),420,3)]:
    bpy.ops.object.light_add(type='AREA',location=location)
    light=bpy.context.object; light.name=name; light.data.energy=energy; light.data.shape='DISK'; light.data.size=size
    light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()

bpy.context.scene.world.color=(.08,.08,.08)
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    if obj.type=='MESH': obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=ROOT+'/public/assets/card-hardware.glb',export_format='GLB',use_selection=True,export_apply=True,export_yup=False)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/art-source/frost-king.blend')
print('CARD_EXPORTED',len([o for o in bpy.context.scene.objects if o.type=='MESH']),'meshes')
