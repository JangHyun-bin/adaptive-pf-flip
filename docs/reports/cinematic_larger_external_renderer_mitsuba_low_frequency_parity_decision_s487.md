# S487 Mitsuba Low Frequency Parity Decision

Generated UTC: `2026-06-20T17:29:36.531317+00:00`

## Decision

Promote `S487_lf3_proxy_close` as the next visual direction, but not as a final renderer-native solution yet.

S487 validates the S486 diagnosis: low-frequency proxy/native parity closes much more of the gap than another scalar light/material sweep. The best candidate improves both mean gap and max-MAD over S481/S485, and it moves close to the S478 proxy gate while preserving the target-dark damping that S486 showed was necessary.

This is still a post-render composite preview. The next step is to port the same bounded low-frequency correction into a renderer-native texture/tone representation.

## Inputs

- S487 gap gallery: `build/shots/s487_mitsuba_low_frequency_parity_sweep/gap_gallery/gap_summary_gallery.json`
- S487 gallery: `build/shots/s487_mitsuba_low_frequency_parity_sweep/gap_gallery/gallery/index.html`
- S486 latest-native parity: `build/shots/s486_mitsuba_proxy_native_parity_lrs4/proxy_native_parity_summary.json`
- S485 LRS4 native baseline: `build/shots/s485_mitsuba_light_response_sweep/lrs4_sparse_spec/target_gap/renderer_target_gap_summary.json`
- S478 proxy gate: `build/shots/s478_mitsuba_response_control_proxy_sweep/p4_soft_wide_target_gap/renderer_target_gap_summary.json`

## Ranking

| Rank | Candidate | Mean MAD | Max MAD | Max Gap | Decision |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | S478 `p4_soft_wide` proxy | `19.079715470679012` | `23.9488554526749` | `176` | current visual gate |
| 2 | S487 `lf3_proxy_close` | `19.144350646219134` | `23.95285943930041` | `214` | promote as next visual direction |
| 3 | S487 `lf2_balanced` | `19.165056825488684` | `23.962381044238683` | `215` | fallback if lf3 looks too proxy-like |
| 4 | S487 `lf4_broad_safe` | `19.16965534979424` | `23.972206790123458` | `215` | safe but weaker |
| 5 | S487 `lf1_soft` | `19.19272850758745` | `23.98187757201646` | `216` | too weak |
| 6 | S485 `lrs4_sparse_spec` | `19.214833622685184` | `23.98198945473251` | `219` | previous native light baseline |
| 7 | S481 light-only | `19.215028131430042` | `23.98206790123457` | `219` | original native light baseline |

## Why LF3 Wins

- LF3 uses gain `0.9`, blur radius `6.0`, max delta `48.0`, and target-dark damping `0.35`.
- It improves mean MAD by about `0.07048` versus S485 LRS4.
- It improves max MAD by about `0.02913` versus S485 LRS4.
- It reduces max gap from `219` to `214`.
- It stays close to the proxy while still applying a low-frequency, bounded correction instead of copying the target directly.

## Guardrails

- Do not treat S487 as final photoreal output. It is a parity preview.
- Do not remove S484/S485 negative-result reports; they are the reason S487 is justified.
- Preserve target-dark damping in the native port because S486 showed dark target regions regress under naive proxy brightening.
- Keep S478 as the current gate until the native port beats or clearly matches it.

## Next

Implement S488 as a renderer-native low-frequency parity port: turn the S487 LF3 correction into a texture/tone asset consumed by Mitsuba XML or material parameters, then compare against S478, S487 LF3 preview, S485 LRS4, and S481 light-only.
