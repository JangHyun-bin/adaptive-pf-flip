# S347 Mitsuba Depth-Aware Native Replacement Gap SC4

Generated UTC: `2026-06-20T01:46:32.232073+00:00`
Summary JSON: `build/shots/s347_mitsuba_depth_aware_native_replacement_gap_sc4/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s347_mitsuba_depth_aware_native_replacement_gap_sc4/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `40.2254558899177`
- Max native->bridge MAD: `61.848001543209875`
- Mean native->target MAD: `37.13381309477881`
- Max native->target MAD: `66.33893840020576`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `13.96 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 33.3229 | 23.6617 | 12.7509 | `build/shots/s347_mitsuba_depth_aware_native_replacement_gap_sc4/strips/frame_0000.png` |
| 4 | 27 | 61.8480 | 62.5697 | 10.2052 | `build/shots/s347_mitsuba_depth_aware_native_replacement_gap_sc4/strips/frame_0004.png` |
| 7 | 47 | 38.0511 | 26.6325 | 14.0102 | `build/shots/s347_mitsuba_depth_aware_native_replacement_gap_sc4/strips/frame_0007.png` |

## Next

SC4 strengthens emitter sprites sampled from the secondary mask; use this as the sprite-mode stress result before shifting to native tone/background calibration.
