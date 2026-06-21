# S620 Mitsuba Response AOV Scene Handoff S075

Generated UTC: `2026-06-21T02:26:51.247794+00:00`
Summary JSON: `build/shots/s620_mitsuba_response_aov_scene_handoff_s075/response_aov_scene_handoff_summary.json`
Gallery: `build/shots/s620_mitsuba_response_aov_scene_handoff_s075/gallery/index.html`
Status: `ready`

## Inputs

- Scene-cache handoff: `build/shots/s578_mitsuba_renderer_scene_cache_handoff/renderer_scene_cache_handoff_summary.json`
- Render-data summary: `build/shots/s580_mitsuba_renderer_scene_render_data/render_data_summary.json`
- Response AOV contract: `build/shots/s618_mitsuba_response_aov_contract_s075/response_aov_contract.json`
- Response AOV consumer: `build/shots/s619_mitsuba_response_aov_consumer_s075/response_aov_consumer_summary.json`

## Checks

- Frames: `48`
- Missing references: `0`
- Response scale: `0.75`
- Max import abs diff: `0`
- Max import mean abs diff: `0.0`
- S577 mean/max/maxabs: `2.9732022274734224` / `5.5108699845679014` / `151`
- S585 mean/max/maxabs: `2.982389550647291` / `5.524723508230453` / `148`
- Unique scene frames: `36`
- Scene frame count mismatch: `True`

## Frame Samples

| Output | Scene | Source | Scale | Import Max | Composite |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0 | 0.75 | 0 | `build/shots/s619_mitsuba_response_aov_consumer_s075/composites/frame_0000.png` |
| 24 | 18 | 18 | 0.75 | 0 | `build/shots/s619_mitsuba_response_aov_consumer_s075/composites/frame_0024.png` |
| 47 | 35 | 35 | 0.75 | 0 | `build/shots/s619_mitsuba_response_aov_consumer_s075/composites/frame_0047.png` |

## Next

Use this scene/AOV handoff to run renderer-cache jobs without recomputing response layers from preview pairs.
