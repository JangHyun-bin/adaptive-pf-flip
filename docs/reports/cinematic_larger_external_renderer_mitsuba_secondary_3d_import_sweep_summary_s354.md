# S354 Mitsuba Secondary 3D Import Sweep Summary

Generated UTC: `2026-06-20T02:40:27.574886+00:00`
Summary JSON: `build/shots/s354_mitsuba_secondary_3d_import_sweep_summary/secondary_candidate_sweep_summary.json`
Status: `ready`
Best candidate: `MW7`
Best max target MAD: `23.951992669753086`
Contract max target MAD: `18.040229552469135`

## Ranking

| Rank | Candidate | Decision | Frames | Mean Target MAD | Max Target MAD | Max Target Diff | Mean Contract MAD | Gallery |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `MW7` | `candidate_needs_work` | 8 | 19.14628649048354 | 23.951992669753086 | 170 | 13.649256044238683 | `build/shots/s351_mitsuba_native_material_mw7_candidate_gap/gallery/index.html` |
| 2 | `SI3` | `candidate_needs_work` | 8 | 19.14765785751029 | 23.95363811728395 | 172 | 13.64452578446502 | `build/shots/s354_mitsuba_secondary_3d_import_si3_candidate_gap/gallery/index.html` |
| 3 | `SI2` | `candidate_needs_work` | 8 | 19.147830905992798 | 23.954052211934158 | 172 | 13.643924012988682 | `build/shots/s354_mitsuba_secondary_3d_import_si2_candidate_gap/gallery/index.html` |
| 4 | `SI1` | `candidate_needs_work` | 8 | 19.148799029063785 | 23.955634002057614 | 172 | 13.642480066872428 | `build/shots/s354_mitsuba_secondary_3d_import_si1_candidate_gap/gallery/index.html` |

## Inputs

- `MW7`: `build/shots/s351_mitsuba_native_material_mw7_candidate_gap/secondary_native_candidate_gap_summary.json` (14.15 MB GIF)
- `SI1`: `build/shots/s354_mitsuba_secondary_3d_import_si1_candidate_gap/secondary_native_candidate_gap_summary.json` (14.17 MB GIF)
- `SI2`: `build/shots/s354_mitsuba_secondary_3d_import_si2_candidate_gap/secondary_native_candidate_gap_summary.json` (14.16 MB GIF)
- `SI3`: `build/shots/s354_mitsuba_secondary_3d_import_si3_candidate_gap/secondary_native_candidate_gap_summary.json` (14.15 MB GIF)

## Next

Keep the sidecar import path, but tune native secondary material/radius/depth attenuation before promoting it over MW7.
