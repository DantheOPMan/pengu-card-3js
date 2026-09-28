"""Winter Crown + Frostbound Lattice, constructed through Blender MCP.
Every frame, jewel setting, lattice strand, snowflake and letter is mesh geometry.
The separate original-art relief remains owned by the Three.js renderer.
"""
import bpy, bmesh, math, random, json
from pathlib import Path
from mathutils import Vector
ROOT=Path('C:/Users/socce/OneDrive/Documents/ClientWebsites/Practice Sites/frost-card-next')
random.seed(38)
for obj in list(bpy.context.scene.objects): bpy.data.objects.remove(obj,do_unlink=True)

def material(name,color,metallic,roughness):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1)
    n.inputs['Metallic'].default_value=metallic;n.inputs['Roughness'].default_value=roughness
    return m
silver=material('Winter silver',(.24,.27,.29),.88,.37)
ivory=material('Carved ivory',(.30,.255,.19),.08,.59)
iron=material('Oxidized recess',(.038,.047,.055),.76,.48)
blue=material('Glacial enamel',(.025,.073,.125),.46,.31)
ice=material('Rock crystal',(.40,.65,.79),.52,.17)
ruby=material('Burgundy enamel',(.15,.008,.022),.47,.22)
snow=material('Frost deposits',(.70,.80,.82),.10,.76)
ink=material('Cut lettering',(.020,.021,.020),.24,.48)
materials=[silver,ivory,iron,blue,ice,ruby,snow,ink]

def mesh(name,verts,faces,mat):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat)
    return obj

def plate(name,pts,z,depth,mat,bevel=.01):
    n=len(pts);verts=[(x,y,z+d) for d in [-depth/2,depth/2] for x,y in pts]
    faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    obj=mesh(name,verts,faces,mat)
    if bevel:
        mod=obj.modifiers.new('Carved edge','BEVEL');mod.width=bevel;mod.segments=2
    return obj

def outline(w,h,r,steps=8):
    out=[]
    for cx,cy,a in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
        for i in range(steps+1):
            t=math.radians(a+i*90/steps);out.append((cx+r*math.cos(t),cy+r*math.sin(t)))
    return out

def panel(name,w,h,x,y,z,depth,mat,r=.07):
    return plate(name,[(px+x,py+y) for px,py in outline(w,h,r)],z,depth,mat,.012)

def ring(name,w,h,r,width,z,depth,mat):
    outer=outline(w,h,r);inner=outline(w-2*width,h-2*width,max(.02,r-width));n=len(outer)
    verts=[(x,y,z+d) for d in [-depth/2,depth/2] for loop in [outer,inner] for x,y in loop]
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    obj=mesh(name,verts,faces,mat);mod=obj.modifiers.new('Polished arris','BEVEL');mod.width=min(width*.18,.008);mod.segments=2
    return obj

def curve(name,points,radius=.012,mat=silver,cyclic=False):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.resolution_u=6;data.bevel_depth=radius;data.bevel_resolution=2
    spl=data.splines.new('BEZIER');spl.bezier_points.add(len(points)-1);spl.use_cyclic_u=cyclic
    for p,co in zip(spl.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);data.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH')
    for p in obj.data.polygons:p.use_smooth=True
    return obj

def rod(name,a,b,radius,mat):
    delta=Vector(b)-Vector(a);n=6;verts=[]
    axis=delta.normalized();u=axis.cross(Vector((0,0,1)))
    if u.length<.01:u=axis.cross(Vector((0,1,0)))
    u.normalize();v=axis.cross(u)
    for center in [Vector(a),Vector(b)]:
        for i in range(n):verts.append(tuple(center+radius*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n))))
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,verts,faces,mat)

def leaf(name,a,b,width,mat=silver,side=1):
    a=Vector(a);b=Vector(b);d=b-a;perp=Vector((-d.y,d.x,0)).normalized()*width
    mid=a+d*.43;spine=mid+Vector((0,0,side*width*.55))
    return mesh(name,[tuple(a),tuple(mid+perp),tuple(b),tuple(mid-perp),tuple(spine)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(0,3,2,1)],mat)

