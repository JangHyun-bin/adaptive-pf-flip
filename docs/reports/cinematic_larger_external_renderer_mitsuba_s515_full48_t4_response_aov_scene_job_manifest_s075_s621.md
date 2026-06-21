# S621 Mitsuba Response AOV Scene Job Manifest S075

Generated UTC: `2026-06-21T02:32:28.374756+00:00`
Manifest JSON: `build/shots/s621_mitsuba_response_aov_scene_job_manifest_s075/response_aov_scene_job_manifest.json`
Gallery: `build/shots/s621_mitsuba_response_aov_scene_job_manifest_s075/gallery/index.html`
Status: `ready`

## Input

- Response AOV scene handoff: `build/shots/s620_mitsuba_response_aov_scene_handoff_s075/response_aov_scene_handoff_summary.json`
- Source status: `ready`

## Checks

- Frames: `48`
- Descriptors: `48`
- Missing inputs: `0`
- SHA mismatches: `0`
- Size mismatches: `0`
- Max import abs diff: `0`
- Max import mean abs diff: `0.0`
- Unique scene frames: `36`
- Scene frame count mismatch: `True`
- Response scale: `0.75`
- Scene asset refs: `192` / `192`
- AOV refs: `240` / `240`

## Frame Samples

| Job | Frame | Scene | Source | AOV | Scene Assets | Import Max | Descriptor |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0 | 0 | 5 | 4 | 0 | `build/shots/s621_mitsuba_response_aov_scene_job_manifest_s075/descriptors/frame_0000_scene_aov_job.json` |
| 24 | 24 | 18 | 18 | 5 | 4 | 0 | `build/shots/s621_mitsuba_response_aov_scene_job_manifest_s075/descriptors/frame_0024_scene_aov_job.json` |
| 47 | 47 | 35 | 35 | 5 | 4 | 0 | `build/shots/s621_mitsuba_response_aov_scene_job_manifest_s075/descriptors/frame_0047_scene_aov_job.json` |

## Next

Run an external renderer/cache backend from these per-frame scene/AOV descriptors and compare the resulting frames against the carried S577/S585 gates.
