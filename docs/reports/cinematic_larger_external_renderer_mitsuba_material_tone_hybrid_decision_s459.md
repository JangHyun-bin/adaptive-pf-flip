# S459 Mitsuba Material Tone Hybrid Decision

Generated UTC: `2026-06-20T15:01:00+00:00`

## Decision

Promote `mt4_balanced` as the current max-MAD safe material/tone hybrid candidate, and keep `mt1_soft_key` as the mean-MAD reference. The material/tone sweep improves over the S458 residual-response preset without raising max absolute gap above `177`.

Do not declare the renderer solved. `SS1_Native` still beats the S459 candidates on max gap MAD with a lower max absolute gap, and `S445_GL3_SurfaceGlint` still has the strongest max gap MAD while remaining visually risky due to max gap `221`.

## Evidence

- Sweep runner: `tools/run_mitsuba_material_tone_hybrid_sweep.py`
- Sweep report: `docs/reports/cinematic_larger_external_renderer_mitsuba_material_tone_hybrid_sweep_s459.md`
- Decision gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_material_tone_hybrid_sweep_decision_gallery_s459.md`
- Best max-MAD safe candidate: `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt4_balanced_target_gap/renderer_target_gap_summary.json`
- Best mean-MAD candidate: `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt1_soft_key_target_gap/renderer_target_gap_summary.json`
- Representative strips:
  - `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt4_balanced_target_gap/strips/frame_0002.png`
  - `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt4_balanced_target_gap/strips/frame_0007.png`

## Ranking

| Candidate | Mean Gap MAD | Max Gap MAD | Max Gap | Result |
| --- | ---: | ---: | ---: | --- |
| `S445_GL3_SurfaceGlint` | `19.204893502443415` | `23.9334458590535` | `221` | Best max MAD, but max-gap artifact risk. |
| `SS1_Native` | `19.146412117412552` | `23.951853137860084` | `170` | Best safe reference by max MAD. |
| `mt4_balanced` | `19.139489695859055` | `23.95333654835391` | `177` | Best S459 safe max-MAD hybrid. |
| `mt2_key_alpha` | `19.139306278935187` | `23.953566100823046` | `177` | Safe, weaker max MAD than mt4. |
| `mt1_soft_key` | `19.138588686342594` | `23.9536021090535` | `177` | Best S459 mean MAD. |
| `mt3_secondary_dim` | `19.139694733796297` | `23.95370306069959` | `177` | Safe but weaker. |
| `S458_residual_response_rr4_lf47_mid` | `19.139147215792182` | `23.95382973251029` | `177` | Previous residual-response preset. |
| `S452_sw2_compact_high` | `19.139631156764402` | `23.954243827160493` | `177` | Earlier sweep baseline. |

## Interpretation

The material/tone branch is now more promising than adding more local residual patches. It improves the residual-response preset on max gap MAD while preserving the same max absolute gap. The best max-MAD setting is not the strongest key-light setting; `mt4_balanced` works because it combines mild water-alpha reduction, mild spray/foam dimming, and a bounded highlight key-light.

The remaining gap to `SS1_Native` is still real. S460 should keep `mt4_balanced` as the base and run a narrower hybrid sweep around it, with max absolute gap capped at `177` and max gap MAD as the primary objective. The mean-MAD behavior of `mt1_soft_key` should be used as a secondary reference, not as the default promotion criterion.

## Next

S460 should search a narrow band around `mt4_balanced`: reduce the key-light strength slightly, test water-alpha drop `0.10..0.14`, and keep secondary dimming near `0.08..0.12` reflectance / `0.04..0.07` opacity.
