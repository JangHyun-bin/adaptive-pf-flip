# S377 Mitsuba Projected Secondary Mask Candidates SV1

Generated UTC: `2026-06-20T05:46:56.460681+00:00`
Summary JSON: `build/shots/s377_mitsuba_projected_secondary_mask_candidates_sv1/projected_secondary_mask_candidate_summary.json`
CSV: `build/shots/s377_mitsuba_projected_secondary_mask_candidates_sv1/projected_secondary_mask_candidates.csv`
Gallery: `build/shots/s377_mitsuba_projected_secondary_mask_candidates_sv1/gallery/index.html`
Public quick-tunnel review: `https://resident-adds-associate-isbn.trycloudflare.com/index.html`
Status: `projected_candidate_below_best`

## Checks

- Frames: `8`
- Candidates: `134`
- Projected candidates: `126`
- Best dark-secondary mask: `layer_secondary_source_luma_0_75` F1 `0.6121749824314828`
- Best projected dark-secondary mask: `projected_all_source_luma_0_75` F1 `0.5365515648458251`
- Best highlight mask: `source_highlight_120` F1 `0.8881401617250673`
- Best projected highlight mask: `projected_depth_far_33` F1 `0.08334572432521266`

## Top Projected Dark Secondary Masks

| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `projected_all_source_luma_0_75` | 0.615419 | 0.475602 | 0.536552 | 0.002731 |
| 2 | `projected_all_source_luma_20_75` | 0.615419 | 0.475602 | 0.536552 | 0.002731 |
| 3 | `projected_radius_large_67_source_luma_0_75` | 0.642211 | 0.459974 | 0.536027 | 0.002531 |
| 4 | `projected_radius_large_67_source_luma_20_75` | 0.642211 | 0.459974 | 0.536027 | 0.002531 |
| 5 | `projected_spray_foam_source_luma_0_75` | 0.642211 | 0.459974 | 0.536027 | 0.002531 |
| 6 | `projected_spray_foam_source_luma_20_75` | 0.642211 | 0.459974 | 0.536027 | 0.002531 |
| 7 | `projected_speed_slow_median_source_luma_0_75` | 0.655073 | 0.402307 | 0.498478 | 0.002170 |
| 8 | `projected_speed_slow_median_source_luma_20_75` | 0.655073 | 0.402307 | 0.498478 | 0.002170 |
| 9 | `projected_spray_source_luma_0_75` | 0.654527 | 0.393708 | 0.491669 | 0.002125 |
| 10 | `projected_spray_source_luma_20_75` | 0.654527 | 0.393708 | 0.491669 | 0.002125 |

## Top All Dark Secondary Masks

| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `layer_secondary_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 2 | `layer_secondary_source_luma_20_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 3 | `projected_all_source_luma_0_75` | 0.615419 | 0.475602 | 0.536552 | 0.002731 |
| 4 | `projected_all_source_luma_20_75` | 0.615419 | 0.475602 | 0.536552 | 0.002731 |
| 5 | `projected_radius_large_67_source_luma_0_75` | 0.642211 | 0.459974 | 0.536027 | 0.002531 |
| 6 | `projected_radius_large_67_source_luma_20_75` | 0.642211 | 0.459974 | 0.536027 | 0.002531 |
| 7 | `projected_spray_foam_source_luma_0_75` | 0.642211 | 0.459974 | 0.536027 | 0.002531 |
| 8 | `projected_spray_foam_source_luma_20_75` | 0.642211 | 0.459974 | 0.536027 | 0.002531 |
| 9 | `layer_secondary_source_luma_0_85` | 0.405955 | 0.660616 | 0.502883 | 0.005750 |
| 10 | `projected_speed_slow_median_source_luma_0_75` | 0.655073 | 0.402307 | 0.498478 | 0.002170 |

## Top Projected Highlight Masks

| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `projected_depth_far_33` | 0.052076 | 0.208603 | 0.083346 | 0.024656 |
| 2 | `projected_spray_depth_far_50` | 0.050974 | 0.205900 | 0.081718 | 0.024863 |
| 3 | `projected_depth_far_50` | 0.041222 | 0.222666 | 0.069566 | 0.033248 |
| 4 | `projected_speed_fast_8` | 0.033482 | 0.204098 | 0.057527 | 0.037520 |
| 5 | `projected_spray` | 0.030490 | 0.219297 | 0.053537 | 0.044271 |
| 6 | `projected_radius_large_67` | 0.025992 | 0.223450 | 0.046568 | 0.052915 |
| 7 | `projected_spray_foam` | 0.025992 | 0.223450 | 0.046568 | 0.052915 |
| 8 | `projected_all` | 0.025719 | 0.238532 | 0.046431 | 0.057087 |

## Sensitivity Sweep

| Setting | Best Projected Dark Mask | Precision | Recall | F1 |
| --- | --- | ---: | ---: | ---: |
| `r050_b24` | `projected_all_source_luma_0_75` | 0.803309 | 0.444005 | 0.571906 |
| `r060_b24` | `projected_all_source_luma_0_75` | 0.776458 | 0.459633 | 0.577442 |
| `r070_b24` | `projected_all_source_luma_0_75` | 0.741707 | 0.471508 | 0.576519 |
| `r075_b24` | `projected_all_source_luma_0_75` | 0.720611 | 0.473145 | 0.571228 |
| `r100_b00` | `projected_all_source_luma_0_85` | 0.626418 | 0.384495 | 0.476509 |
| `r125_b24` | `projected_radius_large_67_source_luma_0_75` | 0.574109 | 0.463659 | 0.513006 |

Best sensitivity setting remains below `layer_secondary_source_luma_0_75`
at F1 `0.612175`, so projected sidecar masks are not promoted to a response
candidate.

## Next

Projected sidecar masks do not replace DS6 unless they exceed the selective layer/source-luma baseline; if below, move to local density/normal evidence.
