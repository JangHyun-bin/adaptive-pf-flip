# S338 Mitsuba Secondary Mist M2 Export

Generated UTC: `2026-06-20T00:33:13.765249+00:00`
Export JSON: `build/shots/s338_mitsuba_secondary_mist_m2/mitsuba_export.json`
Status: `ready`
Target renderer: `mitsuba`
Execution mode: `xml_export_only`

## Inputs

- Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list: `build/shots/s338_mitsuba_secondary_mist_m2/mitsuba_render_commands.txt`
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
- Secondary mist opacity: `0.004`
- Secondary mist radius scale: `4.5`
- Secondary mist shells: `1`
- Secondary mist shell spacing: `0.55`

## Checks

- Frames exported: `8`
- Failures: `0`
- Water mesh bytes: `13.52 MB`
- XML scene bytes: `1.36 MB`
- Secondary proxies emitted: `2297`
- Secondary halo proxies emitted: `2297`
- Secondary mist proxies emitted: `2297`
- Secondary particles available: `2877`
- Phase volume proxies emitted: `0`
- Phase volume cells available: `0`

## Frame Samples

| Output | XML Scene | Sequence | Water Faces | Secondary Total | Secondary Proxies | Mist Proxies | Phase Proxies |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | `build/shots/s338_mitsuba_secondary_mist_m2/scenes/frame_0000.xml` | 8 | 20000 | 256 | 256 | 256 | 0 |
| 27 | `build/shots/s338_mitsuba_secondary_mist_m2/scenes/frame_0004.xml` | 35 | 18576 | 256 | 256 | 256 | 0 |
| 47 | `build/shots/s338_mitsuba_secondary_mist_m2/scenes/frame_0007.xml` | 55 | 22300 | 964 | 384 | 384 | 0 |

## Next

Render this low-strength native mist candidate and compare it against the S335 contract gate.
