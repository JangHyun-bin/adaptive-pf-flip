# S571 Mitsuba S515 T4 Light Response Visual Triage

Generated UTC: `2026-06-20T21:31:00Z`

## Inputs

- S515 raw render: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/mitsuba_render.json`
- S555 accepted correction: `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/runtime_render_sequence_adapter_summary.json`
- S570 native-light sample: `build/shots/s570_mitsuba_s515_full48_t4_low_frequency_light_response_sample_spp4/render/mitsuba_render.json`
- Comparison gallery: `build/shots/s571_mitsuba_s515_full48_t4_light_response_vs_accepted_compare/gallery/index.html`

## Gate

- S569 XML export: `ready`
- S569 XML validation: `ready`
- S570 render: `ready`
- S570 backend validation: `passed`
- S571 comparison gallery: `ready`

## Selected Frame Metrics

| Output | Raw Luma | Accepted Luma | Native Light Luma | Raw vs Accepted MAD | Native Light vs Accepted MAD |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 165.574828 | 163.595500 | 165.579981 | 1.979245 | 2.021260 |
| 7 | 166.209304 | 164.973050 | 166.210008 | 1.236234 | 1.275083 |
| 13 | 165.956831 | 164.735640 | 165.960870 | 1.221150 | 1.259917 |
| 20 | 166.344549 | 165.110658 | 166.345224 | 1.233891 | 1.266921 |
| 27 | 166.291597 | 165.443206 | 166.292490 | 0.848063 | 0.878144 |
| 34 | 166.268740 | 165.335503 | 166.264095 | 0.933237 | 0.965471 |
| 40 | 166.478794 | 163.202402 | 166.485459 | 3.276260 | 3.319457 |
| 47 | 166.750951 | 162.453696 | 166.755750 | 4.296984 | 4.334734 |

Mean raw-vs-accepted MAD: `1.878133`

Mean native-light-vs-accepted MAD: `1.915123`

## Finding

The S568 to S570 native-light path is technically valid, but it does not move
the image toward the accepted S555 correction. The inserted area emitters
preserve the flat high-luma S515 read and slightly increase the error against
the accepted correction on the sampled frames.

This means a light-only consumer is not the right next promotion path for the
current S515 T4 correction. The next useful native step should combine the S568
response evidence with material or tone controls, or filter the anchors to avoid
lifting already over-bright regions.

## Next

Build a bounded material/tone response consumer from the same S567/S568 evidence,
then render another 8-frame sample and compare against S555 before attempting a
full48 renderer-native render.
