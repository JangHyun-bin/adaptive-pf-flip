# S356 Mitsuba Secondary 3D Depth Material Sweep Summary

Generated UTC: `2026-06-20T02:53:28.254414+00:00`
Summary JSON: `build/shots/s356_mitsuba_secondary_3d_depth_sweep_summary/secondary_candidate_sweep_summary.json`
Status: `ready`
Best candidate: `SD4`
Best max target MAD: `23.95192901234568`
Contract max target MAD: `18.040229552469135`

## Ranking

| Rank | Candidate | Decision | Frames | Mean Target MAD | Max Target MAD | Max Target Diff | Mean Contract MAD | Gallery |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `SD4` | `candidate_needs_work` | 8 | 19.146287133487654 | 23.95192901234568 | 170 | 13.649246559927983 | `build/shots/s356_mitsuba_secondary_3d_depth_sd4_candidate_gap/gallery/index.html` |
| 2 | `SD2` | `candidate_needs_work` | 8 | 19.14630787037037 | 23.95194765946502 | 170 | 13.649191100823046 | `build/shots/s356_mitsuba_secondary_3d_depth_sd2_candidate_gap/gallery/index.html` |
| 3 | `SD5` | `candidate_needs_work` | 8 | 19.146268888245885 | 23.951959233539096 | 170 | 13.649220277134773 | `build/shots/s356_mitsuba_secondary_3d_depth_sd5_candidate_gap/gallery/index.html` |
| 4 | `MW7` | `candidate_needs_work` | 8 | 19.14628649048354 | 23.951992669753086 | 170 | 13.649256044238683 | `build/shots/s351_mitsuba_native_material_mw7_candidate_gap/gallery/index.html` |
| 5 | `SR3` | `candidate_needs_work` | 8 | 19.14634050282922 | 23.95214699074074 | 170 | 13.648984535751028 | `build/shots/s355_mitsuba_secondary_3d_radius_sr3_candidate_gap/gallery/index.html` |
| 6 | `SD3` | `candidate_needs_work` | 8 | 19.146252491640947 | 23.95215920781893 | 170 | 13.648978829089506 | `build/shots/s356_mitsuba_secondary_3d_depth_sd3_candidate_gap/gallery/index.html` |
| 7 | `SD1` | `candidate_needs_work` | 8 | 19.146315023791153 | 23.95216370884774 | 170 | 13.648957609953703 | `build/shots/s356_mitsuba_secondary_3d_depth_sd1_candidate_gap/gallery/index.html` |

## Inputs

- `MW7`: `build/shots/s351_mitsuba_native_material_mw7_candidate_gap/secondary_native_candidate_gap_summary.json` (14.15 MB GIF)
- `SR3`: `build/shots/s355_mitsuba_secondary_3d_radius_sr3_candidate_gap/secondary_native_candidate_gap_summary.json` (14.14 MB GIF)
- `SD1`: `build/shots/s356_mitsuba_secondary_3d_depth_sd1_candidate_gap/secondary_native_candidate_gap_summary.json` (14.13 MB GIF)
- `SD2`: `build/shots/s356_mitsuba_secondary_3d_depth_sd2_candidate_gap/secondary_native_candidate_gap_summary.json` (14.15 MB GIF)
- `SD3`: `build/shots/s356_mitsuba_secondary_3d_depth_sd3_candidate_gap/secondary_native_candidate_gap_summary.json` (14.16 MB GIF)
- `SD4`: `build/shots/s356_mitsuba_secondary_3d_depth_sd4_candidate_gap/secondary_native_candidate_gap_summary.json` (14.15 MB GIF)
- `SD5`: `build/shots/s356_mitsuba_secondary_3d_depth_sd5_candidate_gap/secondary_native_candidate_gap_summary.json` (14.15 MB GIF)

## Next

Use SD4 as the first sidecar import candidate that beats MW7 by max target MAD, then tune a more visible sidecar representation without losing that gate.
