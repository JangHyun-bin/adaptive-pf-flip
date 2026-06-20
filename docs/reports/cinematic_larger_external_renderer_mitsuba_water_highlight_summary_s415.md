# S415 Mitsuba Water Highlight Summary

Generated UTC: `2026-06-20T10:01:00Z`

Public compare URL:
`https://logical-mambo-metro-mountain.trycloudflare.com/index.html`

## Goal

Reuse the S410 highlight mask in a renderer-side, world-space way by adding
small Mitsuba area emitters on water mesh vertices whose projections hit the
highlight evidence region.

## Code Change

Added:

- `tools/add_mitsuba_water_mask_highlights.py`

The tool reads a ready `lsfs_mitsuba_xml_export`, a source-response mask
summary, and each frame's water OBJ mesh. It projects water vertices through the
frame camera, selects vertices under the highlight mask and source-luma gate,
and inserts small sphere area emitters at those water-surface positions.

This is not a camera-plane screen card. The emitters are placed in world space
on the water surface.

## Candidates

| Candidate | Emitters | Source Luma Gate | Radius | Radiance | Max Gap MAD |
| --- | ---: | --- | ---: | --- | ---: |
| `WH1` | 150 | `120..255` | 0.035 | `0.35,0.45,0.60` | 23.987836934156377 |
| `WH2` | 230 | `120..255` | 0.050 | `0.65,0.85,1.05` | 23.987466563786008 |
| `WH3` | 98 | `145..255` | 0.045 | `0.75,0.90,1.10` | 23.987263374485597 |
| `WH4` | 145 | `145..255` | 0.065 | `1.20,1.45,1.75` | 23.98679526748971 |
| `WH5` | 6 | `155..255` | 0.075 | `1.60,1.85,2.15` | 23.98888374485597 |

## Result

WH4 is the best native water-highlight direction so far, but it should not be
promoted over SS1 yet.

| Rank | Candidate | Mean Gap MAD | Max Gap MAD | Max Gap |
| ---: | --- | ---: | ---: | ---: |
| 1 | `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| 2 | `S409_SF12_H18` | 18.756908677340533 | 23.687431841563786 | 170 |
| 3 | `SF12_SprayFoam` | 19.120776588220163 | 23.755951646090534 | 170 |
| 4 | `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |
| 5 | `S415_WH4` | 19.225447048611112 | 23.98679526748971 | 234 |
| 6 | `S415_WH3` | 19.220799012988685 | 23.987263374485597 | 226 |
| 7 | `S415_WH2` | 19.21965888631687 | 23.987466563786008 | 226 |
| 8 | `S415_WH1` | 19.221269450874484 | 23.987836934156377 | 226 |

Visual review shows WH4 does add renderer-native water-surface highlight energy,
but it appears as speckled emitter points rather than the broader connected
highlight band visible in S409/S401.

## Artifacts

- WH1 export/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh1_export_s415.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh1_render_s415.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh1_target_gap_s415.md`
- WH2 export/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh2_export_s415.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh2_render_s415.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh2_target_gap_s415.md`
- WH3 export/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh3_export_s415.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh3_render_s415.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh3_target_gap_s415.md`
- WH4 export/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh4_export_s415.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh4_render_s415.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh4_target_gap_s415.md`
- WH5 export/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh5_export_s415.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh5_render_s415.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_wh5_target_gap_s415.md`
- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_sweep_summary_s415.md`
- Compare report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_compare_s415.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_compare_publish_s415.md`

## Validation

- `python -m py_compile tools\add_mitsuba_water_mask_highlights.py`
- WH1/WH2/WH3/WH4/WH5 XML validation: each `ready`, `8` parsed, `0` failures, `0` warnings
- WH1/WH2/WH3/WH4/WH5 Mitsuba render: each `ready`, `8` frames, `0` failures
- WH1/WH2/WH3/WH4/WH5 target gap: each `ready`
- Sweep summary: `ready`
- Public compare `index.html`: HTTP `200`
- Public compare `assets/comparison.gif`: HTTP `200`

## Decision

Keep WH4 as the best native water-highlight probe so far, but do not promote it
as the final renderer-native replacement. It improves the failed native family
but remains below SS1 and far below S409/S401.

## Next

S416 should turn the point-emitter result into an area response: a renderer-side
texture/volume mask, clustered water patch emission, or a combined pass with the
accepted SF12 dark attenuation.
