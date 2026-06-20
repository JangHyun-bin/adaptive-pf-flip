# S532 Mitsuba S515 Low Frequency Compositor Contract

Generated UTC: `2026-06-20T20:08:20.858747+00:00`
Contract JSON: `build/shots/s532_mitsuba_s515_low_frequency_compositor_contract/low_frequency_compositor_contract.json`
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
- Max changed coverage: `1.0`
- Target-gap mean MAD: `32.275872476208846`
- Target-gap max MAD: `63.70094843106996`
- Shader bytes: `1.98 KB`

## Shader Artifacts

| Role | Path | Size |
| --- | --- | ---: |
| `glsl_reference` | `build/shots/s532_mitsuba_s515_low_frequency_compositor_contract/shaders/low_frequency_parity_post_tonemap.glsl` | 705 B |
| `hlsl_reference` | `build/shots/s532_mitsuba_s515_low_frequency_compositor_contract/shaders/low_frequency_parity_post_tonemap.hlsl` | 859 B |
| `pseudocode_reference` | `build/shots/s532_mitsuba_s515_low_frequency_compositor_contract/shaders/low_frequency_parity_post_tonemap.txt` | 465 B |

## Frame Samples

| Frame | Output | Max Diff | Changed Coverage | Base |
| ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0 | 1.0 | `build/shots/s528_mitsuba_s515_low_frequency_texture_package/textures/base_rgb/frame_0000_base_rgb.png` |
| 4 | 27 | 0 | 1.0 | `build/shots/s528_mitsuba_s515_low_frequency_texture_package/textures/base_rgb/frame_0004_base_rgb.png` |
| 7 | 47 | 0 | 1.0 | `build/shots/s528_mitsuba_s515_low_frequency_texture_package/textures/base_rgb/frame_0007_base_rgb.png` |

## Next

Run WebGL and runtime import previews against this S515-calibrated compositor contract.
