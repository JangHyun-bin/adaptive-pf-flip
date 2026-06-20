# S462 Mitsuba Signed Highlight Response Decision

Generated UTC: `2026-06-20T15:26:00+00:00`

## Decision

Promote `S462_signed_highlight` as the current best visual calibration candidate from the signed-gap branch.

It reduces mean gap MAD from `19.139490097736626` to `19.10439911265432`, keeps max gap MAD tied with `S460_mt8`, and lowers max absolute gap from `177` to `176`. This is a real improvement over scalar material/tone tuning.

Do not treat S462 as renderer-native final output yet. It is an image-space bounded response proof. The next stage should either tune response strength in this same safe framework or convert the response requests into renderer-native local light/material controls.

## Evidence

- Response tool: `tools/apply_mitsuba_signed_gap_response.py`
- Signed analyzer: `tools/analyze_mitsuba_signed_target_gap.py`
- Response report: `docs/reports/cinematic_larger_external_renderer_mitsuba_signed_highlight_response_s462.md`
- Target-gap report: `docs/reports/cinematic_larger_external_renderer_mitsuba_signed_highlight_response_target_gap_s462.md`
- Response summary: `build/shots/s462_mitsuba_signed_highlight_response/signed_gap_response_summary.json`
- Target-gap summary: `build/shots/s462_mitsuba_signed_highlight_response_target_gap/renderer_target_gap_summary.json`
- Response gallery: `build/shots/s462_mitsuba_signed_highlight_response/gallery/index.html`
- Target-gap gallery: `build/shots/s462_mitsuba_signed_highlight_response_target_gap/gallery/index.html`

## Comparison

| Candidate | Mean Gap MAD | Max Gap MAD | Max Gap | Result |
| --- | ---: | ---: | ---: | --- |
| `S462_signed_highlight` | `19.10439911265432` | `23.953335905349793` | `176` | Best current mean and lower max gap within the mt8 branch. |
| `S460_mt8` | `19.139490097736626` | `23.953335905349793` | `177` | Previous signed-gap base. |
| `S459_mt4` | `19.139489695859055` | `23.95333654835391` | `177` | Previous material/tone max-MAD-safe base. |
| `SS1_Native` | `19.146412117412552` | `23.951853137860084` | `170` | Still better on max gap MAD and max gap, but worse than S462 on mean. |

## Response Settings

| Setting | Value |
| --- | ---: |
| Regions | `highlight` |
| Directions | `brighten` |
| Max requests | `8` |
| Strength scale | `0.35` |
| Max strength | `0.35` |
| Max channel delta | `24` |
| Feather power | `1.5` |
| Max changed coverage | `0.019110725308641975` |
| Mean applied abs delta | `7.54376749490272` |

## Interpretation

S461 identified the remaining miss as local and signed: the highlight mask needed brightening, while channel-band should not be globally brightened. S462 validates that diagnosis. Applying only bounded highlight/brighten requests improves the visual gap without raising max gap.

The remaining max gap MAD is unchanged because the worst MAD frame is not fully resolved by the first eight highlight requests. The mean improvement is still large enough to justify continuing this branch.

## Next

S463 should run a narrow response-strength sweep around S462. Keep `highlight`/`brighten` only, keep max absolute gap at or below `176`, and try to reduce max gap MAD without giving back the mean MAD improvement.
