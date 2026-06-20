# S346 Mitsuba Depth-Aware Native Replacement Gap SC1

Generated UTC: `2026-06-20T01:32:58.332559+00:00`
Summary JSON: `build/shots/s346_mitsuba_depth_aware_native_replacement_gap_sc1/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s346_mitsuba_depth_aware_native_replacement_gap_sc1/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `40.22522456918724`
- Max native->bridge MAD: `61.84936728395062`
- Mean native->target MAD: `37.133900704089505`
- Max native->target MAD: `66.33952031893004`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `13.97 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 33.3250 | 23.6639 | 12.7509 | `build/shots/s346_mitsuba_depth_aware_native_replacement_gap_sc1/strips/frame_0000.png` |
| 4 | 27 | 61.8494 | 62.5711 | 10.2052 | `build/shots/s346_mitsuba_depth_aware_native_replacement_gap_sc1/strips/frame_0004.png` |
| 7 | 47 | 38.0489 | 26.6309 | 14.0102 | `build/shots/s346_mitsuba_depth_aware_native_replacement_gap_sc1/strips/frame_0007.png` |

## Next

SC1 uses a renderer-side bitmap opacity card from the secondary mask; tune mask orientation/gain only if it improves over MB2 under the S344 gate.
