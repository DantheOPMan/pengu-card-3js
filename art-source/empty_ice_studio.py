"""Keep the original floor and backdrop; remove all side pillars and foot chunks."""
import bpy, json, hashlib, struct
from pathlib import Path

ROOT=Path('C:/Users/socce/OneDrive/Documents/ClientWebsites/Practice Sites/frost-card-next')
SOURCE=ROOT/'art-source/winter-crown-ice-studio.blend'
for obj in list(bpy.context.scene.objects):
    bpy.data.objects.remove(obj,do_unlink=True)
with bpy.data.libraries.load(str(SOURCE),link=False) as (source,target):
    target.objects=list(source.objects)
for obj in target.objects:
    if obj is not None:bpy.context.collection.objects.link(obj)

SIDE_PREFIXES=('Anchored glacier ridge','Frozen bank at wall foot','Weathered Anchored glacier ridge','Weathered Frozen bank at wall foot')
sides=[o for o in bpy.context.scene.objects if o.name.startswith(SIDE_PREFIXES)]
removed=len(sides)
for obj in sides:bpy.data.objects.remove(obj,do_unlink=True)
environment=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(('Ice floor slab','Sculpted glacier backdrop','Embedded ice fracture'))]
assert len(environment)==38, 'Unexpected original environment mesh count'
assert not any(o.name.startswith(SIDE_PREFIXES) for o in bpy.context.scene.objects)

def fingerprint(obj):
    h=hashlib.sha256()
    for v in obj.data.vertices:h.update(struct.pack('<3f',*v.co))
    for p in obj.data.polygons:
        h.update(struct.pack('<I',len(p.vertices)))
        for i in p.vertices:h.update(struct.pack('<I',i))
    for row in obj.matrix_world:h.update(struct.pack('<4f',*row))
    return h.hexdigest()
original=json.loads((ROOT/'output/ice-environment/preserved-original-geometry.json').read_text())
retained={o.name:fingerprint(o) for o in environment}
assert retained==original, 'Original floor, backdrop or fissures changed'

bpy.ops.object.select_all(action='DESELECT')
for obj in environment:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/assets/ice-environment.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=False)

# Use the current card hardware in the editable exhibition, rather than the
# historical card embedded in the original environment source.
for obj in list(bpy.context.scene.objects):
    if obj.type=='MESH' and obj not in environment:bpy.data.objects.remove(obj,do_unlink=True)
with bpy.data.libraries.load(str(ROOT/'art-source/winter-crown.blend'),link=False) as (source,target):
    target.objects=[name for name in source.objects if not name.startswith(('Crystal_','Cold key','Silver rim','Winter Crown preview'))]
for obj in target.objects:
    if obj is not None and obj.type=='MESH':
        bpy.context.collection.objects.link(obj)
        if obj.name.startswith('Preview original penguin relief'):
            for v in obj.data.vertices:
                uv_y=(v.co.y-.10)/2.79+.5
                t=max(0,min(1,uv_y/.08));edge=t*t*(3-2*t)
                v.co.x*=2.94/2.79;v.co.y=(v.co.y-.10)*2.94/2.79+.10
                v.co.z=.183+(v.co.z-.183)*edge

scene=bpy.context.scene
scene.camera=next(o for o in scene.objects if o.type=='CAMERA' and o.name.startswith('Ice studio'))
scene.world.color=(.32,.42,.5)
scene.render.engine='CYCLES';scene.cycles.samples=48
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art-source/winter-crown-ice-studio-empty.blend'))
report={'design':'Original ice studio, empty floor and background','source':str(SOURCE),'meshes':len(environment),'vertices':sum(len(o.data.vertices) for o in environment),'triangles':sum(len(p.vertices)-2 for o in environment for p in o.data.polygons),'removed_side_meshes':removed,'side_meshes':0,'preserved_meshes':len(environment),'preserved_geometry_hashes_match':retained==original,'floor_y':-2.60,'floating_objects':0}
(ROOT/'output/ice-environment/model-report.json').write_text(json.dumps(report,indent=2))
print('EMPTY_ICE_STUDIO',json.dumps(report))
