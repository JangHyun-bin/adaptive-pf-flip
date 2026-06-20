# S574 Mitsuba S515 T4 LFMask Material Tone Visual Triage

Generated UTC: `2026-06-20T21:38:00Z`

## Inputs

- S572 export: `build/shots/s572_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water/mitsuba_export.json`
- S573 render: `build/shots/s573_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water_spp4/render/mitsuba_render.json`
- S574 comparison: `build/shots/s574_mitsuba_s515_full48_t4_lfmask_material_tone_compare/gallery/index.html`
- Accepted reference: `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/runtime_render_sequence_adapter_summary.json`

## Gate

- S572 XML export: `ready`
- S572 XML validation: `ready`
- S573 render: `ready`
- S573 backend validation: `passed`
- S574 comparison gallery: `ready`

## Selected Frame Metrics

| Output | Raw MAD | Native Light MAD | LFMask Material MAD | Raw Luma | Accepted Luma | LFMask Material Luma |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 1.979245 | 2.021260 | 2.271030 | 165.574828 | 163.595500 | 165.597616 |
| 7 | 1.236234 | 1.275083 | 1.504237 | 166.209304 | 164.973050 | 166.214620 |
| 13 | 1.221150 | 1.259917 | 1.476993 | 165.956831 | 164.735640 | 165.950432 |
| 20 | 1.233891 | 1.266921 | 1.620678 | 166.344549 | 165.110658 | 166.352706 |
| 27 | 0.848063 | 0.878144 | 1.449010 | 166.291597 | 165.443206 | 166.303590 |
| 34 | 0.933237 | 0.965471 | 1.653947 | 166.268740 | 165.335503 | 166.260592 |
| 40 | 3.276260 | 3.319457 | 4.114676 | 166.478794 | 163.202402 | 166.506667 |
| 47 | 4.296984 | 4.334734 | 5.071845 | 166.750951 | 162.453696 | 166.737375 |

Mean raw-vs-accepted MAD: `1.878133`

Mean native-light-vs-accepted MAD: `1.915123`

Mean LFMask-material-vs-accepted MAD: `2.395302`

## Finding

The S567 low-frequency mask can drive the existing material/tone modulation
pipeline, but this dark-water/no-key candidate moves farther away from the S555
accepted correction. The preview luminance remains near the S515 baseline while
localized differences increase, especially on late frames.

S571 and S574 together rule out two simple native consumers for this accepted
T4 correction:

- light-only response anchors
- direct S567 material/tone modulation

The remaining useful direction is not another local XML tweak on S322. The
accepted T4 correction behaves like a low-frequency tonemap/texture field, so
the next native-adjacent step should package that field explicitly as a renderer
texture/lookup input, or keep it in the post-tonemap backend while moving other
photoreal work toward real geometry, surface detail, and secondary particles.

## Next

Promote the S555/S564 low-frequency field as an explicit renderer texture/cache
input and stop treating it as local light/material anchors until a real
renderer-side texture consumer exists.
