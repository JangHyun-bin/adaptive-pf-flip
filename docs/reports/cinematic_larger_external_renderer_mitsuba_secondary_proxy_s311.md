# S311 Larger External Renderer Mitsuba Secondary Proxy

Generated UTC: `2026-06-19T22:07:09.864677+00:00`
Export JSON: `build/shots/s311_larger_external_renderer_mitsuba_secondary_proxy/mitsuba_export.json`
Status: `ready`
Target renderer: `mitsuba`
Execution mode: `xml_export_only`

## Inputs

- Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list: `build/shots/s311_larger_external_renderer_mitsuba_secondary_proxy/mitsuba_render_commands.txt`

## Checks

- Frames exported: `48`
- Failures: `0`
- Water mesh bytes: `80.07 MB`
- XML scene bytes: `995.47 KB`
- Secondary proxies emitted: `4608`
- Secondary particles available: `15413`

## Frame Samples

| Output | XML Scene | Sequence | Water Faces | Secondary Total | Proxy Count |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0 | `build/shots/s311_larger_external_renderer_mitsuba_secondary_proxy/scenes/frame_0000.xml` | 8 | 20000 | 256 | 96 |
| 24 | `build/shots/s311_larger_external_renderer_mitsuba_secondary_proxy/scenes/frame_0024.xml` | 32 | 17912 | 256 | 96 |
| 47 | `build/shots/s311_larger_external_renderer_mitsuba_secondary_proxy/scenes/frame_0047.xml` | 55 | 22300 | 964 | 96 |

## Next

Validate these XML scenes with a Mitsuba executable when available, then tune proxy radius/channel materials or expand phase volume conversion.