def diamond(name,x,y,z,rx,ry,mat,side=1,setting=True):
    if setting:plate(name+' silver bezel',[(x,y+ry*1.17),(x+rx*1.2,y),(x,y-ry*1.17),(x-rx*1.2,y)],z-side*.009,.025,silver,.009)
    # A diamond-cut crown with table, bevel facets and pavilion, never a flat decal.
    shape=[(0,ry),(.7*rx,.44*ry),(rx,0),(.7*rx,-.44*ry),(0,-ry),(-.7*rx,-.44*ry),(-rx,0),(-.7*rx,.44*ry)]
    verts=[(x+px,y+py,z) for px,py in shape]+[(x+px*.48,y+py*.48,z+side*rx*.60) for px,py in shape]+[(x,y,z-side*rx*.5)]
    faces=[tuple(range(8,16))]
    for i in range(8):
        j=(i+1)%8;faces += [(i,j,8+j),(i,8+j,8+i),(j,i,16)]
    return mesh(name,verts,faces,mat)

def snowflake(x,y,z,size,side=-1):
    for i in range(6):
        t=i*math.tau/6+math.pi/2;d=Vector((math.cos(t),math.sin(t),0));base=Vector((x,y,z))
        rod('Raised snowflake arm',base,base+d*size,.008,ivory)
        for f in [.48,.76]:
            p=base+d*size*f
            for sign in [-1,1]:
                branch=Vector((math.cos(t+sign*.8),math.sin(t+sign*.8),0))*size*.30
                rod('Raised snowflake barb',p,p+branch,.0075,ivory)

# Structural core and the same finished border on both faces.
panel('Solid silver card core',3.13,4.56,0,0,0,.18,iron)
ring('Thick silver outer rim',3.20,4.63,.09,.065,0,.24,silver)
for side in [1,-1]:
    ring('Ivory carved perimeter',3.06,4.48,.11,.155,side*.13,.055,ivory)
    ring('Outer rope beading',3.15,4.57,.085,.018,side*.177,.020,silver)
    ring('Inner silver fillet',2.76,4.17,.08,.027,side*.188,.021,silver)
    for sx in [-1,1]:
        # Burgundy buried in the side channels with two intertwining bone strands.
        panel('Inset oxblood side channel',.065,3.94,sx*1.44,0,side*.169,.025,ruby,.035)
        for phase in [0,math.pi]:
            points=[(sx*(1.435+.062*math.sin(k*.52+phase)),-2.02+k*4.04/40,side*(.209+.018*math.cos(k*.52+phase))) for k in range(41)]
            curve('Twisted ivory stile',points,.034,ivory)
        points=[(sx*(1.435+.078*math.sin(k*.52+1.5)),-2.02+k*4.04/40,side*.251) for k in range(41)]
        curve('Silver thorn vine',points,.015,silver)
        for j in range(18):
            y=-1.86+j*.22;x=sx*(1.435+.068*math.sin(j*1.15))
            a=(x,y,side*.245);b=(x-sx*.09,y+.145,side*.285)
            leaf('Carved thorn',a,b,.026,ivory,side)
            curve('Leaf silver vein',[a,((a[0]+b[0])*.5,(a[1]+b[1])*.5,side*.285),b],.004,silver)
        diamond('Side garnet',sx*1.44,0,side*.27,.060,.14,ruby,side)
        diamond('Side crystal',sx*1.44,.03,side*.33,.035,.070,ice,side)
    # Four large faceted rock-crystal corner stones with nested dark and silver settings.
    for sx in [-1,1]:
        for sy in [-1,1]:
            x=sx*1.42;y=sy*2.10
            plate('Corner ivory escutcheon',[(x,y+.255),(x+.19,y),(x,y-.255),(x-.19,y)],side*.192,.085,ivory,.012)
            diamond('Corner rock crystal',x,y,side*.262,.145,.202,ice,side)
            diamond('Corner garnet accent',sx*1.22,sy*1.91,side*.233,.058,.095,ruby,side)
            curve('Corner sweeping branch',[(sx*.91,sy*2.13,side*.21),(sx*1.13,sy*2.03,side*.23),(sx*1.30,sy*1.75,side*.25)],.021,silver)
    # Curled thorn branches cross the horizontal edge bands.
    for sy in [-1,1]:
        for phase in [0,math.pi]:
            curve('Horizontal ivory ribbon',[(x,sy*(2.16+.044*math.sin(x*8+phase)),side*.214) for x in [-1.23+i*2.46/30 for i in range(31)]],.021,ivory)
        curve('Horizontal silver branch',[(x,sy*(2.14+.06*math.sin(x*6)),side*.238) for x in [-1.22+i*2.44/24 for i in range(25)]],.013,silver)
        for i in range(14):
            x=-1.10+i*.17
            leaf('Border thorn',(x,sy*2.14,side*.235),(x+.09,sy*(2.07 if i%2 else 2.21),side*.275),.020,silver,side)
        diamond('Center edge garnet',0,sy*2.18,side*.245,.076,.13,ruby,side)

