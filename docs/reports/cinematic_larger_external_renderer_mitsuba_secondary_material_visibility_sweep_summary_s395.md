# S395 Mitsuba Secondary Material Visibility Sweep Summary

Generated UTC: `2026-06-20T07:42:52.501070+00:00`
Summary JSON: `build/shots/s395_mitsuba_secondary_material_visibility_sweep/native_gap_sweep_summary.json`
Best candidate: `SS1`
Best max gap MAD: `23.951853137860084`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `SS1` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 2 | `OV1` | `ready` | 8 | 19.22269949202675 | 23.98887281378601 | 226 | `mitsuba_render_manifest` |
| 3 | `RV1` | `ready` | 8 | 19.223276990097737 | 23.989178883744856 | 226 | `mitsuba_render_manifest` |
| 4 | `OR1` | `ready` | 8 | 19.22330608603395 | 23.989264403292182 | 226 | `mitsuba_render_manifest` |

## Inputs

- `SS1`: `build/shots/s359_mitsuba_secondary_visibility_ss1_render_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `OV1`: `build/shots/s395_mitsuba_secondary_material_ov1_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `RV1`: `build/shots/s395_mitsuba_secondary_material_rv1_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)
- `OR1`: `build/shots/s395_mitsuba_secondary_material_or1_target_gap/renderer_target_gap_summary.json` (8.21 MB GIF)

## Next

Keep SS1 if opacity/radius visibility boosts regress; otherwise expand the best candidate with visual review.
