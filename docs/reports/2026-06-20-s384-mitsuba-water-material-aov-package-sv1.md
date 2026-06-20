# S384 Mitsuba Water Material AOV Package SV1

Generated UTC: `2026-06-20T06:45:27.882234+00:00`
Summary JSON: `build/shots/s384_mitsuba_water_material_aov_package_sv1/water_material_aov_summary.json`
CSV: `build/shots/s384_mitsuba_water_material_aov_package_sv1/water_material_aov_candidates.csv`
Gallery: `build/shots/s384_mitsuba_water_material_aov_package_sv1/gallery/index.html`
Status: `baseline_still_best`

## Checks

- Frames: `8`
- AOVs per frame: `14`
- Candidate masks: `33`
- Best target-dark-secondary candidate: `ds6_secondary_source_luma_0_75` F1 `0.6121749824314828`
- GIF bytes: `8.26 MB`

## AOVs

- `Target`
- `Actual`
- `Layer Alpha`
- `Source Luma`
- `Water Mask`
- `Depth Near`
- `Facing`
- `Flatness`
- `Silhouette Edge`
- `Thickness Proxy`
- `Absorption Proxy`
- `DS6 Mask`
- `Target Dark`
- `Overlay`

## Top Target-Dark Secondary Candidates

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `ds6_secondary_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 2 | `water_secondary_source_luma_0_75` | 0.858780 | 0.475602 | 0.612175 | 0.001957 |
| 3 | `water_facing_ge_160_secondary_source_luma_0_95` | 0.122242 | 0.763530 | 0.210744 | 0.022069 |
| 4 | `water_facing_ge_128_secondary_source_luma_0_95` | 0.117812 | 0.830478 | 0.206350 | 0.024906 |
| 5 | `water_facing_ge_96_secondary_source_luma_0_95` | 0.113872 | 0.858323 | 0.201068 | 0.026632 |
| 6 | `water_depth_near_ge_128_secondary_source_luma_0_95` | 0.111348 | 0.871835 | 0.197476 | 0.027664 |
| 7 | `water_absorption_ge_160_secondary_source_luma_0_95` | 0.111449 | 0.858800 | 0.197294 | 0.027226 |
| 8 | `water_depth_near_ge_160_secondary_source_luma_0_95` | 0.111574 | 0.848222 | 0.197207 | 0.026861 |

## Frame Samples

| Output | Grid |
| ---: | --- |
| 0 | `build/shots/s384_mitsuba_water_material_aov_package_sv1/grids/frame_0000_water_material_aov.png` |
| 7 | `build/shots/s384_mitsuba_water_material_aov_package_sv1/grids/frame_0001_water_material_aov.png` |
| 13 | `build/shots/s384_mitsuba_water_material_aov_package_sv1/grids/frame_0002_water_material_aov.png` |
| 20 | `build/shots/s384_mitsuba_water_material_aov_package_sv1/grids/frame_0003_water_material_aov.png` |
| 27 | `build/shots/s384_mitsuba_water_material_aov_package_sv1/grids/frame_0004_water_material_aov.png` |
| 34 | `build/shots/s384_mitsuba_water_material_aov_package_sv1/grids/frame_0005_water_material_aov.png` |
| 40 | `build/shots/s384_mitsuba_water_material_aov_package_sv1/grids/frame_0006_water_material_aov.png` |
| 47 | `build/shots/s384_mitsuba_water_material_aov_package_sv1/grids/frame_0007_water_material_aov.png` |

## Next

Use these material AOVs as renderer-side evidence; promote only if they explain target-dark secondary misses better than DS6 without broad screen-space over-darkening.
