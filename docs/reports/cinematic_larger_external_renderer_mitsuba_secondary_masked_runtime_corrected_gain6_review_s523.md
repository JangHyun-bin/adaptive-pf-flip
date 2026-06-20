# S523 Mitsuba Secondary Masked Runtime Corrected Gain6 Review

Generated UTC: `2026-06-20T19:57:16.128077+00:00`
Summary JSON: `build/shots/s523_mitsuba_secondary_masked_runtime_corrected_gain6_review/runtime_render_adapter_summary.json`
Gallery: `build/shots/s523_mitsuba_secondary_masked_runtime_corrected_gain6_review/gallery/index.html`
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
- Max corrected abs diff: `99`
- Max corrected mean abs diff: `1.6686921296296295`
- Corrected bytes: `2.39 MB`
- Corrected GIF bytes: `1.36 MB`

## Frame Samples

| Frame | Output | Mean Change | Max Change | Raw | Corrected | Strip |
| ---: | ---: | ---: | ---: | --- | --- | --- |
| 0 | 0 | 0.4722492283950617 | 54 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0000.png` | `build/shots/s523_mitsuba_secondary_masked_runtime_corrected_gain6_review/corrected/frame_0000.png` | `build/shots/s523_mitsuba_secondary_masked_runtime_corrected_gain6_review/strips/frame_0000_low_frequency_render_adapter.png` |
| 4 | 27 | 0.3751176697530864 | 48 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0027.png` | `build/shots/s523_mitsuba_secondary_masked_runtime_corrected_gain6_review/corrected/frame_0004.png` | `build/shots/s523_mitsuba_secondary_masked_runtime_corrected_gain6_review/strips/frame_0004_low_frequency_render_adapter.png` |
| 7 | 47 | 1.6686921296296295 | 99 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0047.png` | `build/shots/s523_mitsuba_secondary_masked_runtime_corrected_gain6_review/corrected/frame_0007.png` | `build/shots/s523_mitsuba_secondary_masked_runtime_corrected_gain6_review/strips/frame_0007_low_frequency_render_adapter.png` |

## Next

Compare gain6 against gain1, gain2, and gain4 before selecting a corrected-render review default.
