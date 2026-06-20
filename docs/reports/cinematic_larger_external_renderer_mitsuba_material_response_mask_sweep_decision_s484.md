# S484 Mitsuba Material Response Mask Sweep Decision

Generated UTC: `2026-06-20T17:10:27.779960+00:00`

## Decision

Pause the current native material-mask path for promotion.

S484 validated that narrow projected water-material masks can be generated, split into the current Mitsuba water shape, rendered, and compared automatically. However, none of the four calibrated mask/BSDF variants improved the native baseline or the promoted S478 proxy gate. The smallest/clearest material candidate is safer than S483, but it still increases mean gap and does not reduce the shared max-MAD plateau.

The next renderer-native work should move away from broad water-material modulation and toward light/glint response, texture/AOV parity, or a lower-level water-shader parameter path that does not create extra face-region color shifts.

## Inputs

- Sweep summary: `build/shots/s484_mitsuba_material_response_mask_sweep/material_response_mask_sweep_summary.json`
- Gap gallery: `build/shots/s484_mitsuba_material_response_mask_sweep/gap_gallery/gap_summary_gallery.json`
- Calibration summary: `build/shots/s484_mitsuba_material_response_mask_sweep/response_calibration/response_calibration_summary.json`
- Base native export: `build/shots/s480_mitsuba_response_control_light_full/mitsuba_export.json`
- Material contract: `build/shots/s479_mitsuba_response_control_handoff/material_response_contract.json`

## Candidate Results

| Candidate | Mean MAD | Max MAD | Max Gap | Response Faces | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| S478 `p4_soft_wide` proxy | `19.079715470679012` | `23.9488554526749` | `176` | `0` | current promoted visual gate |
| S482 RD duplicate mesh | `19.187556423611113` | `23.98206790123457` | `227` | `656` | safe but weak |
| S481 native light-only | `19.215028131430042` | `23.98206790123457` | `219` | `656` | current native baseline |
| S484 `mrms4_minimal_clear` | `19.271615949717077` | `23.98206790123457` | `250` | `320` | best S484 mask, not promoted |
| S484 `mrms1_tiny_neutral` | `19.291198559670782` | `23.98206790123457` | `251` | `480` | not promoted |
| S484 `mrms2_core_soft` | `19.30777504501029` | `23.98206790123457` | `246` | `720` | not promoted |
| S484 `mrms3_narrow_bins` | `19.329058802726337` | `23.98206790123457` | `248` | `900` | not promoted |
| S483 projected mask split | `19.45090920781893` | `23.98206790123457` | `249` | `1800` | superseded by narrower S484 masks |

## Mechanism Checks

- Sweep variants: `4`
- Frames per candidate: `8`
- S484 mask coverage range: `0.02742283950617284` to `0.03297453703703704`
- S484 response faces range: `320` to `900`
- Gap gallery best: `S478_p4_proxy`
- Calibration best max-gap: `S478_p4_proxy`
- Calibration best mean-gap: `S478_p4_proxy`
- Pareto count: `1`

## Interpretation

The S484 result is useful because it separates mechanism validity from image-quality promotion. The projected mask split is operational, less artifact-prone than the S482 duplicate surface, and narrower than S483. The remaining problem is that material-region modulation is still changing the water body in the wrong image-space direction for this target preview.

Lower coverage and lower alpha reduced the damage but did not create a path to improvement. That makes another local alpha/coverage sweep low leverage unless the representation changes.

## Next

Keep the S484 runner as a regression harness, but stop promoting material masks for the current shot. The next useful native pass is a light/glint response sweep or a texture/AOV parity path that tries to match the S478 proxy gate without splitting broad water material regions.
