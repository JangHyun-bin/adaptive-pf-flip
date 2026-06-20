# S483 Mitsuba Material Response Mask Split

Generated UTC: `2026-06-20T16:59:49.318738+00:00`
Export JSON: `build/shots/s483_mitsuba_material_response_mask_split/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s480_mitsuba_response_control_light_full/mitsuba_export.json`
- Mask source: `build/shots/s483_mitsuba_material_response_mask_source/material_response_mask_source_summary.json`

## Water Mask Material Response

- Face limit: `900`
- Face stride: `1`
- Response alpha: `0.012`
- Response bins: `1`
- Distribution: `ggx`
- IOR: `1.0 -> 1.333`
- Specular reflectance: `[0.42, 0.52, 0.72]`
- Specular transmittance: `[0.75, 0.86, 1.0]`
- Mask threshold: `8`
- Source luma gate: `0.0..255.0`
- Use current water shape: `True`
- Response shape ID prefix: `lsfs_s483_water_mask_material`
- Response BSDF ID prefix: `lsfs_s483_water_surface_masked_response`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Empty mask frames ignored: `6`
- Candidate faces: `1800`
- Response faces: `1800`
- Remainder faces: `41184`
- Water shape replacements: `2`
- Response BSDF insertions: `2`
- XML scene bytes: `1.40 MB`

## Frame Samples

| Output | Water Faces | Response Faces | Remainder Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 19963 | 0 | 19963 | `build/shots/s483_mitsuba_material_response_mask_source/masks/frame_0000.png` | `build/shots/s483_mitsuba_material_response_mask_split/scenes/frame_0000.xml` |
| 27 | 18548 | 0 | 18548 | `build/shots/s483_mitsuba_material_response_mask_source/masks/frame_0004.png` | `build/shots/s483_mitsuba_material_response_mask_split/scenes/frame_0004.xml` |
| 47 | 22040 | 900 | 21140 | `build/shots/s483_mitsuba_material_response_mask_source/masks/frame_0007.png` | `build/shots/s483_mitsuba_material_response_mask_split/scenes/frame_0007.xml` |

## Next

Validate, render, and compare this split-water material response against S481, S482, and the S478 p4 proxy gate.
