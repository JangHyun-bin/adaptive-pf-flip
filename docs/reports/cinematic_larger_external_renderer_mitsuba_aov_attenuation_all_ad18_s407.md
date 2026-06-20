# S407 AOV Attenuation All Channels AD18

Generated UTC: `2026-06-20T08:49:10.474922+00:00`
Summary JSON: `build/shots/s407_mitsuba_aov_attenuation_all_ad18/source_region_response_summary.json`
Gallery: `build/shots/s407_mitsuba_aov_attenuation_all_ad18/gallery/index.html`
Status: `ready`

## Settings

- profile: `default`
- secondary_alpha_threshold: `4`
- highlight_source_luma_threshold: `145.0`
- highlight_alpha_max: `255`
- highlight_strength: `0.0`
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
- channel_band_strength: `0.18`
- channel_band_max_delta: `24.0`
- channel_band_dilate_radius: `0`
- channel_mask_channels: `['bubble', 'droplet', 'foam', 'spray']`
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
- Max changed coverage: `0.01922260802469136`
- Max highlight coverage: `0.0`
- Max dark secondary coverage: `0.01922260802469136`
- GIF bytes: `1186546`

## Frame Samples

| Frame | Output | Changed | Highlight | Dark Secondary | Graded |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0.012276234567901235 | 0.0 | 0.012276234567901235 | `build/shots/s407_mitsuba_aov_attenuation_all_ad18/frames/frame_0000.png` |
| 4 | 27 | 0.0058198302469135805 | 0.0 | 0.0058198302469135805 | `build/shots/s407_mitsuba_aov_attenuation_all_ad18/frames/frame_0004.png` |
| 7 | 47 | 0.01922260802469136 | 0.0 | 0.01922260802469136 | `build/shots/s407_mitsuba_aov_attenuation_all_ad18/frames/frame_0007.png` |

## Next

Compare AD18 against SS1, CR21, and spray/foam-only attenuation.
