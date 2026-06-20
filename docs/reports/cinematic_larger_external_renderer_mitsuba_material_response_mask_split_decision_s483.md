# S483 Mitsuba Material Response Mask Split Decision

Generated UTC: `2026-06-20T17:00:13+00:00`

## Decision

Keep the S483 projected material-mask and split-water-material path as a valid renderer-native mechanism, but do not promote this setting.

S483 fixes the S482 duplicate-mesh representation problem: the water mesh is split into remainder/response regions rather than overlaying another response surface. It also handles sparse material masks by passing empty frames through as no-op frames. However, the current mask and BSDF setting is too broad and too blue, so it worsens the target gap versus both S481 light-only and the S478 `p4_soft_wide` proxy.

## Inputs

- Material contract: `build/shots/s479_mitsuba_response_control_handoff/material_response_contract.json`
- Mask source: `build/shots/s483_mitsuba_material_response_mask_source/material_response_mask_source_summary.json`
- Split export: `build/shots/s483_mitsuba_material_response_mask_split/mitsuba_export.json`
- Target-gap summary: `build/shots/s483_mitsuba_material_response_mask_split_target_gap/renderer_target_gap_summary.json`

## Candidate Results

| Candidate | Mean MAD | Max MAD | Max Gap | Decision |
| --- | ---: | ---: | ---: | --- |
| S478 `p4_soft_wide` proxy | `19.079715470679012` | `23.9488554526749` | `176` | current proxy gate |
| S481 native light-only | `19.215028131430042` | `23.98206790123457` | `219` | current native baseline |
| S482 RD duplicate mesh | `19.187556423611113` | `23.98206790123457` | `227` | safe but weak |
| S483 projected mask split | `19.45090920781893` | `23.98206790123457` | `249` | reject current setting |

## Mechanism Checks

- Mask source: `8` frames, `2` controls, max coverage `0.05060956790123457`
- Split export: `8` frames, `6` empty mask frames ignored, `1800` response faces
- Validation: `8` XML scenes parsed, `0` failures, `0` warnings
- Render: `8` frames rendered, `0` failures

## Root Cause Notes

- The first S483 split attempt failed at render time because the S480 base already contained S449/S421 split-water material shapes. The original metadata `water_mesh` path no longer matched the active water shape in XML.
- `split_mitsuba_water_mask_material.py` now supports `--use-current-water-shape`, which finds the actual `lsfs_water_surface` shape in the current XML and splits that mesh instead.
- The rerun also uses unique S483 shape/BSDF prefixes to avoid duplicate Mitsuba IDs.

## Next

Tune a narrower material-response mask and a less color-shifting BSDF. The likely next pass should reduce mask coverage, avoid broad blue transmittance shifts, and target only the low-frequency water-body lift that S478 `p4_soft_wide` captured.
