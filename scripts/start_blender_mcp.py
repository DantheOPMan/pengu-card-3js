"""Launch only in a separate --factory-startup Blender GUI process."""
import bpy
import importlib.util
from pathlib import Path

addon_path = Path(__file__).resolve().parents[2] / 'feadship-next/tools/blender-mcp/upstream/addon.py'
spec = importlib.util.spec_from_file_location('frost_blender_mcp', addon_path)
addon = importlib.util.module_from_spec(spec)
spec.loader.exec_module(addon)
addon.register()
bpy.context.scene.blendermcp_port = 9881
bpy.context.scene.blendermcp_auto_start_server = False
server = addon.BlenderMCPServer(host='127.0.0.1', port=9881)
bpy.types.blendermcp_server = server
server.start()
print('FROST_CARD_BLENDER_MCP_READY port=9881', flush=True)
