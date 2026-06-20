# S423 S409 SF12 H18 Channel Band Mask Source

Generated UTC: `2026-06-20T11:22:04.395362+00:00`
Summary JSON: `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/source_response_mask_source_summary.json`
Gallery: `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/gallery/index.html`
Status: `ready`

## Settings

- Profile: `default`
- Mask kind: `channel-band`
- Alpha value: `255`
- Blur radius: `0.0`
- Dilate radius: `0`
- Channel mask channels: `['foam', 'spray']`
- Secondary alpha threshold: `4`
- Highlight source luma threshold: `120.0`
- Highlight alpha max: `3`
- Channel band source luma: `0.0..95.0`
- Channel band strength: `0.12`
- Channel band max delta: `18.0`

## Checks

- Frames: `8`
- Max mask coverage: `0.0132445987654321`
- Mean mask coverage: `0.00808641975308642`
- Mask bytes: `55.63 KB`
- GIF bytes: `26.64 KB`

## Frames

| Output | Coverage | Mask | Strip |
| ---: | ---: | --- | --- |
| 0 | 0.011321 | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/masks/frame_0000.png` | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/strips/frame_0000_source_response_mask.png` |
| 7 | 0.005876 | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/masks/frame_0001.png` | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/strips/frame_0001_source_response_mask.png` |
| 13 | 0.005380 | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/masks/frame_0002.png` | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/strips/frame_0002_source_response_mask.png` |
| 20 | 0.004552 | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/masks/frame_0003.png` | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/strips/frame_0003_source_response_mask.png` |
| 27 | 0.005208 | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/masks/frame_0004.png` | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/strips/frame_0004_source_response_mask.png` |
| 34 | 0.006622 | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/masks/frame_0005.png` | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/strips/frame_0005_source_response_mask.png` |
| 40 | 0.012486 | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/masks/frame_0006.png` | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/strips/frame_0006_source_response_mask.png` |
| 47 | 0.013245 | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/masks/frame_0007.png` | `build/shots/s423_mitsuba_s409_sf12_h18_channel_band_mask_source/strips/frame_0007_source_response_mask.png` |

## Next

Use this source-response mask package to drive renderer-native spray/foam attenuation.
