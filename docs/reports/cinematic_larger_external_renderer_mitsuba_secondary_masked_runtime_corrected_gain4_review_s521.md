# S521 Mitsuba Secondary Masked Runtime Corrected Gain4 Review

Generated UTC: `2026-06-20T19:54:21.992835+00:00`
Summary JSON: `build/shots/s521_mitsuba_secondary_masked_runtime_corrected_gain4_review/runtime_render_adapter_summary.json`
Gallery: `build/shots/s521_mitsuba_secondary_masked_runtime_corrected_gain4_review/gallery/index.html`
Status: `ready`

## Inputs

- Render manifest: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/mitsuba_render.json`
- Runtime import preview: `build/shots/s495_mitsuba_low_frequency_runtime_import_preview/runtime_import_preview.json`

## Checks

- Render source frames: `48`
- Runtime source frames: `8`
- Frames corrected: `8`
- Missing references: `0`
- Dimension mismatches: `0`
- Max corrected abs diff: `85`
- Max corrected mean abs diff: `1.1587422839506172`
- Corrected bytes: `2.38 MB`
- Corrected GIF bytes: `1.36 MB`

## Frame Samples

| Frame | Output | Mean Change | Max Change | Raw | Corrected | Strip |
| ---: | ---: | ---: | ---: | --- | --- | --- |
| 0 | 0 | 0.3153697273662551 | 37 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0000.png` | `build/shots/s521_mitsuba_secondary_masked_runtime_corrected_gain4_review/corrected/frame_0000.png` | `build/shots/s521_mitsuba_secondary_masked_runtime_corrected_gain4_review/strips/frame_0000_low_frequency_render_adapter.png` |
| 4 | 27 | 0.2503600823045268 | 32 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0027.png` | `build/shots/s521_mitsuba_secondary_masked_runtime_corrected_gain4_review/corrected/frame_0004.png` | `build/shots/s521_mitsuba_secondary_masked_runtime_corrected_gain4_review/strips/frame_0004_low_frequency_render_adapter.png` |
| 7 | 47 | 1.1587422839506172 | 85 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0047.png` | `build/shots/s521_mitsuba_secondary_masked_runtime_corrected_gain4_review/corrected/frame_0007.png` | `build/shots/s521_mitsuba_secondary_masked_runtime_corrected_gain4_review/strips/frame_0007_low_frequency_render_adapter.png` |

## Next

Publish or tune this stronger corrected real Mitsuba render if the added low-frequency response improves visual read without obvious clipping.
