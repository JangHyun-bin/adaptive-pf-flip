# S418 Mitsuba Water Disk Patch DP2 Export

Generated UTC: `2026-06-20T10:26:27.557927+00:00`
Export JSON: `build/shots/s418_mitsuba_water_disk_patch_dp2_wide/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Mask source: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Water Patch Emitters

- Patch limit: `10`
- Cluster screen radius: `55.0`
- Radius range: `0.08..0.72`
- Radiance: `[0.45, 0.62, 0.82]`
- Mask threshold: `8`
- Source luma gate: `145.0..255.0`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Candidate vertices: `541`
- Patches inserted: `24`
- XML scene bytes: `1.36 MB`

## Frame Samples

| Output | Vertices | Candidates | Patches | Mask | XML Scene |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 10000 | 12 | 3 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0000.png` | `build/shots/s418_mitsuba_water_disk_patch_dp2_wide/scenes/frame_0000.xml` |
| 27 | 9290 | 14 | 2 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0004.png` | `build/shots/s418_mitsuba_water_disk_patch_dp2_wide/scenes/frame_0004.xml` |
| 47 | 11152 | 340 | 7 | `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/masks/frame_0007.png` | `build/shots/s418_mitsuba_water_disk_patch_dp2_wide/scenes/frame_0007.xml` |

## Next

Validate, render, and compare DP2 as a wider lower-radiance disk patch candidate.
