# S612 Balanced Dual Rescue Full48 Split MS14 Direct Reference Metrics

Generated UTC: `2026-06-21T01:00:00.0287294Z`
Status: `ready`

## Inputs

- S607 frame peak control full48 split MS9 render: `build/shots/s607_mitsuba_scene_depth_native_material_split_ms9_frame_peak_control_full48/render_vs18/mitsuba_render.json`
- S609 gentle low coverage rescue full48 split MS11 render: `build/shots/s609_mitsuba_scene_depth_native_material_split_ms11_gentle_low_coverage_rescue_full48/render_vs18/mitsuba_render.json`
- S611 mid coverage rescue full48 split MS13 render: `build/shots/s611_mitsuba_scene_depth_native_material_split_ms13_mid_coverage_rescue_full48/render_vs18/mitsuba_render.json`
- S612 balanced dual rescue full48 split MS14 render: `build/shots/s612_mitsuba_scene_depth_native_material_split_ms14_balanced_dual_rescue_full48/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

| Candidate | Reference | Frames | Mean MAD | Max MAD | Max Abs | Max MAD Frame | Max Abs Frame |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S607 frame peak control full48 split MS9 | S577 accepted composite | 48 | 3.0432079609267837 | 5.651857638888889 | 176 | 45 | 14 |
| S607 frame peak control full48 split MS9 | S585 scene-depth target | 48 | 3.054593420460391 | 5.6697800925925925 | 175 | 45 | 14 |
| S609 gentle low coverage rescue full48 split MS11 | S577 accepted composite | 48 | 3.0457930919924556 | 5.651857638888889 | 175 | 45 | 14 |
| S609 gentle low coverage rescue full48 split MS11 | S585 scene-depth target | 48 | 3.0571595561128255 | 5.6697800925925925 | 174 | 45 | 14 |
| S611 mid coverage rescue full48 split MS13 | S577 accepted composite | 48 | 3.0469056096750684 | 5.651857638888889 | 175 | 45 | 14 |
| S611 mid coverage rescue full48 split MS13 | S585 scene-depth target | 48 | 3.0582672244727367 | 5.6697800925925925 | 174 | 45 | 14 |
| S612 balanced dual rescue full48 split MS14 | S577 accepted composite | 48 | 3.048554499957133 | 5.651857638888889 | 173 | 45 | 14 |
| S612 balanced dual rescue full48 split MS14 | S585 scene-depth target | 48 | 3.0598990483539095 | 5.6697800925925925 | 172 | 45 | 34 |

## Key Frames

| Candidate | Reference | Output | MAD | Max Abs |
| --- | --- | ---: | ---: | ---: |
| S609 gentle low coverage rescue full48 split MS11 | S577 accepted composite | 14 | 2.1296977880658434 | 175 |
| S609 gentle low coverage rescue full48 split MS11 | S577 accepted composite | 34 | 2.6321373456790123 | 175 |
| S609 gentle low coverage rescue full48 split MS11 | S577 accepted composite | 35 | 2.8249871399176953 | 175 |
| S609 gentle low coverage rescue full48 split MS11 | S585 scene-depth target | 14 | 2.1397942386831277 | 174 |
| S609 gentle low coverage rescue full48 split MS11 | S585 scene-depth target | 34 | 2.638568029835391 | 174 |
| S609 gentle low coverage rescue full48 split MS11 | S585 scene-depth target | 35 | 2.8339731224279836 | 174 |
| S612 balanced dual rescue full48 split MS14 | S577 accepted composite | 14 | 2.1410661008230454 | 173 |
| S612 balanced dual rescue full48 split MS14 | S577 accepted composite | 34 | 2.6407915380658435 | 173 |
| S612 balanced dual rescue full48 split MS14 | S577 accepted composite | 35 | 2.8455272633744855 | 173 |
| S612 balanced dual rescue full48 split MS14 | S585 scene-depth target | 14 | 2.151122685185185 | 170 |
| S612 balanced dual rescue full48 split MS14 | S585 scene-depth target | 34 | 2.6471965020576134 | 172 |
| S612 balanced dual rescue full48 split MS14 | S585 scene-depth target | 35 | 2.854387217078189 | 172 |

## Finding

S611 proves the mid-coverage band rescue hits the intended frame-33..36 region
without touching frame 37 or the high-coverage late frames. It lowers the
frame-34/35 plateau from `175/174` to `173/172`, but the global max abs stays
at `175/174` because frame 14 remains.

S612 combines S611's narrow mid-coverage band rescue with a stronger but still
bounded low-coverage rescue. It preserves S607/S609 max MAD exactly, keeps the
late frame-45/47 behavior unchanged, and improves global max abs to `173/172`.
The trade off is a small mean-MAD increase relative to S609, but S612 remains
substantially better than S604 on mean MAD and max MAD while recovering more
peak-error margin. Promote S612 as the current native-material split baseline.

## Next

Use S612 as the current full48 native-material split baseline. The next visual
pass should switch from scalar response tuning to either spatially localized
screen-region rescue or renderer-side tone/material separation, because the
remaining max-MAD limiter is frame 45 rather than isolated max-abs peaks.
