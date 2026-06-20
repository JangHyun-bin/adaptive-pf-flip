# S386 Mitsuba Secondary Channel Residual Mask Analysis SV1

Generated UTC: `2026-06-20T06:58:33.064011+00:00`
Summary JSON: `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/secondary_channel_residual_mask_summary.json`
CSV: `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/secondary_channel_residual_mask_candidates.csv`
Gallery: `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/gallery/index.html`
Status: `beats_ds6`

## Checks

- Frames: `8`
- Candidate masks: `109`
- DS6 baseline F1: `0.6121749824314828`
- Best target-dark-secondary candidate: `ds6_or_channel_union_r0_source_luma_75_85` F1 `0.6553528823212499`
- GIF bytes: `7.33 MB`

## Top Target-Dark Secondary Candidates

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `ds6_or_channel_union_r0_source_luma_75_85` | 0.751346 | 0.581110 | 0.655353 | 0.002733 |
| 2 | `channel_union_r12_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 3 | `channel_union_r16_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 4 | `channel_union_r24_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 5 | `channel_union_r32_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 6 | `channel_union_r6_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 7 | `channel_union_r8_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 8 | `ds6_secondary_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 9 | `channel_union_r4_source_luma_0_75` | 0.859277 | 0.475056 | 0.611848 | 0.001953 |
| 10 | `channel_union_r2_source_luma_0_75` | 0.882111 | 0.424350 | 0.573035 | 0.001700 |
| 11 | `ds6_or_channel_union_r2_source_luma_75_85` | 0.491559 | 0.635911 | 0.554494 | 0.004571 |
| 12 | `channel_union_r2_source_luma_0_85` | 0.478871 | 0.584658 | 0.526503 | 0.004314 |

## Frame Samples

| Output | Grid |
| ---: | --- |
| 0 | `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/grids/frame_0000_secondary_channel_residual_mask.png` |
| 7 | `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/grids/frame_0001_secondary_channel_residual_mask.png` |
| 13 | `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/grids/frame_0002_secondary_channel_residual_mask.png` |
| 20 | `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/grids/frame_0003_secondary_channel_residual_mask.png` |
| 27 | `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/grids/frame_0004_secondary_channel_residual_mask.png` |
| 34 | `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/grids/frame_0005_secondary_channel_residual_mask.png` |
| 40 | `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/grids/frame_0006_secondary_channel_residual_mask.png` |
| 47 | `build/shots/s386_mitsuba_secondary_channel_residual_masks_sv1/grids/frame_0007_secondary_channel_residual_mask.png` |

## Next

Promote the best target-free channel residual mask into a bounded visual response and compare target gap against DS6.
