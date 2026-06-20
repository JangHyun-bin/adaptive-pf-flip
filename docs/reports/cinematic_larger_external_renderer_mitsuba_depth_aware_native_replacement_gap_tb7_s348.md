# S348 Mitsuba Depth-Aware Native Replacement Gap TB7

Generated UTC: `2026-06-20T01:58:05.988215+00:00`
Summary JSON: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb7/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb7/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `14.567937483924897`
- Max native->bridge MAD: `25.367307098765433`
- Mean native->target MAD: `20.494666923868312`
- Max native->target MAD: `26.986793981481483`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `14.04 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 15.2091 | 25.3196 | 12.7509 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb7/strips/frame_0000.png` |
| 4 | 27 | 15.2860 | 16.2423 | 10.2052 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb7/strips/frame_0004.png` |
| 7 | 47 | 12.5129 | 24.3106 | 14.0102 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb7/strips/frame_0007.png` |

## Next

TB7 tests the lower edge of the successful background range; keep the best candidate by max target MAD under the C3 bridge gate.
