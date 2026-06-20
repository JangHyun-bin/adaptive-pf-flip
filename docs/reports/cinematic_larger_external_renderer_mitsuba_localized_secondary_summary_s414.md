# S414 Mitsuba Localized Secondary Response Summary

Generated UTC: `2026-06-20T09:52:00Z`

Public compare URL:
`https://italia-mart-wallet-sides.trycloudflare.com/index.html`

## Goal

Move beyond S413 whole-frame secondary material scaling by changing only the
secondary Mitsuba shapes whose projected screen positions hit a response mask.

## Code Change

Added:

- `tools/localize_mitsuba_secondary_material_response.py`

The tool reads a ready `lsfs_mitsuba_xml_export` and a source-response mask
summary. It projects existing secondary `sphere` and `disk` shapes through the
frame camera, samples the mask, and rewrites only matching shapes to duplicated
`*_localized` BSDFs with separate reflectance/opacity scaling.

The tool also supports a source-luma gate so the response can be narrowed beyond
the raw projected spray/foam mask.

## Candidates

| Candidate | Source Luma Gate | Localized Shapes | Reflectance Scale | Opacity Scale | Max Gap MAD |
| --- | --- | ---: | ---: | ---: | ---: |
| `LR1_Wide` | `0..255` | 5200 | 0.45 | 0.70 | 23.98917309670782 |
| `LR3_Luma95` | `0..95` | 980 | 0.45 | 0.70 | 23.989165380658438 |
| `LR4_Luma85` | `0..85` | 202 | 0.40 | 0.65 | 23.989165380658438 |

`LR3_Luma95` proves the source-luma gate works: it rejects `4220` of `5200`
projected spray/foam shapes and localizes only `980` shapes.

## Result

The localized path works technically, but none of the localized secondary
attenuation candidates should be promoted.

| Rank | Candidate | Mean Gap MAD | Max Gap MAD | Max Gap |
| ---: | --- | ---: | ---: | ---: |
| 1 | `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| 2 | `S409_SF12_H18` | 18.756908677340533 | 23.687431841563786 | 170 |
| 3 | `SF12_SprayFoam` | 19.120776588220163 | 23.755951646090534 | 170 |
| 4 | `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |
| 5 | `S411_SplitNative` | 19.222873344264404 | 23.988294110082304 | 226 |
| 6 | `S414_LR4_Luma85` | 19.222742091049383 | 23.989165380658438 | 226 |
| 7 | `S414_LR3_Luma95` | 19.22274241255144 | 23.989165380658438 | 226 |
| 8 | `S413_MR2_Secondary` | 19.22273654513889 | 23.98916859567901 | 226 |
| 9 | `S414_LR1_Wide` | 19.222740805041152 | 23.98917309670782 | 226 |

Visual review confirms the metrics. LR3/LR4 are more localized than MR2, but
they still stay visually close to SS1 and do not recover the S409/S401 center
splash highlight or lower dark response.

## Artifacts

- LR1 export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_lr1_export_s414.md`
- LR1 validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_lr1_validation_s414.md`
- LR1 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_lr1_render_s414.md`
- LR1 target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_lr1_target_gap_s414.md`
- LR3 export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_lr3_export_s414.md`
- LR3 validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_lr3_validation_s414.md`
- LR3 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_lr3_render_s414.md`
- LR3 target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_lr3_target_gap_s414.md`
- LR4 export:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_lr4_export_s414.md`
- LR4 validation:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_lr4_validation_s414.md`
- LR4 render:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_lr4_render_s414.md`
- LR4 target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_lr4_target_gap_s414.md`
- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_sweep_summary_s414.md`
- Compare report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_compare_s414.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_compare_publish_s414.md`

## Validation

- `python -m py_compile tools\localize_mitsuba_secondary_material_response.py`
- LR1 XML validation: `ready`, `8` parsed, `0` failures, `0` warnings
- LR3 XML validation: `ready`, `8` parsed, `0` failures, `0` warnings
- LR4 XML validation: `ready`, `8` parsed, `0` failures, `0` warnings
- LR1/LR3/LR4 Mitsuba renders: each `ready`, `8` frames, `0` failures
- LR1/LR3/LR4 target gaps: each `ready`
- Sweep summary: `ready`
- Public compare `index.html`: HTTP `200`
- Public compare `assets/comparison.gif`: HTTP `200`

## Decision

Do not promote localized secondary attenuation. S414 proves that the renderer
can localize BSDF changes per projected shape, but secondary dark attenuation
alone is still not the missing visual response.

## Next

S415 should use the localized infrastructure for a different response class:
localized source-highlight/light response, or an actual renderer-side texture
mask that can modulate the water/volume surface in the S410 evidence regions.
