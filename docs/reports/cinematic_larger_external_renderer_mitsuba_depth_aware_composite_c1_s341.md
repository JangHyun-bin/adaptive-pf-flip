# S341 Mitsuba Depth-Aware Composite C1

Generated UTC: `2026-06-20T00:58:30.889411+00:00`
Summary JSON: `build/shots/s341_mitsuba_depth_aware_composite_c1/depth_aware_secondary_composite_summary.json`
Gallery: `build/shots/s341_mitsuba_depth_aware_composite_c1/gallery/index.html`
Status: `ready`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean target MAD: `11.936789801954733`
- Max target MAD: `16.35688014403292`
- Max target diff: `208`
- Mean contract MAD: `1.8651991705246913`
- Max contract MAD: `2.7353755144032923`
- Contract max target MAD: `18.040229552469135`
- GIF bytes: `2.71 MB`

## Settings

- fps: `2.0`
- keyframes: `4`
- native_base_strength: `0.045`
- secondary_native_strength: `0.006`
- mask_blur_radius: `2.5`
- mask_gain: `1.35`
- luminance_gamma: `0.0`
- max_target_mean_abs_diff: `24.0`
- grade: `{'autocontrast_cutoff': 0.05, 'bloom_radius': 5.0, 'bloom_strength': 0.1, 'bloom_threshold': 214, 'contrast': 1.12, 'exposure': 1.02, 'fps': 2.0, 'saturation': 1.08, 'sharpness': 1.02, 'tone_rgb': [220, 234, 242], 'tone_strength': 0.08, 'vignette_power': 2.1, 'vignette_strength': 0.18}`

## Frame Samples

| Frame | Output | Target MAD | Contract MAD | Native Weight Mean | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 14.3940 | 1.7295 | 0.0431 | `build/shots/s341_mitsuba_depth_aware_composite_c1/strips/frame_0000.png` |
| 4 | 27 | 10.2920 | 2.0964 | 0.0431 | `build/shots/s341_mitsuba_depth_aware_composite_c1/strips/frame_0004.png` |
| 7 | 47 | 16.3569 | 1.8723 | 0.0430 | `build/shots/s341_mitsuba_depth_aware_composite_c1/strips/frame_0007.png` |

## Next

Use this C1 bridge to decide whether to tune native contribution or lock the post-render composite contract.
