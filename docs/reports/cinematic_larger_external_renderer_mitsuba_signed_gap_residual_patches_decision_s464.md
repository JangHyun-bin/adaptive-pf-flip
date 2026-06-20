# S464 Mitsuba Signed Gap Residual Patches Decision

Generated UTC: `2026-06-20T15:40:00+00:00`

## Decision

Keep `S464_renderer_native` as a working renderer-native bridge, but do not promote it over `S463_sr4_image_space`.

The S464 path successfully converts signed highlight/brighten requests into Mitsuba disk emitters, validates the XML, renders eight frames, and produces a ready target-gap comparison. It improves slightly over the S460 material/tone base on max gap MAD, but it does not preserve the larger S463 image-space improvement.

## Evidence

- Request converter: `tools/convert_mitsuba_signed_gap_to_residual_requests.py`
- Patch exporter: `tools/add_mitsuba_residual_response_patches.py`
- Request report: `docs/reports/cinematic_larger_external_renderer_mitsuba_signed_gap_residual_requests_s464.md`
- Export report: `docs/reports/cinematic_larger_external_renderer_mitsuba_signed_gap_residual_patches_export_s464.md`
- Validation report: `docs/reports/cinematic_larger_external_renderer_mitsuba_signed_gap_residual_patches_validate_s464.md`
- Render report: `docs/reports/cinematic_larger_external_renderer_mitsuba_signed_gap_residual_patches_render_s464.md`
- Target-gap report: `docs/reports/cinematic_larger_external_renderer_mitsuba_signed_gap_residual_patches_target_gap_s464.md`
- Decision gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_signed_gap_residual_patches_decision_gallery_s464.md`

## Comparison

| Candidate | Mean Gap MAD | Max Gap MAD | Max Gap | Result |
| --- | ---: | ---: | ---: | --- |
| `S463_sr4_image_space` | `19.10240579989712` | `23.950307355967077` | `176` | Current best visual calibration candidate. |
| `SS1_Native` | `19.146412117412552` | `23.951853137860084` | `170` | Still safest by max gap. |
| `S464_renderer_native` | `19.139487686471192` | `23.953265817901233` | `177` | Renderer-native bridge works, but not promotion-ready. |
| `S462_image_space` | `19.10439911265432` | `23.953335905349793` | `176` | First bounded image-space signed response. |
| `S460_mt8` | `19.139490097736626` | `23.953335905349793` | `177` | Material/tone base. |

## Checks

| Gate | Result |
| --- | --- |
| Residual requests converted | `12` |
| Patches inserted | `12` |
| Fallback patches | `0` |
| XML validation | `ready`, `8` parsed, `0` failures |
| Render | `ready`, `8` frames, `0` failures |
| Target-gap compare | `ready`, `8` frames, `0` missing references |

## Interpretation

S464 proves the renderer-native route is viable: signed requests can be converted into water-surface disk emitters without XML failures or render failures. The first native mapping is too weak or too spatially different from the image-space response to reproduce the S463 gain.

The likely mismatch is geometric: image-space response directly modifies the highlighted pixels, while disk emitters are placed on projected water mesh vertices and then filtered through scene lighting, material, opacity, and camera projection. The next native pass should tune radius, radiance, and placement, not go back to global material/tone changes.

## Next

S465 should sweep renderer-native residual patch settings around S464: larger radius scale, higher radiance scale, and tighter per-frame request limits. Promotion gate remains strict: max absolute gap must be at or below `176`, and max gap MAD should move toward `23.950307355967077`.
