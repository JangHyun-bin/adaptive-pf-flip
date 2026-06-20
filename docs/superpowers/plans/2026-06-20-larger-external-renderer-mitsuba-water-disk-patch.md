# Larger External Renderer: Mitsuba Water Disk Patch

Status: complete

## Goal

Replace WP4-style water-surface sphere emitters with fewer clustered disk area
emitters to test whether a smoother renderer-native highlight patch can match
the accepted visual response.

## Result

S418 added a clustered disk patch emitter tool and evaluated DP1-DP5.

- Public compare gallery:
  `https://forth-broadcasting-engagement-appointment.trycloudflare.com/index.html`
- Summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_summary_s418.md`
- Sweep:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_disk_patch_sweep_summary_s418.md`

DP2 is the best S418 native disk patch with max target MAD
`23.980085519547327`. This is close to S416 WP4 `23.97967785493827`, but worse
than S417 `WP4_H18_D90` at `23.948739068930042` and SS1 at
`23.951853137860084`.

## Code Change

- Added `tools/add_mitsuba_water_mask_patch_emitters.py`.

The tool projects water vertices into the S410 highlight mask, clusters
selected vertices in screen space, and inserts camera-facing Mitsuba disk area
emitters at the clustered water-surface positions.

## Validation

- `python -m py_compile tools/add_mitsuba_water_mask_patch_emitters.py`
- XML validation for DP1-DP5
- Mitsuba render for DP1-DP5
- Target-gap reports for DP1-DP5
- Sweep summary and compare gallery
- Published compare gallery with HTTP `200`

## Decision

Do not promote disk patch emitters. DP2 is smoother than the hotter disk
variants, but it is still too weak and does not recover the connected
S409/S401 highlight band.

## Next

S419 should move from discrete emitters to water material, texture, or volume
mask controls.
