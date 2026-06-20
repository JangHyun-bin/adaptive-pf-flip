# S345 Mitsuba Depth-Aware Native Replacement Gap MB2

Generated UTC: `2026-06-20T01:25:20.534392+00:00`
Summary JSON: `build/shots/s345_mitsuba_depth_aware_native_replacement_gap_mb2/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s345_mitsuba_depth_aware_native_replacement_gap_mb2/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `40.225236062885806`
- Max native->bridge MAD: `61.84939814814815`
- Mean native->target MAD: `37.13389178240741`
- Max native->target MAD: `66.33950488683128`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `13.97 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 33.3250 | 23.6639 | 12.7509 | `build/shots/s345_mitsuba_depth_aware_native_replacement_gap_mb2/strips/frame_0000.png` |
| 4 | 27 | 61.8494 | 62.5712 | 10.2052 | `build/shots/s345_mitsuba_depth_aware_native_replacement_gap_mb2/strips/frame_0004.png` |
| 7 | 47 | 38.0489 | 26.6309 | 14.0102 | `build/shots/s345_mitsuba_depth_aware_native_replacement_gap_mb2/strips/frame_0007.png` |

## Next

MB2 stress-tests stronger native billboards; use the better MB candidate only if both mean and max target MAD improve over M1 and MB1.
