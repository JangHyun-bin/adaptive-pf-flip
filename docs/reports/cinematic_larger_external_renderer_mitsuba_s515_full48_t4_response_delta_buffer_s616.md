# S616 Mitsuba Response Delta Buffer

Generated UTC: `2026-06-21T02:01:44.950815+00:00`
Summary JSON: `build/shots/s616_mitsuba_response_delta_buffer_probe/response_delta/response_delta_buffer_summary.json`
Gallery: `build/shots/s616_mitsuba_response_delta_buffer_probe/response_delta/gallery/index.html`
Status: `ready`

## Inputs

- Full render: `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/render_vs18/mitsuba_render.json`
- Base render: `build/shots/s616_mitsuba_response_delta_buffer_probe/base_render/mitsuba_render.json`
- Target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

- Frames: `48`
- Missing references: `0`
- Mean abs delta: `2.78263054323131`
- Max abs delta: `184`
- Changed channel fraction: `0.16185079357424553`
- Reconstruction max abs diff: `0`
- GIF bytes: `46.45 MB`

## Scale Sweep

- Best scale: `0.75`
- Best mean MAD: `2.982389550647291`
- Best max MAD: `5.524723508230453`

| Scale | Mean MAD | Max MAD | Max Abs |
| ---: | ---: | ---: | ---: |
| 0.0 | 3.9582350474751373 | 6.012960390946502 | 171 |
| 0.25 | 3.5357163869598764 | 5.705778677983539 | 152 |
| 0.5 | 3.1747733142575445 | 5.540771604938271 | 140 |
| 0.75 | 2.982389550647291 | 5.524723508230453 | 148 |
| 0.9 | 2.988306970164609 | 5.556688528806585 | 161 |
| 1.0 | 3.050464838391632 | 5.595675154320988 | 172 |
| 1.1 | 3.1570717190715025 | 5.64113683127572 | 185 |
| 1.25 | 3.369008527842078 | 5.745953575102881 | 204 |
| 1.5 | 3.8025017146776405 | 5.9814763374485596 | 215 |

## Frame Samples

| Output | Mean Delta | Max Delta | Strip |
| ---: | ---: | ---: | --- |
| 0 | 2.730716306584362 | 152 | `build/shots/s616_mitsuba_response_delta_buffer_probe/response_delta/strips/frame_0000.png` |
| 24 | 2.6648173868312757 | 150 | `build/shots/s616_mitsuba_response_delta_buffer_probe/response_delta/strips/frame_0024.png` |
| 47 | 2.4687969393004114 | 158 | `build/shots/s616_mitsuba_response_delta_buffer_probe/response_delta/strips/frame_0047.png` |

## Next

Use the best response scale as a cheap compositing gate before adding a renderer-native AOV export.
