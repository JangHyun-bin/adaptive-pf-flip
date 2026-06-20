# S472 Mitsuba Visual Cache AOV Package

Generated UTC: `2026-06-20T16:05:15.892658+00:00`
Summary JSON: `build/shots/s472_mitsuba_visual_cache_aov_package/visual_cache_aov_summary.json`
CSV: `build/shots/s472_mitsuba_visual_cache_aov_package/visual_cache_aov_stats.csv`
Gallery: `build/shots/s472_mitsuba_visual_cache_aov_package/gallery/index.html`
Status: `ready`

## Checks

- Frames: `8`
- AOVs per frame: `9`
- Max response mask coverage: `0.019110725308641975`
- Max response alpha: `255`
- Max response luma: `29`
- Max source target-gap MAD: `23.950307355967077`
- AOV bytes: `10.68 MB`
- GIF bytes: `10.12 MB`

## AOVs

- `base_luma`
- `target_luma`
- `composite_luma`
- `response_rgb`
- `response_alpha`
- `response_luma`
- `response_mask`
- `target_gap_diff`
- `response_overlay`

## Frame Samples

| Frame | Output | Coverage | Alpha Max | Grid |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0.0015567129629629629 | 240 | `build/shots/s472_mitsuba_visual_cache_aov_package/grids/frame_0000_visual_cache_aov.png` |
| 4 | 27 | 0.0008545524691358024 | 170 | `build/shots/s472_mitsuba_visual_cache_aov_package/grids/frame_0004_visual_cache_aov.png` |
| 7 | 47 | 0.019110725308641975 | 255 | `build/shots/s472_mitsuba_visual_cache_aov_package/grids/frame_0007_visual_cache_aov.png` |

## Next

Use these signed-response AOVs as the renderer/import contract; next validate a native/import consumer against the S471 composite and target-gap gates.
