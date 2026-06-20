# S388 Mitsuba Secondary Channel Response CR15

Generated UTC: `2026-06-20T07:11:54.124182+00:00`
Summary JSON: `build/shots/s388_mitsuba_secondary_channel_response_cr15/source_region_response_summary.json`
Gallery: `build/shots/s388_mitsuba_secondary_channel_response_cr15/gallery/index.html`
Status: `ready`

## Settings

- secondary_alpha_threshold: `4`
- highlight_source_luma_threshold: `120.0`
- highlight_alpha_max: `3`
- highlight_strength: `1.0`
- highlight_max_delta: `255.0`
- dark_secondary_source_luma_min: `0.0`
- dark_secondary_source_luma_max: `75.0`
- dark_secondary_strength: `1.0`
- dark_secondary_max_delta: `255.0`
- dark_secondary_ring_radius: `0`
- dark_secondary_ring_source_luma_min: `0.0`
- dark_secondary_ring_source_luma_max: `95.0`
- dark_secondary_ring_strength: `0.0`
- dark_secondary_ring_max_delta: `35.0`
- mitsuba_export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- channel_band_source_luma_min: `75.0`
- channel_band_source_luma_max: `82.0`
- channel_band_strength: `0.5`
- channel_band_max_delta: `48.0`
- channel_band_dilate_radius: `0`
- channel_radius_scale: `1.0`
- channel_density_blur_radius: `2.0`
- dark_secondary_soft_source_luma_min: `75.0`
- dark_secondary_soft_source_luma_max: `95.0`
- dark_secondary_soft_strength: `0.0`
- dark_secondary_soft_max_delta: `35.0`
- nonsecondary_lift: `0.0`
- fps: `2.0`
- keyframes: `4`

## Checks

- Frames: `8`
- Max changed coverage: `0.01949652777777778`
- Max highlight coverage: `0.014924768518518518`
- Max dark secondary coverage: `0.0077083333333333335`
- GIF bytes: `1166286`

## Frame Samples

| Frame | Output | Changed | Highlight | Dark Secondary | Graded |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0.00939429012345679 | 0.0016859567901234569 | 0.0077083333333333335 | `build/shots/s388_mitsuba_secondary_channel_response_cr15/frames/frame_0000.png` |
| 4 | 27 | 0.0011246141975308642 | 0.0010686728395061728 | 5.594135802469136e-05 | `build/shots/s388_mitsuba_secondary_channel_response_cr15/frames/frame_0004.png` |
| 7 | 47 | 0.01949652777777778 | 0.014924768518518518 | 0.004571759259259259 | `build/shots/s388_mitsuba_secondary_channel_response_cr15/frames/frame_0007.png` |

## Next

Compare this target-free source response against the target-gap baseline.
