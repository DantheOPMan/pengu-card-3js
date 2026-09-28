# Winter Crown — The Frost King

A local, editable holographic collectible built with Next.js, React, TypeScript, Three.js, and Blender MCP. The character uses the supplied penguin PNG. No runtime requests go to the blocked reference site.

The current version uses the Winter Crown frame and Frostbound Lattice reverse, with a raised penguin portrait in an open ice studio. The darker blue reflective floor separates from the pale backdrop; side pillars and floating particles are removed. The artwork shader removes yellow edge spill while preserving the black outline, orange beak and cap/beard depth. Auto orbit is the only visible control.

## Run

```powershell
npm install
npm run dev
```

Open http://127.0.0.1:4215. For the production version:

```powershell
npm run build
npm run start
```

If Node on this machine cannot verify npm's certificate chain, enable its supported system trust store for that terminal with `$env:NODE_USE_SYSTEM_CA='1'`. Certificate validation stays enabled.

The site can be deployed as a standard Next.js application. This task only runs it locally.

## App icon

`public/brand/winter-crown.png` is the transparent 512px project logo, adapted from the ivory crown and ice crystal on the back of the card. Its editable source is `public/brand/winter-crown.svg`. Next.js serves the matching browser favicon, 32px PNG icon and 180px Apple icon from `src/app/`; these are included in Vercel deployments. Run `npm run icons` to regenerate them from the SVG.

## Explore the card

- Hover to tilt; drag horizontally for a full rotation and inspect the Frostbound Lattice reverse.
- Auto orbit is the only visible control. It starts or pauses a slow full rotation.
- Focus the canvas and use Left/Right arrows to rotate. Home resets rotation.
- The page is a single-screen exhibition with no settings panel, download button, marketing copy or navigation.
- The card stands in a Blender-built ice studio. A live floor reflection follows rotation; the card casts a shadow onto the ice. Floating specks and loose crystal shards are removed.

## How the references work

