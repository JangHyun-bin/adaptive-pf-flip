# Cinematic Warm Cache Command Summary

Generated UTC: `2026-06-18T20:10:52Z`
Source summary: `build/shots/s124_contact_band_composition/shot_summary.json`

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
| `export_render_cache` | 0 | `true` | 0.00ms | `build/shots/s124_contact_band_composition/logs/01_export_render_cache.stdout.log` |
| `validate_render_cache` | 0 | `true` | 1.50s | `build/shots/s124_contact_band_composition/logs/02_validate_render_cache.stdout.log` |
| `reconstruct_water` | 0 | `true` | 1.48s | `build/shots/s124_contact_band_composition/logs/03_reconstruct_water.stdout.log` |
| `convert_render_cache` | 0 | `true` | 1.57s | `build/shots/s124_contact_band_composition/logs/04_convert_render_cache.stdout.log` |
| `render_blender` | 0 | `true` | 0.00ms | `build/shots/s124_contact_band_composition/logs/05_render_blender.stdout.log` |
| `assemble_gif` | 0 | `true` | 0.00ms | `build/shots/s124_contact_band_composition/logs/06_assemble_gif.stdout.log` |

## Totals

- Total command time: `4.55s`
- Reused command time: `4.55s`

## Next

S125 should add a contact-volume integration preset that softens the remaining boxed/tank read.
