# S348 Mitsuba Depth-Aware Native Replacement Gap TB2

Generated UTC: `2026-06-20T01:51:42.785861+00:00`
Summary JSON: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb2/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb2/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `13.282437065972223`
- Max native->bridge MAD: `27.063974408436213`
- Mean native->target MAD: `16.95466579861111`
- Max native->target MAD: `31.891748971193415`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `14.53 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 7.2899 | 14.0727 | 12.7509 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb2/strips/frame_0000.png` |
| 4 | 27 | 27.0640 | 27.8992 | 10.2052 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb2/strips/frame_0004.png` |
| 7 | 47 | 8.7577 | 13.8657 | 14.0102 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb2/strips/frame_0007.png` |

## Next

TB2 calibrates native background toward the C3 bridge gray tone; keep it only if it beats TB1 under the S344 gate.
