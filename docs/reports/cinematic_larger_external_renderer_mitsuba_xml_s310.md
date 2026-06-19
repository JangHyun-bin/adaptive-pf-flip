# S310 Larger External Renderer Mitsuba XML Export

Generated UTC: `2026-06-19T22:00:47.595183+00:00`
Export JSON: `build/shots/s310_larger_external_renderer_mitsuba_xml/mitsuba_export.json`
Status: `ready`
Target renderer: `mitsuba`
Execution mode: `xml_export_only`

## Inputs

- Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list: `build/shots/s310_larger_external_renderer_mitsuba_xml/mitsuba_render_commands.txt`

## Checks

- Frames exported: `48`
- Failures: `0`
- Water mesh bytes: `80.07 MB`
- XML scene bytes: `74.38 KB`

## Frame Samples

| Output | XML Scene | Sequence | Water Faces | Secondary Total |
| ---: | --- | ---: | ---: | ---: |
| 0 | `build/shots/s310_larger_external_renderer_mitsuba_xml/scenes/frame_0000.xml` | 8 | 20000 | 256 |
| 24 | `build/shots/s310_larger_external_renderer_mitsuba_xml/scenes/frame_0024.xml` | 32 | 17912 | 256 |
| 47 | `build/shots/s310_larger_external_renderer_mitsuba_xml/scenes/frame_0047.xml` | 55 | 22300 | 964 |

## Next

Validate these XML scenes with a Mitsuba executable when available, then add particle proxy expansion or volume conversion for phase and secondary channels.
