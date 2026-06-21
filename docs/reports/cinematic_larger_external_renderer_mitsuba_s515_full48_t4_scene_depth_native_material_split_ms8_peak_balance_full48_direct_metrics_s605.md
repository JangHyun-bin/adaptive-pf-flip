# S605 Peak Balance Full48 Split MS8 Direct Reference Metrics

Generated UTC: `2026-06-21T00:08:29.6184206Z`
Status: `ready`

## Inputs

- S602 guarded full48 split MS5 render: `build/shots/s602_mitsuba_scene_depth_native_material_split_ms5_guarded_full48/render_vs18/mitsuba_render.json`
- S604 soft guard full48 split MS7 render: `build/shots/s604_mitsuba_scene_depth_native_material_split_ms7_soft_guard_full48/render_vs18/mitsuba_render.json`
- S605 peak balance full48 split MS8 render: `build/shots/s605_mitsuba_scene_depth_native_material_split_ms8_peak_balance_full48/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

| Candidate | Reference | Frames | Mean MAD | Max MAD | Max Abs |
| --- | --- | ---: | ---: | ---: | ---: |
| S602 guarded full48 split MS5 | S577 accepted composite | 48 | 3.205035231267147 | 5.944519032921811 | 171 |
| S604 soft guard full48 split MS7 | S577 accepted composite | 48 | 3.0665762442129627 | 5.926882716049382 | 176 |
| S605 peak balance full48 split MS8 | S577 accepted composite | 48 | 3.139332534936557 | 5.992344393004116 | 179 |
| S602 guarded full48 split MS5 | S585 scene-depth target | 48 | 3.2147581232853226 | 5.954301054526749 | 167 |
| S604 soft guard full48 split MS7 | S585 scene-depth target | 48 | 3.0774464431155693 | 5.939676568930041 | 175 |
| S605 peak balance full48 split MS8 | S585 scene-depth target | 48 | 3.149561873070988 | 6.003236239711934 | 175 |

## Finding

S605 attempted to sit between S602 and S604 by restoring a little response area
and reflectance while keeping the material mostly guarded. It is not promoted:
mean MAD regresses versus S604 for both S577 and S585, max MAD regresses
substantially, and S577 max absolute diff returns to the earlier S601 outlier
level of `179`. S604 remains the better full48 baseline for this material
family.

## Next

Keep S604 as the current full48 native-material split baseline. The next
useful step is either publishing/packaging S604 for visual review, or moving
from scalar split tuning to frame-aware peak control so peak error can improve
without losing S604's mean/max-MAD gains.
