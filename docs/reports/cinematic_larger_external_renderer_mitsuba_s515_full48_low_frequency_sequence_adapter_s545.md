# S545 Mitsuba S515 Full48 Low Frequency Sequence Adapter

Generated UTC: `2026-06-20T20:25:03.805613+00:00`
Summary JSON: `build/shots/s545_mitsuba_s515_full48_low_frequency_sequence_adapter/runtime_render_sequence_adapter_summary.json`
Gallery: `build/shots/s545_mitsuba_s515_full48_low_frequency_sequence_adapter/gallery/index.html`
Status: `ready`

## Inputs

- Render manifest: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/mitsuba_render.json`
- Runtime import preview: `build/shots/s535_mitsuba_s515_low_frequency_runtime_import_preview/runtime_import_preview.json`

## Checks

- Render source frames: `48`
- Runtime anchor frames: `8`
- Frames corrected: `48`
- Interpolated frames: `40`
- Missing references: `0`
- Dimension mismatches: `0`
- Max corrected abs diff: `43`
- Max corrected mean abs diff: `42.84736625514403`
- Corrected bytes: `14.29 MB`
- Corrected GIF bytes: `8.05 MB`

## Frame Samples

| Frame | Output | Bracket | t | Mean Change | Max Change | Raw | Corrected | Strip |
| ---: | ---: | --- | ---: | ---: | ---: | --- | --- | --- |
| 0 | 0 | 0->0 | 0.0 | 42.51413708847737 | 43 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0000.png` | `build/shots/s545_mitsuba_s515_full48_low_frequency_sequence_adapter/corrected/frame_0000.png` | `build/shots/s545_mitsuba_s515_full48_low_frequency_sequence_adapter/strips/frame_0000_low_frequency_sequence_adapter.png` |
| 24 | 24 | 20->27 | 0.571429 | 42.21103073559671 | 43 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0024.png` | `build/shots/s545_mitsuba_s515_full48_low_frequency_sequence_adapter/corrected/frame_0024.png` | `build/shots/s545_mitsuba_s515_full48_low_frequency_sequence_adapter/strips/frame_0024_low_frequency_sequence_adapter.png` |
| 47 | 47 | 47->47 | 0.0 | 42.478599537037034 | 43 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0047.png` | `build/shots/s545_mitsuba_s515_full48_low_frequency_sequence_adapter/corrected/frame_0047.png` | `build/shots/s545_mitsuba_s515_full48_low_frequency_sequence_adapter/strips/frame_0047_low_frequency_sequence_adapter.png` |

## Next

Publish this full48 corrected S515 sequence and decide whether temporal interpolation is visually acceptable before baking it into the backend contract.
