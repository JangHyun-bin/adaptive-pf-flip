# S331 Mitsuba Renderer Native Gap Export

Generated UTC: `2026-06-19T23:53:31.527210+00:00`
Export JSON: `build/shots/s331_mitsuba_renderer_native_gap_pass/mitsuba_export.json`
Status: `ready`
Target renderer: `mitsuba`
Execution mode: `xml_export_only`

## Inputs

- Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list: `build/shots/s331_mitsuba_renderer_native_gap_pass/mitsuba_render_commands.txt`
- Mitsuba command: `mitsuba`
- Mitsuba mode: `scalar_rgb`
- Samples override: `32`
- Camera position override: `[18.0, 20.0, 58.0]`
- Camera target override: `[18.0, 8.0, 14.0]`
- Camera FOV override: `34.0`
- Water alpha override: `0.018`
- Secondary opacity: `0.18`

## Checks

- Frames exported: `8`
- Failures: `0`
- Water mesh bytes: `13.52 MB`
- XML scene bytes: `465.93 KB`
- Secondary proxies emitted: `2297`
- Secondary particles available: `2877`
- Phase volume proxies emitted: `0`
- Phase volume cells available: `0`

## Frame Samples

| Output | XML Scene | Sequence | Water Faces | Secondary Total | Secondary Proxies | Phase Proxies |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | `build/shots/s331_mitsuba_renderer_native_gap_pass/scenes/frame_0000.xml` | 8 | 20000 | 256 | 256 | 0 |
| 27 | `build/shots/s331_mitsuba_renderer_native_gap_pass/scenes/frame_0004.xml` | 35 | 18576 | 256 | 256 | 0 |
| 47 | `build/shots/s331_mitsuba_renderer_native_gap_pass/scenes/frame_0007.xml` | 55 | 22300 | 964 | 384 | 0 |

## Next

Render this calibrated Mitsuba pass and compare it against the accepted S328 target.
