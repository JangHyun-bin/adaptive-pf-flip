# S460 Mitsuba Material Tone Refine Decision

Generated UTC: `2026-06-20T15:18:00+00:00`

## Decision

Promote `mt8_secondary_light` as the current S460 max-MAD-safe material/tone refinement, but treat the improvement over `S459_mt4_balanced` as a plateau signal rather than a meaningful visual breakthrough.

Keep `S459_mt1_soft_key` as the mean-MAD reference. It remains the lowest-mean material/tone candidate, but its max gap MAD is weaker than `mt8_secondary_light`.

Do not keep spending the next stages on scalar material/tone sweeps alone. The S460 deltas are too small. S461 should move to target-residual-driven, frame-aware response or an SS1-style safe max-gap improvement path.

## Evidence

- Sweep runner: `tools/run_mitsuba_material_tone_hybrid_sweep.py`
- Sweep report: `docs/reports/cinematic_larger_external_renderer_mitsuba_material_tone_refine_sweep_s460.md`
- Decision gallery: `docs/reports/cinematic_larger_external_renderer_mitsuba_material_tone_refine_sweep_decision_gallery_s460.md`
- Selected S460 candidate: `build/shots/s460_mitsuba_material_tone_refine_sweep/mt8_secondary_light_target_gap/renderer_target_gap_summary.json`
- S459 base candidate: `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt4_balanced_target_gap/renderer_target_gap_summary.json`
- Mean-MAD reference: `build/shots/s459_mitsuba_material_tone_hybrid_sweep/mt1_soft_key_target_gap/renderer_target_gap_summary.json`
- Representative S460 strip: `build/shots/s460_mitsuba_material_tone_refine_sweep/mt8_secondary_light_target_gap/strips/frame_0002.png`

## Ranking

| Candidate | Mean Gap MAD | Max Gap MAD | Max Gap | Result |
| --- | ---: | ---: | ---: | --- |
| `S445_GL3_SurfaceGlint` | `19.204893502443415` | `23.9334458590535` | `221` | Best max MAD, but still unsafe by max-gap artifact risk. |
| `SS1_Native` | `19.146412117412552` | `23.951853137860084` | `170` | Best safe reference by max MAD and max gap. |
| `mt8_secondary_light` | `19.139490097736626` | `23.953335905349793` | `177` | Best S460 max-MAD-safe material/tone refinement. |
| `S459_mt4_balanced` | `19.139489695859055` | `23.95333654835391` | `177` | Previous material/tone base; effectively tied with mt8. |
| `mt6_trim_key` | `19.139489936985598` | `23.95333654835391` | `177` | Tied with mt4 on max MAD, no reason to promote. |
| `mt7_alpha_high_key_low` | `19.139264805169752` | `23.953463863168725` | `177` | Slightly lower mean than mt8, weaker max MAD. |
| `mt5_trim_alpha` | `19.139307725694444` | `23.95356674382716` | `177` | Safe, weaker max MAD. |
| `S459_mt1_soft_key` | `19.138588686342594` | `23.9536021090535` | `177` | Best material/tone mean MAD, weaker max MAD. |

## Delta From S459 Base

| Metric | `S459_mt4_balanced` | `mt8_secondary_light` | Delta |
| --- | ---: | ---: | ---: |
| Mean Gap MAD | `19.139489695859055` | `19.139490097736626` | `+0.000000401877571` |
| Max Gap MAD | `23.95333654835391` | `23.953335905349793` | `-0.000000643004117` |
| Max Gap | `177` | `177` | `0` |

## Interpretation

`mt8_secondary_light` is the best S460 choice if the primary objective is max gap MAD while keeping max absolute gap at `177`. The gain is microscopic, so the right conclusion is not that material/tone tuning solved the look. The right conclusion is that this local scalar tuning branch is saturated.

The strongest external-reference candidate remains `S445_GL3_SurfaceGlint`, but its max gap `221` is too high for a safe promotion. `SS1_Native` remains the better safe reference with max gap `170`, so the next improvement should try to capture the safe SS1-like behavior rather than simply increasing highlights.

## Next

S461 should start a frame-aware residual response pass from `mt8_secondary_light`: measure signed target gaps on the selected render frames, split the response by frame and source region, and attempt to reduce the late-frame highlight miss without raising max gap above `177`.
