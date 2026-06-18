# Cinematic Warm Cache Command Summary

Generated UTC: `2026-06-18T18:21:58Z`
Source summary: `build/shots/s115_large_grid_warm_cache_preview/shot_summary.json`

## Reuse Flags

- Export cache reused: `True`
- Validation reused: `True`
- Water reconstruction reused: `True`
- Converted sequence reused: `True`
- Render frames reused: `True`

## Command Timings

| Stage | Exit | Reused | Elapsed | Stdout log |
| --- | ---: | --- | ---: | --- |
| `export_render_cache` | 0 | `true` | 0.00ms | `build/shots/s115_large_grid_warm_cache_preview/logs/01_export_render_cache.stdout.log` |
| `validate_render_cache` | 0 | `true` | 474.34ms | `build/shots/s115_large_grid_warm_cache_preview/logs/02_validate_render_cache.stdout.log` |
| `reconstruct_water` | 0 | `true` | 11.92s | `build/shots/s115_large_grid_warm_cache_preview/logs/03_reconstruct_water.stdout.log` |
| `convert_render_cache` | 0 | `true` | 519.95ms | `build/shots/s115_large_grid_warm_cache_preview/logs/04_convert_render_cache.stdout.log` |
| `render_preview` | 0 | `true` | 0.00ms | `build/shots/s115_large_grid_warm_cache_preview/logs/05_render_preview.stdout.log` |
| `assemble_gif` | 0 | `false` | 690.64ms | `build/shots/s115_large_grid_warm_cache_preview/logs/06_assemble_gif.stdout.log` |

## Totals

- Total command time: `13.60s`
- Reused command time: `12.91s`

## Next

S116 should reduce warm-cache fingerprint overhead, especially water reconstruction asset hashing on larger grids.
