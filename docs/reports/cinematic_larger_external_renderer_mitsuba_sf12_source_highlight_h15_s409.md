# S409 SF12 Highlight H15

Generated UTC: `2026-06-20T09:01:05.997747+00:00`
Summary JSON: `build/shots/s409_mitsuba_sf12_source_highlight_h15/source_region_response_summary.json`
Gallery: `build/shots/s409_mitsuba_sf12_source_highlight_h15/gallery/index.html`
Status: `ready`

## Settings

- profile: `default`
- secondary_alpha_threshold: `4`
- highlight_source_luma_threshold: `120.0`
- highlight_alpha_max: `3`
- highlight_strength: `0.45`
- highlight_max_delta: `55.0`
- dark_secondary_source_luma_min: `20.0`
- dark_secondary_source_luma_max: `105.0`
- dark_secondary_strength: `0.0`
- dark_secondary_max_delta: `55.0`
- dark_secondary_ring_radius: `0`
- dark_secondary_ring_source_luma_min: `0.0`
- dark_secondary_ring_source_luma_max: `95.0`
- dark_secondary_ring_strength: `0.0`
- dark_secondary_ring_max_delta: `35.0`
- mitsuba_export: `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`
- channel_band_source_luma_min: `0.0`
- channel_band_source_luma_max: `95.0`
- channel_band_strength: `0.12`
- channel_band_max_delta: `18.0`
- channel_band_dilate_radius: `0`
- channel_mask_channels: `['foam', 'spray']`
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
- Max changed coverage: `0.028169367283950617`
- Max highlight coverage: `0.014924768518518518`
- Max dark secondary coverage: `0.0132445987654321`
- GIF bytes: `1184472`

## Frame Samples

| Frame | Output | Changed | Highlight | Dark Secondary | Graded |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0.01300733024691358 | 0.0016859567901234569 | 0.011321373456790124 | `build/shots/s409_mitsuba_sf12_source_highlight_h15/frames/frame_0000.png` |
| 4 | 27 | 0.0062770061728395065 | 0.0010686728395061728 | 0.005208333333333333 | `build/shots/s409_mitsuba_sf12_source_highlight_h15/frames/frame_0004.png` |
| 7 | 47 | 0.028169367283950617 | 0.014924768518518518 | 0.0132445987654321 | `build/shots/s409_mitsuba_sf12_source_highlight_h15/frames/frame_0007.png` |

## Next

Compare this SF12 plus bounded source-highlight probe against SF12, SS1, and CR21.
