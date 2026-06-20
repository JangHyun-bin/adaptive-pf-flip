# S482 Mitsuba Response Control Material Contract Decision

Generated UTC: `2026-06-20T16:50:38+00:00`

## Decision

Keep the material-response contract consumer as a validated native path, but do not promote either S482 material candidate over S481 light-only or the S478 `p4_soft_wide` proxy gate.

The diffuse mesh candidate is rejected because it creates visible dark response bands where the projected material mesh overlaps the water surface. The roughdielectric/no-emission candidate is safe enough to keep as the default, but its improvement is too small and it still does not recover the promoted proxy response.

## Inputs

- Material contract: `build/shots/s479_mitsuba_response_control_handoff/material_response_contract.json`
- Light baseline export: `build/shots/s480_mitsuba_response_control_light_full/mitsuba_export.json`
- S481 light-only gap: `build/shots/s481_mitsuba_response_control_light_full_target_gap/renderer_target_gap_summary.json`
- S478 proxy gate: `build/shots/s478_mitsuba_response_control_proxy_sweep/p4_soft_wide_target_gap/renderer_target_gap_summary.json`

## Candidate Results

| Candidate | Mean MAD | Max MAD | Max Gap | Decision |
| --- | ---: | ---: | ---: | --- |
| S478 `p4_soft_wide` proxy | `19.079715470679012` | `23.9488554526749` | `176` | current proxy gate |
| S481 native light-only | `19.215028131430042` | `23.98206790123457` | `219` | current native baseline |
| S482 diffuse material mesh | `20.13989519032922` | `24.73926568930041` | `253` | reject: dark overlap artifacts |
| S482 roughdielectric material mesh | `19.187556423611113` | `23.98206790123457` | `227` | safe default, not promoted |

## Evidence

- S482 diffuse export: `build/shots/s482_mitsuba_response_control_material_contract/mitsuba_export.json`
- S482 diffuse target-gap: `build/shots/s482_mitsuba_response_control_material_contract_target_gap/renderer_target_gap_summary.json`
- S482 RD export: `build/shots/s482_mitsuba_response_control_material_contract_rd/mitsuba_export.json`
- S482 RD target-gap: `build/shots/s482_mitsuba_response_control_material_contract_rd_target_gap/renderer_target_gap_summary.json`
- S482 RD gallery: `build/shots/s482_mitsuba_response_control_material_contract_rd_target_gap/gallery/index.html`

## Interpretation

The current material contract carries useful screen-space intent, but duplicate mesh material overlays are the wrong native representation for that intent. Diffuse overlays occlude the underlying water response, and roughdielectric overlays are too indirect.

The next native step should convert the material contract into a projected mask/texture or calibrated water-BSDF modulation instead of adding more duplicate surface geometry.

## Next

Implement a projected material-response mask/texture path from `lsfs_mitsuba_material_response_contract`, then compare it against S481 light-only and the S478 `p4_soft_wide` proxy gate.
