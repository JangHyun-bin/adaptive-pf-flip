# S416 Mitsuba Water Patch WP2 Export

Generated UTC: `2026-06-20T10:03:23.416476+00:00`
Export JSON: `build/shots/s416_mitsuba_water_patch_wp2_hotcluster/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Highlight Emitters

- Emitter limit: `32`
- Radius: `0.18`
- Radiance: `[1.2, 1.45, 1.75]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `541`
- Emitters inserted: `53`
- XML scene bytes: `1.37 MB`

## Frame Samples

| Output | Vertices | Candidates | Emitters | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 12 | 3 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s416_mitsuba_water_patch_wp2_hotcluster/scenes/frame_0000.xml` |
| 27 | 9290 | 14 | 3 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s416_mitsuba_water_patch_wp2_hotcluster/scenes/frame_0004.xml` |
| 47 | 11152 | 340 | 23 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s416_mitsuba_water_patch_wp2_hotcluster/scenes/frame_0007.xml` |

## Next

Validate, render, and compare WP2 as a compact clustered water-highlight patch candidate.
