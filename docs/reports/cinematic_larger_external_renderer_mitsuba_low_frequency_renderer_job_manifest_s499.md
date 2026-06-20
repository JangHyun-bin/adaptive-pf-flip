# S499 Mitsuba Low Frequency Renderer Job Manifest

Generated UTC: `2026-06-20T18:45:37.818578+00:00`
Job JSON: `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/renderer_job_manifest.json`
Status: `ready`
Target renderer: `mitsuba_or_external_path_tracer`

## Source

- Acceptance package: `build/shots/s498_mitsuba_low_frequency_renderer_acceptance_package/renderer_acceptance_package.json`
- Package status: `ready`
- Public URL: `https://thanks-pending-expired-enlargement.trycloudflare.com`

## Render Settings

- Output root: `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/outputs`
- Output format: `png`
- Frame naming: `frame_%04d`
- Texture gain: `1.0`

## Checks

- Frames: `8`
- Required bindings per frame: `3`
- Required bindings present: `24`
- Missing inputs: `0`
- Missing shaders: `0`
- Reference hash mismatches: `0`
- Public HTTP passed: `True`

## Runtime Contract

- Stage: `renderer_post_tonemap_low_frequency_runtime_consumer`
- Expression: `clamp(base_rgb + (positive_delta_rgb - negative_delta_rgb) * texture_gain, 0, 1)`
- Required bindings: `base_rgb, positive_delta_rgb, negative_delta_rgb`

## Frame Jobs

| Job | Frame | Output | Inputs | Target | Reference |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0 | 0 | 3 | `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/outputs/frame_0000.png` | `build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0000.png` |
| 1 | 1 | 7 | 3 | `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/outputs/frame_0001.png` | `build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0001.png` |
| 2 | 2 | 13 | 3 | `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/outputs/frame_0002.png` | `build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0002.png` |
| 3 | 3 | 20 | 3 | `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/outputs/frame_0003.png` | `build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0003.png` |
| 4 | 4 | 27 | 3 | `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/outputs/frame_0004.png` | `build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0004.png` |
| 5 | 5 | 34 | 3 | `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/outputs/frame_0005.png` | `build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0005.png` |
| 6 | 6 | 40 | 3 | `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/outputs/frame_0006.png` | `build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0006.png` |
| 7 | 7 | 47 | 3 | `build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/outputs/frame_0007.png` | `build/shots/s497_mitsuba_low_frequency_renderer_runtime_preview/renderer_runtime/frame_0007.png` |

## Runner Commands

- `load build/shots/s499_mitsuba_low_frequency_renderer_job_manifest/renderer_job_manifest.json`
- `for each frame_job: bind base_rgb, positive_delta_rgb, negative_delta_rgb`
- `execute renderer_post_tonemap_low_frequency_runtime_consumer`
- `write outputs.image and outputs.metadata`
- `validate outputs.image sha256 or zero-diff against accepted_reference`

## Next

Use this job manifest as the sole input for the first production renderer/export dry run.
