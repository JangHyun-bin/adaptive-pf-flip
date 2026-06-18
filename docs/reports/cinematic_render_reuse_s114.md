# Cinematic Warm Cache Command Summary

Generated UTC: `2026-06-18T18:03:40Z`
Source summary: `build/s114_render_reuse_probe/shot_summary.json`

## Reuse Flags

- Export cache reused: `True`
- Validation reused: `True`
- Water reconstruction reused: `True`
- Converted sequence reused: `True`
- Render frames reused: `True`

## Command Timings

| Stage | Exit | Reused | Elapsed | Stdout log |
| --- | ---: | --- | ---: | --- |
| `export_render_cache` | 0 | `true` | 0.00ms | `build/s114_render_reuse_probe/logs/01_export_render_cache.stdout.log` |
| `validate_render_cache` | 0 | `true` | 184.02ms | `build/s114_render_reuse_probe/logs/02_validate_render_cache.stdout.log` |
| `reconstruct_water` | 0 | `true` | 260.18ms | `build/s114_render_reuse_probe/logs/03_reconstruct_water.stdout.log` |
| `convert_render_cache` | 0 | `true` | 545.26ms | `build/s114_render_reuse_probe/logs/04_convert_render_cache.stdout.log` |
| `render_preview` | 0 | `true` | 0.00ms | `build/s114_render_reuse_probe/logs/05_render_preview.stdout.log` |
| `assemble_gif` | 0 | `false` | 277.97ms | `build/s114_render_reuse_probe/logs/06_assemble_gif.stdout.log` |

## Totals

- Total command time: `1.27s`
- Reused command time: `989.46ms`

## Next

S115 should run a warm-cache larger-grid preview benchmark to measure the full reuse path before returning to render quality.
