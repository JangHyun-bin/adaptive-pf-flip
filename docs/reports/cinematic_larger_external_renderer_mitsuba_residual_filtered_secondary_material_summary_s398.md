# S398 Mitsuba Residual-Filtered Secondary Material Summary

Generated UTC: `2026-06-20`

## Inputs

- Source sidecar: `build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d_sidecar.json`
- Residual mask source: `build/shots/s397_mitsuba_residual_mask_source_best/residual_mask_source_summary.json`
- Filtered sidecar: `build/shots/s398_mitsuba_residual_filtered_sidecar/secondary_3d_sidecar.json`
- Base adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`

## Reports

- Filter report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_filtered_sidecar_s398.md`
- Validation report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_filtered_sidecar_validation_s398.md`
- Export report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_filtered_secondary_material_export_s398.md`
- Render report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_filtered_secondary_material_render_s398.md`
- Target-gap report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_filtered_secondary_material_target_gap_s398.md`
- C1E-gap report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_filtered_secondary_material_c1e_gap_s398.md`

## Candidate

- Filtered particles: `865 / 2877`
- Retention ratio: `0.30066041014946127`
- Filtered channel counts: spray `673`, foam `85`, bubble `107`, droplet `0`
- Rendered frames: `8`
- Render failures: `0`

## Metrics

| Candidate | Mean Target MAD | Max Target MAD | Max Diff |
| --- | ---: | ---: | ---: |
| SS1 baseline | 19.146412 | 23.951853 | 170 |
| S398 filtered sidecar | 19.222542 | 23.988988 | 226 |

Against the S350 C1E bridge, S398 reached mean candidate-vs-bridge MAD
`13.724573206018519` and max candidate-vs-bridge MAD `22.189152520576133`.

## Decision

The sidecar filter works, but filtered-only replacement is too destructive. The
next native renderer test should preserve the full SS1 sidecar and use the
filtered residual set as an additive or boosted local pass.
