# Cinematic Warm Cache Command Summary

Generated UTC: `2026-06-18T17:58:37Z`
Source summary: `build/s112_export_reuse_probe/shot_summary.json`

## Reuse Flags

- Export cache reused: `True`
- Validation reused: `True`
- Water reconstruction reused: `True`
- Converted sequence reused: `True`

## Command Timings

| Stage | Exit | Reused | Elapsed | Stdout log |
| --- | ---: | --- | ---: | --- |
| `export_render_cache` | 0 | `true` | 0.00ms | `build/s112_export_reuse_probe/logs/01_export_render_cache.stdout.log` |
| `validate_render_cache` | 0 | `true` | 152.94ms | `build/s112_export_reuse_probe/logs/02_validate_render_cache.stdout.log` |
| `reconstruct_water` | 0 | `true` | 233.27ms | `build/s112_export_reuse_probe/logs/03_reconstruct_water.stdout.log` |
| `convert_render_cache` | 0 | `true` | 150.54ms | `build/s112_export_reuse_probe/logs/04_convert_render_cache.stdout.log` |
| `render_preview` | 0 | `false` | 380.92ms | `build/s112_export_reuse_probe/logs/05_render_preview.stdout.log` |
| `assemble_gif` | 0 | `false` | 251.23ms | `build/s112_export_reuse_probe/logs/06_assemble_gif.stdout.log` |

## Totals

- Total command time: `1.17s`
- Reused command time: `536.75ms`

## Next

S114 should target render-frame reuse because export, validation, reconstruction, and conversion now have opt-in warm-cache paths.
