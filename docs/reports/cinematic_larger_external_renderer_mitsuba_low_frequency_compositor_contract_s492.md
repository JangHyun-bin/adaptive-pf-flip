# S492 Mitsuba Low Frequency Compositor Contract

Generated UTC: `2026-06-20T17:57:00.210844+00:00`
Contract JSON: `build/shots/s492_mitsuba_low_frequency_compositor_contract/low_frequency_compositor_contract.json`
Status: `ready`

## Operation

- Stage: `post_tonemap`
- Color space: `tonemapped_rgb_normalized`
- Expression: `clamp(base_rgb + (positive_delta_rgb - negative_delta_rgb) * texture_gain, 0, 1)`
- Texture gain: `1.0`

## Checks

- Frames: `8`
- Missing references: `0`
- Max oracle abs diff: `0`
- Max oracle mean diff: `0.0`
- Max mismatched coverage: `0.0`
- Max changed coverage: `0.18508873456790123`
- Target-gap mean MAD: `19.144350646219134`
- Target-gap max MAD: `23.95285943930041`
- Shader bytes: `1.98 KB`

## Shader Artifacts

| Role | Path | Size |
| --- | --- | ---: |
| `glsl_reference` | `build/shots/s492_mitsuba_low_frequency_compositor_contract/shaders/low_frequency_parity_post_tonemap.glsl` | 705 B |
| `hlsl_reference` | `build/shots/s492_mitsuba_low_frequency_compositor_contract/shaders/low_frequency_parity_post_tonemap.hlsl` | 859 B |
| `pseudocode_reference` | `build/shots/s492_mitsuba_low_frequency_compositor_contract/shaders/low_frequency_parity_post_tonemap.txt` | 465 B |

## Frame Samples

| Frame | Output | Max Diff | Changed Coverage | Base |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0 | 0.08149112654320988 | `build/shots/s489_mitsuba_low_frequency_parity_texture_package/textures/base_rgb/frame_0000_base_rgb.png` |
| 4 | 27 | 0 | 0.06519868827160494 | `build/shots/s489_mitsuba_low_frequency_parity_texture_package/textures/base_rgb/frame_0004_base_rgb.png` |
| 7 | 47 | 0 | 0.18508873456790123 | `build/shots/s489_mitsuba_low_frequency_parity_texture_package/textures/base_rgb/frame_0007_base_rgb.png` |

## Next

Use this shader contract to implement the low-frequency correction in an engine-native compositor and check parity against S491.
