# Cinematic Warm Cache Command Summary

Generated UTC: `2026-06-18T20:58:15Z`
Source summary: `build/shots/s125_contact_volume_integrated/shot_summary.json`

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
| `export_render_cache` | 0 | `true` | 0.00ms | `build/shots/s125_contact_volume_integrated/logs/01_export_render_cache.stdout.log` |
| `validate_render_cache` | 0 | `true` | 1.54s | `build/shots/s125_contact_volume_integrated/logs/02_validate_render_cache.stdout.log` |
| `reconstruct_water` | 0 | `true` | 1.53s | `build/shots/s125_contact_volume_integrated/logs/03_reconstruct_water.stdout.log` |
| `convert_render_cache` | 0 | `true` | 1.59s | `build/shots/s125_contact_volume_integrated/logs/04_convert_render_cache.stdout.log` |
| `render_blender` | 0 | `true` | 0.00ms | `build/shots/s125_contact_volume_integrated/logs/05_render_blender.stdout.log` |
| `assemble_gif` | 0 | `true` | 0.00ms | `build/shots/s125_contact_volume_integrated/logs/06_assemble_gif.stdout.log` |

## Totals

- Total command time: `4.66s`
- Reused command time: `4.66s`

## Next

S126 should add a scene/background/camera composition pass that reduces the remaining boxed/tank read without relaxing the current gates.
