# S350 Mitsuba Depth-Aware Composite TB6 C2

Generated UTC: `2026-06-20T02:06:56.496923+00:00`
Summary JSON: `build/shots/s350_mitsuba_depth_aware_composite_tb6_c2/depth_aware_secondary_composite_summary.json`
Gallery: `build/shots/s350_mitsuba_depth_aware_composite_tb6_c2/gallery/index.html`
Status: `ready`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean target MAD: `12.310201581790123`
- Max target MAD: `20.083314043209878`
- Max target diff: `181`
- Mean contract MAD: `10.19741914223251`
- Max contract MAD: `14.892814429012345`
- Contract max target MAD: `18.040229552469135`
- GIF bytes: `3.17 MB`

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
| 0 | 0 | 11.7663 | 8.7934 | 0.2466 | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c2/strips/frame_0000.png` |
| 4 | 27 | 11.9898 | 12.9644 | 0.2466 | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c2/strips/frame_0004.png` |
| 7 | 47 | 12.9471 | 8.7908 | 0.2464 | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c2/strips/frame_0007.png` |

## Next

Use this composite as a post-render bridge while replacing screen-space secondary with depth-aware data.
