# S558 Mitsuba S515 Full48 T4 Renderer Job Manifest

Generated UTC: `2026-06-20T20:58:46.387163+00:00`
Job JSON: `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/renderer_job_manifest.json`
Status: `ready`
Target renderer: `mitsuba_or_external_path_tracer`

## Source

- Acceptance package: `build/shots/s557_mitsuba_s515_full48_t4_sequence_acceptance_package/renderer_acceptance_package.json`
- Package status: `ready`
- Public URL: `https://operating-intended-analyses-individually.trycloudflare.com`

## Render Settings

- Output root: `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs`
- Output format: `png`
- Frame naming: `frame_%04d`
- Texture gain: `1.0`

## Checks

- Frames: `48`
- Required bindings per frame: `3`
- Required bindings present: `144`
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
| 0 | 0 | 0 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0000.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0000.png` |
| 1 | 1 | 1 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0001.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0001.png` |
| 2 | 2 | 2 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0002.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0002.png` |
| 3 | 3 | 3 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0003.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0003.png` |
| 4 | 4 | 4 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0004.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0004.png` |
| 5 | 5 | 5 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0005.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0005.png` |
| 6 | 6 | 6 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0006.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0006.png` |
| 7 | 7 | 7 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0007.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0007.png` |
| 8 | 8 | 8 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0008.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0008.png` |
| 9 | 9 | 9 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0009.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0009.png` |
| 10 | 10 | 10 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0010.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0010.png` |
| 11 | 11 | 11 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0011.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0011.png` |
| 12 | 12 | 12 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0012.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0012.png` |
| 13 | 13 | 13 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0013.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0013.png` |
| 14 | 14 | 14 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0014.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0014.png` |
| 15 | 15 | 15 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0015.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0015.png` |
| 16 | 16 | 16 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0016.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0016.png` |
| 17 | 17 | 17 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0017.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0017.png` |
| 18 | 18 | 18 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0018.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0018.png` |
| 19 | 19 | 19 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0019.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0019.png` |
| 20 | 20 | 20 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0020.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0020.png` |
| 21 | 21 | 21 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0021.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0021.png` |
| 22 | 22 | 22 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0022.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0022.png` |
| 23 | 23 | 23 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0023.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0023.png` |
| 24 | 24 | 24 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0024.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0024.png` |
| 25 | 25 | 25 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0025.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0025.png` |
| 26 | 26 | 26 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0026.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0026.png` |
| 27 | 27 | 27 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0027.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0027.png` |
| 28 | 28 | 28 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0028.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0028.png` |
| 29 | 29 | 29 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0029.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0029.png` |
| 30 | 30 | 30 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0030.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0030.png` |
| 31 | 31 | 31 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0031.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0031.png` |
| 32 | 32 | 32 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0032.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0032.png` |
| 33 | 33 | 33 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0033.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0033.png` |
| 34 | 34 | 34 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0034.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0034.png` |
| 35 | 35 | 35 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0035.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0035.png` |
| 36 | 36 | 36 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0036.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0036.png` |
| 37 | 37 | 37 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0037.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0037.png` |
| 38 | 38 | 38 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0038.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0038.png` |
| 39 | 39 | 39 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0039.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0039.png` |
| 40 | 40 | 40 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0040.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0040.png` |
| 41 | 41 | 41 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0041.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0041.png` |
| 42 | 42 | 42 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0042.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0042.png` |
| 43 | 43 | 43 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0043.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0043.png` |
| 44 | 44 | 44 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0044.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0044.png` |
| 45 | 45 | 45 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0045.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0045.png` |
| 46 | 46 | 46 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0046.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0046.png` |
| 47 | 47 | 47 | 3 | `build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/outputs/frame_0047.png` | `build/shots/s555_mitsuba_s515_full48_low_frequency_raw_contrast_t4_bindings/corrected/frame_0047.png` |

## Runner Commands

- `load build/shots/s558_mitsuba_s515_full48_t4_renderer_job_manifest/renderer_job_manifest.json`
- `for each frame_job: bind base_rgb, positive_delta_rgb, negative_delta_rgb`
- `execute renderer_post_tonemap_low_frequency_runtime_consumer`
- `write outputs.image and outputs.metadata`
- `validate outputs.image sha256 or zero-diff against accepted_reference`

## Next

Run the renderer job dry-run and require zero-diff parity against accepted full-sequence references.
