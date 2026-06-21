# S617 Response Scale Composite S075 Direct Metrics

Generated UTC: `2026-06-21T02:11:00Z`
Status: `ready`

## Inputs

- Response-scale composite: `build/shots/s617_mitsuba_response_scale_composite_s075/response_scale_composite_summary.json`
- Response buffer: `build/shots/s616_mitsuba_response_delta_buffer_probe/response_delta/response_delta_buffer_summary.json`
- S577 accepted composite: `build/shots/s577_mitsuba_s515_full48_t4_low_frequency_texture_consumer/low_frequency_texture_consumer_summary.json`
- S585 scene depth/material target: `build/shots/s585_mitsuba_renderer_scene_depth_material_target/depth_material_target_summary.json`

## Metrics

| Candidate | Reference | Mean MAD | Max MAD | Max Abs |
| --- | --- | ---: | ---: | ---: |
| S614 automatic screen-error render | S577 | `3.038890683942044` | `5.5758995627572014` | `173` |
| S614 automatic screen-error render | S585 | `3.050464838391632` | `5.595675154320989` | `172` |
| S617 response scale `0.75` composite | S577 | `2.9732022274734224` | `5.5108699845679014` | `151` |
| S617 response scale `0.75` composite | S585 | `2.982389550647291` | `5.524723508230453` | `148` |

## Decision

Promote S617 as the next AOV/export integration target. It keeps the S614
automatic local-control source, but moves the final response strength into a
separable full/base response buffer. The promoted `0.75` response scale improves
both mean MAD and max MAD against S577 and S585, and it substantially lowers
the max absolute error of the composited probe versus S614.

## Next

Move the S617 response-scale composite from an image-space promoted candidate
into a renderer-native AOV/export contract: base render, signed response layer,
selected scale, composite, S577/S585 gate metrics, and gallery references in one
portable manifest.
