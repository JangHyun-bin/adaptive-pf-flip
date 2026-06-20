# S350 Mitsuba Depth-Aware Composite TB6 C0

Generated UTC: `2026-06-20T02:07:20.465274+00:00`
Summary JSON: `build/shots/s350_mitsuba_depth_aware_composite_tb6_c0/depth_aware_secondary_composite_summary.json`
Gallery: `build/shots/s350_mitsuba_depth_aware_composite_tb6_c0/gallery/index.html`
Status: `ready`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean target MAD: `11.601414046424898`
- Max target MAD: `15.565737525720165`
- Max target diff: `203`
- Mean contract MAD: `3.28618465470679`
- Max contract MAD: `4.7344483024691355`
- Contract max target MAD: `18.040229552469135`
- GIF bytes: `2.86 MB`

## Settings

- fps: `2.0`
- keyframes: `4`
- native_base_strength: `0.08`
- secondary_native_strength: `0.012`
- mask_blur_radius: `2.5`
- mask_gain: `1.35`
- luminance_gamma: `0.0`
- max_target_mean_abs_diff: `24.0`
- grade: `{'autocontrast_cutoff': 0.05, 'bloom_radius': 5.0, 'bloom_strength': 0.1, 'bloom_threshold': 214, 'contrast': 1.12, 'exposure': 1.02, 'fps': 2.0, 'saturation': 1.08, 'sharpness': 1.02, 'tone_rgb': [220, 234, 242], 'tone_strength': 0.08, 'vignette_power': 2.1, 'vignette_strength': 0.18}`

## Frame Samples

| Frame | Output | Target MAD | Contract MAD | Native Weight Mean | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 13.7353 | 2.8811 | 0.0783 | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c0/strips/frame_0000.png` |
| 4 | 27 | 9.8110 | 4.0462 | 0.0783 | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c0/strips/frame_0004.png` |
| 7 | 47 | 15.5657 | 2.8296 | 0.0782 | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c0/strips/frame_0007.png` |

## Next

Use this composite as a post-render bridge while replacing screen-space secondary with depth-aware data.
