# S434 Mitsuba Residual Native Decision Detail

Generated UTC: `2026-06-20T12:31:30Z`

## Inputs

- Native/residual ranking: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_native_decision_s434.md`
- Source-response channel analysis: `docs/reports/cinematic_larger_external_renderer_mitsuba_source_response_intent_channel_analysis_s423.md`
- Surface-contact foam sweep: `docs/reports/cinematic_larger_external_renderer_mitsuba_surface_contact_foam_sweep_summary_s433.md`
- Residual mask baseline: `docs/reports/2026-06-20-s386-mitsuba-secondary-channel-residual-masks-sv1.md`
- Residual screen-card result: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_local_screen_card_summary_s397.md`
- Residual sidecar augment result: `docs/reports/cinematic_larger_external_renderer_mitsuba_residual_augmented_secondary_material_ra1_summary_s399.md`

## Current Evidence

| Candidate | Mean target MAD | Max target MAD | Decision |
| --- | ---: | ---: | --- |
| S401 CR21 profile | 18.657218 | 23.552905 | Keep as score leader and upper-bound reference |
| S409 SF12 H18 | 18.756909 | 23.687432 | Keep as secondary/channel-band reference |
| SS1 native | 19.146412 | 23.951853 | Keep as renderer-native baseline |
| S433 surface-contact foam SCF3 | 19.226232 | 23.988884 | Valid native geometry, rejected as improvement |
| S397 residual screen card | 19.222715 | 23.988895 | Valid residual mask source, rejected as screen-card replacement |
| S399 residual augment RA1 | 19.223066 | 23.989043 | Valid sidecar plumbing, rejected as quantity/radius replacement |

## Decision

The next native renderer work should not add more low-level secondary particles, screen cards, water patches, or small BSDF tweaks. Those paths now repeatedly converge near `23.9889` max target MAD and do not beat `SS1_Native`.

S423 shows one useful split:

- `S409_SF12_H18_channel_band` is strongly explained by projected spray/foam: best candidate `spray` F1 `0.564300`, and `spray_or_foam` reaches recall `1.000000`.
- `S401_CR21_highlight` is not explained by secondary channels: best secondary overlap F1 is only `0.008123`.
- `S401_CR21_dark_primary` and `S401_CR21_channel_band` are weakly explained by current projected secondary channels, so CR21 remains an upper-bound post-response reference.

## Next Implementation

S435 should implement a bounded native `secondary channel-band attenuation` pass, not another additive patch:

- Input: existing secondary 3D sidecar proxies and the S409 channel-band intent.
- Mechanism: attenuate or darken selected spray/foam material response in a narrow source-luma/channel-density band instead of adding extra geometry.
- Gate: compare against `SS1_Native`, `S409_SF12_H18`, and S433 SCF3.
- Reject condition: if it lands near the `23.9889` cluster again, stop native secondary-response patching and move to a renderer-side target/reference decomposition or a true high-fidelity surface/volume representation.
