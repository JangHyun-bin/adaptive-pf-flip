# S319 Larger External Renderer Mitsuba Command Fix

Generated UTC: `2026-06-19T22:45:06.357107+00:00`
Export JSON: `build/shots/s319_larger_external_renderer_mitsuba_render_probe/mitsuba_export.json`
Status: `ready`
Target renderer: `mitsuba`
Execution mode: `xml_export_only`

## Inputs

- Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list: `build/shots/s319_larger_external_renderer_mitsuba_render_probe/mitsuba_render_commands.txt`
- Mitsuba command: `mitsuba`
- Mitsuba mode: `scalar_rgb`

## Checks

- Frames exported: `48`
- Failures: `0`
- Water mesh bytes: `80.07 MB`
- XML scene bytes: `1.52 MB`
- Secondary proxies emitted: `4608`
- Secondary particles available: `15413`
- Phase volume proxies emitted: `3072`
- Phase volume cells available: `261158`

## Frame Samples

| Output | XML Scene | Sequence | Water Faces | Secondary Total | Secondary Proxies | Phase Proxies |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | `build/shots/s319_larger_external_renderer_mitsuba_render_probe/scenes/frame_0000.xml` | 8 | 20000 | 256 | 96 | 64 |
| 24 | `build/shots/s319_larger_external_renderer_mitsuba_render_probe/scenes/frame_0024.xml` | 32 | 17912 | 256 | 96 | 64 |
| 47 | `build/shots/s319_larger_external_renderer_mitsuba_render_probe/scenes/frame_0047.xml` | 55 | 22300 | 964 | 96 | 64 |

## Next

Use the corrected command list or the Python render probe to produce actual Mitsuba frames.
