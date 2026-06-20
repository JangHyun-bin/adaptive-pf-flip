# S441 Mitsuba S401 Light Response Contract

Generated UTC: `2026-06-20T12:55:20.203444+00:00`
Contract JSON: `build/reports/s441_mitsuba_s401_light_response_contract/light_response_contract.json`
Gallery: `build/reports/s441_mitsuba_s401_light_response_contract/gallery/index.html`
Status: `ready`

## Inputs

- Mask source: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`
- Mask kind: `highlight`

## Checks

- Frames: `8`
- Anchors: `49`
- Max anchors per frame: `8`
- Mean mask coverage: `0.003991849922839507`
- Max mask coverage: `0.014924768518518518`
- Overlay bytes: `1.95 MB`

## Frame Anchors

| Output | Coverage | Anchors | Largest Anchor | Mean Luma | Overlay |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0.0016859567901234569 | 7 | 0.0007581018518518518 | 140.671731 | `build/reports/s441_mitsuba_s401_light_response_contract/overlays/frame_0000_light_response_overlay.png` |
| 7 | 0.0007947530864197531 | 6 | 0.00021219135802469136 | 138.261346 | `build/reports/s441_mitsuba_s401_light_response_contract/overlays/frame_0001_light_response_overlay.png` |
| 13 | 0.0007330246913580247 | 5 | 0.00027584876543209876 | 138.100385 | `build/reports/s441_mitsuba_s401_light_response_contract/overlays/frame_0002_light_response_overlay.png` |
| 20 | 0.000773533950617284 | 5 | 0.00027391975308641974 | 140.857054 | `build/reports/s441_mitsuba_s401_light_response_contract/overlays/frame_0003_light_response_overlay.png` |
| 27 | 0.0010686728395061728 | 2 | 0.0007986111111111112 | 143.359416 | `build/reports/s441_mitsuba_s401_light_response_contract/overlays/frame_0004_light_response_overlay.png` |
| 34 | 0.0015258487654320988 | 8 | 0.0005787037037037037 | 138.736149 | `build/reports/s441_mitsuba_s401_light_response_contract/overlays/frame_0005_light_response_overlay.png` |
| 40 | 0.010428240740740741 | 8 | 0.00797067901234568 | 137.219128 | `build/reports/s441_mitsuba_s401_light_response_contract/overlays/frame_0006_light_response_overlay.png` |
| 47 | 0.014924768518518518 | 8 | 0.006902006172839506 | 142.001326 | `build/reports/s441_mitsuba_s401_light_response_contract/overlays/frame_0007_light_response_overlay.png` |

## Decision Use

This contract is renderer-neutral. It does not apply a post-composite grade,
does not add a screen card, and does not mutate the water mesh. It packages
the nonsecondary highlight evidence as bounded per-frame light-response
anchors that a renderer backend can consume as area lights, caustic/glint
controls, or volume-light metadata.

## Next

Implement a renderer backend that consumes this contract as bounded area-light, caustic/glint, or participating-volume response metadata; compare it against SS1_Native without using post-composite CR21 grading.
