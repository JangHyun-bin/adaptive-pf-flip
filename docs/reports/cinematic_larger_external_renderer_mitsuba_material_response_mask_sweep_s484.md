# S484 Mitsuba Material Response Mask Sweep

Generated UTC: `2026-06-20T17:09:38.654465+00:00`
Summary JSON: `build/shots/s484_mitsuba_material_response_mask_sweep/material_response_mask_sweep_summary.json`
Status: `ready`

## Variants

| Candidate | Mask Max Cov | Response Faces | Mean Gap MAD | Max Gap MAD | Max Gap | Target Gap |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `mrms1_tiny_neutral` | 0.02953703703703704 | 480 | 19.291198559670782 | 23.98206790123457 | 251 | `build/shots/s484_mitsuba_material_response_mask_sweep/mrms1_tiny_neutral/target_gap/renderer_target_gap_summary.json` |
| `mrms2_core_soft` | 0.032137345679012344 | 720 | 19.30777504501029 | 23.98206790123457 | 246 | `build/shots/s484_mitsuba_material_response_mask_sweep/mrms2_core_soft/target_gap/renderer_target_gap_summary.json` |
| `mrms3_narrow_bins` | 0.03297453703703704 | 900 | 19.329058802726337 | 23.98206790123457 | 248 | `build/shots/s484_mitsuba_material_response_mask_sweep/mrms3_narrow_bins/target_gap/renderer_target_gap_summary.json` |
| `mrms4_minimal_clear` | 0.02742283950617284 | 320 | 19.271615949717077 | 23.98206790123457 | 250 | `build/shots/s484_mitsuba_material_response_mask_sweep/mrms4_minimal_clear/target_gap/renderer_target_gap_summary.json` |

## Summaries

- Gap gallery: `build/shots/s484_mitsuba_material_response_mask_sweep/gap_gallery/gap_summary_gallery.json`
- Gap gallery report: `docs\reports\cinematic_larger_external_renderer_mitsuba_material_response_mask_sweep_gap_gallery_s484.md`
- Gap gallery best: `S478_p4_proxy`
- Calibration summary: `build/shots/s484_mitsuba_material_response_mask_sweep/response_calibration/response_calibration_summary.json`
- Calibration report: `docs\reports\cinematic_larger_external_renderer_mitsuba_material_response_mask_sweep_calibration_s484.md`
- Calibration best max-gap: `S478_p4_proxy`

## Next

Use the best candidate to decide whether native material masks stay active or the path returns to light-only controls.
