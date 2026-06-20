# S348 Mitsuba Depth-Aware Native Replacement Gap TB5

Generated UTC: `2026-06-20T01:55:41.719167+00:00`
Summary JSON: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb5/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb5/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `13.144793917181069`
- Max native->bridge MAD: `20.340931712962963`
- Mean native->target MAD: `18.48948760609568`
- Max native->target MAD: `25.238513374485596`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `14.23 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 10.8463 | 20.3176 | 12.7509 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb5/strips/frame_0000.png` |
| 4 | 27 | 20.3409 | 21.2235 | 10.2052 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb5/strips/frame_0004.png` |
| 7 | 47 | 9.2389 | 19.4826 | 14.0102 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb5/strips/frame_0007.png` |

## Next

TB5 narrows the background sweep around TB4; keep the best candidate by max target MAD under the C3 bridge gate.
