# Original Ice Wall Refinement

**Goal:** Restore the user's original ice studio and improve only the realism of its left and right walls.

**Architecture:** Load the saved `winter-crown-ice-studio.blend`. Retain the exact floor, backdrop, fissures, card, camera and lights. Replace the existing side-wall and foot meshes in their original bounds with subdivided, eroded fracture geometry. Export the same environment GLB and restore the original Three.js lighting, camera, floor reflection and page colors. Apply refined materials only to the new side-wall meshes.

**Tech Stack:** Blender MCP, Python, Three.js, Next.js.

- [x] Restore the original Blender scene, sculpt the wall meshes, verify preserved geometry hashes, export GLB, save a separate refined Blender scene.
- [x] Restore the original renderer framing, lighting and pale page palette; retain wall-specific frost/roughness refinements.
- [x] Verify the desktop composition against the original screenshot, mobile fit, reflection, card rotation and console errors. Run `npm run build` and confirm exit 0.
- [x] Save screenshots and reports, update README, close only this task's Blender helper and leave the preview running.
