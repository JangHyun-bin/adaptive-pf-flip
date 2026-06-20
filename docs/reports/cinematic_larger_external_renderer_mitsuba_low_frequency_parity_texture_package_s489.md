# S489 Mitsuba Low Frequency Parity Texture Package

Generated UTC: `2026-06-20T17:44:00.282023+00:00`
Summary JSON: `build/shots/s489_mitsuba_low_frequency_parity_texture_package/low_frequency_parity_texture_package_summary.json`
CSV: `build/shots/s489_mitsuba_low_frequency_parity_texture_package/low_frequency_parity_texture_stats.csv`
Gallery: `build/shots/s489_mitsuba_low_frequency_parity_texture_package/gallery/index.html`
Status: `ready`

## Checks

- Frames: `8`
- Textures per frame: `12`
- Max applied delta: `23`
- Max signed-offset clipped channels: `0`
- Max dark damping coverage: `0.07431712962962964`
- Max reconstruction abs diff: `0`
- Max reconstruction mean diff: `0.0`
- Texture bytes: `10.68 MB`
- GIF bytes: `8.95 MB`

## Textures

- `base_rgb`
- `target_rgb`
- `proxy_rgb`
- `parity_composite_rgb`
- `raw_low_frequency_delta_rgb`
- `applied_positive_delta_rgb`
- `applied_negative_delta_rgb`
- `applied_signed_offset_rgb`
- `applied_magnitude_luma`
- `applied_mask_luma`
- `dark_damping_mask_luma`
- `dark_damping_weight_luma`

## Frame Samples

| Frame | Output | Coverage | Max Delta | Recon Max Diff | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 0.08149112654320988 | 13 | 0 | `build/shots/s489_mitsuba_low_frequency_parity_texture_package/strips/frame_0000_texture_package.png` |
| 4 | 27 | 0.06519868827160494 | 10 | 0 | `build/shots/s489_mitsuba_low_frequency_parity_texture_package/strips/frame_0004_texture_package.png` |
| 7 | 47 | 0.18508873456790123 | 23 | 0 | `build/shots/s489_mitsuba_low_frequency_parity_texture_package/strips/frame_0007_texture_package.png` |

## Next

Consume this texture package through a native post-tonemap texture stage, then compare against S478, S487 LF3, and S485 LRS4 target-gap gates.
