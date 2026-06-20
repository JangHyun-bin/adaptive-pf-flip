# S491 Mitsuba Low Frequency Post-Tonemap Texture Stage Target Gap

Generated UTC: `2026-06-20T17:52:56.797241+00:00`
Summary JSON: `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage_target_gap/renderer_target_gap_summary.json`
Gallery: `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage_target_gap/gallery/index.html`
Status: `ready`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean gap mean abs diff: `19.144350646219134`
- Max gap mean abs diff: `23.95285943930041`
- Max gap max abs diff: `214`
- GIF bytes: `8.28 MB`

## Frame Samples

| Frame | Output | Gap MAD | Gap Max | Strip |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 22.4394 | 209 | `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage_target_gap/strips/frame_0000.png` |
| 4 | 27 | 19.1587 | 177 | `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage_target_gap/strips/frame_0004.png` |
| 7 | 47 | 20.8878 | 214 | `build/shots/s491_mitsuba_low_frequency_post_tonemap_texture_stage_target_gap/strips/frame_0007.png` |

## Next

Use S491 as the renderer-facing post-tonemap gate, then port the positive/negative texture delta contract into engine-native shader or compositor code.
