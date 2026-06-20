# S339 Mitsuba Secondary Billboard B4 Export

Generated UTC: `2026-06-20T00:45:19.065147+00:00`
Export JSON: `build/shots/s339_mitsuba_secondary_billboard_b4/mitsuba_export.json`
Status: `ready`
Target renderer: `mitsuba`
Execution mode: `xml_export_only`

## Inputs

- Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list: `build/shots/s339_mitsuba_secondary_billboard_b4/mitsuba_render_commands.txt`
- Mitsuba command: `mitsuba`
- Mitsuba mode: `scalar_rgb`
- Samples override: `32`
- Camera position override: `[18.0, 20.0, 58.0]`
- Camera target override: `[18.0, 8.0, 14.0]`
- Camera FOV override: `34.0`
- Water alpha override: `0.014`
- Secondary opacity: `0.14`
- Secondary halo opacity: `0.075`
- Secondary halo radius scale: `3.0`
- Secondary mist opacity: `None`
- Secondary mist radius scale: `5.0`
- Secondary mist shells: `1`
- Secondary mist shell spacing: `0.55`
- Secondary billboard opacity: `0.035`
- Secondary billboard radius scale: `1.15`
- Secondary billboard aspect: `1.0`

## Checks

- Frames exported: `8`
- Failures: `0`
- Water mesh bytes: `13.52 MB`
- XML scene bytes: `1.54 MB`
- Secondary proxies emitted: `2297`
- Secondary halo proxies emitted: `2297`
- Secondary mist proxies emitted: `0`
- Secondary billboard proxies emitted: `2297`
- Secondary particles available: `2877`
- Phase volume proxies emitted: `0`
- Phase volume cells available: `0`

## Frame Samples

| Output | XML Scene | Sequence | Water Faces | Secondary Total | Secondary Proxies | Mist Proxies | Billboard Proxies | Phase Proxies |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | `build/shots/s339_mitsuba_secondary_billboard_b4/scenes/frame_0000.xml` | 8 | 20000 | 256 | 256 | 0 | 256 | 0 |
| 27 | `build/shots/s339_mitsuba_secondary_billboard_b4/scenes/frame_0004.xml` | 35 | 18576 | 256 | 256 | 0 | 256 | 0 |
| 47 | `build/shots/s339_mitsuba_secondary_billboard_b4/scenes/frame_0007.xml` | 55 | 22300 | 964 | 384 | 0 | 384 | 0 |

## Next

Render this background-controlled camera-facing disk candidate and compare it against the S335 contract gate.
