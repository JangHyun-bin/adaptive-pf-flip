# S347 Mitsuba Depth-Aware Native Replacement Gap SC3

Generated UTC: `2026-06-20T01:44:24.808838+00:00`
Summary JSON: `build/shots/s347_mitsuba_depth_aware_native_replacement_gap_sc3/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s347_mitsuba_depth_aware_native_replacement_gap_sc3/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `40.225885497042185`
- Max native->bridge MAD: `61.84857381687243`
- Mean native->target MAD: `37.13424913194444`
- Max native->target MAD: `66.33931455761316`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `13.96 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 33.3269 | 23.6655 | 12.7509 | `build/shots/s347_mitsuba_depth_aware_native_replacement_gap_sc3/strips/frame_0000.png` |
| 4 | 27 | 61.8486 | 62.5702 | 10.2052 | `build/shots/s347_mitsuba_depth_aware_native_replacement_gap_sc3/strips/frame_0004.png` |
| 7 | 47 | 38.0504 | 26.6323 | 14.0102 | `build/shots/s347_mitsuba_depth_aware_native_replacement_gap_sc3/strips/frame_0007.png` |

## Next

SC3 adds emitter sprites sampled from the secondary mask; continue only if it improves over S345 MB2 under the C3 bridge gate.
