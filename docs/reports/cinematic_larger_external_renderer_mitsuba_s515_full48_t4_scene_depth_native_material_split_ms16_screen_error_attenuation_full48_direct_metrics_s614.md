# S614 Screen Error Attenuation Full48 Split MS16 Direct Reference Metrics

Generated UTC: `2026-06-21T01:32:39.5466907Z`
Status: `ready`

## Inputs

- S612 balanced dual rescue full48 split MS14 render: `build/shots/s612_mitsuba_scene_depth_native_material_split_ms14_balanced_dual_rescue_full48/render_vs18/mitsuba_render.json`
- S613 screen region attenuation full48 split MS15 render: `build/shots/s613_mitsuba_scene_depth_native_material_split_ms15_screen_region_attenuation_full48/render_vs18/mitsuba_render.json`
- S614 screen error attenuation full48 split MS16 render: `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`
- S614 signed-error input gap: `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/s613_to_s585_gap/renderer_target_gap_summary.json`
- S614 signed-gap analysis: `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/signed_gap_analysis/signed_target_gap_analysis.json`

## Checks

| Candidate | Reference | Frames | Mean MAD | Max MAD | Max Abs | Max MAD Frame | Max Abs Frame |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S612 balanced dual rescue full48 split MS14 | S577 accepted composite | 48 | 3.048554499957133 | 5.651857638888889 | 173 | 45 | 14 |
| S612 balanced dual rescue full48 split MS14 | S585 scene-depth target | 48 | 3.0598990483539095 | 5.6697800925925925 | 172 | 45 | 34 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 48 | 3.0386621897505144 | 5.580354295267489 | 173 | 45 | 14 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 48 | 3.050184823495371 | 5.599894547325103 | 172 | 45 | 34 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 48 | 3.038890683942044 | 5.5758995627572014 | 173 | 45 | 14 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 48 | 3.050464838391632 | 5.595675154320989 | 172 | 45 | 34 |

## Late Frames

| Candidate | Reference | Output | MAD | Max Abs |
| --- | --- | ---: | ---: | ---: |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 42 | 4.830065200617284 | 161 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 43 | 4.808717721193416 | 161 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 44 | 5.421139403292181 | 142 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 45 | 5.580354295267489 | 156 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 46 | 5.543792438271605 | 156 |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 47 | 5.510895576131687 | 153 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 42 | 4.812719135802469 | 161 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 43 | 4.791305169753086 | 161 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 44 | 5.470202803497942 | 151 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 45 | 5.5758995627572014 | 153 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 46 | 5.541238940329218 | 151 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 47 | 5.514565715020576 | 154 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 42 | 4.840845936213992 | 157 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 43 | 4.827087319958848 | 157 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 44 | 5.440850565843621 | 138 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 45 | 5.599894547325103 | 152 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 46 | 5.563603137860082 | 152 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 47 | 5.543927083333333 | 148 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 42 | 4.823734696502058 | 157 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 43 | 4.810139274691358 | 157 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 44 | 5.4906390174897115 | 146 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 45 | 5.595675154320989 | 149 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 46 | 5.56149279835391 | 152 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 47 | 5.547967849794239 | 149 |

## Screen Error Gate

S614 uses the S613-to-S585 full48 target gap as a signed-error field and samples
that field at each selected split-water response face. It drops only response
faces whose projected luma delta says the actual render is too bright:

- Gap input: `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/s613_to_s585_gap/renderer_target_gap_summary.json`
- Strength: `0.30`
- Negative threshold: `8`
- Negative width: `48`
- Max drop fraction: `0.10`
- Coverage gate: `0.15..0.20`
- Output frame gate: `42..47`

The export check reports `6` attenuated frames, `5806` sampled faces, `3301`
candidate faces, `532` dropped response faces, and max drop fraction
`0.10032362459546926`.

## Finding

S614 replaces S613's hand-selected screen box with face-level signed-error
sampling. It does not dominate S613 on every metric: S613 keeps a slightly lower
mean MAD (`3.0386621897505144` vs `3.038890683942044` against S577, and
`3.050184823495371` vs `3.050464838391632` against S585). S614 does improve the
remaining global limiter, lowering frame-45 max MAD from `5.580354295267489` to
`5.5758995627572014` against S577 and from `5.599894547325103` to
`5.595675154320989` against S585. Max abs remains unchanged at `173/172`.

Treat S614 as the preferred direction for the next renderer-native pass because
it reaches S613-level quality without a manually guessed screen box. Keep S613
as the slightly better mean-MAD reference until visual review accepts the S614
late-frame tradeoff.

## Visual Proof

- S614 render gallery: `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/gallery/index.html`
- S614 sequence comparison gallery: `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/sequence_compare_s577_s585_s612_s613/gallery/index.html`
- S614 output gap gallery: `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/s614_to_s585_gap/gallery/assets/shot.gif`

## Next

Move from destructive response-face removal to a separated water/response buffer
or per-bin attenuation path. S614 proves the signed-error field can drive local
renderer-native decisions, but the next pass should attenuate material response
continuously instead of removing selected mesh faces.
