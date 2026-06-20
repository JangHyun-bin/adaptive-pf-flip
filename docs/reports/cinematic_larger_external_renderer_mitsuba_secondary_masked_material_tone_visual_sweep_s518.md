# S518 Mitsuba Secondary Masked Material Tone Visual Sweep

Generated UTC: `2026-06-20T19:46:06.373637+00:00`
Summary JSON: `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/material_tone_hybrid_sweep_summary.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json`
- Channel mask: `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`
- Highlight mask: `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

## Variants

| Candidate | Mean Gap MAD | Max Gap MAD | Max Gap | Key Lights | Water Alpha Replacements | Target Gap |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `mt9_sharp_key` | 74.17916160300926 | 104.49566872427984 | 193 | 8 | 8 | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt9_sharp_key_target_gap/renderer_target_gap_summary.json` |
| `mt10_dim_secondary_strong_key` | 74.17561623906893 | 104.48653549382716 | 195 | 8 | 8 | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt10_dim_secondary_strong_key_target_gap/renderer_target_gap_summary.json` |
| `mt11_soft_water_bright` | 74.18103997878086 | 104.49457304526749 | 194 | 8 | 8 | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt11_soft_water_bright_target_gap/renderer_target_gap_summary.json` |
| `mt12_highlight_cut` | 74.17765817901234 | 104.48696887860082 | 194 | 8 | 8 | `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/mt12_highlight_cut_target_gap/renderer_target_gap_summary.json` |

## Decision Gallery

- Summary: `build/shots/s518_mitsuba_secondary_masked_material_tone_visual_sweep/decision_gallery/gap_summary_gallery.json`
- Report: `docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_masked_material_tone_visual_sweep_decision_gallery_s518.md`
- Best candidate: `S445_GL3_SurfaceGlint`
- Best max gap MAD: `23.9334458590535`

## Next

Pick the best material/tone candidate for a longer S322 secondary masked real Mitsuba render.