# A substantial sculpted crown, not a wire outline.
crown_pts=[(-.74,2.27),(-.67,2.62),(-.50,2.38),(-.40,2.40),(-.29,2.76),(-.17,2.48),(0,2.81),(.17,2.48),(.29,2.76),(.40,2.40),(.50,2.38),(.67,2.62),(.74,2.27)]
plate('Carved bone crown',crown_pts,0,.20,ivory,.023)
for side in [1,-1]:
    curve('Crown silver edge',[(x,y,side*.12) for x,y in crown_pts],.017,silver,True)
    diamond('Crown main crystal',0,2.58,side*.155,.145,.235,ice,side)
    diamond('Crown red foot',0,2.28,side*.21,.068,.105,ruby,side)
    for sx in [-1,1]:
        curve('Crown inset arc',[(sx*.12,2.36,side*.15),(sx*.27,2.34,side*.17),(sx*.37,2.43,side*.13)],.014,silver)

# Front: bone plaques and a deeply framed glacial portrait recess.
window=ring('Portrait window bezel',2.66,2.92,.14,.029,.184,.038,silver);window.location.y=.10
panel('Title plaque',2.59,.51,0,1.83,.208,.074,ivory,.14)
ring('Title plaque inset',2.58,.50,.13,.016,.252,.015,silver).location.y=1.83
panel('Lore plaque',2.59,.67,0,-1.69,.208,.074,ivory,.18)
ring('Lore plaque inset',2.58,.66,.16,.016,.252,.015,silver).location.y=-1.69
for sy in [-1,1]:
    for sx in [-1,1]:
        y=1.62 if sy==1 else -1.42
        curve('Plaque thorn scroll',[(sx*1.12,y,.255),(sx*.90,y+sy*.045,.264),(sx*.81,y-sy*.035,.265),(sx*.9,y-sy*.065,.266)],.014,silver)

font_regular=bpy.data.fonts.load(str(ROOT/'public/fonts/IMFellEnglish-Regular.ttf'))
font_italic=bpy.data.fonts.load(str(ROOT/'public/fonts/IMFellEnglish-Italic.ttf'))
def lettering(body,y,size,font,width):
    data=bpy.data.curves.new(body,'FONT');data.body=body;data.font=font;data.align_x='CENTER';data.align_y='CENTER';data.size=size;data.extrude=.003;data.bevel_depth=.0007;data.resolution_u=8
    obj=bpy.data.objects.new('Engraved '+body,data);bpy.context.collection.objects.link(obj);obj.location=(0,y,.257);data.materials.append(ink)
    bpy.context.view_layer.update()
    if obj.dimensions.x>width:obj.scale.x*=width/obj.dimensions.x
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH')
lettering('The Frost King',1.84,.345,font_regular,2.32)
lettering('Even winter bends the knee.',-1.69,.172,font_italic,2.22)

# Back design 5: a regular checker repeat clipped beneath the inner frame.
panel('Frostbound ivory back',2.73,4.12,0,0,-.126,.049,ivory,.095)
back_x=1.35;back_y=2.055
def clip_to_back(points):
    for axis,bound,keep in [(0,-back_x,1),(0,back_x,-1),(1,-back_y,1),(1,back_y,-1)]:
        result=[]
        for a,b in zip(points,points[1:]+points[:1]):
            ain=keep*(a[axis]-bound)>=0;bin=keep*(b[axis]-bound)>=0
            if ain:result.append(a)
            if ain!=bin:
                t=(bound-a[axis])/(b[axis]-a[axis]);result.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
        points=result
        if not points:break
    return points
def polygon_area(points):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1])))*.5

