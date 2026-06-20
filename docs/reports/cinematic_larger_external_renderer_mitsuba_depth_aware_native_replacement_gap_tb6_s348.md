# S348 Mitsuba Depth-Aware Native Replacement Gap TB6

Generated UTC: `2026-06-20T01:56:57.115661+00:00`
Summary JSON: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb6/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb6/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `13.710569621270576`
- Max native->bridge MAD: `22.76778034979424`
- Mean native->target MAD: `19.411650913065845`
- Max native->target MAD: `24.390221193415638`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `14.38 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 12.8610 | 22.7683 | 12.7509 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb6/strips/frame_0000.png` |
| 4 | 27 | 17.8480 | 18.7616 | 10.2052 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb6/strips/frame_0004.png` |
| 7 | 47 | 10.6267 | 21.8352 | 14.0102 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb6/strips/frame_0007.png` |

## Next

TB6 tests a lower background than TB5; keep the best candidate by max target MAD under the C3 bridge gate.
