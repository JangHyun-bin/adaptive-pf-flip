# S332 Mitsuba Native Gap Sweep Summary

Generated UTC: `2026-06-20T00:00:38.863948+00:00`
Summary JSON: `build/shots/s332_mitsuba_native_gap_sweep_summary/sweep_summary.json`
Best candidate: `sweep_b`
Best max gap MAD: `67.67647762345679`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `sweep_b` | `ready` | 8 | 37.73105774176955 | 67.67647762345679 | 171 | `mitsuba_render_manifest` |
| 2 | `sweep_c` | `ready` | 8 | 40.326414448302465 | 70.31346450617283 | 173 | `mitsuba_render_manifest` |
| 3 | `native_s331` | `ready` | 8 | 55.544113136574076 | 85.7207773919753 | 189 | `mitsuba_render_manifest` |
| 4 | `baseline_s330` | `ready` | 8 | 74.16963405028292 | 104.48981417181069 | 153 | `handoff_base_preview` |

## Inputs

- `baseline_s330`: `build/shots/s330_mitsuba_renderer_target_gap/renderer_target_gap_summary.json` (7.72 MB GIF)
- `native_s331`: `build/shots/s331_mitsuba_renderer_native_target_gap/renderer_target_gap_summary.json` (8.06 MB GIF)
- `sweep_b`: `build/shots/s332_mitsuba_native_gap_sweep_b_target_gap/renderer_target_gap_summary.json` (8.15 MB GIF)
- `sweep_c`: `build/shots/s332_mitsuba_native_gap_sweep_c_target_gap/renderer_target_gap_summary.json` (7.78 MB GIF)

## Next

Use sweep_b as the next renderer-native baseline and spend the next pass on a non-sphere secondary representation.
