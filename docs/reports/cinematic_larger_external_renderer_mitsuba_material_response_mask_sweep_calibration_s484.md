# S484 Mitsuba Material Response Mask Calibration

Generated UTC: `2026-06-20T17:09:38.636815+00:00`
Summary JSON: `build/shots/s484_mitsuba_material_response_mask_sweep/response_calibration/response_calibration_summary.json`
CSV: `build/shots/s484_mitsuba_material_response_mask_sweep/response_calibration/response_calibration_candidates.csv`
Status: `ready`

## Ranking

| Rank | Pareto | Candidate | Max Gap MAD | Mean Gap MAD | Max Gap | Patches | Response Faces | Artifact Proxy |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `True` | `S478_p4_proxy` | 23.9488554526749 | 19.079715470679012 | 176 | 0 | 0 | 176 |
| 2 | `False` | `S482_rd_mesh` | 23.98206790123457 | 19.187556423611113 | 227 | 7 | 656 | 249.26 |
| 3 | `False` | `S481_light_only` | 23.98206790123457 | 19.215028131430042 | 219 | 7 | 656 | 241.26 |
| 4 | `False` | `mrms4_minimal_clear` | 23.98206790123457 | 19.271615949717077 | 250 | 7 | 320 | 272.26 |
| 5 | `False` | `mrms1_tiny_neutral` | 23.98206790123457 | 19.291198559670782 | 251 | 7 | 480 | 273.26 |
| 6 | `False` | `mrms2_core_soft` | 23.98206790123457 | 19.30777504501029 | 246 | 7 | 720 | 268.26 |
| 7 | `False` | `mrms3_narrow_bins` | 23.98206790123457 | 19.329058802726337 | 248 | 7 | 900 | 270.26 |
| 8 | `False` | `S483_mask_split` | 23.98206790123457 | 19.45090920781893 | 249 | 7 | 1800 | 271.26 |

## Pareto Front

- `S478_p4_proxy`: max MAD `23.9488554526749`, mean MAD `19.079715470679012`, complexity `0.0`

## Next

Use the Pareto summary to decide whether to narrow the mask further or return to light-only native controls.
