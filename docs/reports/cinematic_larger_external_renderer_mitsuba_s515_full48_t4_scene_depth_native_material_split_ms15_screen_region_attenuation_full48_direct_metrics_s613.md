# S613 Screen Region Attenuation Full48 Split MS15 Direct Reference Metrics

Generated UTC: `2026-06-21T01:16:33.3774315Z`
Status: `ready`

## Inputs

- S607 frame peak control full48 split MS9 render: `build/shots/s607_mitsuba_scene_depth_native_material_split_ms9_frame_peak_control_full48/render_vs18/mitsuba_render.json`
- S609 gentle low coverage rescue full48 split MS11 render: `build/shots/s609_mitsuba_scene_depth_native_material_split_ms11_gentle_low_coverage_rescue_full48/render_vs18/mitsuba_render.json`
- S612 balanced dual rescue full48 split MS14 render: `build/shots/s612_mitsuba_scene_depth_native_material_split_ms14_balanced_dual_rescue_full48/render_vs18/mitsuba_render.json`
- S613 screen region attenuation full48 split MS15 render: `build/shots/s613_mitsuba_scene_depth_native_material_split_ms15_screen_region_attenuation_full48/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Checks

| Candidate | Reference | Frames | Mean MAD | Max MAD | Max Abs | Max MAD Frame | Max Abs Frame |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S607 frame peak control full48 split MS9 | S577 accepted composite | 48 | 3.043207960926783 | 5.651857638888889 | 176 | 45 | 14 |
| S607 frame peak control full48 split MS9 | S585 scene-depth target | 48 | 3.054593420460391 | 5.6697800925925925 | 175 | 45 | 14 |
| S609 gentle low coverage rescue full48 split MS11 | S577 accepted composite | 48 | 3.0457930919924556 | 5.651857638888889 | 175 | 45 | 14 |
| S609 gentle low coverage rescue full48 split MS11 | S585 scene-depth target | 48 | 3.0571595561128255 | 5.6697800925925925 | 174 | 45 | 14 |
| S612 balanced dual rescue full48 split MS14 | S577 accepted composite | 48 | 3.048554499957133 | 5.651857638888889 | 173 | 45 | 14 |
| S612 balanced dual rescue full48 split MS14 | S585 scene-depth target | 48 | 3.0598990483539095 | 5.6697800925925925 | 172 | 45 | 34 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 48 | 3.0386621897505144 | 5.580354295267489 | 173 | 45 | 14 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 48 | 3.050184823495371 | 5.599894547325103 | 172 | 45 | 34 |

## Late Frames

| Candidate | Reference | Output | MAD | Max Abs |
| --- | --- | ---: | ---: | ---: |
| S612 balanced dual rescue full48 split MS14 | S577 accepted composite | 42 | 4.920345293209877 | 161 |
| S612 balanced dual rescue full48 split MS14 | S577 accepted composite | 43 | 4.897523791152263 | 161 |
| S612 balanced dual rescue full48 split MS14 | S577 accepted composite | 44 | 5.501527649176955 | 151 |
| S612 balanced dual rescue full48 split MS14 | S577 accepted composite | 45 | 5.651857638888889 | 151 |
| S612 balanced dual rescue full48 split MS14 | S577 accepted composite | 46 | 5.619966563786008 | 162 |
| S612 balanced dual rescue full48 split MS14 | S577 accepted composite | 47 | 5.578572273662552 | 164 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 42 | 4.830065200617284 | 161 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 43 | 4.808717721193416 | 161 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 44 | 5.421139403292181 | 142 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 45 | 5.580354295267489 | 156 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 46 | 5.543792438271605 | 156 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 47 | 5.510895576131687 | 153 |
| S612 balanced dual rescue full48 split MS14 | S585 scene-depth target | 42 | 4.93033024691358 | 157 |
| S612 balanced dual rescue full48 split MS14 | S585 scene-depth target | 43 | 4.914694958847737 | 157 |
| S612 balanced dual rescue full48 split MS14 | S585 scene-depth target | 44 | 5.519514660493827 | 146 |
| S612 balanced dual rescue full48 split MS14 | S585 scene-depth target | 45 | 5.6697800925925925 | 147 |
| S612 balanced dual rescue full48 split MS14 | S585 scene-depth target | 46 | 5.637929783950617 | 158 |
| S612 balanced dual rescue full48 split MS14 | S585 scene-depth target | 47 | 5.610241769547325 | 159 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 42 | 4.840845936213992 | 157 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 43 | 4.827087319958848 | 157 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 44 | 5.440850565843621 | 138 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 45 | 5.599894547325103 | 152 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 46 | 5.563603137860082 | 152 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 47 | 5.543927083333333 | 148 |

## Screen Region Gate

S613 applies a bounded, deterministic screen-region attenuation to the split
water material response only for output frames `42..47` with layer coverage
`0.15..0.20`. The selected region is normalized screen box
`x=0.25..0.625`, `y=0.333..0.667`, with strength `0.10`.

The export check reports `6` attenuated frames, `5457` candidate faces, `522`
dropped response faces, and max drop fraction `0.09924487594390508`.

## Finding

S613 improves the remaining late-frame MAD limiter without giving back the
peak-error margin recovered in S612. Against S577, mean MAD drops from
`3.048554499957133` to `3.0386621897505144` and frame-45 max MAD drops from
`5.651857638888889` to `5.580354295267489`; max abs remains `173`. Against
S585, mean MAD drops from `3.0598990483539095` to `3.050184823495371` and
frame-45 max MAD drops from `5.6697800925925925` to `5.599894547325103`; max
abs remains `172`.

Promote S613 as the current native-material split baseline if the sequence
compare gallery does not show visible late-frame flicker. The remaining
frame-45 max MAD is still the global limiter, so the next pass should use a
more semantic region model or renderer-side water/response separation instead
of only scalar global tuning.

## Visual Proof

- S613 render gallery: `build/shots/s613_mitsuba_scene_depth_native_material_split_ms15_screen_region_attenuation_full48/gallery/index.html`
- S613 sequence comparison gallery: `build/shots/s613_mitsuba_scene_depth_native_material_split_ms15_screen_region_attenuation_full48/sequence_compare_s577_s585_s607_s609_s612/gallery/index.html`

## Next

Use S613 as the next screen-region material-response baseline. The next visual
step should either automate region derivation from signed-error maps or move to
renderer-native separated water/secondary-response buffers so local corrections
can be applied without guessing screen boxes manually.
