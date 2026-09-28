# Ice Sanctuary Implementation Plan

**Goal:** Build a natural ice throne room around the existing Winter Crown card. The user rejected the initial formal arches during implementation and explicitly redirected the design to a natural glacier chamber.

**Architecture:** Blender authors a continuous noise-sculpted cavern, frozen-waterfall walls, an eroded throne crest, low glacial shelves and a riven vault. Three.js preserves the card and interaction, separates the room floor from the dais height, and provides restrained ice materials and cold overhead light.

**Tech Stack:** Blender MCP, Python, Three.js, Next.js.

The user's annotated refinement directly authorizes this local implementation. Use the existing project and execute inline.

- [x] Author `art-source/build_ice_throne_room.py` with a continuous glacial cavern, natural throne crest and low frozen dais. Keep the foreground open and integrate icicle roots into the vault.
- [x] Export `public/assets/ice-environment.glb` through the isolated Blender MCP instance; save the complete editable scene as `art-source/winter-crown-ice-throne-room.blend`.
- [x] Refine `src/scene/iceEnvironment.ts` for clouded blue ice, restrained reflections and fixed overhead lighting. Separate room floor and card contact height. Widen the desktop camera and adapt text contrast to the cold dark scene.
- [x] Run `npm run build`, confirm exit 0 including TypeScript, then inspect desktop and mobile, the front and back, live reflection, and orbit behavior in the browser. Save final screenshots and the geometry report under `output/ice-environment`.
- [x] Update README and this checklist; leave the production preview running and close only the isolated Blender helper created for this build.

Visual acceptance: the setting reads as a continuous natural cavern with an ice throne and low dais, with no formal architectural arches. The card remains the focal point; its relief and complete back design remain intact. No airborne particles or extra interface controls are introduced.
