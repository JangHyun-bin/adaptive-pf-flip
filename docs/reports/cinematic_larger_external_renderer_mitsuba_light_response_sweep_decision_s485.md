# S485 Mitsuba Light Response Sweep Decision

Generated UTC: `2026-06-20T17:17:02.068642+00:00`

## Decision

Keep the S485 light/glint sweep runner as a regression harness, but do not promote any light-response knob variant over the S478 `p4_soft_wide` proxy gate.

The sweep proves that the S479 light-response contract can be retuned across radius, radiance, localization, and anchor-selection settings without breaking XML export or rendering. The best variants are slightly better than the original S481 light-only baseline, but the improvement is too small to close the target gap. The remaining difference is not primarily a scalar light strength problem.

## Inputs

- Sweep summary: `build/shots/s485_mitsuba_light_response_sweep/light_response_sweep_summary.json`
- Gap gallery: `build/shots/s485_mitsuba_light_response_sweep/gap_gallery/gap_summary_gallery.json`
- Base native export: `build/shots/s465_mitsuba_native_patch_setting_sweep/nr4_focus_worst/mitsuba_export.json`
- Light contract: `build/shots/s479_mitsuba_response_control_handoff/light_response_contract.json`

## Candidate Results

| Candidate | Mean MAD | Max MAD | Max Gap | Lights | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| S478 `p4_soft_wide` proxy | `19.079715470679012` | `23.9488554526749` | `176` | `0` | current promoted visual gate |
| S485 `lrs4_sparse_spec` | `19.214833622685184` | `23.98198945473251` | `219` | `8` | best mean among S485, not promoted |
| S485 `lrs2_bright_glint` | `19.21484358924897` | `23.98198945473251` | `219` | `8` | not promoted |
| S485 `lrs1_warm_compact` | `19.214923482510287` | `23.98198945473251` | `219` | `8` | not promoted |
| S481 native light-only | `19.215028131430042` | `23.98206790123457` | `219` | `8` | baseline reproduced |
| S482 RD duplicate mesh | `19.187556423611113` | `23.98206790123457` | `227` | `8` | still not proxy parity |
| S484 best material mask | `19.271615949717077` | `23.98206790123457` | `250` | `8` | rejected material direction |
| S485 `lrs0_s480_default` | `19.215028131430042` | `23.98206790123457` | `219` | `8` | S480/S481 reproduction |
| S485 `lrs3_soft_area` | `19.21494510352366` | `23.982425411522634` | `219` | `8` | not promoted |

## Mechanism Checks

- Sweep variants: `5`
- Frames per candidate: `8`
- Contract frames matched per candidate: `5`
- Missing contract frames ignored per candidate: `3`
- Localized anchors per candidate: `8`
- Lights inserted per candidate: `8`
- Gap gallery best: `S478_p4_proxy`

## Interpretation

Changing light radius, radiance, color temperature, and localization changes the score only in the fourth decimal place. That is useful evidence: the current native light contract is stable, but the missing proxy response is not recoverable by simply making glints smaller, brighter, warmer, broader, or sparser.

The material-mask path from S484 also failed to close the gap. Together, S484 and S485 suggest that the next useful path is a representation change, not another scalar sweep.

## Next

Move to AOV/texture parity analysis: compare the S478 proxy improvement against native renders per frame and isolate whether the missing response is low-frequency water-body tone, screen-space highlight texture, reflection breakup, or a composite-only target artifact. Then implement the smallest renderer-native representation that matches that isolated residual.
