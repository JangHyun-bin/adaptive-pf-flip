# Cinematic Warm Cache Command Summary

Generated UTC: `2026-06-18T19:15:09Z`
Source summary: `build/shots/s119_blender_quality_baseline_comparison/shot_summary.json`

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
| `export_render_cache` | 0 | `true` | 0.00ms | `build/shots/s119_blender_quality_baseline_comparison/logs/01_export_render_cache.stdout.log` |
| `validate_render_cache` | 0 | `true` | 1.50s | `build/shots/s119_blender_quality_baseline_comparison/logs/02_validate_render_cache.stdout.log` |
| `reconstruct_water` | 0 | `true` | 1.51s | `build/shots/s119_blender_quality_baseline_comparison/logs/03_reconstruct_water.stdout.log` |
| `convert_render_cache` | 0 | `true` | 1.58s | `build/shots/s119_blender_quality_baseline_comparison/logs/04_convert_render_cache.stdout.log` |
| `render_blender` | 0 | `true` | 0.00ms | `build/shots/s119_blender_quality_baseline_comparison/logs/05_render_blender.stdout.log` |
| `assemble_gif` | 0 | `true` | 0.00ms | `build/shots/s119_blender_quality_baseline_comparison/logs/06_assemble_gif.stdout.log` |

## Totals

- Total command time: `4.59s`
- Reused command time: `4.59s`

## Next

S120 should package the current Blender comparison artifacts for quick visual inspection and sharing.
