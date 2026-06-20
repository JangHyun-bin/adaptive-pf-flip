# S418 Mitsuba Water Disk Patch DP4 Export

Generated UTC: `2026-06-20T10:29:36.847194+00:00`
Export JSON: `build/shots/s418_mitsuba_water_disk_patch_dp4_bright/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Patch Emitters

- Patch limit: `12`
- Cluster screen radius: `50.0`
- Radius range: `0.08..1.05`
- Radiance: `[3.0, 4.2, 5.6]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `541`
- Patches inserted: `25`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | Vertices | Candidates | Patches | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 12 | 3 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s418_mitsuba_water_disk_patch_dp4_bright/scenes/frame_0000.xml` |
| 27 | 9290 | 14 | 2 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s418_mitsuba_water_disk_patch_dp4_bright/scenes/frame_0004.xml` |
| 47 | 11152 | 340 | 8 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s418_mitsuba_water_disk_patch_dp4_bright/scenes/frame_0007.xml` |

## Next

Validate, render, and compare DP4 as a bright disk patch candidate.
