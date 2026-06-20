# S348 Mitsuba Depth-Aware Native Replacement Gap TB1

Generated UTC: `2026-06-20T01:51:42.785554+00:00`
Summary JSON: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb1/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb1/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `16.804846563143006`
- Max native->bridge MAD: `27.432226080246913`
- Mean native->target MAD: `16.39866785622428`
- Max native->target MAD: `32.140062371399175`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `14.46 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 13.0844 | 13.5696 | 12.7509 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb1/strips/frame_0000.png` |
| 4 | 27 | 27.4322 | 28.1427 | 10.2052 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb1/strips/frame_0004.png` |
| 7 | 47 | 13.9511 | 13.2112 | 14.0102 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb1/strips/frame_0007.png` |

## Next

TB1 calibrates native background toward the accepted target; compare with TB2 and keep the better tone baseline.
