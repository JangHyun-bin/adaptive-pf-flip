# S399 Mitsuba Residual-Augmented Secondary Material RA1 Summary

Generated UTC: `2026-06-20`

## Inputs

- Source sidecar: `build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d_sidecar.json`
- Residual mask source: `build/shots/s397_mitsuba_residual_mask_source_best/residual_mask_source_summary.json`
- RA1 sidecar: `build/shots/s399_mitsuba_residual_augmented_sidecar_ra1/secondary_3d_sidecar.json`
- Base adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`

## Reports

- Sidecar report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_augmented_sidecar_ra1_s399.md`
- Validation report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_augmented_sidecar_ra1_validation_s399.md`
- Export report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_augmented_secondary_material_ra1_export_s399.md`
- Render report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_augmented_secondary_material_ra1_render_s399.md`
- Target-gap report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_augmented_secondary_material_ra1_target_gap_s399.md`
- C1E-gap report: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_augmented_secondary_material_ra1_c1e_gap_s399.md`

## Candidate

- Mode: `augment`
- Selected residual particles: `865 / 2877`
- Output particles: `3742`
- Duplicate count: `1`
- Duplicate radius scale: `1.7`
- Rendered frames: `8`
- Render failures: `0`

## Metrics

| Candidate | Mean Target MAD | Max Target MAD | Max Diff |
| --- | ---: | ---: | ---: |
| SS1 baseline | 19.146412 | 23.951853 | 170 |
| S399 RA1 residual augment | 19.223066 | 23.989043 | 226 |

Against the S350 C1E bridge, RA1 reached mean candidate-vs-bridge MAD
`13.72472455311214` and max candidate-vs-bridge MAD `22.18906121399177`.

## Decision

The augment plumbing is valid, but simple residual particle boost is not the
CR21 replacement. The next renderer work should move away from sidecar
quantity/radius controls and toward material, lighting, and water-surface
transport gates.
