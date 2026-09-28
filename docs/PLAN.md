# Frost King card

Build a local Next.js / React / TypeScript collectible showroom using Three.js and Blender MCP. The user's supplied penguin remains the focal artwork. Meng To's post supplies the layered-image/3D-extrusion concept; vgpu supplies the spectral diffraction reference. The blocked threeui site is not needed.

- [x] Capture reference video frames and document confirmed versus inferred behavior.
- [x] Create an isolated Blender MCP session; author a beveled frame, corner details, snowflake medallion and floating crystals; save editable .blend and export GLB.
- [x] Build a Three.js stage with original artwork, image-derived depth, real extrusion, independent foil lighting and a designed reverse face.
- [x] Add readable React controls for three foil finishes, intensity, light movement, flip, auto-rotation, reset and image capture.
- [x] Verify the production build, desktop/mobile layout, rendered output, interactions, errors, asset loading and cleanup. Save screenshots and a reading guide.

Visual direction: a quiet near-black gallery, ivory editorial typography, fine ruled labels and an oversized luminous silver collectible. Cyan, lavender and pale gold reflections support the red cap and blue scarf. Card surfaces use original procedural engraving, not a screenshot of the source demo.

Implementation boundaries: src/components owns the accessible UI; src/scene owns all GPU resources, input, animation and teardown; art-source owns reproducible Blender authoring; public/assets owns runtime media. Keep source-study material under reference, outside the runtime.
