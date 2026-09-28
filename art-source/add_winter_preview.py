"""Complete the editable .blend with a matching relief and procedural preview materials.
These preview-only meshes are excluded from the runtime hardware GLB, where Three.js
owns the original-art relief, its keyed alpha and animated spectral lighting.
"""
import bpy, math
from pathlib import Path
ROOT=Path('C:/Users/socce/OneDrive/Documents/ClientWebsites/Practice Sites/frost-card-next')
for obj in list(bpy.context.scene.objects):
    if obj.name.startswith('Preview '):bpy.data.objects.remove(obj,do_unlink=True)

# The same cap and beard depth field as the preserved browser shader.
steps=120;verts=[];uvs=[];faces=[]
for j in range(steps+1):
    v=j/steps
    for i in range(steps+1):
        u=i/steps
        beard=math.exp(-(((u-.60)/.29)**2+((v-.29)/.28)**2)*1.8)
        cap=math.exp(-(((u-.48)/.39)**2+((v-.67)/.19)**2)*1.7)
        verts.append(((u-.5)*2.79,(v-.5)*2.79+.10,.183+.045+beard*.16+cap*.09));uvs.append((u,v))
for j in range(steps):
    for i in range(steps):
        a=j*(steps+1)+i;faces.append((a,a+1,a+steps+2,a+steps+1))
data=bpy.data.meshes.new('Original art relief grid');data.from_pydata(verts,[],faces);data.update()
obj=bpy.data.objects.new('Preview original penguin relief',data);bpy.context.collection.objects.link(obj)
uv=data.uv_layers.new(name='Artwork UV')
for p in data.polygons:
    p.use_smooth=True
    for li in p.loop_indices:uv.data[li].uv=uvs[data.loops[li].vertex_index]
mat=bpy.data.materials.new('Preview original penguin enamel');mat.use_nodes=True
nodes=mat.node_tree.nodes;links=mat.node_tree.links;nodes.clear()
out=nodes.new('ShaderNodeOutputMaterial');principled=nodes.new('ShaderNodeBsdfPrincipled');transparent=nodes.new('ShaderNodeBsdfTransparent');mix=nodes.new('ShaderNodeMixShader')
principled.inputs['Roughness'].default_value=.36
tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ROOT/'public/assets/penguin-original.png'),check_existing=True);tex.image.pack()
links.new(tex.outputs['Color'],principled.inputs['Base Color'])
sep=nodes.new('ShaderNodeSeparateColor');links.new(tex.outputs['Color'],sep.inputs['Color'])
minimum=nodes.new('ShaderNodeMath');minimum.operation='MINIMUM';links.new(sep.outputs['Red'],minimum.inputs[0]);links.new(sep.outputs['Green'],minimum.inputs[1])
diff=nodes.new('ShaderNodeMath');diff.operation='SUBTRACT';links.new(minimum.outputs[0],diff.inputs[0]);links.new(sep.outputs['Blue'],diff.inputs[1])
mask=nodes.new('ShaderNodeMath');mask.operation='GREATER_THAN';mask.inputs[1].default_value=.65;links.new(diff.outputs[0],mask.inputs[0])
links.new(mask.outputs[0],mix.inputs[0]);links.new(principled.outputs[0],mix.inputs[1]);links.new(transparent.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs['Surface'])
if hasattr(mat,'surface_render_method'):mat.surface_render_method='DITHERED'
obj.data.materials.append(mat)

# Frosted portrait well for standalone Blender preview.
bpy.ops.mesh.primitive_plane_add(size=1,location=(0,.10,.148));well=bpy.context.object;well.name='Preview glacial portrait well';well.scale=(2.60,2.86,1)
well_mat=bpy.data.materials.new('Preview glacial portrait');well_mat.use_nodes=True
nodes=well_mat.node_tree.nodes;links=well_mat.node_tree.links;n=nodes.get('Principled BSDF');n.inputs['Roughness'].default_value=.56
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=28;noise.inputs['Detail'].default_value=4
ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.05,.10,.16,1);ramp.color_ramp.elements[1].color=(.20,.32,.40,1);links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],n.inputs['Base Color']);well.data.materials.append(well_mat)

# Add editable procedural aging nodes after export; glTF keeps the base PBR values.
for material in bpy.data.materials:
    if material.users==0 or not material.name.startswith(('Carved ivory','Winter silver','Glacial enamel','Rock crystal')):continue
    nodes=material.node_tree.nodes;links=material.node_tree.links;p=nodes.get('Principled BSDF')
    if not p or any(n.name=='Winter surface noise' for n in nodes):continue
    noise=nodes.new('ShaderNodeTexNoise');noise.name='Winter surface noise';noise.inputs['Scale'].default_value=72;noise.inputs['Detail'].default_value=3
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.23;bump.inputs['Distance'].default_value=.014;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
    ramp=nodes.new('ShaderNodeValToRGB');base=tuple(p.inputs['Base Color'].default_value)
    ramp.color_ramp.elements[0].color=tuple(c*.62 for c in base[:3])+(1,);ramp.color_ramp.elements[1].color=base
    links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],p.inputs['Base Color'])

bpy.context.scene.camera.location.y=.24
bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=32
bpy.context.scene.render.resolution_x=1000;bpy.context.scene.render.resolution_y=1200;bpy.context.scene.render.resolution_percentage=100
bpy.context.scene['approved_front']='Winter Crown';bpy.context.scene['approved_reverse']='Frostbound Lattice - design 5'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art-source/winter-crown.blend'))
print('EDITABLE_WINTER_CROWN_COMPLETE: packed original artwork, matching relief geometry, both card faces, editable material nodes')
