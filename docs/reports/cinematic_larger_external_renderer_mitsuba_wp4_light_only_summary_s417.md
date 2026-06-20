# S417 Mitsuba WP4 Light Only Summary

Generated UTC: `2026-06-20T10:22:00Z`

Public compare URL:
`https://fires-factors-can-eugene.trycloudflare.com/index.html`

## Goal

Test whether S416 WP4 can be improved by combining it with the previously
accepted SF12 response family. The pass starts with the planned WP4 plus SF12
dark-band combination, then isolates light-only variants after the dark-band
path regresses.

## Code Change

Added:

- `tools/build_mitsuba_render_response_input.py`

The tool wraps a Mitsuba render manifest as an
`lsfs_mitsuba_secondary_composite` input by preserving existing secondary layer
metadata and replacing the composite source image with the render preview. This
lets existing source-region response tooling run on native render candidates
without duplicating response code.

## Candidates

| Candidate | Response | Max Gap MAD |
| --- | --- | ---: |
| `S417_WP4_H18_D90` | Light only, threshold `120`, strength `0.85`, max delta `90` | 23.948739068930042 |
| `S417_WP4_H18_T130` | Light only, threshold `130`, strength `0.85`, max delta `120` | 23.94876350308642 |
| `S417_WP4_H18_LightOnly` | Light only, threshold `120`, strength `0.85`, max delta `120` | 23.949612911522635 |
| `S417_WP4_H18_S075_D110` | Light only, threshold `120`, strength `0.75`, max delta `110` | 23.951015303497943 |
| `S417_WP4_H17_LightOnly` | Light only, threshold `120`, strength `0.70`, max delta `90` | 23.951739326131687 |
| `S417_WP4_H19_LightOnly` | Light only, threshold `120`, strength `1.0`, max delta `255` | 23.95417309670782 |
| `S417_WP4_H15_LightOnly` | Light only, threshold `120`, strength `0.45`, max delta `55` | 23.959123585390948 |
| `S417_WP4_SF12_H18` | SF12 dark band plus H18 highlight | 24.126077031893004 |
| `S417_WP4_SF12_H15` | SF12 dark band plus H15 highlight | 24.135587705761317 |
| `S417_WP4_SF12_DarkOnly` | SF12 dark band only | 24.156141975308643 |

## Result

S417 found a small upper-bound improvement over WP4 and SS1, but it did not
close the larger S409/S401 gap.

| Rank | Candidate | Mean Gap MAD | Max Gap MAD | Max Gap |
| ---: | --- | ---: | ---: | ---: |
| 1 | `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| 2 | `S409_SF12_H18` | 18.756908677340533 | 23.687431841563786 | 170 |
| 3 | `SF12_SprayFoam` | 19.120776588220163 | 23.755951646090534 | 170 |
| 4 | `S417_WP4_H18_D90` | 19.182991817772635 | 23.948739068930042 | 255 |
| 5 | `S417_WP4_H18_T130` | 19.159292775848765 | 23.94876350308642 | 255 |
| 6 | `S417_WP4_H18_LightOnly` | 19.18498119212963 | 23.949612911522635 | 255 |
| 7 | `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |
| 8 | `S416_WP4` | 19.31142160172325 | 23.97967785493827 | 255 |
| 9 | `S417_WP4_SF12_H18` | 19.287424125514402 | 24.126077031893004 | 255 |
| 10 | `S417_WP4_SF12_DarkOnly` | 19.413864535108026 | 24.156141975308643 | 255 |

Visual review matches the numbers. `S417_WP4_H18_D90` broadens the bright
source-highlight band over WP4, but the dark-band SF12 combination suppresses
the image in the wrong places and should not be carried forward.

## Artifacts

- Response input wrapper:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_sf12_response_input_s417.md`
- WP4 plus SF12 H18 response and target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_sf12_h18_combined_s417.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_sf12_h18_combined_target_gap_s417.md`
- WP4 plus SF12 dark-only response and target gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_sf12_dark_only_s417.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_sf12_dark_only_target_gap_s417.md`
- WP4 light-only H15/H17/H18/H19 response and target-gap reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_h15_light_only_s417.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_h17_light_only_s417.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_h18_light_only_s417.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_h19_light_only_s417.md`
- WP4 H18 tuning reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_h18_d90_light_only_s417.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_h18_t130_light_only_s417.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_h18_t145_light_only_s417.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_h18_s075_d110_light_only_s417.md`
- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_light_only_sweep_summary_s417.md`
- Compare report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_light_only_compare_s417.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_wp4_light_only_compare_publish_s417.md`

## Validation

- `python -m py_compile tools/build_mitsuba_render_response_input.py`
- Response input wrapper: `ready`, `8` frames
- S417 response candidates: each `ready`, `8` frames
- S417 target-gap reports: each `ready`, `8` frames
- Sweep summary: `ready`
- Compare gallery: `ready`
- Public compare `index.html`: HTTP `200`
- Public compare `assets/comparison.gif`: HTTP `200`

## Decision

Carry `S417_WP4_H18_D90` as a small upper-bound improvement over WP4 and SS1.
Reject SF12 dark-band combination on WP4; it makes the target gap worse.

## Next

S418 should migrate the light-only behavior away from post-response grading and
toward a renderer-native water texture, area patch, or volume/emission mask.
