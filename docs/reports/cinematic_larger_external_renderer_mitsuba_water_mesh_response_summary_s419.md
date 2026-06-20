# S419 Mitsuba Water Mesh Response Summary

Generated UTC: `2026-06-20T10:46:00Z`

Public compare URL:
`https://junction-start-consistency-worldcat.trycloudflare.com/index.html`

## Goal

Move beyond discrete sphere/disk emitters by using the actual water mesh as the
mask carrier. The pass cuts the source-highlight mask region out of each water
OBJ and inserts that selected water-surface mesh back into the Mitsuba scene as
a renderer-native material/light response.

## Code Change

Added:

- `tools/add_mitsuba_water_mask_mesh_response.py`

The tool projects water-mesh face centroids into the S410 highlight mask,
selects matching faces, writes a compact per-frame OBJ for those selected
faces, and inserts that OBJ into the Mitsuba XML. It supports reversed face
winding so the emitted side faces the camera.

## Candidates

| Candidate | Faces | Setup | Max Gap MAD |
| --- | ---: | --- | ---: |
| `MMR1` | 1242 | original winding, soft emissive mesh | 24.858103137860084 |
| `MMR2` | 1242 | original winding, stronger emissive mesh | 25.083195730452676 |
| `MMR3` | 2247 | original winding, broader mask | 28.17601980452675 |
| `MMR4` | 1242 | reversed winding, soft emissive mesh | 23.96551183127572 |
| `MMR5` | 1242 | reversed winding, emissive plus diffuse reflectance | 23.965932998971194 |
| `MMR8` | 1212 | reversed winding, top-limited mesh | 23.96551183127572 |
| `MMR9` | 736 | reversed winding, tighter top-limited mesh | 23.96646154835391 |

## Result

The face direction fix is important, but masked emissive water mesh still should
not be promoted.

| Rank | Candidate | Mean Gap MAD | Max Gap MAD | Max Gap |
| ---: | --- | ---: | ---: | ---: |
| 1 | `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| 2 | `S409_SF12_H18` | 18.756908677340533 | 23.687431841563786 | 170 |
| 3 | `SF12_SprayFoam` | 19.120776588220163 | 23.755951646090534 | 170 |
| 4 | `S417_WP4_H18_D90` | 19.182991817772635 | 23.948739068930042 | 255 |
| 5 | `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |
| 6 | `S419_MMR8` | 19.766804028420783 | 23.96551183127572 | 254 |
| 7 | `S419_MMR4` | 19.785509178883743 | 23.96551183127572 | 254 |
| 8 | `S419_MMR5` | 19.465720968364195 | 23.965932998971194 | 233 |
| 9 | `S419_MMR9` | 19.33238522376543 | 23.96646154835391 | 249 |
| 10 | `S416_WP4` | 19.31142160172325 | 23.97967785493827 | 255 |
| 11 | `S418_DP2` | 19.237632458847738 | 23.980085519547327 | 232 |

Original winding candidates render black backside patches and are rejected.
Reversed winding fixes that problem and beats WP4/DP2, but the selected mesh
still lights too much lower water-surface structure and does not beat S417
`WP4_H18_D90`.

## Artifacts

- MMR1-MMR5, MMR8, MMR9 export/validation/render/target reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_mesh_response_mmr*_s419.md`
- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_mesh_response_sweep_summary_s419.md`
- Compare report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_mesh_response_compare_s419.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_mesh_response_compare_publish_s419.md`

## Validation

- `python -m py_compile tools/add_mitsuba_water_mask_mesh_response.py`
- MMR1-MMR5/MMR8/MMR9 XML validation: each `ready`, `8` parsed, `0` failures, `0` warnings
- MMR1-MMR5/MMR8/MMR9 Mitsuba render: each `ready`, `8` frames, `0` failures
- MMR1-MMR5/MMR8/MMR9 target gap: each `ready`
- Sweep summary: `ready`
- Compare gallery: `ready`
- Public compare `index.html`: HTTP `200`
- Public compare `assets/comparison.gif`: HTTP `200`

## Decision

Keep reversed masked water mesh response as useful native evidence, but do not
promote it. S417 `WP4_H18_D90` remains the better current visual candidate.

## Next

S420 should stop treating the highlight evidence as extra emitting geometry.
The next attempt should encode the mask into calibrated material/texture
response, or build a post-free light mask that does not add lower water-surface
noise.
