"""Call the installed Blender MCP server via its standard MCP stdio transport."""
import asyncio
import json
import sys
from pathlib import Path
from datetime import timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(command=sys.executable, args=['-m', 'blender_mcp.server', '--host', '127.0.0.1', '--port', '9881'])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=180)) as session:
            await session.initialize()
            if len(sys.argv) > 1:
                code = Path(sys.argv[1]).read_text(encoding='utf-8')
                result = await session.call_tool('execute_blender_code', {'code': code, 'user_prompt': 'Delete the side pillars and the small ice chunks at their bases. Keep the original empty ice floor, background and card.'})
            else:
                result = await session.call_tool('get_scene_info', {'user_prompt': 'Inspect the isolated Blender session for the requested holographic card.'})
            output = result.model_dump(mode='json')
            print(json.dumps({'isError':output.get('isError'),'messages':[item.get('text','')[-1100:] for item in output.get('content',[])]}, indent=2))
            destination = Path(__file__).resolve().parents[1] / 'art-source' / 'mcp-last-result.json'
            destination.write_text(json.dumps(output, indent=2), encoding='utf-8')

asyncio.run(main())
