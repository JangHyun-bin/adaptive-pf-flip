# S397 Mitsuba Residual Local Screen Card C1E Gap

Generated UTC: `2026-06-20T07:57:42.429914+00:00`
Summary JSON: `build/shots/s397_mitsuba_residual_local_screen_card_c1e_gap/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s397_mitsuba_residual_local_screen_card_c1e_gap/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `13.724674961419753`
- Max native->bridge MAD: `22.189097865226337`
- Mean native->target MAD: `19.222715486754115`
- Max native->target MAD: `23.988894675925927`
- Bridge mean target MAD: `11.464264805169753`
- Bridge max target MAD: `14.389824459876543`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `14.37 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 12.5668 | 22.4833 | 12.9329 | `build/shots/s397_mitsuba_residual_local_screen_card_c1e_gap/strips/frame_0000.png` |
| 4 | 27 | 18.5911 | 19.1483 | 10.1813 | `build/shots/s397_mitsuba_residual_local_screen_card_c1e_gap/strips/frame_0004.png` |
| 7 | 47 | 10.6246 | 21.2165 | 14.3401 | `build/shots/s397_mitsuba_residual_local_screen_card_c1e_gap/strips/frame_0007.png` |

## Next

Use this native replacement gap before claiming a renderer-native secondary pass can replace the bridge.
