# S421 Mitsuba Water Mask Material Split WMS2 Export

Generated UTC: `2026-06-20T11:04:10.998039+00:00`
Export JSON: `build/shots/s421_mitsuba_water_mask_material_split_wms2_limited/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Mask Material Response

- Face limit: `700`
- Face stride: `1`
- Response alpha: `0.003`
- IOR: `1.0 -> 1.333`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate faces: `1212`
- Response faces: `1212`
- Remainder faces: `155552`
- Water shape replacements: `8`
- Response BSDF insertions: `8`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | Water Faces | Response Faces | Remainder Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 20000 | 37 | 19963 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s421_mitsuba_water_mask_material_split_wms2_limited/scenes/frame_0000.xml` |
| 27 | 18576 | 28 | 18548 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s421_mitsuba_water_mask_material_split_wms2_limited/scenes/frame_0004.xml` |
| 47 | 22300 | 700 | 21600 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s421_mitsuba_water_mask_material_split_wms2_limited/scenes/frame_0007.xml` |

## Next

Validate, render, and compare WMS2 limited sharp split-water material response.
