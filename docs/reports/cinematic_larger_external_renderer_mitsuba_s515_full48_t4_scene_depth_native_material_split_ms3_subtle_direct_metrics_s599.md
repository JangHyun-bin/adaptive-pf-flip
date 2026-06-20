# S599 Subtle Split MS3 Direct Reference Metrics

Generated UTC: `2026-06-20T23:39:51.4206256Z`
Status: `ready`

## Inputs

- S596 full-water native XML render: `build/shots/s596_mitsuba_scene_depth_native_material_xml_sample_spp4/render_vs18/mitsuba_render.json`
- S597 localized split MS1 render: `build/shots/s597_mitsuba_scene_depth_native_material_split_ms1_soft/render_vs18/mitsuba_render.json`
- S598 tight split MS2 render: `build/shots/s598_mitsuba_scene_depth_native_material_split_ms2_tight/render_vs18/mitsuba_render.json`
- S599 subtle split MS3 render: `build/shots/s599_mitsuba_scene_depth_native_material_split_ms3_subtle/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

| Candidate | Reference | Mean MAD | Max MAD | Max Abs |
| --- | --- | ---: | ---: | ---: |
| S596 full-water native XML | S577 accepted composite | 19.077447916666667 | 21.961886574074075 | 205 |
| S597 localized split MS1 | S577 accepted composite | 12.761129275977366 | 17.793814943415637 | 204 |
| S598 tight split MS2 | S577 accepted composite | 3.87780647183642 | 5.825584490740741 | 181 |
| S599 subtle split MS3 | S577 accepted composite | 3.833308577674897 | 5.722929526748971 | 178 |
| S596 full-water native XML | S585 scene-depth target | 19.062724810313785 | 21.960004501028806 | 200 |
| S597 localized split MS1 | S585 scene-depth target | 12.754131060313785 | 17.761696244855965 | 200 |
| S598 tight split MS2 | S585 scene-depth target | 3.875843139146091 | 5.817881944444444 | 176 |
| S599 subtle split MS3 | S585 scene-depth target | 3.8382736143261313 | 5.7325109310699585 | 176 |

## Finding

S599 keeps the localized renderer-native material split path but makes the
response weaker and slightly tighter than S598. It renders cleanly through the
same Mitsuba SPP4 sample path, selects 20,000 response faces across the 8-frame
sample, and improves the direct S577/S585 mean MAD over S598 by a small margin.
The legacy broad S328 target gap remains worse than S596/S597, so S599 should
be treated as the current localized native-material tuning baseline rather than
as a full48 visual promotion.

## Next

Use S599 as the current native-material split baseline. The next pass should
either extend this subtle MS3 setting to a longer/full48 sample for stability,
or sweep a very narrow neighborhood around `face_limit=2500`, response alpha,
and bin alpha while continuing to rank by direct S577/S585 metrics.
