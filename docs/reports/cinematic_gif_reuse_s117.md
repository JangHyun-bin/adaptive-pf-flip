# Cinematic Warm Cache Command Summary

Generated UTC: `2026-06-18T18:37:50Z`
Source summary: `build/shots/s117_gif_reuse_probe/shot_summary.json`

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
| `export_render_cache` | 0 | `true` | 0.00ms | `build/shots/s117_gif_reuse_probe/logs/01_export_render_cache.stdout.log` |
| `validate_render_cache` | 0 | `true` | 457.05ms | `build/shots/s117_gif_reuse_probe/logs/02_validate_render_cache.stdout.log` |
| `reconstruct_water` | 0 | `true` | 450.74ms | `build/shots/s117_gif_reuse_probe/logs/03_reconstruct_water.stdout.log` |
| `convert_render_cache` | 0 | `true` | 530.36ms | `build/shots/s117_gif_reuse_probe/logs/04_convert_render_cache.stdout.log` |
| `render_preview` | 0 | `true` | 0.00ms | `build/shots/s117_gif_reuse_probe/logs/05_render_preview.stdout.log` |
| `assemble_gif` | 0 | `true` | 0.00ms | `build/shots/s117_gif_reuse_probe/logs/06_assemble_gif.stdout.log` |

## Totals

- Total command time: `1.44s`
- Reused command time: `1.44s`

## Next

S118 should return to Blender render-quality work with the full warm-cache path enabled.