[Meng To's post](https://x.com/MengTo/status/2104565735288938804) explicitly describes PNG layers with depth maps plus 3D objects and card extrusion. The recovered 29.7-second video shows an ornate rotating card, raised character art, a reverse face, floating sparks, and a separate sword prop. The linked threeui site was not accessed, so its exact rendering code, geometry, maps and easing are unknown.

The [vgpu holographic card](https://vgpu.sh/examples/holographic-card) is a different construction: a fullscreen WGSL effect analytically intersects a ray with a tilted plane, draws a rounded card and engravings, and adds a baked lettering mask. Its iridescence combines approximate RGB wavelength responses, three diffraction orders, a broad pearlescent palette, a pointer-driven reflection band, and surface-locked micrograin.

This project combines those ideas using a real Three.js scene. It ports the reference's optical equations to GLSL, uses Blender-authored card hardware, and places the original artwork in front of the foil surface. A smooth, hand-authored depth field lifts the beard and cap. This is an original penguin adaptation, not recovered source code or a pixel-exact copy of the Dark Souls scene.

## Reading path

1. `src/app/page.tsx` mounts the experience.
2. `src/components/CardExperience.tsx` owns Auto orbit and loading/error feedback. React state is passed into one scene instance.
3. `src/scene/createCardScene.ts` owns asset loading, renderer, camera, lighting, pointer/keyboard input, animation and disposal. `src/scene/iceEnvironment.ts` owns the ice materials, live floor reflection and shadow receiver.
4. `src/scene/shaders.ts` defines the foil and relief materials. Shader comments explain the optical reference and depth field.
5. `src/scene/winterMaterials.ts` adds local surface cracks, pitting, and spectral reflections to the Blender materials. Front lettering is now actual Blender text geometry; the old `cardLettering.ts` is retained as an earlier design source.
6. `art-source/build_winter_crown.py` builds the selected front and back through Blender MCP. `art-source/add_winter_preview.py` completes the standalone source with a packed original-art relief and editable preview materials. `art-source/winter-crown.blend` is the complete editable source; `public/assets/winter-crown.glb` contains runtime hardware.

## Coordinates and render flow

The card face occupies XY; +Z is the front. The outer frame is 3.2 × 4.6 units. Blender exports with `export_yup=False` so these authored coordinates remain unchanged in Three.js. The glacial portrait recess is Z=.148; a soft contact shadow sits above it. The original image begins at Z=.183 and its unchanged smooth cap/beard relief projects further forward. Bone plaques and text, silver lattice, snowflakes and gems are actual geometry. The reverse faces -Z.

Pointer position is normalized to -1..1 in the canvas. An exponential interpolation smooths the tilt and reflection. The shader projects light and view vectors into the card's local tangents; changing card orientation therefore changes its diffraction, not just its CSS transform. Contour derivatives determine local engraving direction. The fragment shader sums three diffraction orders and combines them with broad pearlescence and a narrow highlight. These are appearance approximations, not a laboratory spectral renderer.

Blender meshes use physically based metallic materials under an environment map and two directional lights. Foil is a separate procedural material. Artwork retains its original file and is keyed against its yellow background in the GPU; the runtime character uses the original file without regeneration. Generated concept images guide the frame and reverse design. Depth fields are smooth spatial masks, not an AI-inferred metric depth map. The portrait is a relief, not a complete sculpted penguin.

The renderer stops updating hidden tabs, caps DPR at 1.75, respects reduced-motion preferences, responds to container resizing, and owns its event listeners and GPU resources. Async loads check instance retirement before attaching assets. On teardown, geometry, materials, textures, environment targets and the renderer are disposed. The only external network links are explicitly clicked source references.

## Customization examples

- **New artwork:** replace `public/assets/penguin-original.png`, then change `artworkVertex`'s cap/beard centers and `artworkFragment`'s background key in `shaders.ts`. Those are specific to this illustration. Check its edges while rotating.
- **New foil palette:** edit `pearl()` in `shaders.ts` and the corresponding finish labels/swatches in `CardExperience.tsx` and `globals.css`.
- **Card copy:** edit the `lettering()` calls in `build_winter_crown.py` and rebuild the hardware.
- **Motion:** edit the damping, tilt limits and `autoRotation` speed in `createCardScene.ts`. Angles are radians, time is seconds and pointer positions are normalized.
- **Hardware:** edit `build_winter_crown.py`, run it through Blender MCP, then reload the GLB. Preserve the XY/+Z convention.

## Blender MCP reproduction

`scripts/start_blender_mcp.py` loads this workspace's already-present Blender MCP addon into a separate factory-startup session on loopback port 9881. It does not change Blender preferences or the original running Blender session. `scripts/blender_client.py` uses the installed MCP Python client's standard stdio transport and the `execute_blender_code` tool. The saved `art-source/mcp-last-result.json` records the successful export.

The helper currently references the existing sibling `feadship-next/tools/blender-mcp` installation; update that path if moving the project. The website itself is portable and does not require Blender or MCP at runtime. The `.blend` source opens independently.

## Attribution and limits

The spectral/grating and pearlescent equations are adapted from Vercel Labs vgpu under its MIT license, retained in `reference/vgpu-LICENSE`. The full studied source is preserved at `reference/vgpu-source.md`. Three.js and the framework packages retain their own licenses in npm distributions. The supplied character artwork is user-provided; no new ownership or trademark claim is made.

See `REFERENCE_INVENTORY.md` and `VISUAL_DIFFS.md` for evidence, visual adjustments, and the precise verification scope.


## Earlier Northern Realms design

The earlier bronze version used IM Fell English and Cinzel (locally bundled with OFL licenses), a crowned bronze frame, cast scrollwork, moonstone settings, and an engraved dark portrait recess. Wraith, Moonsteel, and Gilded finishes retain the pointer-responsive reflections. The original artwork file and the cap/beard displacement equations are unchanged.

The Blender MCP source is `art-source/build_card.py`; the editable scene is `art-source/frost-king.blend`. Static hardware is consolidated by material into four meshes, plus seven floating stones. The previous hardware/source is preserved in `art-source/first-edition/`.

Validation: production build and TypeScript pass; front/reverse, all three finishes, intensity/light controls, keyboard rotation, auto orbit, reset, and 390px responsive rendering checked in the in-app browser. The original and served artwork SHA-256 match. The Windows GPU emits the same harmless RoomEnvironment precision warning as the prior version; no runtime errors were observed.


## Selected Winter Crown implementation

Approved references are `output/concepts/02-winter-crown.png` (front) and `output/concepts/winter-crown-backs/05-frostbound-lattice.png` (back). This is a realtime modeled interpretation of those images: no generated card render is used as a flat front/back texture.

The current GLB combines 1,496 modeled parts into 13 meshes, approximately 260,000 hardware triangles. It contains physical card thickness, ivory and silver borders, thorn vines, crown, faceted crystal and burgundy settings, title/lore lettering, the complete back lattice, raised snowflakes, and the central reverse crown. Each face has one top-center red gem; the front title plaque has no hanging icicles crossing the lettering. The original penguin keeps its prior 150-segment relief surface in Three.js; a corresponding relief is packed into the editable Blender source for standalone inspection.

The reverse uses 49 evenly spaced cells in a true alternating blue-snowflake / ivory-garnet repeat. Each shared lattice edge and crystal junction is modeled once. Boundary motifs are clipped beneath the frame instead of omitted, and the raised crown remains centered above the field. `output/winter-crown/pattern-report.json` records the layout and verifies complete field coverage.

The render uses direct/environment lighting, shadow mapping, and procedural cracks and pitting. Moonlight is the fixed finish. The selected references and the earlier bronze model remain available alongside the new assets.

## Ice exhibition

The current environment uses the original pale ice floor and background, with all 24 side pillars and foot fragments removed. `art-source/empty_ice_studio.py` loads the original scene through Blender MCP and exports only the floor, curved backdrop and embedded fissures. These 38 meshes retain identical geometry hashes, recorded in `output/ice-environment/preserved-original-geometry.json`. The GLB has 9,764 triangles. The complete edited scene is saved separately as `art-source/winter-crown-ice-studio-empty.blend`.

The original camera, pale lighting, floor reflection, background and page colors remain. Three.js adds a 768px planar reflection with subtle blur and distortion plus a shadow receiver, with the card tracking the original floor at Y=-2.60. The original backdrop and floor shaders are preserved. The enlarged portrait extends behind the lower bezel and has a matching rounded mask while retaining cap and beard relief. Previous environment experiments remain saved as separate Blender files, but are not loaded on the website.

Five one-page design images and their full imagegen prompts are preserved in `output/concepts/one-page-designs/`. The ice environment is a real 3D implementation, not a generated background image.
