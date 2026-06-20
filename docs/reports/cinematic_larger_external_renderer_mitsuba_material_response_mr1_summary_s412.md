# S412 Mitsuba Material Response MR1 Summary

Generated UTC: `2026-06-20T09:34:00Z`

Public compare URL:
`https://barcelona-prevent-respect-sticker.trycloudflare.com/index.html`

## Goal

Move beyond S411 camera-plane card/sprite inserts by applying S410 response
masks to actual Mitsuba scene data: water material roughness, secondary
spray/foam material response, and a bounded source-response key light.

## Code Change

Added:

- `tools/modulate_mitsuba_material_response.py`

The tool reads a ready `lsfs_mitsuba_xml_export` plus two source-response mask
summaries and emits a new ready Mitsuba XML export. It does not add screen-space
cards or sprites. Instead, it patches each frame's XML with:

- per-frame water `roughdielectric` alpha modulation
- per-frame secondary `spray,foam` reflectance scaling
- per-frame secondary `spray,foam` opacity scaling
- a bounded real Mitsuba area light scaled by highlight-mask coverage

## MR1 Settings

- Base export:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- Channel mask:
  `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask:
  `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`
- Secondary channels: `spray,foam`
- Secondary reflectance drop: `0.45`
- Secondary opacity drop: `0.30`
- Water alpha drop: `0.45`
- Water alpha min: `0.006`
- Highlight key light max radiance: `0.10,0.13,0.17`

## Result

MR1 rendered and validated, but should not be promoted.

| Rank | Candidate | Mean Gap MAD | Max Gap MAD | Max Gap |
| ---: | --- | ---: | ---: | ---: |
| 1 | `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| 2 | `S409_SF12_H18` | 18.756908677340533 | 23.687431841563786 | 170 |
| 3 | `SF12_SprayFoam` | 19.120776588220163 | 23.755951646090534 | 170 |
| 4 | `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |
| 5 | `S411_SplitNative` | 19.222873344264404 | 23.988294110082304 | 226 |
| 6 | `S412_MR1_Material` | 19.22435016396605 | 23.990219907407408 | 230 |

Visual review confirms the numeric result: MR1 stays close to SS1, misses the
S409/S401 center splash response, and the broad key-light/material change does
not recover localized highlights.

## Artifacts

- Export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr1_export_s412.md`
- Validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr1_validation_s412.md`
- Render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr1_render_s412.md`
- Target-gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr1_target_gap_s412.md`
- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr1_sweep_summary_s412.md`
- Compare report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr1_compare_s412.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr1_compare_publish_s412.md`

## Validation

- `python -m py_compile tools\modulate_mitsuba_material_response.py`
- XML export: `ready`, `8` frames
- XML validation: `ready`, `8` parsed, `0` failures, `0` warnings
- Mitsuba render: `ready`, `8` frames, `0` failures
- Target gap: `ready`, max gap MAD `23.990219907407408`
- Sweep summary: `ready`, ranked below SS1 and S411
- Public compare `index.html`: HTTP `200`
- Public compare `assets/comparison.gif`: HTTP `200`

## Decision

Do not promote MR1. Keep `modulate_mitsuba_material_response.py` as the first
export/material response patcher, but avoid broad per-frame key-light lifting as
the next strategy.

## Next

S413/MR2 should use the patcher for a tighter experiment: disable or greatly
reduce global key-light lifting, keep secondary material attenuation localized
to spray/foam evidence, and investigate a true localized material/AOV response
instead of a whole-frame material/light adjustment.
