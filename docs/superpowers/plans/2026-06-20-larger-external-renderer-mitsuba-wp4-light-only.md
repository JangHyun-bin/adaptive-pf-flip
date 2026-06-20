# Larger External Renderer: Mitsuba WP4 Light Only

Status: complete

## Goal

Test S416 WP4 with the accepted SF12 response family, then isolate which part
of the response helps.

## Result

S417 added a render-response wrapper tool and tested dark-band plus light-only
combinations over WP4.

- Public compare gallery:
  `https://fires-factors-can-eugene.trycloudflare.com/index.html`
- Summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_light_only_summary_s417.md`
- Sweep:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_light_only_sweep_summary_s417.md`

The best S417 candidate is `S417_WP4_H18_D90` with max target MAD
`23.948739068930042`. This is a small improvement over SS1
`23.951853137860084` and S416 WP4 `23.97967785493827`, but it is still far
behind S409 `SF12_H18` at `23.687431841563786`.

## Code Change

- Added `tools/build_mitsuba_render_response_input.py`.

The tool converts a Mitsuba render manifest into a secondary-composite wrapper
so source-region response tools can be reused on native render candidates.

## Validation

- `python -m py_compile tools/build_mitsuba_render_response_input.py`
- Response input wrapper
- S417 response candidates
- S417 target-gap reports
- Sweep summary and compare gallery
- Published compare gallery with HTTP `200`

## Decision

Carry `S417_WP4_H18_D90` as the best WP4 upper-bound response. Do not carry the
SF12 dark-band combination on WP4; dark-only and dark-plus-highlight variants
worsen the target gap.

## Next

S418 should migrate the winning light-only behavior into renderer-native water
texture, area patch, or volume/emission controls.
