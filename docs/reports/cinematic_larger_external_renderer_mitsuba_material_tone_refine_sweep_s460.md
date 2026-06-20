# S460 Mitsuba Material Tone Refine Sweep

Generated UTC: `2026-06-20T15:03:02.602180+00:00`
Summary JSON: `build/shots/s460_mitsuba_material_tone_refine_sweep/material_tone_hybrid_sweep_summary.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s457_mitsuba_residual_response_late_frame_sweep/lf47_mid/mitsuba_export.json`
- Channel mask: `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask: `build/shots/s423_mitsuba_s401_cr21_highlight_mask_source/source_response_mask_source_summary.json`

## Variants

| Candidate | Mean Gap MAD | Max Gap MAD | Max Gap | Key Lights | Water Alpha Replacements | Target Gap |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `mt5_trim_alpha` | 19.139307725694444 | 23.95356674382716 | 177 | 8 | 8 | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt5_trim_alpha_target_gap/renderer_target_gap_summary.json` |
| `mt6_trim_key` | 19.139489936985598 | 23.95333654835391 | 177 | 8 | 8 | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt6_trim_key_target_gap/renderer_target_gap_summary.json` |
| `mt7_alpha_high_key_low` | 19.139264805169752 | 23.953463863168725 | 177 | 8 | 8 | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt7_alpha_high_key_low_target_gap/renderer_target_gap_summary.json` |
| `mt8_secondary_light` | 19.139490097736626 | 23.953335905349793 | 177 | 8 | 8 | `build/shots/s460_mitsuba_material_tone_refine_sweep/mt8_secondary_light_target_gap/renderer_target_gap_summary.json` |

## Decision Gallery

- Summary: `build/shots/s460_mitsuba_material_tone_refine_sweep/decision_gallery/gap_summary_gallery.json`
- Report: `docs\reports\cinematic_larger_external_renderer_mitsuba_material_tone_refine_sweep_decision_gallery_s460.md`
- Best candidate: `S445_GL3_SurfaceGlint`
- Best max gap MAD: `23.9334458590535`

## Next

Use this narrow sweep to decide whether mt4_balanced can be improved without raising max absolute gap.
