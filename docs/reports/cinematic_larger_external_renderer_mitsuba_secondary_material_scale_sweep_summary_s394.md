# S394 Mitsuba Secondary Material Scale Sweep Summary

Generated UTC: `2026-06-20T07:39:19.250006+00:00`
Summary JSON: `build/shots/s394_mitsuba_secondary_material_scale_sweep/native_gap_sweep_summary.json`
Best candidate: `SS1`
Best max gap MAD: `23.951853137860084`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `SS1` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 2 | `SM75` | `ready` | 8 | 19.222744743441357 | 23.989165380658438 | 226 | `mitsuba_render_manifest` |
| 3 | `SM60` | `ready` | 8 | 19.222747636959877 | 23.989165380658438 | 226 | `mitsuba_render_manifest` |
| 4 | `SM45` | `ready` | 8 | 19.22274988747428 | 23.989165380658438 | 226 | `mitsuba_render_manifest` |

## Inputs

- `SS1`: `build/shots/s359_mitsuba_secondary_visibility_ss1_render_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `SM45`: `build/shots/s394_mitsuba_secondary_material_sm45_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `SM60`: `build/shots/s394_mitsuba_secondary_material_sm60_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `SM75`: `build/shots/s394_mitsuba_secondary_material_sm75_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)

## Next

Do not replace SS1 with reflectance-only scaling; test opacity/radius or visibility-cached material response next.
