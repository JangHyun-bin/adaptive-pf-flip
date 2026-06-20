# S520 Mitsuba Secondary Masked Runtime Corrected Review

Generated UTC: `2026-06-20T19:53:31.882611+00:00`
Summary JSON: `build/shots/s520_mitsuba_secondary_masked_runtime_corrected_review/runtime_render_adapter_summary.json`
Gallery: `build/shots/s520_mitsuba_secondary_masked_runtime_corrected_review/gallery/index.html`
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
- Max corrected abs diff: `23`
- Max corrected mean abs diff: `0.30087319958847736`
- Corrected bytes: `2.33 MB`
- Corrected GIF bytes: `1.32 MB`

## Frame Samples

| Frame | Output | Mean Change | Max Change | Raw | Corrected | Strip |
| ---: | ---: | ---: | ---: | --- | --- | --- |
| 0 | 0 | 0.07914673353909465 | 10 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0000.png` | `build/shots/s520_mitsuba_secondary_masked_runtime_corrected_review/corrected/frame_0000.png` | `build/shots/s520_mitsuba_secondary_masked_runtime_corrected_review/strips/frame_0000_low_frequency_render_adapter.png` |
| 4 | 27 | 0.06275848765432099 | 9 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0027.png` | `build/shots/s520_mitsuba_secondary_masked_runtime_corrected_review/corrected/frame_0004.png` | `build/shots/s520_mitsuba_secondary_masked_runtime_corrected_review/strips/frame_0004_low_frequency_render_adapter.png` |
| 7 | 47 | 0.30087319958847736 | 23 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0047.png` | `build/shots/s520_mitsuba_secondary_masked_runtime_corrected_review/corrected/frame_0007.png` | `build/shots/s520_mitsuba_secondary_masked_runtime_corrected_review/strips/frame_0007_low_frequency_render_adapter.png` |

## Next

Publish this corrected real Mitsuba render review and compare it against the raw S515 full48 gallery.
