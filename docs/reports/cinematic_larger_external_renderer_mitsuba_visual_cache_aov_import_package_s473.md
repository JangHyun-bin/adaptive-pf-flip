# S473 Mitsuba Visual Cache AOV Import Package

Generated UTC: `2026-06-20T16:08:59.060109+00:00`
Summary JSON: `build/shots/s473_mitsuba_visual_cache_aov_import_package/visual_cache_aov_summary.json`
CSV: `build/shots/s473_mitsuba_visual_cache_aov_import_package/visual_cache_aov_stats.csv`
Gallery: `build/shots/s473_mitsuba_visual_cache_aov_import_package/gallery/index.html`
Status: `ready`

## Checks

- Frames: `8`
- AOVs per frame: `12`
- Max response mask coverage: `0.019110725308641975`
- Max response alpha: `255`
- Max response luma: `29`
- Max source target-gap MAD: `23.950307355967077`
- AOV bytes: `18.32 MB`
- GIF bytes: `10.12 MB`

## AOVs

- `base_rgb`
- `target_rgb`
- `composite_rgb`
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
| 0 | 0 | 0.0015567129629629629 | 240 | `build/shots/s473_mitsuba_visual_cache_aov_import_package/grids/frame_0000_visual_cache_aov.png` |
| 4 | 27 | 0.0008545524691358024 | 170 | `build/shots/s473_mitsuba_visual_cache_aov_import_package/grids/frame_0004_visual_cache_aov.png` |
| 7 | 47 | 0.019110725308641975 | 255 | `build/shots/s473_mitsuba_visual_cache_aov_import_package/grids/frame_0007_visual_cache_aov.png` |

## Next

Consume this package through the AOV importer and compare it against the target preview before promoting it as the renderer/import bridge.
