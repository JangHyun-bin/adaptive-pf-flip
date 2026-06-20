# S378 Mitsuba Secondary Layer Density Mask Candidates SV1

Generated UTC: `2026-06-20T06:01:35.596700+00:00`
Summary JSON: `build/shots/s378_mitsuba_secondary_layer_density_mask_candidates_sv1/secondary_layer_density_mask_candidate_summary.json`
CSV: `build/shots/s378_mitsuba_secondary_layer_density_mask_candidates_sv1/secondary_layer_density_mask_candidates.csv`
Gallery: `build/shots/s378_mitsuba_secondary_layer_density_mask_candidates_sv1/gallery/index.html`
Public quick-tunnel review: `https://prove-place-bond-players.trycloudflare.com/index.html`
Status: `density_matches_current_best`

## Checks

- Frames: `8`
- Candidates: `1500`
- Density candidates: `1498`
- Best dark-secondary mask: `alpha_ge_4_source_luma_0_75` F1 `0.6121749824314828`
- Best density dark-secondary mask: `alpha_ge_4_source_luma_0_75` F1 `0.6121749824314828`
- Best highlight mask: `source_highlight_120` F1 `0.8881401617250673`

## Top Density Dark Secondary Masks

| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `alpha_ge_4_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 2 | `alpha_ge_4_source_luma_20_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 3 | `density_b1_ge_4_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 4 | `density_b1_ge_4_source_luma_20_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 5 | `density_b2_ge_4_source_luma_0_75` | 0.789152 | 0.475602 | 0.593510 | 0.002129 |
| 6 | `density_b2_ge_4_source_luma_20_75` | 0.789152 | 0.475602 | 0.593510 | 0.002129 |
| 7 | `density_b2_ge_6_source_luma_0_75` | 0.858222 | 0.449874 | 0.590311 | 0.001852 |
| 8 | `density_b2_ge_6_source_luma_20_75` | 0.858222 | 0.449874 | 0.590311 | 0.001852 |
| 9 | `density_b3_ge_6_source_luma_0_75` | 0.820841 | 0.459633 | 0.589290 | 0.001978 |
| 10 | `density_b3_ge_6_source_luma_20_75` | 0.820841 | 0.459633 | 0.589290 | 0.001978 |
| 11 | `density_b1_ge_2_source_luma_0_75` | 0.726998 | 0.475602 | 0.575024 | 0.002311 |
| 12 | `density_b1_ge_2_source_luma_20_75` | 0.726998 | 0.475602 | 0.575024 | 0.002311 |

## Top All Dark Secondary Masks

| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `alpha_ge_4_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 2 | `alpha_ge_4_source_luma_20_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 3 | `density_b1_ge_4_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 4 | `density_b1_ge_4_source_luma_20_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 5 | `density_b2_ge_4_source_luma_0_75` | 0.789152 | 0.475602 | 0.593510 | 0.002129 |
| 6 | `density_b2_ge_4_source_luma_20_75` | 0.789152 | 0.475602 | 0.593510 | 0.002129 |
| 7 | `density_b2_ge_6_source_luma_0_75` | 0.858222 | 0.449874 | 0.590311 | 0.001852 |
| 8 | `density_b2_ge_6_source_luma_20_75` | 0.858222 | 0.449874 | 0.590311 | 0.001852 |
| 9 | `density_b3_ge_6_source_luma_0_75` | 0.820841 | 0.459633 | 0.589290 | 0.001978 |
| 10 | `density_b3_ge_6_source_luma_20_75` | 0.820841 | 0.459633 | 0.589290 | 0.001978 |
| 11 | `density_b1_ge_2_source_luma_0_75` | 0.726998 | 0.475602 | 0.575024 | 0.002311 |
| 12 | `density_b1_ge_2_source_luma_20_75` | 0.726998 | 0.475602 | 0.575024 | 0.002311 |

## Next

Density masks match or fall below the DS6 evidence mask; move to surface-normal or water-contact evidence instead of wider layer-density gates.
