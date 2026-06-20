# S333 Mitsuba Secondary Halo Sweep Summary

Generated UTC: `2026-06-20T00:06:52.494589+00:00`
Summary JSON: `build/shots/s333_mitsuba_secondary_halo_sweep_summary/sweep_summary.json`
Best candidate: `halo_h2`
Best max gap MAD: `67.40660365226337`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `halo_h2` | `ready` | 8 | 37.58172702867798 | 67.40660365226337 | 171 | `mitsuba_render_manifest` |
| 2 | `halo_h1` | `ready` | 8 | 37.646964136445476 | 67.5240412808642 | 171 | `mitsuba_render_manifest` |
| 3 | `sweep_b_s332` | `ready` | 8 | 37.73105774176955 | 67.67647762345679 | 171 | `mitsuba_render_manifest` |
| 4 | `native_s331` | `ready` | 8 | 55.544113136574076 | 85.7207773919753 | 189 | `mitsuba_render_manifest` |
| 5 | `baseline_s330` | `ready` | 8 | 74.16963405028292 | 104.48981417181069 | 153 | `handoff_base_preview` |

## Inputs

- `baseline_s330`: `build/shots/s330_mitsuba_renderer_target_gap/renderer_target_gap_summary.json` (7.72 MB GIF)
- `native_s331`: `build/shots/s331_mitsuba_renderer_native_target_gap/renderer_target_gap_summary.json` (8.06 MB GIF)
- `sweep_b_s332`: `build/shots/s332_mitsuba_native_gap_sweep_b_target_gap/renderer_target_gap_summary.json` (8.15 MB GIF)
- `halo_h1`: `build/shots/s333_mitsuba_secondary_halo_h1_target_gap/renderer_target_gap_summary.json` (8.18 MB GIF)
- `halo_h2`: `build/shots/s333_mitsuba_secondary_halo_h2_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)

## Next

Use halo_h2 as the renderer-side secondary baseline, but move to a true screen-space or volumetric secondary representation next because halo spheres only marginally reduce the gap.
