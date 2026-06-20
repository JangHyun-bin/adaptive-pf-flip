# S465 Mitsuba Native Patch Setting Sweep Decision

Generated UTC: `2026-06-20T15:52:00+00:00`

## Decision

Keep `nr2_wide_bright` as the current best renderer-native residual patch preset, but do not promote it over `S463_sr4_image_space`.

S465 confirms that native patch tuning can move max gap MAD in the right direction, but the first radius/radiance sweep still cannot reproduce the image-space signed-response gain. Native residual patches should remain a bridge, not the final visual preset.

## Evidence

- Patch exporter: `tools/add_mitsuba_residual_response_patches.py`
- Request source: `build/shots/s464_mitsuba_signed_gap_residual_requests/target_residual_analysis.json`
- Decision gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_native_patch_setting_sweep_decision_gallery_s465.md`
- Best native target-gap summary: `build/shots/s465_mitsuba_native_patch_setting_sweep/nr2_wide_bright_target_gap/renderer_target_gap_summary.json`
- Best native render summary: `build/shots/s465_mitsuba_native_patch_setting_sweep/nr2_wide_bright_render/mitsuba_render.json`

## Ranking

| Candidate | Mean Gap MAD | Max Gap MAD | Max Gap | Result |
| --- | ---: | ---: | ---: | --- |
| `S463_sr4_image_space` | `19.10240579989712` | `23.950307355967077` | `176` | Still best visual calibration candidate. |
| `SS1_Native` | `19.146412117412552` | `23.951853137860084` | `170` | Still safest max-gap reference. |
| `nr2_wide_bright` | `19.143609744727367` | `23.953197016460905` | `177` | Best S465 renderer-native preset. |
| `nr3_big_soft` | `19.14228587962963` | `23.953218235596708` | `177` | Slightly better mean than nr2, weaker max MAD. |
| `nr1_wide_soft` | `19.14094240290638` | `23.953218878600822` | `177` | Lower mean, weaker max MAD. |
| `nr4_focus_worst` | `19.142737911522634` | `23.953241383744857` | `177` | Focused worst-frame attempt did not help enough. |
| `S464_renderer_native` | `19.139487686471192` | `23.953265817901233` | `177` | First native bridge baseline. |

## Sweep Settings

| Candidate | Patches | Requests | Radius Scale | Radiance Scale | Output Frames |
| --- | ---: | ---: | ---: | ---: | --- |
| `nr1_wide_soft` | `12` | `12` | `0.24` | `0.85` | all |
| `nr2_wide_bright` | `12` | `12` | `0.24` | `1.15` | all |
| `nr3_big_soft` | `12` | `12` | `0.32` | `0.95` | all |
| `nr4_focus_worst` | `7` | `7` | `0.28` | `1.10` | `13,40,47` |

## Interpretation

The native patch branch is responsive but inefficient. Increasing radiance at moderate radius (`nr2_wide_bright`) improves max MAD more than simply making patches larger (`nr3_big_soft`) or focusing only on the worst/late frames (`nr4_focus_worst`).

However, all native candidates keep max gap at `177`, and none approach the `S463_sr4_image_space` max MAD. The likely issue is not just energy. Disk emitters are affected by 3D placement, incidence, water material, and visibility, so the same screen-space request needs a more explicit projection/parity model.

## Next

S466 should build a native/image-space parity diagnostic: compare each signed request's screen bbox against the projected native patch footprint after rendering, then explain where the native patch misses the image-space response. Do not keep increasing radiance blindly until that footprint mismatch is measured.
