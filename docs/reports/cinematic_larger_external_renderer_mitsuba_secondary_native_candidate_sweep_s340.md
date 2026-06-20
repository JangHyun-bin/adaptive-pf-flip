# S340 Mitsuba Secondary Native Candidate Sweep

Generated UTC: `2026-06-20T00:50:12.584668+00:00`
Summary JSON: `build/shots/s340_mitsuba_secondary_native_candidate_sweep/candidate_sweep_summary.json`
Status: `ready`
Best candidate: `mist_m1`
Best max target MAD: `66.5063766718107`
Contract max target MAD: `18.040229552469135`

## Ranking

| Rank | Candidate | Decision | Frames | Mean Target MAD | Max Target MAD | Max Target Diff | Mean Contract MAD | Gallery |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `mist_m1` | `candidate_needs_work` | 8 | 37.286685796039094 | 66.5063766718107 | 165 | 45.988710615997945 | `build/shots/s338_mitsuba_secondary_mist_m1_candidate_gap/gallery/index.html` |
| 2 | `mist_m2` | `candidate_needs_work` | 8 | 37.38058802726338 | 66.78048096707819 | 165 | 46.11256831918725 | `build/shots/s338_mitsuba_secondary_mist_m2_candidate_gap/gallery/index.html` |
| 3 | `billboard_b4` | `candidate_needs_work` | 8 | 37.57644900977366 | 67.3997678755144 | 171 | 46.398785686728395 | `build/shots/s339_mitsuba_secondary_billboard_b4_candidate_gap/gallery/index.html` |
| 4 | `h2` | `candidate_needs_work` | 8 | 37.58172702867798 | 67.40660365226337 | 171 | 46.4042014692644 | `build/shots/s339_mitsuba_runtime_h2_rerender_control_candidate_gap/gallery/index.html` |

## Inputs

- `h2`: `build/shots/s339_mitsuba_runtime_h2_rerender_control_candidate_gap/secondary_native_candidate_gap_summary.json` (13.79 MB GIF)
- `mist_m1`: `build/shots/s338_mitsuba_secondary_mist_m1_candidate_gap/secondary_native_candidate_gap_summary.json` (13.82 MB GIF)
- `mist_m2`: `build/shots/s338_mitsuba_secondary_mist_m2_candidate_gap/secondary_native_candidate_gap_summary.json` (13.83 MB GIF)
- `billboard_b4`: `build/shots/s339_mitsuba_secondary_billboard_b4_candidate_gap/secondary_native_candidate_gap_summary.json` (13.81 MB GIF)

## Next

Use mist_m1 as the current best native Mitsuba secondary baseline, but move next to depth-aware renderer compositing because all native candidates still trail the S335 overlay contract.
