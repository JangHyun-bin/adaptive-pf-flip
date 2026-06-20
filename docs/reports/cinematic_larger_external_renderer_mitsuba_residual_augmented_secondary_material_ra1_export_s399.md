# S399 Mitsuba Residual Augmented Secondary Material RA1 Export

Generated UTC: `2026-06-20T08:07:03.949805+00:00`
Export JSON: `build/shots/s399_mitsuba_residual_augmented_secondary_material_ra1/mitsuba_export.json`
Status: `ready`
Target renderer: `mitsuba`
Execution mode: `xml_export_only`

## Inputs

- Adapter manifest: `build/shots/s308_larger_external_renderer_generic_adapter/adapter_manifest.json`
- Command list: `build/shots/s399_mitsuba_residual_augmented_secondary_material_ra1/mitsuba_render_commands.txt`
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
- Secondary 3D sidecar: `{'repo_path': 'build/shots/s399_mitsuba_residual_augmented_sidecar_ra1/secondary_3d_sidecar.json', 'sha256': 'ef76dfeced4a273918d7feaf3013257bbe715315b573b87fa64c3d6722cd288b', 'secondary_particles': 3742}`
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
- XML scene bytes: `1.75 MB`
- Secondary proxies emitted: `3742`
- Secondary halo proxies emitted: `0`
- Secondary mist proxies emitted: `0`
- Secondary billboard proxies emitted: `3742`
- Secondary particles available: `3742`
- Phase volume proxies emitted: `0`
- Phase volume cells available: `0`

## Frame Samples

| Output | XML Scene | Sequence | Water Faces | Secondary Total | Secondary Proxies | Mist Proxies | Billboard Proxies | Phase Proxies |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | `build/shots/s399_mitsuba_residual_augmented_secondary_material_ra1/scenes/frame_0000.xml` | 8 | 20000 | 256 | 388 | 0 | 388 | 0 |
| 27 | `build/shots/s399_mitsuba_residual_augmented_secondary_material_ra1/scenes/frame_0004.xml` | 35 | 18576 | 256 | 291 | 0 | 291 | 0 |
| 47 | `build/shots/s399_mitsuba_residual_augmented_secondary_material_ra1/scenes/frame_0007.xml` | 55 | 22300 | 964 | 1360 | 0 | 1360 | 0 |

## Next

Render and compare the residual-augmented native secondary material candidate.
