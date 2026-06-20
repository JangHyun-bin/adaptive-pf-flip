# S423 S401 CR21 Channel Band Mask Source

Generated UTC: `2026-06-20T11:21:30.423652+00:00`
Summary JSON: `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/source_response_mask_source_summary.json`
Gallery: `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/gallery/index.html`
Status: `ready`

## Settings

- Profile: `cr21`
- Mask kind: `channel-band`
- Alpha value: `255`
- Blur radius: `0.0`
- Dilate radius: `0`
- Channel mask channels: `['bubble', 'droplet', 'foam', 'spray']`
- Secondary alpha threshold: `4`
- Highlight source luma threshold: `120.0`
- Highlight alpha max: `3`
- Channel band source luma: `75.0..82.0`
- Channel band strength: `0.6`
- Channel band max delta: `56.0`

## Checks

- Frames: `8`
- Max mask coverage: `0.0014429012345679012`
- Mean mask coverage: `0.0004523533950617284`
- Mask bytes: `30.27 KB`
- GIF bytes: `14.35 KB`

## Frames

| Output | Coverage | Mask | Strip |
| ---: | ---: | --- | --- |
| 0 | 0.001443 | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/masks/frame_0000.png` | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/strips/frame_0000_source_response_mask.png` |
| 7 | 0.000218 | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/masks/frame_0001.png` | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/strips/frame_0001_source_response_mask.png` |
| 13 | 0.000262 | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/masks/frame_0002.png` | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/strips/frame_0002_source_response_mask.png` |
| 20 | 0.000014 | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/masks/frame_0003.png` | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/strips/frame_0003_source_response_mask.png` |
| 27 | 0.000039 | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/masks/frame_0004.png` | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/strips/frame_0004_source_response_mask.png` |
| 34 | 0.000079 | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/masks/frame_0005.png` | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/strips/frame_0005_source_response_mask.png` |
| 40 | 0.000575 | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/masks/frame_0006.png` | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/strips/frame_0006_source_response_mask.png` |
| 47 | 0.000990 | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/masks/frame_0007.png` | `build/shots/s423_mitsuba_s401_cr21_channel_band_mask_source/strips/frame_0007_source_response_mask.png` |

## Next

Use this source-response mask package to drive renderer-native channel-band attenuation.
