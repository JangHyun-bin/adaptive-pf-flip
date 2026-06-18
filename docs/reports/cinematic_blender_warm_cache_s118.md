# Cinematic Warm Cache Command Summary

Generated UTC: `2026-06-18T18:59:50Z`
Source summary: `build/shots/s118_blender_quality_warm_cache_return/shot_summary.json`

## Reuse Flags

- Export cache reused: `True`
- Validation reused: `True`
- Water reconstruction reused: `True`
- Converted sequence reused: `True`
- Render frames reused: `True`
- GIF reused: `True`

## Command Timings

| Stage | Exit | Reused | Elapsed | Stdout log |
| --- | ---: | --- | ---: | --- |
| `export_render_cache` | 0 | `true` | 0.00ms | `build/shots/s118_blender_quality_warm_cache_return/logs/01_export_render_cache.stdout.log` |
| `validate_render_cache` | 0 | `true` | 1.52s | `build/shots/s118_blender_quality_warm_cache_return/logs/02_validate_render_cache.stdout.log` |
| `reconstruct_water` | 0 | `true` | 1.51s | `build/shots/s118_blender_quality_warm_cache_return/logs/03_reconstruct_water.stdout.log` |
| `convert_render_cache` | 0 | `true` | 1.60s | `build/shots/s118_blender_quality_warm_cache_return/logs/04_convert_render_cache.stdout.log` |
| `render_blender` | 0 | `true` | 0.00ms | `build/shots/s118_blender_quality_warm_cache_return/logs/05_render_blender.stdout.log` |
| `assemble_gif` | 0 | `true` | 0.00ms | `build/shots/s118_blender_quality_warm_cache_return/logs/06_assemble_gif.stdout.log` |

## Totals

- Total command time: `4.64s`
- Reused command time: `4.64s`

## Next

S119 should add a side-by-side Blender quality comparison against the previous large-grid baseline.
