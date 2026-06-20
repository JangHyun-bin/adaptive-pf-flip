# S459 Mitsuba Material Tone Hybrid Sweep

Generated UTC: `2026-06-20T14:59:02.861787+00:00`
Summary JSON: `build/shots/s459_mitsuba_material_tone_hybrid_sweep/material_tone_hybrid_sweep_summary.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid/mitsuba_export.json`
- Channel mask: `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Variants

| Candidate | Mean Gap MAD | Max Gap MAD | Max Gap | Key Lights | Water Alpha Replacements | Target Gap |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `mt1_soft_key` | 19.138588686342594 | 23.9536021090535 | 177 | 8 | 8 | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt1_soft_key_target_gap/renderer_target_gap_summary.json` |
| `mt2_key_alpha` | 19.139306278935187 | 23.953566100823046 | 177 | 8 | 8 | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt2_key_alpha_target_gap/renderer_target_gap_summary.json` |
| `mt3_secondary_dim` | 19.139694733796297 | 23.95370306069959 | 177 | 8 | 8 | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt3_secondary_dim_target_gap/renderer_target_gap_summary.json` |
| `mt4_balanced` | 19.139489695859055 | 23.95333654835391 | 177 | 8 | 8 | `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt4_balanced_target_gap/renderer_target_gap_summary.json` |

## Decision Gallery

- Summary: `build/shots/s459_mitsuba_material_tone_hybrid_sweep/decision_gallery/gap_summary_gallery.json`
- Report: `docs\reports\cinematic_larger_external_renderer_mitsuba_material_tone_hybrid_sweep_decision_gallery_s459.md`
- Best candidate: `S445_GL3_SurfaceGlint`
- Best max gap MAD: `23.9334458590535`

## Next

Use the decision gallery to decide whether material/tone modulation should replace or supplement the residual-response preset.
