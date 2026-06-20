# S513 Mitsuba Secondary Masked 16F SPP4 Decision

## Decision

Keep S513 as the current longer real-render sequence baseline for the Mitsuba backend adapter path.

## Evidence

- Adapter summary: `build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/backend_command_adapter_summary.json`
- Validation JSON: `build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/backend_command_adapter_validation.json`
- Render manifest: `build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/render/mitsuba_render.json`
- Gallery manifest: `build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/gallery/gallery_manifest.json`
- Gallery index: `build/shots/s513_mitsuba_xml_backend_secondary_masked_16f_spp4/gallery/index.html`
- Source export: `build/shots/s322_larger_external_renderer_mitsuba_secondary_masked/mitsuba_export.json`

## Metrics

- Adapter status: `ready`
- Validation status: `passed`
- Frames requested: `16`
- Frames rendered: `16`
- Source output range: `0` to `47`
- Render failures: `0`
- Process failures: `0`
- Render elapsed ms: `8210.878`
- Gallery elapsed ms: `699.117`
- Image bytes: `46685835`
- Preview bytes: `5067642`
- GIF bytes: `2472350`
- Validation checks: `82`
- Failed validation checks: `0`

## Why This Matters

S506 and S508 proved the real Mitsuba backend command adapter on 8-frame samples. S513 extends that path to a 16-frame SPP4 sequence from a 48-frame secondary-masked export, while preserving the same process logs, render manifest, preview gallery, and validator gates.

This is a better baseline for judging motion, secondary continuity, and full-window timing than the earlier 8-frame samples.

## Next

Publish the S513 gallery for external visual review, then choose whether the next scale step should be a full 48-frame render, a larger export, or a visual/material adjustment.
