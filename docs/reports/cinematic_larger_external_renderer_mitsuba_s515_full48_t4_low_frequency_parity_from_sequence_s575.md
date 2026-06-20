# S575 Mitsuba S515 Full48 T4 Low Frequency Parity From Sequence

Generated UTC: `2026-06-20T21:39:00.499803+00:00`
Summary JSON: `build/shots/s575_mitsuba_s515_full48_t4_low_frequency_parity_from_sequence/low_frequency_parity_summary.json`
Status: `ready`

## Inputs

- Sequence adapter: `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/runtime_render_sequence_adapter_summary.json`
- Source schema: `lsfs_mitsuba_low_frequency_runtime_render_sequence_adapter`

## Checks

- Frames: `48`
- Missing references: `0`
- Dimension mismatches: `0`
- Max target abs diff: `43`
- Max target mean diff: `4.552690972222222`
- Max target mismatched coverage: `0.17741319444444445`
- Source bytes: `29.52 MB`

## Frame Samples

| Frame | Output | Mean Diff | Max Diff | Raw | Corrected |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0 | 1.979245113168724 | 43 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0000.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0000.png` |
| 24 | 24 | 1.3040605709876543 | 43 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0024.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0024.png` |
| 47 | 47 | 4.296983667695473 | 43 | `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/frame_0047.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0047.png` |

## Next

Build a full48 renderer texture/cache package from this S555 accepted low-frequency parity summary.
