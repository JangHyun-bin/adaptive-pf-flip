# S601 Quiet Full48 Split MS4 Direct Reference Metrics

Generated UTC: `2026-06-20T23:51:45.1622422Z`
Status: `ready`

## Inputs

- S600 full48 subtle split MS3 render: `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48/render_vs18/mitsuba_render.json`
- S601 quiet full48 split MS4 render: `build/shots/s601_mitsuba_scene_depth_native_material_split_ms4_quiet_full48/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

| Candidate | Reference | Frames | Mean MAD | Max MAD | Max Abs |
| --- | --- | ---: | ---: | ---: | ---: |
| S600 full48 subtle split MS3 | S577 accepted composite | 48 | 3.9167686096107683 | 5.936532278806585 | 178 |
| S601 quiet full48 split MS4 | S577 accepted composite | 48 | 3.5123040578918037 | 5.91944508744856 | 179 |
| S600 full48 subtle split MS3 | S585 scene-depth target | 48 | 3.921020661865569 | 5.934954989711934 | 176 |
| S601 quiet full48 split MS4 | S585 scene-depth target | 48 | 3.520047702867798 | 5.926575360082304 | 175 |

## Finding

S601 reduces the selected response region from 120,000 faces to 86,400 faces
across full48 and uses a rougher, lower-reflectance localized water response.
This lowers full48 mean MAD substantially against both S577 and S585 while
keeping render stability unchanged at 48/48 frames and failures `0`. The trade
off is that S577 max absolute diff rises by `1` (`178 -> 179`), while S585 max
absolute diff improves by `1` (`176 -> 175`). Visual review confirms the late
frame highlight is quieter than S600 but still more renderer-native than the
accepted image-space references.

## Next

Use S601 as the current full48 native-material split baseline. The next pass
should run a narrow neighborhood around MS4, with either a small selected-face
increase to recover detail without S600's highlight strength or a max-abs-aware
gate that prevents the S577 `179` pixel outlier from growing.
