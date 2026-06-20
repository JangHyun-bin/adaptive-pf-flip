# S348 Mitsuba Depth-Aware Native Replacement Gap TB3

Generated UTC: `2026-06-20T01:53:08.502168+00:00`
Summary JSON: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb3/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb3/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `18.47231240354938`
- Max native->bridge MAD: `32.89957690329218`
- Mean native->target MAD: `24.183378584747942`
- Max native->target MAD: `34.51135030864197`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `14.35 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 22.5371 | 32.7278 | 12.7509 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb3/strips/frame_0000.png` |
| 4 | 27 | 8.8901 | 9.7424 | 10.2052 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb3/strips/frame_0004.png` |
| 7 | 47 | 19.3963 | 31.5840 | 14.0102 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb3/strips/frame_0007.png` |

## Next

TB3 lowers native background further; use it as the tone baseline only if it beats TB2 under the C3 bridge gate.
