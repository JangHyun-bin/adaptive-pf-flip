# S491 Mitsuba Low Frequency Post-Tonemap Texture Stage

Generated UTC: `2026-06-20T17:52:44.711839+00:00`
Summary JSON: `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage/grade_summary.json`
Gallery: `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage/gallery/index.html`
Status: `ready`

## Settings

- texture_gain: `1.0`
- stage: `post_tonemap_positive_negative_delta`
- fps: `2.0`
- keyframes: `4`

## Checks

- Frames: `8`
- Missing references: `0`
- Max expected abs diff: `0`
- Max expected mean diff: `0.0`
- Max changed coverage: `0.18508873456790123`
- Graded bytes: `1.93 MB`
- GIF bytes: `8.15 MB`

## Frame Samples

| Frame | Output | Max Delta | Expected Max Diff | Graded | Strip |
| ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0 | 13 | 0 | `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage/frames/frame_0000.png` | `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage/strips/frame_0000_post_tonemap_texture_stage.png` |
| 4 | 27 | 10 | 0 | `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage/frames/frame_0004.png` | `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage/strips/frame_0004_post_tonemap_texture_stage.png` |
| 7 | 47 | 23 | 0 | `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage/frames/frame_0007.png` | `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage/strips/frame_0007_post_tonemap_texture_stage.png` |

## Next

Compare this post-tonemap stage against S478, S487 LF3, S490 consumer, and S485 LRS4; then replace the Python stage with engine-native shader or compositor code.