# Four diamonds span the width; five span the height. Alternating rows give
# the rotated square grid a true two-color checker rather than broken stripes.
rx=back_x/4;ry=back_y/5
lattice_edges={};lattice_vertices=set();cells=[]
pattern_start=set(bpy.context.scene.objects)
for row in range(-6,7):
    cy=row*ry
    for col in range(-3,4):
        cx=col*rx*2+(rx if row%2 else 0)
        raw=[(cx,cy+ry),(cx+rx,cy),(cx,cy-ry),(cx-rx,cy)]
        pts=clip_to_back(raw)
        if len(pts)<3 or polygon_area(pts)<1e-8:continue
        cells.append({'row':row,'column':col,'center':[cx,cy],'blue':row%2==0,'area':polygon_area(pts)})
        if row%2==0:
            # Inset before clipping so boundary cells have the same margins.
            inset=clip_to_back([(cx+(x-cx)*.93,cy+(y-cy)*.93) for x,y in raw])
            if len(inset)>2 and polygon_area(inset)>1e-8:
                plate('Blue snowflake enamel lozenge',inset,-.168,.025,blue,.009)
            snowflake(cx,cy,-.213,.192)
        else:
            diamond('Burgundy lattice lozenge',cx,cy,-.203,.048,.100,ruby,-1)
        # A shared edge is authored once. No offset duplicate strands or uneven
        # knots where neighboring cells meet; the shallow arch repeats exactly.
        for a,b in zip(pts,pts[1:]+pts[:1]):
            if math.dist(a,b)<1e-7:continue
            if any(abs(a[axis]-sign*bound)<1e-7 and abs(b[axis]-sign*bound)<1e-7 for axis,bound in [(0,back_x),(1,back_y)] for sign in [-1,1]):continue
            key=tuple(sorted(tuple(round(c,6) for c in point) for point in [a,b]))
            lattice_edges[key]=(a,b)
        for x,y in raw:
            if abs(x)<back_x-.055 and abs(y)<back_y-.065:
                lattice_vertices.add((round(x,6),round(y,6)))
        for sign in [-1,1]:
            leaf('Lattice thorn',(cx+sign*rx*.58,cy+ry*.45,-.213),(cx+sign*rx*.88,cy+ry*.58,-.25),.013,silver,-1)

for a,b in lattice_edges.values():
    curve('Shared silver lattice strand',[(a[0],a[1],-.207),((a[0]+b[0])*.5,(a[1]+b[1])*.5,-.214),(b[0],b[1],-.207)],.021,silver)
for x,y in sorted(lattice_vertices):
    diamond('Lattice crystal pin',x,y,-.245,.035,.049,ice,-1)

# Crop motifs geometrically at the field boundary instead of omitting whole
# snowflakes near the edges. The frame covers these cuts as on an inlaid object.
pattern_objects=set(bpy.context.scene.objects)-pattern_start
planes=[((sign*back_x,0,0),(sign,0,0)) for sign in [-1,1]]+[((0,sign*back_y,0),(0,sign,0)) for sign in [-1,1]]
for obj in pattern_objects:
    if obj.type!='MESH':continue
    if all(abs(v.co.x)<=back_x and abs(v.co.y)<=back_y for v in obj.data.vertices):continue
    bm=bmesh.new();bm.from_mesh(obj.data)
    for co,normal in planes:
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=co,plane_no=normal,clear_outer=True,clear_inner=False)
    if not bm.faces:
        bm.free();bpy.data.objects.remove(obj,do_unlink=True);continue
    bm.to_mesh(obj.data);bm.free();obj.data.update()

covered_area=sum(c['area'] for c in cells)
assert abs(covered_area-4*back_x*back_y)<1e-6,'The lattice must cover the complete back field'
pattern_report={'cells':len(cells),'blue_snowflake_cells':sum(c['blue'] for c in cells),'ivory_garnet_cells':sum(not c['blue'] for c in cells),'unique_shared_edges':len(lattice_edges),'unique_crystal_junctions':len(lattice_vertices),'field_area':4*back_x*back_y,'covered_area':covered_area,'diamond_half_width':rx,'diamond_half_height':ry,'crown_center':[0,0],'repeat':'alternating blue snowflake and ivory garnet rows','cell_layout':cells}
(ROOT/'output/winter-crown/pattern-report.json').write_text(json.dumps(pattern_report,indent=2))

