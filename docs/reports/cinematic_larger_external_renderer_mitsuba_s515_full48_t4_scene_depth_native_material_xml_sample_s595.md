# S595 Mitsuba Scene Depth Native Material XML Sample

Generated UTC: `2026-06-20T23:07:55.541329+00:00`
Export JSON: `build/shots/s595_mitsuba_scene_depth_native_material_xml_sample/mitsuba_export.json`
Status: `ready`

## Inputs

- Base export: `build/shots/s572_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water/mitsuba_export.json`
- Material package: `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/native_material_package_summary.json`

## Checks

- Frames exported: `8`
- Missing references: `0`
- Snippet insertions: `8`
- Water ref replacements: `8`
- Package frames matched: `8`
- XML scene bytes: `328.94 KB`

## Frame Samples

| Output | Base XML | Bound XML | Snippet | Water Refs |
| ---: | --- | --- | --- | ---: |
| 0 | `build/shots/s572_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water/scenes/frame_0000.xml` | `build/shots/s595_mitsuba_scene_depth_native_material_xml_sample/scenes/frame_0000.xml` | `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/snippets/frame_0000_scene_depth_material.xml` | 1 |
| 27 | `build/shots/s572_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water/scenes/frame_0004.xml` | `build/shots/s595_mitsuba_scene_depth_native_material_xml_sample/scenes/frame_0004.xml` | `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/snippets/frame_0027_scene_depth_material.xml` | 1 |
| 47 | `build/shots/s572_mitsuba_s515_full48_t4_lfmask_material_tone_dark_water/scenes/frame_0007.xml` | `build/shots/s595_mitsuba_scene_depth_native_material_xml_sample/scenes/frame_0007.xml` | `build/shots/s594_mitsuba_renderer_scene_depth_material_native_material_package/snippets/frame_0047_scene_depth_material.xml` | 1 |

## Next

Validate this XML export and render a bounded sample through the native Mitsuba backend.
