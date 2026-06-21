# S615 Screen Error Material Attenuation Full48 Split MS17 Direct Reference Metrics

Generated UTC: `2026-06-21T01:45:06.4580775Z`
Status: `ready`

## Inputs

- S613 screen region attenuation full48 split MS15 render: `build/shots/s613_mitsuba_scene_depth_native_material_split_ms15_screen_region_attenuation_full48/render_vs18/mitsuba_render.json`
- S614 screen error attenuation full48 split MS16 render: `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/render_vs18/mitsuba_render.json`
- S615 screen error material attenuation full48 split MS17 render: `build/shots/s615_mitsuba_scene_depth_native_material_split_ms17_screen_error_material_attenuation_full48/render_vs18/mitsuba_render.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene-depth target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`
- S615 signed-error input gap: `build/shots/s614_mitsuba_scene_depth_native_material_split_ms16_screen_error_attenuation_full48/s613_to_s585_gap/renderer_target_gap_summary.json`

## Checks

| Candidate | Reference | Frames | Mean MAD | Max MAD | Max Abs | Max MAD Frame | Max Abs Frame |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S613 screen region attenuation full48 split MS15 | S577 accepted composite | 48 | 3.0386621897505144 | 5.580354295267489 | 173 | 45 | 14 |
| S613 screen region attenuation full48 split MS15 | S585 scene-depth target | 48 | 3.050184823495371 | 5.599894547325103 | 172 | 45 | 34 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 48 | 3.038890683942044 | 5.5758995627572014 | 173 | 45 | 14 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 48 | 3.050464838391632 | 5.595675154320989 | 172 | 45 | 34 |
| S615 screen error material attenuation full48 split MS17 | S577 accepted composite | 48 | 3.049201630015432 | 5.654789737654322 | 173 | 45 | 14 |
| S615 screen error material attenuation full48 split MS17 | S585 scene-depth target | 48 | 3.0605547785922496 | 5.672728909465021 | 172 | 45 | 34 |

## Late Frames

| Candidate | Reference | Output | MAD | Max Abs |
| --- | --- | ---: | ---: | ---: |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 42 | 4.812719135802469 | 161 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 43 | 4.791305169753086 | 161 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 44 | 5.470202803497942 | 151 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 45 | 5.5758995627572014 | 153 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 46 | 5.541238940329218 | 151 |
| S614 screen error attenuation full48 split MS16 | S577 accepted composite | 47 | 5.514565715020576 | 154 |
| S615 screen error material attenuation full48 split MS17 | S577 accepted composite | 42 | 4.927975951646091 | 161 |
| S615 screen error material attenuation full48 split MS17 | S577 accepted composite | 43 | 4.903107638888889 | 161 |
| S615 screen error material attenuation full48 split MS17 | S577 accepted composite | 44 | 5.506565586419753 | 151 |
| S615 screen error material attenuation full48 split MS17 | S577 accepted composite | 45 | 5.654789737654322 | 151 |
| S615 screen error material attenuation full48 split MS17 | S577 accepted composite | 46 | 5.622279320987654 | 163 |
| S615 screen error material attenuation full48 split MS17 | S577 accepted composite | 47 | 5.586136574074074 | 165 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 42 | 4.823734696502058 | 157 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 43 | 4.810139274691358 | 157 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 44 | 5.4906390174897115 | 146 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 45 | 5.595675154320989 | 149 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 46 | 5.56149279835391 | 152 |
| S614 screen error attenuation full48 split MS16 | S585 scene-depth target | 47 | 5.547967849794239 | 149 |
| S615 screen error material attenuation full48 split MS17 | S585 scene-depth target | 42 | 4.938210133744856 | 157 |
| S615 screen error material attenuation full48 split MS17 | S585 scene-depth target | 43 | 4.920530221193416 | 157 |
| S615 screen error material attenuation full48 split MS17 | S585 scene-depth target | 44 | 5.524768518518518 | 146 |
| S615 screen error material attenuation full48 split MS17 | S585 scene-depth target | 45 | 5.672728909465021 | 147 |
| S615 screen error material attenuation full48 split MS17 | S585 scene-depth target | 46 | 5.639997685185185 | 159 |
| S615 screen error material attenuation full48 split MS17 | S585 scene-depth target | 47 | 5.617730195473251 | 160 |

## Material Gate

S615 keeps all response faces and uses the S613-to-S585 signed-error field to
split selected response faces into attenuated material bins:

- Strength: `0.30`
- Min material scale: `0.65`
- Alpha boost: `0.10`
- Negative threshold: `8`
- Negative width: `48`
- Coverage gate: `0.15..0.20`
- Output frame gate: `42..47`

The export check reports `6` material-attenuated frames, `5806` sampled faces,
`3301` candidate faces, `3297` attenuated faces, min scale `0.7`, and mean
applied scale `0.8417577422656962`. Response faces are preserved at `56058`;
no screen-error face drops are used.

## Finding

S615 should not be promoted. The new continuous material path is operational
and validates correctly, but roughdielectric reflectance scaling regresses the
late-frame error. Against S585, max MAD worsens from S614's
`5.595675154320989` to `5.672728909465021`, and mean MAD worsens from
`3.050464838391632` to `3.0605547785922496`. Against S577, max MAD worsens
from `5.5758995627572014` to `5.654789737654322`.

The result is still useful: it proves that the next renderer-native path should
not be another roughdielectric scalar material tweak. Keep S614 as the current
automatic local-control direction and move next to separated water/response
buffers or an explicit response AOV where local correction can be applied
without distorting the base water material.

## Visual Proof

- S615 render gallery: `build/shots/s615_mitsuba_scene_depth_native_material_split_ms17_screen_error_material_attenuation_full48/gallery/index.html`
- S615 sequence comparison gallery: `build/shots/s615_mitsuba_scene_depth_native_material_split_ms17_screen_error_material_attenuation_full48/sequence_compare_s577_s585_s613_s614/gallery/index.html`
- S615 output gap: `build/shots/s615_mitsuba_scene_depth_native_material_split_ms17_screen_error_material_attenuation_full48/s615_to_s585_gap/renderer_target_gap_summary.json`

## Next

Build a separated response-buffer probe: render or export base water and
response water as separately inspectable channels, then apply signed-error
control to the response channel instead of altering the roughdielectric material
directly.
