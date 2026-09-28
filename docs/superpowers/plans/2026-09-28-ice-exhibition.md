# Ice Exhibition Implementation Plan

**Goal:** Place the Winter Crown card in a real Blender-authored ice environment, remove floating particles, eliminate the portrait cutoff, and retain only Auto orbit on a single-screen page.

**Architecture:** Export the static ice floor, fractured walls and frozen formations as a separate GLB. Three.js owns live lighting, a floor reflection and shared shadows. Preserve the card geometry, repeat pattern and cap/beard relief. The complete Blender scene includes the card for inspection.

**Tech Stack:** Blender MCP, Python, Next.js, Three.js WebGLRenderer and Reflector.

- [x] Simplify the live page and generate five separate visual alternatives. Save the images and exact prompts.
- [x] Build `art-source/build_ice_environment.py`, export `public/assets/ice-environment.glb`, and save an editable Blender scene containing the setting and card.
- [x] Implement `src/scene/iceEnvironment.ts` for material detail, floor reflection and shadow reception. Integrate it into the scene lifecycle.
- [x] Remove points and detached shards from the live scene; extend and mask the portrait beneath the frame. Preserve original artwork bytes.
- [x] Update single-screen CSS for the lighter environment and readable title/control placement.
- [x] Build the app, inspect desktop/mobile framing, exercise drag and Auto orbit, verify no runtime errors, and save screenshots. Inspect floor reflection, contact shadow, portrait edge and complete back pattern.

No deployment or new design-selection approval is needed: these edits are directly authorized in the conversation. The five generated alternatives remain available for later refinement.
