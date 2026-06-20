# S465 Mitsuba Native Patch nr2_wide_bright Export

Generated UTC: `2026-06-20T15:33:37.465759+00:00`
Export JSON: `build/shots/s465_mitsuba_native_patch_setting_sweep/nr2_wide_bright/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s460_mitsuba_material_tone_refine_sweep/mt8_secondary_light/mitsuba_export.json`
- Residual analysis: `build/shots/s464_mitsuba_signed_gap_residual_requests/target_residual_analysis.json`

## Residual Response Patches

- Request limit: `12`
- Per-frame request limit: `4`
- Output frame filter: `None`
- Radius range: `0.035..0.34`
- Radius scale: `0.24`
- Radiance scale: `1.15`
- ID prefix: `lsfs_s465_nr2_wide_bright`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Residual requests consumed: `12`
- Candidate vertices: `2952`
- Patches inserted: `12`
- Fallback patches: `0`
- XML scene bytes: `1.40 MB`

## Frame Samples

| Output | Vertices | Requests | Patches | Fallback | XML Scene |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 10000 | 2 | 2 | 0 | `build/shots/s465_mitsuba_native_patch_setting_sweep/nr2_wide_bright/scenes/frame_0000.xml` |
| 27 | 9290 | 1 | 1 | 0 | `build/shots/s465_mitsuba_native_patch_setting_sweep/nr2_wide_bright/scenes/frame_0004.xml` |
| 47 | 11152 | 3 | 3 | 0 | `build/shots/s465_mitsuba_native_patch_setting_sweep/nr2_wide_bright/scenes/frame_0007.xml` |

## Next

Validate, render, and compare this S465 native patch setting candidate.
