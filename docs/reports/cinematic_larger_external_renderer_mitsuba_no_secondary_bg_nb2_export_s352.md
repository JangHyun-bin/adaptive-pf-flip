# S352 Mitsuba No Secondary BG NB2 Export

Generated UTC: `2026-06-20T02:26:31.466615+00:00`
Export JSON: `build/shots/s352_mitsuba_no_secondary_bg_nb2/mitsuba_export.json`
Status: `ready`
Target renderer: `mitsuba`
Execution mode: `xml_export_only`

## Inputs

- Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list: `build/shots/s352_mitsuba_no_secondary_bg_nb2/mitsuba_render_commands.txt`
- Mitsuba command: `mitsuba`
- Mitsuba mode: `scalar_rgb`
- Samples override: `32`
- Camera position override: `[18.0, 20.0, 58.0]`
- Camera target override: `[18.0, 8.0, 14.0]`
- Camera FOV override: `34.0`
- Water alpha override: `0.014`
- Secondary opacity: `0.02`
- Secondary halo opacity: `0.006`
- Secondary halo radius scale: `3.0`
- Secondary mist opacity: `0.001`
- Secondary mist radius scale: `5.2`
- Secondary mist shells: `1`
- Secondary mist shell spacing: `0.55`
- Secondary billboard opacity: `0.025`
- Secondary billboard radius scale: `4.0`
- Secondary billboard aspect: `1.4`

## Checks

- Frames exported: `8`
- Failures: `0`
- Water mesh bytes: `13.52 MB`
- XML scene bytes: `39.39 KB`
- Secondary proxies emitted: `0`
- Secondary halo proxies emitted: `0`
- Secondary mist proxies emitted: `0`
- Secondary billboard proxies emitted: `0`
- Secondary particles available: `0`
- Phase volume proxies emitted: `0`
- Phase volume cells available: `0`

## Frame Samples

| Output | XML Scene | Sequence | Water Faces | Secondary Total | Secondary Proxies | Mist Proxies | Billboard Proxies | Phase Proxies |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | `build/shots/s352_mitsuba_no_secondary_bg_nb2/scenes/frame_0000.xml` | 8 | 20000 | 256 | 0 | 0 | 0 | 0 |
| 27 | `build/shots/s352_mitsuba_no_secondary_bg_nb2/scenes/frame_0004.xml` | 35 | 18576 | 256 | 0 | 0 | 0 | 0 |
| 47 | `build/shots/s352_mitsuba_no_secondary_bg_nb2/scenes/frame_0007.xml` | 55 | 22300 | 964 | 0 | 0 | 0 | 0 |

## Next

Render and compare against S335/S350 gates.
