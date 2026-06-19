# S321 Larger External Renderer Mitsuba Closeup Export

Generated UTC: `2026-06-19T22:57:05.466890+00:00`
Export JSON: `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/mitsuba_export.json`
Status: `ready`
Target renderer: `mitsuba`
Execution mode: `xml_export_only`

## Inputs

- Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list: `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/mitsuba_render_commands.txt`
- Mitsuba command: `mitsuba`
- Mitsuba mode: `scalar_rgb`
- Samples override: `24`
- Camera position override: `[18.0, 20.0, 58.0]`
- Camera target override: `[18.0, 8.0, 14.0]`
- Camera FOV override: `34.0`
- Water alpha override: `0.025`

## Checks

- Frames exported: `48`
- Failures: `0`
- Water mesh bytes: `80.07 MB`
- XML scene bytes: `1.86 MB`
- Secondary proxies emitted: `9216`
- Secondary particles available: `15413`
- Phase volume proxies emitted: `0`
- Phase volume cells available: `0`

## Frame Samples

| Output | XML Scene | Sequence | Water Faces | Secondary Total | Secondary Proxies | Phase Proxies |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/scenes/frame_0000.xml` | 8 | 20000 | 256 | 192 | 0 |
| 24 | `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/scenes/frame_0024.xml` | 32 | 17912 | 256 | 192 | 0 |
| 47 | `build/shots/s321_larger_external_renderer_mitsuba_closeup_render/scenes/frame_0047.xml` | 55 | 22300 | 964 | 192 | 0 |

## Next

Validate and render a higher-readability Mitsuba close-up probe from this XML bundle.
