# S517 Mitsuba Secondary Masked Full48 Visual Triage

Generated UTC: `2026-06-20T19:43:09Z`

## Inputs

- Render summary: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/backend_command_adapter_summary.json`
- Validation summary: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/backend_command_adapter_validation.json`
- Published gallery: `https://laura-favorites-happiness-occasional.trycloudflare.com`
- Source export: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json`

## Render Gate

- Status: `ready`
- Frames requested: `48`
- Frames rendered: `48`
- Render failures: `0`
- Process failures: `0`
- Validation checks: `146`
- Validation failures: `0`
- Image bytes: `139439678`
- Preview bytes: `15094754`
- GIF bytes: `7162433`
- Render elapsed ms: `14759.603`
- Gallery elapsed ms: `1600.937`

## Preview Metrics

Metrics were computed over `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/previews/*.png`.

| Metric | Min | Mean | Max |
| --- | ---: | ---: | ---: |
| Mean luminance | `165.378102` | `166.265066` | `166.781283` |
| Luma contrast | `144.978800` | `168.351346` | `191.629800` |
| P95 luminance | `166.957000` | `168.113571` | `168.957000` |
| P99 luminance | `170.957000` | `186.392717` | `255.000000` |
| Bright ratio, luma >= 220 | `0.000700` | `0.004165` | `0.021491` |
| Highlight ratio, luma >= 245 | `0.000563` | `0.003620` | `0.019522` |
| Nonblank ratio, luma > 8 | `1.000000` | `1.000000` | `1.000000` |
| PNG bytes | `284865` | `314474.041667` | `366136` |

## Sample Frames

| Frame | Mean Luma | Contrast | P95 | P99 | Bright >= 220 | Highlight >= 245 | PNG Bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `frame_0000` | `165.599776` | `180.557600` | `167.957000` | `175.029200` | `0.002689` | `0.002350` | `339811` |
| `frame_0024` | `166.366373` | `158.625800` | `167.957000` | `171.957000` | `0.000702` | `0.000563` | `295222` |
| `frame_0047` | `166.781283` | `181.557600` | `168.957000` | `255.000000` | `0.021491` | `0.019522` | `365950` |

## Decision

The full 48-frame real Mitsuba backend path is technically ready: every frame rendered, no process failures were reported, all validation checks passed, and the public review gallery is reachable.

The visual response is not yet the desired cinematic target. The preview sequence is mostly nonblank and stable, but it reads flat: mean luminance stays near `166`, the P95 band is almost fixed near `168`, and strong highlight occupancy is very low except in the final frames. The next meaningful improvement axis is material, lighting, tone response, and secondary visibility, not another larger render of the same setup.

## Next

Find the existing Mitsuba channel mask, highlight mask, renderer handoff, and target-gap summaries, then run a bounded material/tone sweep on 8-16 frames before spending another full 48-frame render.
