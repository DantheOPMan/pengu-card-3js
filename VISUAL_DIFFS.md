# Visual verification

Target: a new penguin card using the references' layered depth and optical behavior. The user's follow-up authorizes a new design. No claim of Dark Souls screenshot equivalence is made.

| Item | Finding | Action / status |
| --- | --- | --- |
| Uneven portrait outlines | Thresholded vertex depth caused visible deformation along black strokes | Replaced with continuous beard/cap depth fields; smooth edges visually confirmed |
| Washed artwork | Global filmic tone mapping lifted the illustration | Disabled tone mapping for the artwork layer; retained it for hardware/foil |
| Short desktop viewport | First pass exceeded viewport height | Reduced minimum stage height and tightened short-screen controls; page confirmed 1280 × 720 with no overflow |
| Hint overlap | Card silhouette intruded into instruction line | Reserved canvas space above the hint |
| Front small labels | Edition/rarity labels were too close to image well | Raised labels into the header band |
| Spectral rotation | Initial shader projected lighting in world XY | Converted to card-local tangents and corrected derivative-based groove direction |
| Mobile composition | Initial screenshot checked at 390 × 844 | No horizontal overflow; original art and controls retained |
| Original 3D character | Source may use multiple independent image layers | This version uses a curved relief surface in front of the foil; no full 3D penguin claimed |
| Original environment | Source has sword, throne-like environment and sparks | User's penguin version uses crystals, cool motes and a minimal gallery |
| Device coverage | Codex in-app Chromium / Windows desktop and responsive emulation | Physical phone, Safari and Firefox not tested |
| Driver warning | One ANGLE precision warning while compiling Three.js environment-map shader | No shader failure or application exception observed; warning left attributed to upstream compilation |

Final interaction checks and export evidence are recorded in `output/verification.json`.
