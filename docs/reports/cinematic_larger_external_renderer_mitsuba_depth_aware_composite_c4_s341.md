# S341 Mitsuba Depth-Aware Composite C4

Generated UTC: `2026-06-20T00:59:36.393815+00:00`
Summary JSON: `build/shots/s341_mitsuba_depth_aware_composite_c4/depth_aware_secondary_composite_summary.json`
Gallery: `build/shots/s341_mitsuba_depth_aware_composite_c4/gallery/index.html`
Status: `ready`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean target MAD: `12.195964104295268`
- Max target MAD: `19.998582175925925`
- Max target diff: `179`
- Mean contract MAD: `10.306521106610083`
- Max contract MAD: `14.806318158436214`
- Contract max target MAD: `18.040229552469135`
- GIF bytes: `2.80 MB`

## Settings

- fps: `2.0`
- keyframes: `4`
- native_base_strength: `0.25`
- secondary_native_strength: `0.035`
- mask_blur_radius: `2.5`
- mask_gain: `1.35`
- luminance_gamma: `0.0`
- max_target_mean_abs_diff: `24.0`
- grade: `{'autocontrast_cutoff': 0.05, 'bloom_radius': 5.0, 'bloom_strength': 0.1, 'bloom_threshold': 214, 'contrast': 1.12, 'exposure': 1.02, 'fps': 2.0, 'saturation': 1.08, 'sharpness': 1.02, 'tone_rgb': [220, 234, 242], 'tone_strength': 0.08, 'vignette_power': 2.1, 'vignette_strength': 0.18}`

## Frame Samples

| Frame | Output | Target MAD | Contract MAD | Native Weight Mean | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 11.5210 | 8.9908 | 0.2466 | `build/shots/s341_mitsuba_depth_aware_composite_c4/strips/frame_0000.png` |
| 4 | 27 | 12.0021 | 13.0149 | 0.2466 | `build/shots/s341_mitsuba_depth_aware_composite_c4/strips/frame_0004.png` |
| 7 | 47 | 12.2882 | 9.3169 | 0.2464 | `build/shots/s341_mitsuba_depth_aware_composite_c4/strips/frame_0007.png` |

## Next

Use this C4 bridge only if the stronger native contribution still improves the S335 target gap without washing out secondary regions.
