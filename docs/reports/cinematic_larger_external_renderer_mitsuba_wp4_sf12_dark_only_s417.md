# S417 Mitsuba WP4 plus SF12 Dark Only

Generated UTC: `2026-06-20T10:15:55.374775+00:00`
Summary JSON: `build/shots/s417_mitsuba_wp4_sf12_dark_only/source_region_response_summary.json`
Gallery: `build/shots/s417_mitsuba_wp4_sf12_dark_only/gallery/index.html`
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
- Max changed coverage: `0.02787615740740741`
- Max highlight coverage: `0.0`
- Max dark secondary coverage: `0.02787615740740741`
- GIF bytes: `1086665`

## Frame Samples

| Frame | Output | Changed | Highlight | Dark Secondary | Graded |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0.021554783950617284 | 0.0 | 0.021554783950617284 | `build/shots/s417_mitsuba_wp4_sf12_dark_only/frames/frame_0000.png` |
| 4 | 27 | 0.01992091049382716 | 0.0 | 0.01992091049382716 | `build/shots/s417_mitsuba_wp4_sf12_dark_only/frames/frame_0004.png` |
| 7 | 47 | 0.02787615740740741 | 0.0 | 0.02787615740740741 | `build/shots/s417_mitsuba_wp4_sf12_dark_only/frames/frame_0007.png` |

## Next

Compare this dark-only response against WP4 and the stronger H15/H18 variants.