# Central enlarged crown diamond, the focal point of the approved patterned back.
plate('Central crown silver setting',[(0,.64),(.44,0),(0,-.64),(-.44,0)],-.25,.055,silver,.016)
plate('Central crown enamel field',[(0,.585),(.39,0),(0,-.585),(-.39,0)],-.288,.027,blue,.011)
central=[(-.25,-.10),(-.30,.23),(-.14,.10),(0,.36),(.14,.10),(.30,.23),(.25,-.10)]
plate('Raised back crown',central,-.342,.050,ivory,.012)
curve('Crown tracery',[(x,y,-.375) for x,y in central],.012,silver,True)
curve('Crown curved base',[(-.25,-.10,-.376),(0,-.058,-.39),(.25,-.10,-.376)],.024,silver)
for x in [-.22,0,.22]:diamond('Crown tiny gemstone',x,.06 if x else .18,-.391,.029,.044,ice,-1)
diamond('Crystal under crown',0,-.30,-.326,.10,.18,ice,-1)

# Small irregular frost accumulations and downward icicles, on both faces.
for side in [1,-1]:
    for sy in [-1,1]:
        for i in range(44):
            x=-1.34+i*2.68/43;y=sy*(2.20+random.uniform(-.018,.018));z=side*random.uniform(.24,.27)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=random.uniform(.009,.022),location=(x,y,z))
            obj=bpy.context.object;obj.name='Frost grain';obj.scale=(1.5,.65,.5);obj.data.materials.append(snow)
    for x in [-1.19,-.88,.92,1.21]:
        length=random.uniform(.12,.22)
        bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=.002,radius2=.025,depth=length,location=(x,2.02-length*.5,side*.25),rotation=(math.pi/2,0,0))
        bpy.context.object.name='Hanging icicle';bpy.context.object.data.materials.append(ice)

# Independent small shards retain the existing subtle orbit behavior.
for i in range(5):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(2.14*math.cos(i*2.4),2.18*math.sin(i*2.4),.1))
    obj=bpy.context.object;obj.name='Crystal_%02d'%i;obj.scale=(.045,.12,.045);obj.data.materials.append(ice)

# Keep draw calls bounded: one static casting per material plus five loose shards.
source_count=len([o for o in bpy.context.scene.objects if o.type=='MESH'])
for mat in materials:
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('Crystal_') and o.active_material==mat]
    for obj in objects:
        bpy.context.view_layer.objects.active=obj
        for mod in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
    if objects:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:obj.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name=mat.name+' casting'

# Reduce densely tessellated bevels while retaining the sculpted silhouette.
for obj in list(bpy.context.scene.objects):
    if obj.type=='MESH' and len(obj.data.polygons)>3000:
        bpy.context.view_layer.objects.active=obj
        mod=obj.modifiers.new('Realtime casting LOD','DECIMATE');mod.ratio=.23
        bpy.ops.object.modifier_apply(modifier=mod.name)

for obj in bpy.context.scene.objects:
    if obj.type=='MESH':
        obj.data.validate(verbose=False,clean_customdata=True);obj.data.update()

bpy.ops.object.camera_add(location=(0,0,9));camera=bpy.context.object;camera.name='Winter Crown preview';camera.rotation_euler=(0,0,0);bpy.context.scene.camera=camera;camera.data.type='ORTHO';camera.data.ortho_scale=6.0
for name,loc,power,size in [('Cold key',(-3,4,5),700,5),('Silver rim',(3,0,3),450,3)]:
    bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.name=name;light.data.energy=power;light.data.size=size;light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.world.color=(.10,.12,.15)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/assets/winter-crown.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=False)
exec((ROOT/'art-source/add_winter_preview.py').read_text(encoding='utf-8-sig'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('Preview ')]
report={'source_meshes':source_count,'exported_meshes':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'triangles':sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),'materials':[m.name for m in materials],'front_reference':'02-winter-crown.png','back_reference':'05-frostbound-lattice.png'}
(ROOT/'output/winter-crown/model-report.json').write_text(json.dumps(report,indent=2))
print('WINTER_CROWN_EXPORTED',json.dumps(report))
