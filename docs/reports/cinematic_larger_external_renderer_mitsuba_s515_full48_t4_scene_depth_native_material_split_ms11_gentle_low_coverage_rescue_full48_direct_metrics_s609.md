# S609 Gentle Low Coverage Rescue Full48 Split MS11 Direct Reference Metrics

Generated UTC: `2026-06-21T00:44:12.1252722Z`
Status: `ready`

## Inputs

- S602 guarded full48 split MS5 render: `build/shots/s602_mitsuba_scene_depth_native_material_split_ms5_guarded_full48/render_vs18/mitsuba_render.json`
- S604 soft guard full48 split MS7 render: `build/shots/s604_mitsuba_scene_depth_native_material_split_ms7_soft_guard_full48/render_vs18/mitsuba_render.json`
- S607 frame peak control full48 split MS9 render: `build/shots/s607_mitsuba_scene_depth_native_material_split_ms9_frame_peak_control_full48/render_vs18/mitsuba_render.json`
- S608 low coverage rescue full48 split MS10 render: `build/shots/s608_mitsuba_scene_depth_native_material_split_ms10_low_coverage_rescue_full48/render_vs18/mitsuba_render.json`
- S609 gentle low coverage rescue full48 split MS11 render: `build/shots/s609_mitsuba_scene_depth_native_material_split_ms11_gentle_low_coverage_rescue_full48/render_vs18/mitsuba_render.json`
- S610 minimal low coverage rescue full48 split MS12 render: `build/shots/s610_mitsuba_scene_depth_native_material_split_ms12_minimal_low_coverage_rescue_full48/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

| Candidate | Reference | Frames | Mean MAD | Max MAD | Max Abs | Max MAD Frame | Max Abs Frame |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S602 guarded full48 split MS5 | S577 accepted composite | 48 | 3.205035231267147 | 5.944519032921811 | 171 | 45 | 42 |
| S602 guarded full48 split MS5 | S585 scene-depth target | 48 | 3.2147581232853226 | 5.954301054526749 | 167 | 45 | 42 |
| S604 soft guard full48 split MS7 | S577 accepted composite | 48 | 3.0665762442129627 | 5.926882716049382 | 176 | 45 | 14 |
| S604 soft guard full48 split MS7 | S585 scene-depth target | 48 | 3.0774464431155693 | 5.939676568930041 | 175 | 45 | 14 |
| S607 frame peak control full48 split MS9 | S577 accepted composite | 48 | 3.0432079609267837 | 5.651857638888889 | 176 | 45 | 14 |
| S607 frame peak control full48 split MS9 | S585 scene-depth target | 48 | 3.054593420460391 | 5.6697800925925925 | 175 | 45 | 14 |
| S608 low coverage rescue full48 split MS10 | S577 accepted composite | 48 | 3.0633944723079565 | 5.651857638888889 | 175 | 45 | 34 |
| S608 low coverage rescue full48 split MS10 | S585 scene-depth target | 48 | 3.074621967163923 | 5.6697800925925925 | 174 | 45 | 34 |
| S609 gentle low coverage rescue full48 split MS11 | S577 accepted composite | 48 | 3.0457930919924556 | 5.651857638888889 | 175 | 45 | 14 |
| S609 gentle low coverage rescue full48 split MS11 | S585 scene-depth target | 48 | 3.0571595561128255 | 5.6697800925925925 | 174 | 45 | 14 |
| S610 minimal low coverage rescue full48 split MS12 | S577 accepted composite | 48 | 3.045021071780693 | 5.651857638888889 | 176 | 45 | 14 |
| S610 minimal low coverage rescue full48 split MS12 | S585 scene-depth target | 48 | 3.056393108603395 | 5.6697800925925925 | 175 | 45 | 14 |

## Finding

S608 proves that low-coverage highlight rescue can fix the frame-14 max-abs
outlier, but the rescue is too strong: frame 14 drops to `150/147` max abs
against S577/S585, while full48 mean MAD regresses close to S604. S610 proves
the lower bound: a max rescue of `0.08` is too weak and leaves the S607
`176/175` max-abs peak unchanged.

S609 is the best tested compromise. It keeps S607's max MAD exactly unchanged
against both S577 and S585, improves max abs from `176/175` to `175/174`, and
keeps the full48 mean-MAD regression small (`+0.0025851310656719` against S577
and `+0.0025661356524345` against S585 relative to S607). It remains materially
better than S604 on mean MAD and max MAD, while recovering one level of peak
error margin. Promote S609 as the current native-material split baseline.

## Next

Use S609 as the current full48 native-material split baseline. The next visual
pass should target the remaining frame-34/35 max-abs plateau only if it does
not disturb S609's frame-45 max-MAD and high-coverage late-frame improvements.
