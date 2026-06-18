# Cinematic Warm Cache Command Summary

Generated UTC: `2026-06-18T21:53:23Z`
Source summary: `build/shots/s127_nonboxed_falling_water/shot_summary.json`

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
| `export_render_cache` | 0 | `true` | 0.00ms | `build/shots/s127_nonboxed_falling_water/logs/01_export_render_cache.stdout.log` |
| `validate_render_cache` | 0 | `true` | 1.51s | `build/shots/s127_nonboxed_falling_water/logs/02_validate_render_cache.stdout.log` |
| `reconstruct_water` | 0 | `true` | 1.50s | `build/shots/s127_nonboxed_falling_water/logs/03_reconstruct_water.stdout.log` |
| `convert_render_cache` | 0 | `true` | 1.54s | `build/shots/s127_nonboxed_falling_water/logs/04_convert_render_cache.stdout.log` |
| `render_blender` | 0 | `true` | 0.00ms | `build/shots/s127_nonboxed_falling_water/logs/05_render_blender.stdout.log` |
| `assemble_gif` | 0 | `true` | 0.00ms | `build/shots/s127_nonboxed_falling_water/logs/06_assemble_gif.stdout.log` |

## Totals

- Total command time: `4.56s`
- Reused command time: `4.56s`

## Next

S128 should package and publish the S127 gallery so the current non-boxed scene can be reviewed externally.
