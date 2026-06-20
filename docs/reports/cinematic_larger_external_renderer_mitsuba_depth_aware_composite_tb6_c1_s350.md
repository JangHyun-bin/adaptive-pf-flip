# S350 Mitsuba Depth-Aware Composite TB6 C1

Generated UTC: `2026-06-20T02:06:32.802644+00:00`
Summary JSON: `build/shots/s350_mitsuba_depth_aware_composite_tb6_c1/depth_aware_secondary_composite_summary.json`
Gallery: `build/shots/s350_mitsuba_depth_aware_composite_tb6_c1/gallery/index.html`
Status: `ready`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean target MAD: `11.465766300154321`
- Max target MAD: `14.592011959876544`
- Max target diff: `195`
- Mean contract MAD: `5.6863149434156375`
- Max contract MAD: `8.30991512345679`
- Contract max target MAD: `18.040229552469135`
- GIF bytes: `2.99 MB`

## Settings

- fps: `2.0`
- keyframes: `4`
- native_base_strength: `0.14`
- secondary_native_strength: `0.02`
- mask_blur_radius: `2.5`
- mask_gain: `1.35`
- luminance_gamma: `0.0`
- max_target_mean_abs_diff: `24.0`
- grade: `{'autocontrast_cutoff': 0.05, 'bloom_radius': 5.0, 'bloom_strength': 0.1, 'bloom_threshold': 214, 'contrast': 1.12, 'exposure': 1.02, 'fps': 2.0, 'saturation': 1.08, 'sharpness': 1.02, 'tone_rgb': [220, 234, 242], 'tone_strength': 0.08, 'vignette_power': 2.1, 'vignette_strength': 0.18}`

## Frame Samples

| Frame | Output | Target MAD | Contract MAD | Native Weight Mean | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 12.8482 | 4.9376 | 0.1370 | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c1/strips/frame_0000.png` |
| 4 | 27 | 10.2079 | 7.2016 | 0.1370 | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c1/strips/frame_0004.png` |
| 7 | 47 | 14.2512 | 4.8594 | 0.1369 | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c1/strips/frame_0007.png` |

## Next

Use this composite as a post-render bridge while replacing screen-space secondary with depth-aware data.
