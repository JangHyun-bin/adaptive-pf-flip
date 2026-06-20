# S600 Full48 Subtle Split MS3 Direct Reference Metrics

Generated UTC: `2026-06-20T23:47:21.0000000Z`
Status: `ready`

## Inputs

- S600 full48 subtle split MS3 render: `build/shots/s600_mitsuba_scene_depth_native_material_split_ms3_subtle_full48/render_vs18/mitsuba_render.json`
- S599 8-frame subtle split MS3 render: `build/shots/s599_mitsuba_scene_depth_native_material_split_ms3_subtle/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

| Candidate | Reference | Frames | Mean MAD | Max MAD | Max Abs |
| --- | --- | ---: | ---: | ---: | ---: |
| S600 full48 subtle split MS3 | S577 accepted composite | 48 | 3.9167686096107683 | 5.936532278806585 | 178 |
| S599 8-frame subtle split MS3 | S577 accepted composite | 8 | 3.833308577674897 | 5.722929526748971 | 178 |
| S600 full48 subtle split MS3 | S585 scene-depth target | 48 | 3.921020661865569 | 5.934954989711934 | 176 |
| S599 8-frame subtle split MS3 | S585 scene-depth target | 8 | 3.8382736143261313 | 5.7325109310699585 | 176 |

## Finding

S600 proves the S599 subtle localized material split can scale from the
representative 8-frame sample to a full48 Mitsuba render without XML failures,
render failures, missing frame references, or max-absolute drift. The full48
mean MAD is slightly worse than the 8-frame S599 sample, and visual review of
the late frames shows a stronger water-surface highlight than S577/S585. Treat
S600 as a full48 stability pass, not a final promotion.

## Next

Use S600 as the full48 stability baseline. The next pass should tune the same
full48 path with slightly weaker localized response, lower selected-face count,
or frame-aware attenuation for late high-coverage frames, then rank by full48
direct S577/S585 metrics before publishing.
