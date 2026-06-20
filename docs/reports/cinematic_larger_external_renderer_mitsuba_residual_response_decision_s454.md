# S454 Mitsuba Residual Response Decision

Generated UTC: `2026-06-20T14:36:00+00:00`

## Decision

Keep `tools/add_mitsuba_residual_response_patches.py` and promote `RR4` as the best S454 diagnostic candidate. It consumes the S453 residual request table, converts the selected request regions back onto projected water mesh vertices, and writes a normal `lsfs_mitsuba_xml_export` bundle with local disk emitters.

Do not promote RR1, RR2, or RR3 as renderer defaults. RR1 was too conservative, RR2 improved the worst-frame mean gap but introduced late-frame max-gap artifacts, and RR3 over-drove the focused frame. RR4 is the useful result: it targets only output frame `13`, improves both mean and max gap MAD versus S452 `sw2_compact_high`, and keeps max absolute gap unchanged.

## Evidence

- Tool: `tools/add_mitsuba_residual_response_patches.py`
- Residual analysis input: `build/shots/s453_mitsuba_sw2_target_residual/target_residual_analysis.json`
- Best candidate export: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_response_rr4_export_s454.md`
- Best candidate validation: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_response_rr4_validate_s454.md`
- Best candidate render: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_response_rr4_render_s454.md`
- Best candidate target gap: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_response_rr4_target_gap_s454.md`
- Visual strip: `build/shots/s454_mitsuba_residual_response_rr4_target_gap/strips/frame_0002.png`

## Ranking

| Candidate | Scope | Mean Gap MAD | Max Gap MAD | Max Gap | Result |
| --- | --- | ---: | ---: | ---: | --- |
| `S452_sw2_compact_high` | mask-cluster sweep baseline | `19.139631156764402` | `23.954243827160493` | `177` | Previous S452 leader. |
| `RR1` | all residual requests, conservative | `19.151900479038066` | `23.95425925925926` | `177` | Too weak, slightly worse than sw2. |
| `RR2` | all residual requests, stronger | `19.175778517232512` | `23.95382973251029` | `206` | Improves max MAD but adds late-frame artifact. |
| `RR3` | output 13 only, over-driven | `19.143790991512347` | `23.98752250514403` | `188` | Too strong for the focused frame. |
| `RR4` | output 13 only, mid-strength | `19.13957939493313` | `23.95382973251029` | `177` | Best S454 diagnostic candidate. |

## RR4 Settings

| Setting | Value |
| --- | --- |
| Output frame filter | `[13]` |
| Residual requests consumed | `2` |
| Patches inserted | `2` |
| Candidate vertices | `155` |
| Fallback patches | `0` |
| Radius scale | `0.28` |
| Radius range | `0.045..0.65` |
| Radiance scale | `2.2` |

## Interpretation

The S453/S454 loop works, but the improvement is still small. The remaining renderer gap is not solved by blindly adding more patch energy: RR2 and RR3 show that over-driving residual patches can create worse max-gap artifacts or overshoot the focused frame.

The next useful direction is not another manual RR sweep. S455 should make the residual patch placement adaptive: estimate per-request energy from the measured local before/after response, cap max-gap risk, and solve for a bounded radiance/radius pair per request instead of using a single global scale.

## Next

Build an S455 adaptive residual response fitter. It should run a tiny per-request calibration pass or score model, select only requests that reduce the active objective, and reject candidates that raise max absolute gap beyond the S452/S454 safe range.
