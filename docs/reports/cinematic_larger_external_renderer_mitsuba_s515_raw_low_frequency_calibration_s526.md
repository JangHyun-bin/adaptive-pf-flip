# S526 Mitsuba S515 Raw Low Frequency Calibration

Generated UTC: `2026-06-20T20:00:49.872016+00:00`
Summary JSON: `build/shots/s526_mitsuba_s515_raw_low_frequency_calibration/low_frequency_parity_summary.json`
Gallery: `build/shots/s526_mitsuba_s515_raw_low_frequency_calibration/gallery/index.html`
Status: `ready`

## Settings

- gain: `0.9`
- blur_radius: `6.0`
- max_delta: `48.0`
- target_dark_luma: `55.0`
- dark_damping: `0.35`
- layer_gain: `5.0`
- fps: `2.0`
- keyframes: `4`

## Checks

- Frames: `8`
- Mean target MAD: `32.275872476208846`
- Max target MAD: `63.70094843106996`
- Max target diff: `138`
- Mean proxy parity MAD: `39.0278013278035`
- Max proxy parity MAD: `40.56531378600823`

## Frame Samples

| Frame | Output | Target MAD | Proxy MAD | Layer Max | Composite | Strip |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 0 | 18.12492862654321 | 38.67649112654321 | 216 | `build/shots/s526_mitsuba_s515_raw_low_frequency_calibration/composites/frame_0000.png` | `build/shots/s526_mitsuba_s515_raw_low_frequency_calibration/strips/frame_0000_low_frequency_parity.png` |
| 4 | 27 | 58.62373906893004 | 39.775761316872426 | 216 | `build/shots/s526_mitsuba_s515_raw_low_frequency_calibration/composites/frame_0004.png` | `build/shots/s526_mitsuba_s515_raw_low_frequency_calibration/strips/frame_0004_low_frequency_parity.png` |
| 7 | 47 | 21.669796167695473 | 38.5488683127572 | 216 | `build/shots/s526_mitsuba_s515_raw_low_frequency_calibration/composites/frame_0007.png` | `build/shots/s526_mitsuba_s515_raw_low_frequency_calibration/strips/frame_0007_low_frequency_parity.png` |

## Next

Package this S515-family low-frequency calibration into runtime textures if it beats the global-gain correction review candidate.
