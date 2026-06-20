# Larger External Renderer: Mitsuba Water Patch

Status: complete

## Goal

Convert the S415 point-emitter water-highlight result into a broader
water-surface patch response using the existing water-highlight tool.

## Result

S416 tested WP1-WP5. WP4 is the best native water-patch probe in this group,
but it is not promoted over SS1.

- Public compare gallery:
  `https://full-fuji-tone-vii.trycloudflare.com/index.html`
- Summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_summary_s416.md`
- Sweep:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_sweep_summary_s416.md`

WP4 max target MAD is `23.97967785493827`. This is better than S415 WH4
`23.98679526748971`, but SS1 remains better at `23.951853137860084`, and S409
`SF12_H18` remains much better at `23.687431841563786`.

## Code Change

No code change.

The sweep reused `tools/add_mitsuba_water_mask_highlights.py` with larger
emitter radius, fewer emitters, and larger minimum screen spacing.

## Validation

- XML validation for WP1-WP5
- Mitsuba render for WP1-WP5
- Target-gap reports for WP1-WP5
- Sweep summary and compare gallery
- Published compare gallery with HTTP `200`

## Decision

Keep WP4 as useful evidence, but do not promote clustered/discrete emitters as
the final native source-highlight mechanism. The response is wider than WH4 but
still too speckled and not connected enough.

## Next

S417 should combine WP4 with accepted SF12 dark attenuation, or move to a true
renderer-side water texture/volume mask.
