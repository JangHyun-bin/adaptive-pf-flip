# S508 Mitsuba XML Backend Command Adapter SPP4 Decision

## Decision

Keep S508 as the first higher-SPP real-render sample on the Mitsuba XML backend command-adapter path.

## Evidence

- S508 adapter summary: `build/shots/s508_mitsuba_xml_backend_command_adapter_spp4/backend_command_adapter_summary.json`
- S508 validation JSON: `build/shots/s508_mitsuba_xml_backend_command_adapter_spp4/backend_command_adapter_validation.json`
- S508 render manifest: `build/shots/s508_mitsuba_xml_backend_command_adapter_spp4/render/mitsuba_render.json`
- S508 gallery manifest: `build/shots/s508_mitsuba_xml_backend_command_adapter_spp4/gallery/gallery_manifest.json`
- S508 gallery index: `build/shots/s508_mitsuba_xml_backend_command_adapter_spp4/gallery/index.html`
- S506 baseline summary: `build/shots/s506_mitsuba_xml_backend_command_adapter/backend_command_adapter_summary.json`

## Metrics

| Metric | S506 SPP1 | S508 SPP4 |
| --- | ---: | ---: |
| Frames rendered | `8` | `8` |
| Render failures | `0` | `0` |
| Process failures | `0` | `0` |
| Render elapsed ms | `5759.801` | `6003.532` |
| Image bytes | `18415437` | `21582385` |
| Preview bytes | `2174507` | `2135660` |
| GIF bytes | `1083586` | `1099895` |

Validation checks: `66`
Failed validation checks: `0`

## Why This Matters

S506 proved that the real Mitsuba backend command adapter works at SPP1. S508 raises the sample count to SPP4 while preserving the same output contract: render process logs, EXR outputs, PNG previews, gallery assets, and validation gates.

The runtime increase is small on this scene, so SPP4 is a practical next visual review baseline before scaling frame count, resolution, or scene complexity.

## Next

Publish the S508 SPP4 gallery for visual comparison, then decide whether the next scale step should increase SPP, frame count, or scene size.
