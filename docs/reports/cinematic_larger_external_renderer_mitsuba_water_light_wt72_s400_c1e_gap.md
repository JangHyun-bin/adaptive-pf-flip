# S400 Mitsuba Water Transmittance 72 C1E Gap

Generated UTC: `2026-06-20T08:12:37.595138+00:00`
Summary JSON: `build/shots/s400_mitsuba_water_light_wt72_c1e_gap/depth_aware_native_replacement_gap_summary.json`
Gallery: `build/shots/s400_mitsuba_water_light_wt72_c1e_gap/gallery/index.html`
Status: `ready`
Decision: `native_candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean native->bridge MAD: `16.511500691229422`
- Max native->bridge MAD: `26.125221193415637`
- Mean native->target MAD: `21.136787712191357`
- Max native->target MAD: `27.907768775720164`
- Bridge mean target MAD: `11.464264805169753`
- Bridge max target MAD: `14.389824459876543`
- Native beats bridge mean: `False`
- Native beats bridge max: `False`
- GIF bytes: `13.73 MB`

## Frame Samples

| Frame | Output | Native->Bridge MAD | Native->Target MAD | Bridge->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 16.5374 | 26.4457 | 12.9329 | `build/shots/s400_mitsuba_water_light_wt72_c1e_gap/strips/frame_0000.png` |
| 4 | 27 | 17.6469 | 16.1615 | 10.1813 | `build/shots/s400_mitsuba_water_light_wt72_c1e_gap/strips/frame_0004.png` |
| 7 | 47 | 14.1860 | 24.9807 | 14.3401 | `build/shots/s400_mitsuba_water_light_wt72_c1e_gap/strips/frame_0007.png` |

## Next

Use this native replacement gap before claiming a renderer-native secondary pass can replace the bridge.
