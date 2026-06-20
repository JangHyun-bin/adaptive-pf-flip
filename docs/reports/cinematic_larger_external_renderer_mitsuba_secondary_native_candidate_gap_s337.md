# S337 Mitsuba Secondary Native Candidate Gap

Generated UTC: `2026-06-20T00:26:24.337834+00:00`
Summary JSON: `build/shots/s337_mitsuba_secondary_native_candidate_gap/secondary_native_candidate_gap_summary.json`
Gallery: `build/shots/s337_mitsuba_secondary_native_candidate_gap/gallery/index.html`
Status: `ready`
Decision: `candidate_needs_work`

## Checks

- Frames: `8`
- Missing references: `0`
- Mean candidate->contract MAD: `46.4042014692644`
- Max candidate->contract MAD: `69.76750578703704`
- Mean candidate->target MAD: `37.58172702867798`
- Max candidate->target MAD: `67.40660365226337`
- Contract mean overlay MAD: `12.566030735596708`
- Contract max overlay MAD: `18.040229552469135`
- Candidate beats contract mean: `False`
- Candidate beats contract max: `False`
- GIF bytes: `13.79 MB`

## Frame Samples

| Frame | Output | Candidate->Contract MAD | Candidate->Target MAD | Contract->Target MAD | Strip |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0 | 38.6374 | 23.8175 | 15.6195 | `build/shots/s337_mitsuba_secondary_native_candidate_gap/strips/frame_0000.png` |
| 4 | 27 | 69.7675 | 63.2584 | 10.8319 | `build/shots/s337_mitsuba_secondary_native_candidate_gap/strips/frame_0004.png` |
| 7 | 47 | 43.8805 | 27.0691 | 18.0402 | `build/shots/s337_mitsuba_secondary_native_candidate_gap/strips/frame_0007.png` |

## Next

Use this measured gap to tune the next renderer-native Mitsuba secondary representation; do not replace the S335 overlay contract until a native candidate beats both mean and max target MAD.
