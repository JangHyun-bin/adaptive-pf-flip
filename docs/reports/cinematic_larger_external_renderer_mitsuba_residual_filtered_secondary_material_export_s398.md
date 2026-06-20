# S398 Mitsuba Residual Filtered Secondary Material Export

Generated UTC: `2026-06-20T08:02:40.898991+00:00`
Export JSON: `build/shots/s398_mitsuba_residual_filtered_secondary_material/mitsuba_export.json`
Status: `ready`
Target renderer: `mitsuba`
Execution mode: `xml_export_only`

## Inputs

- Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list: `build/shots/s398_mitsuba_residual_filtered_secondary_material/mitsuba_render_commands.txt`
- Mitsuba command: `mitsuba`
- Mitsuba mode: `scalar_rgb`
- Samples override: `32`
- Camera position override: `[18.0, 20.0, 58.0]`
- Camera target override: `[18.0, 8.0, 14.0]`
- Camera FOV override: `34.0`
- Water alpha override: `0.014`
- Water int IOR override: `None`
- Water ext IOR override: `None`
- Water specular transmittance: `None`
- Key light radiance: `None`
- Key light position: `None`
- Key light target: `None`
- Key light scale: `None`
- Secondary opacity: `None`
- Secondary 3D sidecar: `{'repo_path': 'build/shots/s398_mitsuba_residual_filtered_sidecar/secondary_3d_sidecar.json', 'sha256': '87839d5dc7d16f7658e44a61e4ed3f074faca7c5a9e9fce22ecf1a1558d03787', 'secondary_particles': 865}`
- Secondary 3D radius scale: `0.2`
- Secondary 3D depth radius falloff: `0.8`
- Secondary 3D channel opacity: `{'spray': 0.001, 'foam': 0.015, 'bubble': 0.01, 'droplet': 0.001}`
- Secondary channel reflectance scale: `None`
- Secondary halo opacity: `None`
- Secondary halo radius scale: `2.2`
- Secondary mist opacity: `None`
- Secondary mist radius scale: `5.0`
- Secondary mist shells: `1`
- Secondary mist shell spacing: `0.55`
- Secondary billboard opacity: `0.002`
- Secondary billboard radius scale: `2.2`
- Secondary billboard aspect: `1.2`

## Checks

- Frames exported: `8`
- Failures: `0`
- Water mesh bytes: `13.52 MB`
- XML scene bytes: `436.30 KB`
- Secondary proxies emitted: `865`
- Secondary halo proxies emitted: `0`
- Secondary mist proxies emitted: `0`
- Secondary billboard proxies emitted: `865`
- Secondary particles available: `865`
- Phase volume proxies emitted: `0`
- Phase volume cells available: `0`

## Frame Samples

| Output | XML Scene | Sequence | Water Faces | Secondary Total | Secondary Proxies | Mist Proxies | Billboard Proxies | Phase Proxies |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | `build/shots/s398_mitsuba_residual_filtered_secondary_material/scenes/frame_0000.xml` | 8 | 20000 | 256 | 132 | 0 | 132 | 0 |
| 27 | `build/shots/s398_mitsuba_residual_filtered_secondary_material/scenes/frame_0004.xml` | 35 | 18576 | 256 | 35 | 0 | 35 | 0 |
| 47 | `build/shots/s398_mitsuba_residual_filtered_secondary_material/scenes/frame_0007.xml` | 55 | 22300 | 964 | 396 | 0 | 396 | 0 |

## Next

Render and compare the residual-filtered native secondary material candidate.
