# S602 Guarded Full48 Split MS5 Direct Reference Metrics

Generated UTC: `2026-06-20T23:55:34.3896395Z`
Status: `ready`

## Inputs

- S601 quiet full48 split MS4 render: `build/shots/s601_mitsuba_scene_depth_native_material_split_ms4_quiet_full48/render_vs18/mitsuba_render.json`
- S602 guarded full48 split MS5 render: `build/shots/s602_mitsuba_scene_depth_native_material_split_ms5_guarded_full48/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

| Candidate | Reference | Frames | Mean MAD | Max MAD | Max Abs |
| --- | --- | ---: | ---: | ---: | ---: |
| S601 quiet full48 split MS4 | S577 accepted composite | 48 | 3.5123040578918037 | 5.91944508744856 | 179 |
| S602 guarded full48 split MS5 | S577 accepted composite | 48 | 3.205035231267147 | 5.944519032921811 | 171 |
| S601 quiet full48 split MS4 | S585 scene-depth target | 48 | 3.520047702867798 | 5.926575360082304 | 175 |
| S602 guarded full48 split MS5 | S585 scene-depth target | 48 | 3.2147581232853226 | 5.954301054526749 | 167 |

## Finding

S602 further reduces the selected response region from 86,400 faces to 67,200
faces across full48, increases localized roughness, and removes tinted
reflectance pressure from the strongest response bins. It keeps 48/48 render
stability, lowers full48 mean MAD against both S577 and S585, and fixes the
S601 max-absolute outlier. The cost is a small max-MAD increase versus S601,
which means one of the selected frames still has a slightly worse average local
gap even though the global mean and peak pixel error improve.

## Next

Use S602 as the current full48 native-material split baseline. The next pass
should either hold this guarded material setting and inspect/publish the
full48 gallery, or run one narrow neighbor with a small face-count recovery
while keeping S577 max abs below the S601 `179` outlier.
