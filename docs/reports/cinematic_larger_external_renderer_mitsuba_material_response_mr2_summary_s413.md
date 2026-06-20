# S413 Mitsuba Material Response MR2 Summary

Generated UTC: `2026-06-20T09:38:00Z`

Public compare URL:
`https://zinc-birth-deleted-wales.trycloudflare.com/index.html`

## Goal

Use the S412 material-response patcher to isolate secondary spray/foam material
attenuation without broad key-light lifting or water-alpha modulation.

## MR2 Settings

- Base export:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Channel mask:
  `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask:
  `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`
- Secondary channels: `spray,foam`
- Secondary reflectance drop: `0.35`
- Secondary opacity drop: `0.20`
- Water alpha drop: `0.0`
- Highlight key light strength: `0.0`
- Key lights inserted: `0`

## Result

MR2 is slightly better than MR1 but still below SS1, so it should not be
promoted.

| Rank | Candidate | Mean Gap MAD | Max Gap MAD | Max Gap |
| ---: | --- | ---: | ---: | ---: |
| 1 | `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| 2 | `S409_SF12_H18` | 18.756908677340533 | 23.687431841563786 | 170 |
| 3 | `SF12_SprayFoam` | 19.120776588220163 | 23.755951646090534 | 170 |
| 4 | `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |
| 5 | `S411_SplitNative` | 19.222873344264404 | 23.988294110082304 | 226 |
| 6 | `S413_MR2_Secondary` | 19.22273654513889 | 23.98916859567901 | 226 |
| 7 | `S412_MR1_Material` | 19.22435016396605 | 23.990219907407408 | 230 |

Visual review matches the metrics. MR2 avoids the broad MR1 lift, but it remains
close to SS1 and does not recover the localized S409/S401 center splash and dark
secondary response.

## Artifacts

- Export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr2_export_s413.md`
- Validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr2_validation_s413.md`
- Render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr2_render_s413.md`
- Target-gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr2_target_gap_s413.md`
- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr2_sweep_summary_s413.md`
- Compare report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr2_compare_s413.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr2_compare_publish_s413.md`

## Validation

- XML export: `ready`, `8` frames, `0` key lights
- XML validation: `ready`, `8` parsed, `0` failures, `0` warnings
- Mitsuba render: `ready`, `8` frames, `0` failures
- Target gap: `ready`, max gap MAD `23.98916859567901`
- Sweep summary: `ready`, ranked below SS1 and S411
- Public compare `index.html`: HTTP `200`
- Public compare `assets/comparison.gif`: HTTP `200`

## Decision

Do not promote MR2. Secondary material attenuation alone is not expressive
enough when applied as a whole-frame per-channel scale.

## Next

S414 should move from whole-frame material scaling to localized response data:
either a native projected AOV/material mask, per-particle/material grouping
derived from the source-response mask, or a renderer-side texture/volume mask
that can affect only the evidence region.
