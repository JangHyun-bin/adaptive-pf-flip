# S313 Larger External Renderer Mitsuba XML Validation

Generated UTC: `2026-06-19T22:15:07.599571+00:00`
Validation JSON: `build/shots/s313_larger_external_renderer_mitsuba_xml_validation/mitsuba_validation.json`
Status: `ready`

## Mitsuba

- Command: `mitsuba`
- Found: `False`
- Required: `False`
- Path: `n/a`

## Export

- Export manifest: `build/shots/s312_larger_external_renderer_mitsuba_phase_proxy/mitsuba_export.json`

## Checks

- Frames: `48`
- XML parsed: `48`
- Command count: `48`
- OBJ shapes: `48`
- Sphere shapes: `7680`
- BSDFs: `288`
- Failures: `0`
- Warnings: `1`

## Frame Samples

| Output | XML Scene | OBJ Shapes | Sphere Shapes | BSDFs |
| ---: | --- | ---: | ---: | ---: |
| 0 | `build/shots/s312_larger_external_renderer_mitsuba_phase_proxy/scenes/frame_0000.xml` | 1 | 160 | 6 |
| 24 | `build/shots/s312_larger_external_renderer_mitsuba_phase_proxy/scenes/frame_0024.xml` | 1 | 160 | 6 |
| 47 | `build/shots/s312_larger_external_renderer_mitsuba_phase_proxy/scenes/frame_0047.xml` | 1 | 160 | 6 |

## Warnings

- `mitsuba_executable_missing`

## Next

Install Mitsuba or configure a renderer command, then rerun this gate with --require-mitsuba before invoking full48 renders.
