# S421 Mitsuba WP4 Water Mask Material Split WMS4 Export

Generated UTC: `2026-06-20T11:08:56.180858+00:00`
Export JSON: `build/shots/s421_mitsuba_wp4_water_mask_material_split_wms4_defaultdist/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s416_mitsuba_water_patch_wp4_midwide/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Mask Material Response

- Face limit: `0`
- Face stride: `1`
- Response alpha: `0.006`
- Distribution: `none`
- IOR: `1.0 -> 1.333`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate faces: `1242`
- Response faces: `1242`
- Remainder faces: `155522`
- Water shape replacements: `8`
- Response BSDF insertions: `8`
- XML scene bytes: `1.38 MB`

## Frame Samples

| Output | Water Faces | Response Faces | Remainder Faces | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 20000 | 37 | 19963 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s421_mitsuba_wp4_water_mask_material_split_wms4_defaultdist/scenes/frame_0000.xml` |
| 27 | 18576 | 28 | 18548 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s421_mitsuba_wp4_water_mask_material_split_wms4_defaultdist/scenes/frame_0004.xml` |
| 47 | 22300 | 730 | 21570 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s421_mitsuba_wp4_water_mask_material_split_wms4_defaultdist/scenes/frame_0007.xml` |

## Next

Validate, render, and apply H18 D90 to this default-distribution split-water material candidate.
