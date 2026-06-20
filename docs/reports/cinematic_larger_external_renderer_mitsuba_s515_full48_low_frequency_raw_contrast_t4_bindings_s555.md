# S555 Mitsuba S515 Full48 Low Frequency Raw Contrast T4 Bindings

Generated UTC: `2026-06-20T20:54:07.929270+00:00`
Summary JSON: `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/runtime_render_sequence_adapter_summary.json`
Gallery: `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/gallery/index.html`
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
- Max mask coverage: `0.18578510802469136`
- Max strong mask coverage: `0.10993827160493827`
- Missing references: `0`
- Dimension mismatches: `0`
- Max corrected abs diff: `43`
- Max corrected mean abs diff: `4.552690972222222`
- Corrected bytes: `15.13 MB`
- Corrected GIF bytes: `6.78 MB`

## Frame Samples

| Frame | Output | Bracket | t | Mask Coverage | Mean Change | Max Change | Raw | Corrected | Strip |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| 0 | 0 | 0->0 | 0.0 | 0.10051890432098766 | 1.9792451131687243 | 43 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0000.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0000.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/strips/frame_0000_low_frequency_sequence_adapter.png` |
| 24 | 24 | 20->27 | 0.571429 | 0.08406635802469135 | 1.3040605709876543 | 43 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0024.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0024.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/strips/frame_0024_low_frequency_sequence_adapter.png` |
| 47 | 47 | 47->47 | 0.0 | 0.18329089506172838 | 4.296983667695473 | 43 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0047.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0047.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/strips/frame_0047_low_frequency_sequence_adapter.png` |

## Next

Package these per-frame masked delta bindings into a renderer acceptance/job/backend contract.
