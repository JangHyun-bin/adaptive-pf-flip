# S418 Mitsuba Water Disk Patch Summary

Generated UTC: `2026-06-20T10:34:00Z`

Public compare URL:
`https://forth-broadcasting-engagement-appointment.trycloudflare.com/index.html`

## Goal

Move the S417 light-only improvement toward a renderer-native representation by
replacing many small water-surface sphere emitters with fewer clustered
camera-facing disk area emitters.

## Code Change

Added:

- `tools/add_mitsuba_water_mask_patch_emitters.py`

The tool consumes the same base Mitsuba XML export and S410 highlight mask
source used by S415/S416. It projects water mesh vertices to screen space,
clusters mask-hit vertices, and inserts a small number of world-space Mitsuba
disk area emitters at the clustered water-surface positions.

This is renderer-native XML geometry/light input. It is not a camera-plane
screen card and it is not a post-response grade.

## Candidates

| Candidate | Patches | Style | Max Gap MAD |
| --- | ---: | --- | ---: |
| `DP1` | 32 | soft clustered disks | 23.99034465020576 |
| `DP2` | 24 | wider lower-radiance disks | 23.980085519547327 |
| `DP3` | 26 | stronger clustered disks | 24.00698431069959 |
| `DP4` | 25 | bright larger disks | 24.130503472222223 |
| `DP5` | 22 | hot wide disks | 24.014149305555556 |

## Result

DP2 is the best S418 native disk-patch candidate, but it should not be
promoted.

| Rank | Candidate | Mean Gap MAD | Max Gap MAD | Max Gap |
| ---: | --- | ---: | ---: | ---: |
| 1 | `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| 2 | `S409_SF12_H18` | 18.756908677340533 | 23.687431841563786 | 170 |
| 3 | `SF12_SprayFoam` | 19.120776588220163 | 23.755951646090534 | 170 |
| 4 | `S417_WP4_H18_D90` | 19.182991817772635 | 23.948739068930042 | 255 |
| 5 | `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |
| 6 | `S416_WP4` | 19.31142160172325 | 23.97967785493827 | 255 |
| 7 | `S418_DP2` | 19.237632458847738 | 23.980085519547327 | 232 |
| 8 | `S418_DP1` | 19.2402053594393 | 23.99034465020576 | 226 |
| 9 | `S418_DP3` | 19.276629533179012 | 24.00698431069959 | 226 |
| 10 | `S418_DP5` | 19.711589988425924 | 24.014149305555556 | 255 |
| 11 | `S418_DP4` | 19.599884420010287 | 24.130503472222223 | 255 |

Visual review shows the same split as the numbers. DP2 is smoother but too dim
and too close to SS1. DP5 makes the highlight more visible, but the result
returns to an over-patched, speckled look. The disk approach does not reproduce
the connected S409/S401 highlight band.

## Artifacts

- DP1 export/validation/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp1_export_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp1_validation_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp1_render_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp1_target_gap_s418.md`
- DP2 export/validation/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp2_export_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp2_validation_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp2_render_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp2_target_gap_s418.md`
- DP3 export/validation/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp3_export_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp3_validation_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp3_render_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp3_target_gap_s418.md`
- DP4 export/validation/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp4_export_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp4_validation_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp4_render_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp4_target_gap_s418.md`
- DP5 export/validation/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp5_export_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp5_validation_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp5_render_s418.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_dp5_target_gap_s418.md`
- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_sweep_summary_s418.md`
- Compare report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_compare_s418.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_compare_publish_s418.md`

## Validation

- `python -m py_compile tools/add_mitsuba_water_mask_patch_emitters.py`
- DP1-DP5 XML validation: each `ready`, `8` parsed, `0` failures, `0` warnings
- DP1-DP5 Mitsuba render: each `ready`, `8` frames, `0` failures
- DP1-DP5 target gap: each `ready`
- Sweep summary: `ready`
- Compare gallery: `ready`
- Public compare `index.html`: HTTP `200`
- Public compare `assets/comparison.gif`: HTTP `200`

## Decision

Do not promote clustered disk patch emitters as the final renderer-native
replacement. Keep the tool as evidence and a reusable native-light probe, but
carry S417 `WP4_H18_D90` as the better current upper-bound candidate.

## Next

S419 should move the S417/S418 evidence into water material, texture, or volume
mask controls instead of adding more discrete geometry emitters.
