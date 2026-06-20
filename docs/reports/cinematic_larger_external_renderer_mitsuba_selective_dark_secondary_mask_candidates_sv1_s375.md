# S375 Mitsuba Selective Dark Secondary Mask Candidates SV1

Generated UTC: `2026-06-20T05:26:28.519368+00:00`
Summary JSON: `build/shots/s375_mitsuba_selective_dark_secondary_mask_candidates_sv1/region_mask_candidate_summary.json`
CSV: `build/shots/s375_mitsuba_selective_dark_secondary_mask_candidates_sv1/region_mask_candidates.csv`
Gallery: `build/shots/s375_mitsuba_selective_dark_secondary_mask_candidates_sv1/gallery/index.html`
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
| 1 | `secondary_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 2 | `secondary_source_luma_20_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 3 | `secondary_source_luma_40_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 4 | `secondary_source_luma_0_85` | 0.405955 | 0.660616 | 0.502883 | 0.005750 |
| 5 | `secondary_source_luma_0_65` | 0.978509 | 0.304511 | 0.464477 | 0.001100 |
| 6 | `secondary_source_luma_20_105` | 0.086989 | 0.965468 | 0.159599 | 0.039214 |
| 7 | `secondary_source_luma_30_125` | 0.079977 | 1.000000 | 0.148108 | 0.044178 |
| 8 | `secondary_native_weight_32` | 0.078391 | 0.999386 | 0.145379 | 0.045044 |

## Next

Use secondary_source_luma_0_75 as the target-free dark-secondary response mask and compare DS candidates.
