"""Sculpt a natural glacial throne chamber through the isolated Blender MCP."""
import bpy, bmesh, math, random, json
from pathlib import Path
from mathutils import Vector, noise

ROOT=Path('C:/Users/socce/OneDrive/Documents/ClientWebsites/Practice Sites/frost-card-next')
random.seed(162)
for obj in list(bpy.context.scene.objects): bpy.data.objects.remove(obj,do_unlink=True)
FLOOR=-3.32
DAIS=-2.60

def fbm(x,y,z):
    return noise.noise(Vector((x,y,z)))*.64+noise.noise(Vector((x*2.11+7,y*2.11,z*2.11)))*.25+noise.noise(Vector((x*4.31,y*4.31+4,z*4.31)))*.11

def material(name,color,roughness,metallic=.04):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=(*color,1)
    p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness;p.inputs['Metallic'].default_value=metallic
    p.inputs['Coat Weight'].default_value=.48;p.inputs['Coat Roughness'].default_value=.15
    return mat

deep=material('Glacier ancient blue ice',(.025,.100,.17),.27)
ice=material('Glacier sculpted ice',(.065,.23,.31),.22)
frost=material('Glacier snow worn edges',(.28,.46,.52),.46)
floor_mat=material('Ice floor substrate',(.055,.14,.19),.21,.12)
materials=[deep,ice,frost,floor_mat]

def mesh(name,verts,faces,mat,smooth=True):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);data.materials.append(mat)
    for p in data.polygons:p.use_smooth=smooth
    return obj

def grid_faces(nx,ny):
    return [(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i) for j in range(ny) for i in range(nx)]

# The entire room is one sculpted horseshoe glacier, rather than separate props.
verts=[];nt=156;nh=68
for j in range(nh+1):
    t=j/nh;y=FLOOR+t*13.6
    for i in range(nt+1):
        a=-1.93+i/nt*3.86
        n=fbm(math.sin(a)*3.0,y*.28,math.cos(a)*3.0)
        folds=.38*math.sin(a*13+y*.23)+.20*math.sin(a*29-y*.48)
        radius=8.8+1.1*n+folds+.28*math.sin(y*.8+a*3)
        x=math.sin(a)*radius;z=-2.4-math.cos(a)*(6.5+n*.9+folds*.55)
        foot=math.exp(-t*12)*.62
        verts.append((x-math.sin(a)*foot,y,z+math.cos(a)*foot))
mesh('Continuous glacier cavern',verts,grid_faces(nt,nh),deep)

verts=[];nx=96;nz=50
for j in range(nz+1):
    z=-12+j/nz*13
    for i in range(nx+1):
        x=-14+i/nx*28
        cleft=2.4*math.exp(-((x-1.2)**2/3+(z+5)**2/8))
        y=4.30+cleft+fbm(x*.3,z*.3,3)*1.35+.24*math.sin(x*2.2+z*.6)
        verts.append((x,y,z))
mesh('Riven frozen vault',verts,grid_faces(nx,nz),deep)

def mass(name,loc,scale,mat,seed,detail=4,rough=.17):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=detail,radius=1,location=loc)
    obj=bpy.context.object;obj.name=name;obj.data.materials.append(mat)
    for v in obj.data.vertices:
        p=v.co.copy();r=1+fbm(p.x*2+seed,p.y*2,p.z*2)*rough
        v.co=(p.x*scale[0]*r,p.y*scale[1]*r,p.z*scale[2]*r)
    for p in obj.data.polygons:p.use_smooth=True
    return obj

# Broad continuous frozen waterfalls meet the vault and floor. Their folds are
# sculpted into each wall, leaving an open foreground around the throne.
for side in [-1,1]:
    verts=[];nu=82;nv=76
    for j in range(nv+1):
        y=FLOOR+j/nv*11
        for i in range(nu+1):
            u=i/nu
            x=side*(4.85+u*7+.21*math.sin(y*.68+side)+fbm(u*3,y*.30,side)*.22)
            z=-4.3+u*3.2+.44*math.sin(u*17+y*.23+side)+fbm(u*4,y*.43,2+side)*.55
            verts.append((x,y,z))
    mesh('Sculpted frozen waterfall wall',verts,grid_faces(nu,nv),ice)

def dais(name,rx,rz,top,bottom,mat,seed):
    count=180;verts=[(0,top,-.30)];faces=[]
    for ring in range(4):
        for i in range(count):
            a=math.tau*i/count;r=1+.035*math.sin(5*a+seed)+.023*math.sin(9*a+1.7)+.013*math.sin(21*a)
            if ring==0:s=.77;y=top
            elif ring==1:s=.96;y=top-.025+.012*math.sin(6*a)
            elif ring==2:s=1.0;y=top-.17+fbm(math.cos(a)*3,math.sin(a)*3,seed)*.10
            else:s=1.03;y=bottom
            verts.append((math.cos(a)*rx*r*s,y,math.sin(a)*rz*r*s-.30))
    for i in range(count):faces.append((0,1+i,1+(i+1)%count))
    for ring in range(3):
        for i in range(count):
            a=1+ring*count+i;b=1+ring*count+(i+1)%count;faces.append((a,b,b+count,a+count))
    faces.append(tuple(reversed([1+3*count+i for i in range(count)])))
    return mesh(name,verts,faces,mat)

dais('Lower glacial shelf',3.65,2.45,-2.94,FLOOR-.08,ice,2)
dais('Frozen throne dais',2.94,1.95,DAIS,-3.08,frost,5)

