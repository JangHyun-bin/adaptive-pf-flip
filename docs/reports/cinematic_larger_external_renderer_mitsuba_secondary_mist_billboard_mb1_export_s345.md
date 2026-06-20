# S345 Mitsuba Secondary Mist Billboard MB1 Export

Generated UTC: `2026-06-20T01:22:59.557744+00:00`
Export JSON: `build/shots/s345_mitsuba_secondary_mist_billboard_mb1/mitsuba_export.json`
Status: `ready`
Target renderer: `mitsuba`
Execution mode: `xml_export_only`

## Inputs

- Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list: `build/shots/s345_mitsuba_secondary_mist_billboard_mb1/mitsuba_render_commands.txt`
- Mitsuba command: `mitsuba`
- Mitsuba mode: `scalar_rgb`
- Samples override: `32`
- Camera position override: `[18.0, 20.0, 58.0]`
- Camera target override: `[18.0, 8.0, 14.0]`
- Camera FOV override: `34.0`
- Water alpha override: `0.014`
- Secondary opacity: `0.12`
- Secondary halo opacity: `0.06`
- Secondary halo radius scale: `3.0`
- Secondary mist opacity: `0.026`
- Secondary mist radius scale: `5.2`
- Secondary mist shells: `1`
- Secondary mist shell spacing: `0.55`
- Secondary billboard opacity: `0.09`
- Secondary billboard radius scale: `2.5`
- Secondary billboard aspect: `1.25`

## Checks

- Frames exported: `8`
- Failures: `0`
- Water mesh bytes: `13.52 MB`
- XML scene bytes: `1.98 MB`
- Secondary proxies emitted: `2297`
- Secondary halo proxies emitted: `2297`
- Secondary mist proxies emitted: `2297`
- Secondary billboard proxies emitted: `2297`
- Secondary particles available: `2877`
- Phase volume proxies emitted: `0`
- Phase volume cells available: `0`

## Frame Samples

| Output | XML Scene | Sequence | Water Faces | Secondary Total | Secondary Proxies | Mist Proxies | Billboard Proxies | Phase Proxies |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | `build/shots/s345_mitsuba_secondary_mist_billboard_mb1/scenes/frame_0000.xml` | 8 | 20000 | 256 | 256 | 256 | 256 | 0 |
| 27 | `build/shots/s345_mitsuba_secondary_mist_billboard_mb1/scenes/frame_0004.xml` | 35 | 18576 | 256 | 256 | 256 | 256 | 0 |
| 47 | `build/shots/s345_mitsuba_secondary_mist_billboard_mb1/scenes/frame_0007.xml` | 55 | 22300 | 964 | 384 | 384 | 384 | 0 |

## Next

Install Mitsuba or add a renderer invocation gate that consumes the exported XML scenes.
