# S348 Mitsuba Depth-Aware Native Replacement Gap TB4

Generated UTC: `2026-06-20T01:54:15.283955+00:00`
Summary JSON: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb4/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb4/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `12.977909834747942`
- Max native->bridge MAD: `23.152771347736625`
- Mean native->target MAD: `17.635921103395063`
- Max native->target MAD: `28.016278935185184`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `14.55 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 9.0234 | 17.5941 | 12.7509 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb4/strips/frame_0000.png` |
| 4 | 27 | 23.1528 | 24.0064 | 10.2052 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb4/strips/frame_0004.png` |
| 7 | 47 | 8.5071 | 16.9213 | 14.0102 | `build/shots/s348_mitsuba_depth_aware_native_replacement_gap_tb4/strips/frame_0007.png` |

## Next

TB4 narrows the background sweep around TB2; keep the best candidate by max target MAD under the C3 bridge gate.
