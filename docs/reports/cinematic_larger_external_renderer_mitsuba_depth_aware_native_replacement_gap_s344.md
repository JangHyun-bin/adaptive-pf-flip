# S344 Mitsuba Depth-Aware Native Replacement Gap M1

Generated UTC: `2026-06-20T01:21:01.547062+00:00`
Summary JSON: `build/shots/s344_mitsuba_depth_aware_native_replacement_gap_m1/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s344_mitsuba_depth_aware_native_replacement_gap_m1/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `40.380344087577164`
- Max native->bridge MAD: `62.06783050411523`
- Mean native->target MAD: `37.286685796039094`
- Max native->target MAD: `66.5063766718107`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `13.91 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 33.3926 | 23.7279 | 12.7509 | `build/shots/s344_mitsuba_depth_aware_native_replacement_gap_m1/strips/frame_0000.png` |
| 4 | 27 | 62.0678 | 62.7899 | 10.2052 | `build/shots/s344_mitsuba_depth_aware_native_replacement_gap_m1/strips/frame_0004.png` |
| 7 | 47 | 38.2524 | 26.7924 | 14.0102 | `build/shots/s344_mitsuba_depth_aware_native_replacement_gap_m1/strips/frame_0007.png` |

## Next

Use this gate to drive the next renderer-native secondary pass; native candidates should beat the C3 bridge mean and max target MAD before replacing the post-render bridge.
