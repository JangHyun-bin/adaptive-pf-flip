# S547 Mitsuba S515 Full48 Low Frequency Raw Contrast Mask

Generated UTC: `2026-06-20T20:34:13.215381+00:00`
Summary JSON: `build/shots/s547_mitsuba_s515_full48_low_frequency_raw_contrast_mask/runtime_render_sequence_adapter_summary.json`
Gallery: `build/shots/s547_mitsuba_s515_full48_low_frequency_raw_contrast_mask/gallery/index.html`
Status: `ready`

## Inputs

- Render manifest: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/mitsuba_render.json`
- Runtime import preview: `build/shots/s535_mitsuba_s515_low_frequency_runtime_import_preview/runtime_import_preview.json`

## Checks

- Render source frames: `48`
- Runtime anchor frames: `8`
- Frames corrected: `48`
- Interpolated frames: `40`
- Mask mode: `raw-contrast`
- Max mask coverage: `0.15819637345679013`
- Max strong mask coverage: `0.10177276234567902`
- Missing references: `0`
- Dimension mismatches: `0`
- Max corrected abs diff: `43`
- Max corrected mean abs diff: `4.0935641718107`
- Corrected bytes: `14.93 MB`
- Corrected GIF bytes: `6.79 MB`

## Frame Samples

| Frame | Output | Bracket | t | Mask Coverage | Mean Change | Max Change | Raw | Corrected | Strip |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| 0 | 0 | 0->0 | 0.0 | 0.08330439814814815 | 1.719391718106996 | 43 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0000.png` | `build/shots/s547_mitsuba_s515_full48_low_frequency_raw_contrast_mask/corrected/frame_0000.png` | `build/shots/s547_mitsuba_s515_full48_low_frequency_raw_contrast_mask/strips/frame_0000_low_frequency_sequence_adapter.png` |
| 24 | 24 | 20->27 | 0.571429 | 0.06475308641975308 | 1.0422569444444445 | 43 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0024.png` | `build/shots/s547_mitsuba_s515_full48_low_frequency_raw_contrast_mask/corrected/frame_0024.png` | `build/shots/s547_mitsuba_s515_full48_low_frequency_raw_contrast_mask/strips/frame_0024_low_frequency_sequence_adapter.png` |
| 47 | 47 | 47->47 | 0.0 | 0.1558275462962963 | 3.8331179269547326 | 43 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0047.png` | `build/shots/s547_mitsuba_s515_full48_low_frequency_raw_contrast_mask/corrected/frame_0047.png` | `build/shots/s547_mitsuba_s515_full48_low_frequency_raw_contrast_mask/strips/frame_0047_low_frequency_sequence_adapter.png` |

## Next

Publish this spatially bounded full48 correction and compare it against the unbounded S545 sequence.
