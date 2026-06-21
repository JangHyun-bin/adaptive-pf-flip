# S607 Frame Peak Control Full48 Split MS9 Direct Reference Metrics

Generated UTC: `2026-06-21T00:29:06.0336334Z`
Status: `ready`

## Inputs

- S602 guarded full48 split MS5 render: `build/shots/s602_mitsuba_scene_depth_native_material_split_ms5_guarded_full48/render_vs18/mitsuba_render.json`
- S604 soft guard full48 split MS7 render: `build/shots/s604_mitsuba_scene_depth_native_material_split_ms7_soft_guard_full48/render_vs18/mitsuba_render.json`
- S605 peak balance full48 split MS8 render: `build/shots/s605_mitsuba_scene_depth_native_material_split_ms8_peak_balance_full48/render_vs18/mitsuba_render.json`
- S607 frame peak control full48 split MS9 render: `build/shots/s607_mitsuba_scene_depth_native_material_split_ms9_frame_peak_control_full48/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

| Candidate | Reference | Frames | Mean MAD | Max MAD | Max Abs | Max MAD Frame | Max Abs Frame |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S602 guarded full48 split MS5 | S577 accepted composite | 48 | 3.205035231267147 | 5.944519032921811 | 171 | 45 | 42 |
| S602 guarded full48 split MS5 | S585 scene-depth target | 48 | 3.2147581232853226 | 5.954301054526749 | 167 | 45 | 42 |
| S604 soft guard full48 split MS7 | S577 accepted composite | 48 | 3.0665762442129627 | 5.926882716049382 | 176 | 45 | 14 |
| S604 soft guard full48 split MS7 | S585 scene-depth target | 48 | 3.0774464431155693 | 5.939676568930041 | 175 | 45 | 14 |
| S605 peak balance full48 split MS8 | S577 accepted composite | 48 | 3.139332534936557 | 5.992344393004116 | 179 | 45 | 42 |
| S605 peak balance full48 split MS8 | S585 scene-depth target | 48 | 3.149561873070988 | 6.003236239711934 | 175 | 45 | 42 |
| S607 frame peak control full48 split MS9 | S577 accepted composite | 48 | 3.0432079609267837 | 5.651857638888889 | 176 | 45 | 14 |
| S607 frame peak control full48 split MS9 | S585 scene-depth target | 48 | 3.054593420460391 | 5.6697800925925925 | 175 | 45 | 14 |

## Finding

S607 improves the S604 full48 baseline on mean MAD and max MAD against both
S577 and S585. The coverage-aware attenuation affects 11 high-coverage frames,
reducing the late-frame selected response from 1200 faces to 924-1033 faces in
the strongest frames. This pulls frame 45 down substantially, which is why max
MAD improves from `5.926882716049382` to `5.651857638888889` against S577 and
from `5.939676568930041` to `5.6697800925925925` against S585.

S607 does not improve the max absolute outlier. The remaining max abs is still
frame 14, with `176` against S577 and `175` against S585, matching S604. That
frame is below the coverage attenuation pivot, so the new control deliberately
does not touch it. Treat S607 as a promoted mean/max-MAD baseline, with a
separate S608 pass needed if max-abs cleanup remains important.

## Next

Promote S607 over S604 for the renderer-native material split baseline. The next
small visual correction should target the frame-14 single-pixel peak path
without undoing S607's high-coverage late-frame improvement.
