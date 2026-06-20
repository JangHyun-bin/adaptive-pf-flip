# S345 Mitsuba Depth-Aware Native Replacement Gap MB1

Generated UTC: `2026-06-20T01:23:37.150877+00:00`
Summary JSON: `build/shots/s345_mitsuba_depth_aware_native_replacement_gap_mb1/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s345_mitsuba_depth_aware_native_replacement_gap_mb1/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `40.337390367798356`
- Max native->bridge MAD: `62.021087962962966`
- Mean native->target MAD: `37.244551263503084`
- Max native->target MAD: `66.46181069958848`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `13.95 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 33.3836 | 23.7184 | 12.7509 | `build/shots/s345_mitsuba_depth_aware_native_replacement_gap_mb1/strips/frame_0000.png` |
| 4 | 27 | 62.0211 | 62.7432 | 10.2052 | `build/shots/s345_mitsuba_depth_aware_native_replacement_gap_mb1/strips/frame_0004.png` |
| 7 | 47 | 38.1665 | 26.7210 | 14.0102 | `build/shots/s345_mitsuba_depth_aware_native_replacement_gap_mb1/strips/frame_0007.png` |

## Next

MB1 is measured against the C3 bridge gate; continue native proxy tuning only if it improves both mean and max target MAD over M1.
