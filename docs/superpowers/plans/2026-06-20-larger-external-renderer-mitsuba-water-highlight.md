# Larger External Renderer: Mitsuba Water Highlight

Status: complete

## Goal

Move from secondary attenuation to source-highlight response by placing
world-space highlight emitters on water mesh vertices under the S410 highlight
mask.

## Result

S415 added the water-highlight emitter tool and tested WH1-WH5. WH4 is the best
native water-highlight probe so far, but it is not promoted over SS1.

- Public compare gallery:
  `https://logical-mambo-metro-mountain.trycloudflare.com/index.html`
- Summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_summary_s415.md`
- Sweep:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_highlight_sweep_summary_s415.md`

WH4 max target MAD is `23.98679526748971`. This improves over S411/S414 native
attempts, but SS1 remains better at `23.951853137860084`, and S409 `SF12_H18`
remains much better at `23.687431841563786`.

## Code Change

- Added `tools/add_mitsuba_water_mask_highlights.py`.

The tool projects water OBJ vertices through the frame camera, samples a
source-response mask, and inserts small Mitsuba sphere area emitters at selected
water-surface vertices.

## Validation

- `python -m py_compile tools\add_mitsuba_water_mask_highlights.py`
- XML validation for WH1-WH5
- Mitsuba render for WH1-WH5
- Target-gap reports for WH1-WH5
- Sweep summary and compare gallery
- Published compare gallery with HTTP `200`

## Decision

Keep WH4 as useful evidence, but do not promote point emitters as the final
native source-highlight mechanism. The visual response is too speckled.

## Next

S416 should convert this into broader area response: texture/volume mask,
clustered water patch emission, or combination with accepted SF12 dark
attenuation.
