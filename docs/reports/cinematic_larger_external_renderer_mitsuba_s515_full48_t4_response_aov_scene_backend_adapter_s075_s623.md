# S623 Mitsuba Response AOV Scene Backend Adapter S075

Generated UTC: `2026-06-21T02:45:59.636225+00:00`
Summary JSON: `build/shots/s623_mitsuba_response_aov_scene_backend_adapter_s075/response_aov_scene_backend_adapter_summary.json`
Gallery: `build/shots/s623_mitsuba_response_aov_scene_backend_adapter_s075/gallery/index.html`
Status: `passed`

## Inputs

- Job manifest: `build/shots/s621_mitsuba_response_aov_scene_job_manifest_s075/response_aov_scene_job_manifest.json`
- Backend script: `tools/mitsuba_response_aov_scene_backend.py`

## Checks

- Frames: `48`
- Passed frames: `48`
- Failed frames: `0`
- Process failures: `0`
- Max selected abs diff: `0`
- Max selected mean abs diff: `0.0`
- Max imported abs diff: `0`
- Max imported mean abs diff: `0.0`
- Output bytes: `14.77 MB`
- GIF bytes: `7.91 MB`
- Stdout bytes: `70394`
- Stderr bytes: `0`

## Frame Samples

| Job | Frame | Scene | Source | Status | Return | Selected Max | Imported Max | Output |
| ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| 0 | 0 | 0 | 0 | `passed` | 0 | 0 | 0 | `build/shots/s623_mitsuba_response_aov_scene_backend_adapter_s075/backend_frames/frame_0000.png` |
| 24 | 24 | 18 | 18 | `passed` | 0 | 0 | 0 | `build/shots/s623_mitsuba_response_aov_scene_backend_adapter_s075/backend_frames/frame_0024.png` |
| 47 | 47 | 35 | 35 | `passed` | 0 | 0 | 0 | `build/shots/s623_mitsuba_response_aov_scene_backend_adapter_s075/backend_frames/frame_0047.png` |

## Next

Replace the parity backend internals with native renderer/cache work while preserving this external process contract, descriptor IO, and S577/S585 gate reporting.
