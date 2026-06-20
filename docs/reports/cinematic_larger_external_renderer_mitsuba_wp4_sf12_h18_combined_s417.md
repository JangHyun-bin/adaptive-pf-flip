# S417 Mitsuba WP4 plus SF12 H18 Combined

Generated UTC: `2026-06-20T10:14:28.707926+00:00`
Summary JSON: `build/shots/s417_mitsuba_wp4_sf12_h18_combined/source_region_response_summary.json`
Gallery: `build/shots/s417_mitsuba_wp4_sf12_h18_combined/gallery/index.html`
Status: `ready`

## Settings

- profile: `default`
- secondary_alpha_threshold: `4`
- highlight_source_luma_threshold: `120.0`
- highlight_alpha_max: `3`
- highlight_strength: `0.85`
- highlight_max_delta: `120.0`
- dark_secondary_source_luma_min: `20.0`
- dark_secondary_source_luma_max: `105.0`
- dark_secondary_strength: `0.0`
- dark_secondary_max_delta: `55.0`
- dark_secondary_ring_radius: `0`
- dark_secondary_ring_source_luma_min: `0.0`
- dark_secondary_ring_source_luma_max: `95.0`
- dark_secondary_ring_strength: `0.0`
- dark_secondary_ring_max_delta: `35.0`
- mitsuba_export: `build/shots/s416_mitsuba_water_patch_wp4_midwide/mitsuba_export.json`
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
- Max changed coverage: `0.04753858024691358`
- Max highlight coverage: `0.021516203703703704`
- Max dark secondary coverage: `0.02787615740740741`
- GIF bytes: `1081483`

## Frame Samples

| Frame | Output | Changed | Highlight | Dark Secondary | Graded |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0.023996913580246915 | 0.0026099537037037037 | 0.021554783950617284 | `build/shots/s417_mitsuba_wp4_sf12_h18_combined/frames/frame_0000.png` |
| 4 | 27 | 0.021356095679012345 | 0.001693672839506173 | 0.01992091049382716 | `build/shots/s417_mitsuba_wp4_sf12_h18_combined/frames/frame_0004.png` |
| 7 | 47 | 0.04753858024691358 | 0.021516203703703704 | 0.02787615740740741 | `build/shots/s417_mitsuba_wp4_sf12_h18_combined/frames/frame_0007.png` |

## Next

Compare this upper-bound response combination against WP4, SS1, S409 SF12_H18, and S401 CR21 before deciding whether to migrate the combined behavior into renderer-native texture/volume controls.
