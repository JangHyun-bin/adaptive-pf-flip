# S515 Mitsuba Secondary Masked Full48 SPP4 Decision

## Decision

Keep S515 as the current full-window real Mitsuba secondary sequence baseline.

## Evidence

- Adapter summary: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/backend_command_adapter_summary.json`
- Validation JSON: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/backend_command_adapter_validation.json`
- Render manifest: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/render/mitsuba_render.json`
- Gallery manifest: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/gallery/gallery_manifest.json`
- Gallery index: `build/shots/s515_mitsuba_xml_backend_secondary_masked_full48_spp4/gallery/index.html`
- Source export: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json`

## Metrics

- Adapter status: `ready`
- Validation status: `passed`
- Frames requested: `48`
- Frames rendered: `48`
- Source output range: `0` to `47`
- Render failures: `0`
- Process failures: `0`
- Render elapsed ms: `14759.603`
- Gallery elapsed ms: `1600.937`
- Image bytes: `139439678`
- Preview bytes: `15094754`
- GIF bytes: `7162433`
- Validation checks: `146`
- Failed validation checks: `0`

## Why This Matters

S513 proved the same secondary-masked export on a 16-frame SPP4 sample. S515 renders all 48 exported frames, so it is the first full-window real Mitsuba secondary sequence in this current backend-adapter chain.

This gives a stronger motion and temporal-continuity baseline than the 8-frame and 16-frame samples while still completing fast enough to use as an iteration gate.

## Next

Publish the S515 full48 gallery for external visual review. After that, the next useful work is either full48 comparison packaging against S513/S322 or a material/lighting pass to improve the gray low-contrast read of the current Mitsuba preview.
