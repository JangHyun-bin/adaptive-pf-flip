# S385 Mitsuba Secondary Channel AOV Package SV1

Generated UTC: `2026-06-20T06:51:01.230615+00:00`
Summary JSON: `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/secondary_channel_aov_summary.json`
CSV: `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/secondary_channel_aov_candidates.csv`
Gallery: `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/gallery/index.html`
Status: `baseline_still_best`

## Checks

- Frames: `8`
- AOVs per frame: `11`
- Candidate masks: `45`
- Best target-dark-secondary candidate: `ds6_secondary_source_luma_0_75` F1 `0.6121749824314828`
- GIF bytes: `7.56 MB`

## AOVs

- `Target`
- `Actual`
- `Layer Alpha`
- `Source Luma`
- `Spray Density`
- `Foam Density`
- `Bubble Density`
- `Union Density`
- `DS6 Mask`
- `Target Dark`
- `Channel Overlay`

## Top Target-Dark Secondary Candidates

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `ds6_secondary_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 2 | `all_secondary_channels_source_luma_0_75` | 0.940143 | 0.215451 | 0.350564 | 0.000810 |
| 3 | `secondary_channel_union_source_luma_0_75` | 0.940143 | 0.215451 | 0.350564 | 0.000810 |
| 4 | `spray_or_foam_source_luma_0_75` | 0.954737 | 0.201529 | 0.332807 | 0.000746 |
| 5 | `spray_source_luma_0_75` | 0.947479 | 0.153893 | 0.264780 | 0.000574 |
| 6 | `foam_density_ge_64_source_luma_0_95` | 0.218909 | 0.276053 | 0.244182 | 0.004456 |
| 7 | `foam_density_ge_96_source_luma_0_95` | 0.282320 | 0.213267 | 0.242983 | 0.002669 |
| 8 | `foam_density_ge_32_source_luma_0_95` | 0.181787 | 0.361701 | 0.241965 | 0.007030 |
| 9 | `spray_or_foam_density_ge_96_source_luma_0_95` | 0.164442 | 0.450624 | 0.240955 | 0.009682 |
| 10 | `spray_or_foam_source_luma_0_95` | 0.172471 | 0.394731 | 0.240055 | 0.008086 |

## Frame Samples

| Output | Grid |
| ---: | --- |
| 0 | `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/grids/frame_0000_secondary_channel_aov.png` |
| 7 | `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/grids/frame_0001_secondary_channel_aov.png` |
| 13 | `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/grids/frame_0002_secondary_channel_aov.png` |
| 20 | `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/grids/frame_0003_secondary_channel_aov.png` |
| 27 | `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/grids/frame_0004_secondary_channel_aov.png` |
| 34 | `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/grids/frame_0005_secondary_channel_aov.png` |
| 40 | `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/grids/frame_0006_secondary_channel_aov.png` |
| 47 | `build/shots/s385_mitsuba_secondary_channel_aov_package_sv1/grids/frame_0007_secondary_channel_aov.png` |

## Next

Use secondary channel AOVs as residual-localization evidence; if they do not beat DS6, move to residual clustering or renderer-side shadow/occlusion cues.
