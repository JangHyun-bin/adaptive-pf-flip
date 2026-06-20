# S441 Mitsuba Light Response Contract Decision

Generated UTC: `2026-06-20T12:55:20+00:00`

## Scope

S441 converts the accepted nonsecondary source-highlight evidence into a
renderer-neutral light-response contract. This is deliberately different from
the rejected paths:

- not CR21 post-composite grading;
- not a screen card or sprite overlay;
- not another water mesh smoothing/replacement pass;
- not another water-surface emitter sweep.

## Inputs

- Source-highlight mask:
  `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`
- S437 decomposition decision:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_response_decomposition_s437.md`
- S440 water silhouette/depth decision:
  `docs/reports/cinematic_larger_external_renderer_water_silhouette_depth_decision_s440.md`

## Contract Output

- Contract JSON:
  `build/reports/s441_mitsuba_s401_light_response_contract/light_response_contract.json`
- Gallery:
  `build/reports/s441_mitsuba_s401_light_response_contract/gallery/index.html`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_light_response_contract_s441.md`
- Tool:
  `tools/build_mitsuba_light_response_contract.py`

## Checks

| Metric | Value |
| --- | ---: |
| Frames | 8 |
| Anchors | 49 |
| Max anchors per frame | 8 |
| Mean mask coverage | 0.003991849922839507 |
| Max mask coverage | 0.014924768518518518 |
| Overlay bytes | 1.95 MB |

## Decision

Keep the contract and move forward. It gives the renderer backend an explicit
target-free input for the remaining highlight response without hiding the effect
inside post-composite grading.

The next implementation should consume these anchors as one of:

- bounded area lights tied to screen-projected source highlights;
- glint/caustic response metadata;
- participating-volume or mist-light response controls.

The first backend should be conservative and compare against `SS1_Native`,
`S417_WP4_H18_D90`, and `S401_CR21_Profile`. It should not use the target image
or CR21 grade as a runtime input.

## Next

S442 should implement a Mitsuba export consumer for
`lsfs_mitsuba_light_response_contract`, render a small candidate, and compare
target gap against the current native baseline.
