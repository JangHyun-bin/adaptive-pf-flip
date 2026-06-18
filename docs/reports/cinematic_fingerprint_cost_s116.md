# Cinematic Warm Cache Command Summary

Generated UTC: `2026-06-18T18:31:09Z`
Source summary: `build/shots/s116_fingerprint_cost_probe/shot_summary.json`

## Reuse Flags

- Export cache reused: `True`
- Validation reused: `True`
- Water reconstruction reused: `True`
- Converted sequence reused: `True`
- Render frames reused: `True`

## Command Timings

| Stage | Exit | Reused | Elapsed | Stdout log |
| --- | ---: | --- | ---: | --- |
| `export_render_cache` | 0 | `true` | 0.00ms | `build/shots/s116_fingerprint_cost_probe/logs/01_export_render_cache.stdout.log` |
| `validate_render_cache` | 0 | `true` | 478.70ms | `build/shots/s116_fingerprint_cost_probe/logs/02_validate_render_cache.stdout.log` |
| `reconstruct_water` | 0 | `true` | 466.09ms | `build/shots/s116_fingerprint_cost_probe/logs/03_reconstruct_water.stdout.log` |
| `convert_render_cache` | 0 | `true` | 536.67ms | `build/shots/s116_fingerprint_cost_probe/logs/04_convert_render_cache.stdout.log` |
| `render_preview` | 0 | `true` | 0.00ms | `build/shots/s116_fingerprint_cost_probe/logs/05_render_preview.stdout.log` |
| `assemble_gif` | 0 | `false` | 735.26ms | `build/shots/s116_fingerprint_cost_probe/logs/06_assemble_gif.stdout.log` |

## Totals

- Total command time: `2.22s`
- Reused command time: `1.48s`

## Next

S117 should add warm-cache GIF assembly reuse because the remaining repeated-preview work is now mostly assembling an unchanged frame sequence.
