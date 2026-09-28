# Reference inventory — 2026-09-28

## Scope

Initial request: study Meng To's video and recreate the technique with Three.js and Blender MCP. Follow-up: learn from vgpu's holographic card and create a fancy new card using the attached penguin. The follow-up defines the new visual subject; the Dark Souls art and sword are not reused.

## Evidence

| Source | Observed / confirmed | Local evidence |
| --- | --- | --- |
| X post 2104565735288938804 | Author explicitly states layered PNGs, a depth map, 3D objects and card extrusion | `reference/post.json`; post read in Codex browser |
| Post video | 29.7 seconds; rotating ornate front/back card, independent sword prop, character relief and drifting sparks | `reference/reference-video.mp4`; `reference/contact-sheet.jpg`, six frames at five-second intervals |
| vgpu example | Source has pointer smoothing, analytic card ray/plane intersection, procedural engravings, diffraction, pearlescence, glint, micrograin and baked lettering | `reference/vgpu-source.md` |
| vgpu license | MIT, copyright 2025 Vercel, Inc. | `reference/vgpu-LICENSE` |
| User artwork | 1000 × 1000 PNG; flat yellow background, penguin with red cap, pale blue beard and blue scarf | Unmodified copy `public/assets/penguin-original.png` |
| Blender authoring | Standard MCP stdio client → installed Blender MCP server → isolated Blender 5.2.1 session on loopback 9881 | `scripts/blender_client.py`; `art-source/mcp-last-result.json` |

The X video was retrieved from its public video.twimg.com URL reported by the post metadata, with normal HTTP User-Agent/Referer headers. No blocked-site content or security setting was used. Initial web-reader access and native X playback failed; metadata and a valid MP4 plus decoded frames supplied the evidence.

## Reconstruction contracts

| Subsystem | Implementation | Evidence class |
| --- | --- | --- |
| Card body | Real Blender GLB, bevels, side milling, inlays, rivets | Newly authored adaptation |
| Portrait | Original RGB texture; shader background key; smooth spatial relief field | New approximation of layered-depth concept |
| Foil | GLSL wavelength response and 3-order diffraction, local tangent-space lighting | Adapted from inspected vgpu source |
| Typography | Separate transparent canvas textures; DOM controls | Newly authored |
| Reverse | Foil security patterns, concentric seal, real raised snowflake | Newly authored |
| Floating props | Seven detached Blender crystals and 75 GPU points | Adapted from video's independent prop/particle concept |
| Interaction | Smoothed pointer tilt, drag yaw, keyboard yaw, flip, full auto orbit, reset | Video-inspired behavior plus local controls |
| Responsive | Three-column desktop, tablet controls row, single-column phone | Original adaptation; original phone layout unavailable |
| Resource ownership | Per-component scene setup/dispose, late-load guards, hidden-tab skip, reduced motion | Original implementation |

The exact source site's architecture, source assets, camera parameters, mobile behavior and timings remain unknown. The runtime has no dependency on threeui.com or the reference video.
