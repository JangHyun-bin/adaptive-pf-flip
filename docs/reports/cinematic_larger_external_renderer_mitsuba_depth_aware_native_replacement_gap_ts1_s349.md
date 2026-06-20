# S349 Mitsuba Depth-Aware Native Replacement Gap TS1

Generated UTC: `2026-06-20T02:03:02.882096+00:00`
Summary JSON: `build/shots/s349_mitsuba_depth_aware_native_replacement_gap_ts1/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s349_mitsuba_depth_aware_native_replacement_gap_ts1/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `13.712686471193416`
- Max native->bridge MAD: `22.768213091563787`
- Mean native->target MAD: `19.41354994534465`
- Max native->target MAD: `24.39063721707819`
- Bridge mean target MAD: `11.423722591949588`
- Bridge max target MAD: `14.571005658436214`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `14.36 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 12.8621 | 22.7702 | 12.7509 | `build/shots/s349_mitsuba_depth_aware_native_replacement_gap_ts1/strips/frame_0000.png` |
| 4 | 27 | 17.8472 | 18.7607 | 10.2052 | `build/shots/s349_mitsuba_depth_aware_native_replacement_gap_ts1/strips/frame_0004.png` |
| 7 | 47 | 10.6315 | 21.8380 | 14.0102 | `build/shots/s349_mitsuba_depth_aware_native_replacement_gap_ts1/strips/frame_0007.png` |

## Next

TS1 combines the TB6 tone baseline with SC4-style secondary sprites; keep it only if it improves over TB6 under the C3 bridge gate.