def fin(name,x,z,width,height,depth,lean,seed):
    sides=14;levels=26;verts=[];faces=[]
    for j in range(levels+1):
        t=j/levels;envelope=max(.016,(1-t)**.67)*(.94+.08*math.sin(t*9+seed))
        for i in range(sides):
            a=math.tau*i/sides;n=fbm(math.cos(a)*2+seed,t*5,math.sin(a)*2)
            u=math.cos(a)*width*envelope*(1+n*.14);d=math.sin(a)*depth*envelope*(1+n*.16)
            verts.append((x+u+lean*t*t,FLOOR+height*t,z+d-.38*t*t))
    for j in range(levels):
        for i in range(sides):
            a=j*sides+i;b=j*sides+(i+1)%sides;faces.append((a,b,b+sides,a+sides))
    faces.extend([tuple(reversed(range(sides))),tuple(levels*sides+i for i in range(sides))])
    obj=mesh(name,verts,faces,ice);obj.data.materials.append(frost)
    for p in obj.data.polygons:
        if p.normal.y>.65:p.material_index=1
    return obj

# A connected fan of eroded blue ice rises from one common throne back.
mass('Throne glacier root',(0,-2.05,-3.5),(3.35,1.16,1.0),ice,25,rough=.25)
for i,(x,z,w,h,d,lean) in enumerate([
    (-3.02,-3.25,.70,4.10,.65,-.45),(-2.28,-3.32,.80,5.14,.58,-.35),
    (-1.38,-3.54,.76,6.01,.62,-.23),(-.38,-3.64,.86,6.62,.68,-.16),
    (.72,-3.48,.75,6.25,.60,.24),(1.68,-3.38,.85,5.46,.63,.35),
    (2.62,-3.10,.86,4.39,.75,.35)]):
    fin('Eroded throne crest',x,z,w,h,d,lean,i*4.3)

for side in [-1,1]:
    for i in range(9):
        x=side*(4.0+i*.42+random.uniform(-.18,.18));z=-4.6+random.uniform(-1.5,1.2);length=random.uniform(.75,2.15)
        obj=fin('Vault icicle',0,0,random.uniform(.09,.22),length,random.uniform(.10,.24),random.uniform(-.12,.12),i+50)
        root=4.55+2.4*math.exp(-((x-1.2)**2/3+(z+5)**2/8))+fbm(x*.3,z*.3,3)*1.35+.24*math.sin(x*2.2+z*.6)
        for v in obj.data.vertices:v.co.y=root-(v.co.y-FLOOR)
        obj.location.x=x;obj.location.z=z

bpy.ops.mesh.primitive_cube_add(size=1,location=(0,FLOOR-.25,-2))
slab=bpy.context.object;slab.name='Ice floor slab';slab.scale=(40,.5,40)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);slab.data.materials.append(floor_mat)

environment_objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in environment_objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/assets/ice-environment.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=False)
report={'meshes':len(environment_objects),'vertices':sum(len(o.data.vertices) for o in environment_objects),'triangles':sum(len(p.vertices)-2 for o in environment_objects for p in o.data.polygons),'floor_y':FLOOR,'card_ground_y':DAIS,'design':'Natural glacial throne chamber','floating_objects':0,'architecture':'Continuous sculpted cavern and vault, connected throne crest, two low irregular frozen shelves'}
(ROOT/'output/ice-environment/model-report.json').write_text(json.dumps(report,indent=2))

with bpy.data.libraries.load(str(ROOT/'art-source/winter-crown.blend'),link=False) as (source,target):
    target.objects=[name for name in source.objects if not name.startswith(('Crystal_','Cold key','Silver rim','Winter Crown preview'))]
assembly=bpy.data.objects.new('Grounded Winter Crown assembly',None);bpy.context.collection.objects.link(assembly)
for obj in target.objects:
    if obj is not None and obj.type=='MESH':
        bpy.context.collection.objects.link(obj);transform=obj.matrix_world.copy();obj.parent=assembly;obj.matrix_world=transform
        if obj.name.startswith('Preview original penguin relief'):
            for v in obj.data.vertices:
                uv_y=(v.co.y-.10)/2.79+.5;t=max(0,min(1,uv_y/.08));edge=t*t*(3-2*t)
                v.co.x*=2.94/2.79;v.co.y=(v.co.y-.10)*2.94/2.79+.10;v.co.z=.183+(v.co.z-.183)*edge
assembly.location.y=-.22

for mat in materials:
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF')
    tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=5;tex.inputs['Roughness'].default_value=.72
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.18;bump.inputs['Distance'].default_value=.055
    links.new(tex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],p.inputs['Normal'])

bpy.ops.object.camera_add(location=(0,1.8,12.9));camera=bpy.context.object;camera.name='Natural throne chamber preview'
camera.rotation_euler=(Vector((0,-.10,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=42;bpy.context.scene.camera=camera
for name,loc,power,size,color in [('Glacial cleft',(1.8,7,-3),2200,4,(.6,.85,1)),('Card soft key',(-3,6,5),1200,5,(.82,.91,1)),('Ice wall bounce',(-5,1,-1),1100,3,(.23,.65,1))]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.name=name;light.data.energy=power;light.data.size=size;light.data.color=color
    light.rotation_euler=(Vector((0,-1,-1))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.world.color=(.035,.07,.12)
bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=48
bpy.context.scene.render.resolution_x=1600;bpy.context.scene.render.resolution_y=1000;bpy.context.scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art-source/winter-crown-ice-throne-room.blend'))
print('ICE_ENVIRONMENT_COMPLETE',json.dumps(report))
