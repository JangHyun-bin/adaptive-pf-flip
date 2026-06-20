# S400 Mitsuba Water/Light Native Gap Sweep

Generated UTC: `2026-06-20T08:13:04.783108+00:00`
Summary JSON: `build/shots/s400_mitsuba_water_light_sweep/native_gap_sweep_summary.json`
Best candidate: `SS1`
Best max gap MAD: `23.951853137860084`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `SS1` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `mitsuba_render_manifest` |
| 2 | `KL1` | `ready` | 8 | 19.222773517875513 | 23.988705632716048 | 226 | `mitsuba_render_manifest` |
| 3 | `WA006` | `ready` | 8 | 19.235979616769548 | 23.990507973251027 | 226 | `mitsuba_render_manifest` |
| 4 | `WA028` | `ready` | 8 | 19.209451999742797 | 24.001432613168724 | 223 | `mitsuba_render_manifest` |
| 5 | `WT72` | `ready` | 8 | 21.136787712191357 | 27.907768775720164 | 231 | `mitsuba_render_manifest` |

## Inputs

- `SS1`: `build/shots/s359_mitsuba_secondary_visibility_ss1_render_gap/renderer_target_gap_summary.json` (8.20 MB GIF)
- `WA006`: `build/shots/s400_mitsuba_water_light_wa006_target_gap/renderer_target_gap_summary.json` (8.17 MB GIF)
- `WA028`: `build/shots/s400_mitsuba_water_light_wa028_target_gap/renderer_target_gap_summary.json` (8.26 MB GIF)
- `WT72`: `build/shots/s400_mitsuba_water_light_wt72_target_gap/renderer_target_gap_summary.json` (8.11 MB GIF)
- `KL1`: `build/shots/s400_mitsuba_water_light_kl1_target_gap/renderer_target_gap_summary.json` (8.20 MB GIF)

## Next

Keep SS1 as the native baseline; if continuing native renderer work, focus on localized/key-light or BSDF model changes rather than water transmittance reduction.
