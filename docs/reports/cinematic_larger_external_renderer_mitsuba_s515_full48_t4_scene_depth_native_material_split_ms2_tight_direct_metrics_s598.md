# S598 Tight Split MS2 Direct Reference Metrics

Generated UTC: `2026-06-20T23:32:43.9826654Z`
Status: `ready`

## Inputs

- S596 full-water native XML render: `build/shots/s596_mitsuba_scene_depth_native_material_xml_sample_spp4/render_vs18/mitsuba_render.json`
- S597 localized split MS1 render: `build/shots/s597_mitsuba_scene_depth_native_material_split_ms1_soft/render_vs18/mitsuba_render.json`
- S598 tight split MS2 render: `build/shots/s598_mitsuba_scene_depth_native_material_split_ms2_tight/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

| Candidate | Reference | Mean MAD | Max MAD | Max Abs |
| --- | --- | ---: | ---: | ---: |
| S596 full-water native XML | S577 accepted composite | 19.077447916666667 | 21.961886574074075 | 205 |
| S597 localized split MS1 | S577 accepted composite | 12.761129275977366 | 17.793814943415637 | 204 |
| S598 tight split MS2 | S577 accepted composite | 3.87780647183642 | 5.825584490740741 | 181 |
| S596 full-water native XML | S585 scene-depth target | 19.062724810313785 | 21.960004501028806 | 200 |
| S597 localized split MS1 | S585 scene-depth target | 12.754131060313785 | 17.761696244855965 | 200 |
| S598 tight split MS2 | S585 scene-depth target | 3.875843139146091 | 5.817881944444444 | 176 |

## Finding

S598 is the first native-material XML path in this chain that moves back toward the accepted S577/S585 look while still rendering through Mitsuba. S596 proved the full-water BSDF binding is renderable but too strong. S597 proved alpha-aware localized splitting works but selected too much of the water surface. S598 keeps the localized split path and reduces the selected faces to 24,000 total, dropping direct S577/S585 mean MAD to about 3.88 on the 8-frame sample.

## Next

Use S598 as the current native-material tuning baseline. Continue with a small sweep around MS2: lower response tint/contrast, cap late-frame selected faces below 3000, and compare directly against S577/S585 before scaling beyond 8 frames.
