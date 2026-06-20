# S370 Mitsuba Material Key Light Sweep Summary

Generated UTC: `2026-06-20T04:36:03.390885+00:00`
Summary JSON: `build/shots/s370_mitsuba_material_keylight_sweep_summary/material_keylight_sweep_summary.json`
Best candidate: `SV1-cache`
Best max gap MAD: `23.72217142489712`

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | Source |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `SV1-cache` | `ready` | 8 | 19.103672839506174 | 23.72217142489712 | 170 | `secondary_composite_summary` |
| 2 | `KL3` | `ready` | 8 | 109.67923394097222 | 140.33243569958847 | 240 | `secondary_composite_summary` |
| 3 | `KL1` | `ready` | 8 | 109.67945400913067 | 140.33249035493827 | 240 | `secondary_composite_summary` |
| 4 | `KL2` | `ready` | 8 | 110.30775487075617 | 140.94324395576132 | 239 | `secondary_composite_summary` |

## Inputs

- `SV1-cache`: `build/shots/s362_mitsuba_secondary_visibility_cache_apply_sv1_candidate_gap/renderer_target_gap_summary.json` (8.25 MB GIF)
- `KL1`: `build/shots/s370_mitsuba_material_keylight_kl1_candidate_gap/renderer_target_gap_summary.json` (7.86 MB GIF)
- `KL2`: `build/shots/s370_mitsuba_material_keylight_kl2_candidate_gap/renderer_target_gap_summary.json` (7.81 MB GIF)
- `KL3`: `build/shots/s370_mitsuba_material_keylight_kl3_candidate_gap/renderer_target_gap_summary.json` (7.86 MB GIF)

## Next

Reject visible/area key-light material candidates for now; move to bounded renderer response controls that do not raise the full water body/background.
