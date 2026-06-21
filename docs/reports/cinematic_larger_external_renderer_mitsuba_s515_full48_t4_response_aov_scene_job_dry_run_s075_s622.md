# S622 Mitsuba Response AOV Scene Job Dry Run S075

Generated UTC: `2026-06-21T02:38:08.328763+00:00`
Summary JSON: `build/shots/s622_mitsuba_response_aov_scene_job_dry_run_s075/response_aov_scene_job_dry_run_summary.json`
Gallery: `build/shots/s622_mitsuba_response_aov_scene_job_dry_run_s075/gallery/index.html`
Status: `passed`

## Input

- Job manifest: `build/shots/s621_mitsuba_response_aov_scene_job_manifest_s075/response_aov_scene_job_manifest.json`

## Checks

- Frames: `48`
- Passed frames: `48`
- Failed frames: `0`
- Missing frames: `0`
- Max selected abs diff: `0`
- Max selected mean abs diff: `0.0`
- Max imported abs diff: `0`
- Max imported mean abs diff: `0.0`
- Output bytes: `14.77 MB`
- GIF bytes: `7.91 MB`

## Frame Samples

| Job | Frame | Scene | Source | Status | Selected Max | Imported Max | Output |
| ---: | ---: | ---: | ---: | --- | ---: | ---: | --- |
| 0 | 0 | 0 | 0 | `passed` | 0 | 0 | `build/shots/s621_mitsuba_response_aov_scene_job_manifest_s075/renderer_frames/frame_0000.png` |
| 24 | 24 | 18 | 18 | `passed` | 0 | 0 | `build/shots/s621_mitsuba_response_aov_scene_job_manifest_s075/renderer_frames/frame_0024.png` |
| 47 | 47 | 35 | 35 | `passed` | 0 | 0 | `build/shots/s621_mitsuba_response_aov_scene_job_manifest_s075/renderer_frames/frame_0047.png` |

## Next

Replace this dry-run compositor with the external renderer/cache backend while preserving descriptor IO, selected-composite parity, imported-composite parity, and S577/S585 gate reporting.
