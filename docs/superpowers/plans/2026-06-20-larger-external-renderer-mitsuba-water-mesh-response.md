# Larger External Renderer: Mitsuba Water Mesh Response

Status: complete

## Goal

Use the actual water mesh as the renderer-native mask carrier by extracting
mask-hit water faces into a separate Mitsuba OBJ response layer.

## Result

S419 added a masked water mesh response tool and evaluated MMR1-MMR5, MMR8, and
MMR9.

- Public compare gallery:
  `https://junction-start-consistency-worldcat.trycloudflare.com/index.html`
- Summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_mesh_response_summary_s419.md`
- Sweep:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_mesh_response_sweep_summary_s419.md`

MMR4/MMR8 are the best native mesh-mask candidates with max target MAD
`23.96551183127572`. This improves over S416 WP4 `23.97967785493827` and S418
DP2 `23.980085519547327`, but remains worse than S417 `WP4_H18_D90`
`23.948739068930042`.

## Code Change

- Added `tools/add_mitsuba_water_mask_mesh_response.py`.

The tool projects water OBJ face centroids into the S410 highlight mask, writes
a compact selected-face OBJ, and inserts it into Mitsuba XML. Reversed face
winding is supported and required for the useful variants.

## Validation

- `python -m py_compile tools/add_mitsuba_water_mask_mesh_response.py`
- XML validation for MMR1-MMR5/MMR8/MMR9
- Mitsuba render for MMR1-MMR5/MMR8/MMR9
- Target-gap reports for MMR1-MMR5/MMR8/MMR9
- Sweep summary and compare gallery
- Published compare gallery with HTTP `200`

## Decision

Do not promote masked emissive water mesh. It is the best native geometry-mask
attempt so far, but it still adds too much lower water-surface response.

## Next

S420 should move to calibrated material/texture response or a post-free light
mask rather than more emitting geometry.
