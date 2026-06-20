# S373 Mitsuba Region Mask Candidates SV1

Generated UTC: `2026-06-20T05:08:24.237377+00:00`
Summary JSON: `build/shots/s373_mitsuba_region_mask_candidates_sv1/region_mask_candidate_summary.json`
CSV: `build/shots/s373_mitsuba_region_mask_candidates_sv1/region_mask_candidates.csv`
Gallery: `build/shots/s373_mitsuba_region_mask_candidates_sv1/gallery/index.html`
Public preview: `https://bind-apps-continent-francisco.trycloudflare.com/index.html`
Status: `ready`

## Top Target Highlight Masks

| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `source_highlight_120` | 0.997656 | 0.800290 | 0.888140 | 0.004938 |
| 2 | `source_highlight_135` | 0.999885 | 0.680221 | 0.809643 | 0.004187 |
| 3 | `source_highlight_120_nonsecondary` | 0.997765 | 0.647080 | 0.785039 | 0.003992 |
| 4 | `source_highlight_135_nonsecondary` | 0.999857 | 0.548791 | 0.708635 | 0.003378 |
| 5 | `source_highlight_145` | 1.000000 | 0.421044 | 0.592584 | 0.002592 |
| 6 | `source_highlight_145_nonsecondary` | 1.000000 | 0.345595 | 0.513669 | 0.002127 |
| 7 | `source_highlight_150` | 1.000000 | 0.040545 | 0.077931 | 0.000250 |
| 8 | `secondary_native_weight_32` | 0.023982 | 0.175500 | 0.042198 | 0.045044 |

## Top Target Dark Secondary Masks

| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `secondary_source_luma_20_105` | 0.086989 | 0.965468 | 0.159599 | 0.039214 |
| 2 | `secondary_source_luma_30_125` | 0.079977 | 1.000000 | 0.148108 | 0.044178 |
| 3 | `secondary_native_weight_32` | 0.078391 | 0.999386 | 0.145379 | 0.045044 |
| 4 | `secondary_alpha_4` | 0.078358 | 1.000000 | 0.145328 | 0.045091 |
| 5 | `secondary_native_weight_16` | 0.078358 | 1.000000 | 0.145328 | 0.045091 |
| 6 | `secondary_alpha_16` | 0.080145 | 0.613253 | 0.141763 | 0.027036 |
| 7 | `secondary_source_luma_55_130` | 0.071165 | 0.882208 | 0.131706 | 0.043800 |
| 8 | `secondary_alpha_32` | 0.086488 | 0.180577 | 0.116958 | 0.007377 |

## Next

Use this mask precision/recall diagnosis to choose the next renderer-native response path.
