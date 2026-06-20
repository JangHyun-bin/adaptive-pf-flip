# S484 Mitsuba Material Response Mask Split mrms3_narrow_bins

Generated UTC: `2026-06-20T17:09:15.598184+00:00`
Export JSON: `build/shots/s484_mitsuba_material_response_mask_sweep/mrms3_narrow_bins/split_export/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s480_mitsuba_response_control_light_full/mitsuba_export.json`
- Mask source: `build/shots/s484_mitsuba_material_response_mask_sweep/mrms3_narrow_bins/mask_source/material_response_mask_source_summary.json`

## Water Mask Material Response

- Face limit: `450`
- Face stride: `1`
- Response alpha: `0.008`
- Response bins: `2`
- Distribution: `ggx`
- IOR: `1.0 -> 1.333`
- Specular reflectance: `[0.34, 0.42, 0.56]`
- Specular transmittance: `[0.94, 0.97, 1.0]`
- Mask threshold: `8`
- Source luma gate: `0.0..255.0`
- Use current water shape: `True`
- Response shape ID prefix: `lsfs_s484_mrms3_narrow_bins_water_mask_material`
- Response BSDF ID prefix: `lsfs_s484_mrms3_narrow_bins_water_surface_masked_response`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Empty mask frames ignored: `6`
- Candidate faces: `900`
- Response faces: `900`
- Remainder faces: `42084`
- Water shape replacements: `2`
- Response BSDF insertions: `2`
- XML scene bytes: `1.41 MB`

## Frame Samples

| Output | Water Faces | Response Faces | Remainder Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 19963 | 0 | 19963 | `build/shots/s484_mitsuba_material_response_mask_sweep/mrms3_narrow_bins/mask_source/masks/frame_0000.png` | `build/shots/s484_mitsuba_material_response_mask_sweep/mrms3_narrow_bins/split_export/scenes/frame_0000.xml` |
| 27 | 18548 | 0 | 18548 | `build/shots/s484_mitsuba_material_response_mask_sweep/mrms3_narrow_bins/mask_source/masks/frame_0004.png` | `build/shots/s484_mitsuba_material_response_mask_sweep/mrms3_narrow_bins/split_export/scenes/frame_0004.xml` |
| 47 | 22040 | 450 | 21590 | `build/shots/s484_mitsuba_material_response_mask_sweep/mrms3_narrow_bins/mask_source/masks/frame_0007.png` | `build/shots/s484_mitsuba_material_response_mask_sweep/mrms3_narrow_bins/split_export/scenes/frame_0007.xml` |

## Next

Validate, render, and compare mrms3_narrow_bins.
