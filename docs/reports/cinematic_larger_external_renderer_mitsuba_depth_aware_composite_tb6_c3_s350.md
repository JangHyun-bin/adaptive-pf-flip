# S350 Mitsuba Depth-Aware Composite TB6 C3

Generated UTC: `2026-06-20T02:06:56.633288+00:00`
Summary JSON: `build/shots/s350_mitsuba_depth_aware_composite_tb6_c3/depth_aware_secondary_composite_summary.json`
Gallery: `build/shots/s350_mitsuba_depth_aware_composite_tb6_c3/gallery/index.html`
Status: `review`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean target MAD: `13.718946277006172`
- Max target MAD: `25.861554783950616`
- Max target diff: `167`
- Mean contract MAD: `14.440004501028806`
- Max contract MAD: `21.00066550925926`
- Contract max target MAD: `18.040229552469135`
- GIF bytes: `3.28 MB`

## Settings

- fps: `2.0`
- keyframes: `4`
- native_base_strength: `0.35`
- secondary_native_strength: `0.05`
- mask_blur_radius: `2.5`
- mask_gain: `1.35`
- luminance_gamma: `0.0`
- max_target_mean_abs_diff: `24.0`
- grade: `{'autocontrast_cutoff': 0.05, 'bloom_radius': 5.0, 'bloom_strength': 0.1, 'bloom_threshold': 214, 'contrast': 1.12, 'exposure': 1.02, 'fps': 2.0, 'saturation': 1.08, 'sharpness': 1.02, 'tone_rgb': [220, 234, 242], 'tone_strength': 0.08, 'vignette_power': 2.1, 'vignette_strength': 0.18}`

## Frame Samples

| Frame | Output | Target MAD | Contract MAD | Native Weight Mean | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 11.0648 | 12.5156 | 0.3482 | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c3/strips/frame_0000.png` |
| 4 | 27 | 13.9361 | 18.2229 | 0.3483 | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c3/strips/frame_0004.png` |
| 7 | 47 | 12.1441 | 12.4586 | 0.3478 | `build/shots/s350_mitsuba_depth_aware_composite_tb6_c3/strips/frame_0007.png` |

## Next

Use this composite as a post-render bridge while replacing screen-space secondary with depth-aware data.
