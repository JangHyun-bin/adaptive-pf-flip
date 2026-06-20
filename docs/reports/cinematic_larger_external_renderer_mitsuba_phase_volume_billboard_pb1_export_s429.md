# S429 Mitsuba Phase Volume Billboard PB1 Export

Generated UTC: `2026-06-20T12:00:54.323421+00:00`
Export JSON: `build/shots/s429_mitsuba_phase_volume_billboard_pb1/mitsuba_export.json`
Status: `ready`
Target renderer: `mitsuba`
Execution mode: `xml_export_only`

## Inputs

- Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list: `build/shots/s429_mitsuba_phase_volume_billboard_pb1/mitsuba_render_commands.txt`
- Mitsuba command: `mitsuba`
- Mitsuba mode: `scalar_rgb`
- Samples override: `32`
- Camera position override: `[18.0, 20.0, 58.0]`
- Camera target override: `[18.0, 8.0, 14.0]`
- Camera FOV override: `34.0`
- Water alpha override: `0.014`
- Water distribution: `None`
- Water int IOR override: `None`
- Water ext IOR override: `None`
- Water specular transmittance: `None`
- Key light radiance: `None`
- Key light position: `None`
- Key light target: `None`
- Key light scale: `None`
- Secondary opacity: `None`
- Secondary 3D sidecar: `{'repo_path': 'build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d_sidecar.json', 'sha256': '9f5850e964db0a8be1161367551e1186da4435de171aec5ec45431e930944bd3', 'secondary_particles': 2877}`
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
- Phase volume shape mode: `billboard`
- Phase volume opacity: `None`
- Phase volume billboard opacity: `0.01`
- Phase volume billboard radius scale: `4.0`
- Phase volume billboard aspect: `1.4`
- Phase volume reflectance: `[0.18, 0.42, 0.72]`

## Checks

- Frames exported: `8`
- Failures: `0`
- Water mesh bytes: `13.52 MB`
- XML scene bytes: `2.40 MB`
- Secondary proxies emitted: `2877`
- Secondary halo proxies emitted: `0`
- Secondary mist proxies emitted: `0`
- Secondary billboard proxies emitted: `2877`
- Secondary particles available: `2877`
- Phase volume proxies emitted: `4096`
- Phase volume sphere proxies emitted: `0`
- Phase volume billboard proxies emitted: `4096`
- Phase volume cells available: `43635`

## Frame Samples

| Output | XML Scene | Sequence | Water Faces | Secondary Total | Secondary Proxies | Mist Proxies | Billboard Proxies | Phase Proxies | Phase Spheres | Phase Billboards |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | `build/shots/s429_mitsuba_phase_volume_billboard_pb1/scenes/frame_0000.xml` | 8 | 20000 | 256 | 256 | 0 | 256 | 512 | 0 | 512 |
| 27 | `build/shots/s429_mitsuba_phase_volume_billboard_pb1/scenes/frame_0004.xml` | 35 | 18576 | 256 | 256 | 0 | 256 | 512 | 0 | 512 |
| 47 | `build/shots/s429_mitsuba_phase_volume_billboard_pb1/scenes/frame_0007.xml` | 55 | 22300 | 964 | 964 | 0 | 964 | 512 | 0 | 512 |

## Next

Validate, render, and compare PB1 against PV2 and SS1.
