# S604 Soft Guard Full48 Split MS7 Direct Reference Metrics

Generated UTC: `2026-06-21T00:03:39.4229443Z`
Status: `ready`

## Inputs

- S602 guarded full48 split MS5 render: `build/shots/s602_mitsuba_scene_depth_native_material_split_ms5_guarded_full48/render_vs18/mitsuba_render.json`
- S603 detail recovery full48 split MS6 render: `build/shots/s603_mitsuba_scene_depth_native_material_split_ms6_detail_recovery_full48/render_vs18/mitsuba_render.json`
- S604 soft guard full48 split MS7 render: `build/shots/s604_mitsuba_scene_depth_native_material_split_ms7_soft_guard_full48/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

| Candidate | Reference | Frames | Mean MAD | Max MAD | Max Abs |
| --- | --- | ---: | ---: | ---: | ---: |
| S602 guarded full48 split MS5 | S577 accepted composite | 48 | 3.205035231267147 | 5.944519032921811 | 171 |
| S603 detail recovery full48 split MS6 | S577 accepted composite | 48 | 3.365041460369513 | 5.936041023662551 | 171 |
| S604 soft guard full48 split MS7 | S577 accepted composite | 48 | 3.0665762442129627 | 5.926882716049382 | 176 |
| S602 guarded full48 split MS5 | S585 scene-depth target | 48 | 3.2147581232853226 | 5.954301054526749 | 167 |
| S603 detail recovery full48 split MS6 | S585 scene-depth target | 48 | 3.374113069594479 | 5.94494212962963 | 167 |
| S604 soft guard full48 split MS7 | S585 scene-depth target | 48 | 3.0774464431155693 | 5.939676568930041 | 175 |

## Finding

S603 confirms that recovering selected faces from S602 can improve max MAD a
little, but it worsens mean MAD enough that it should not replace S602. S604
moves the other direction: it softens and narrows the response further. That
improves full48 mean MAD and max MAD against both S577 and S585. The trade off
is peak error: S604 max abs is worse than S602 (`171 -> 176` against S577 and
`167 -> 175` against S585), but it stays below the S601 S577 outlier of `179`.
On the visual strip, S604 also reads less over-highlighted than S603 while
remaining close to S602.

## Next

Use S604 as the current full48 native-material split baseline. The next pass
should treat S604 as the publishing candidate or run one max-abs-aware neighbor
that preserves S604's lower mean MAD while pulling the S585/S577 peak errors
back toward S602.
