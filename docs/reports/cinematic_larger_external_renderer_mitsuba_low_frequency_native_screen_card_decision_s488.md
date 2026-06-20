# S488 Mitsuba Low Frequency Native Screen Card Decision

Generated UTC: `2026-06-20T17:36:40.955476+00:00`

## Decision

Reject the S488 screen-card port as the native implementation path for S487 low-frequency parity.

The existing Mitsuba screen-card mechanism can consume the S487 LF3 correction layer as a bitmap opacity texture, validates successfully, and renders through Mitsuba XML. However, it does not recover the S487 LF3 preview improvement. All S488 candidates remain near the S485 light baseline, and the best S488 candidate is still worse than S485 on mean gap.

This confirms that the useful S487 correction is not just "put a translucent card in front of the camera." The next native port should move the correction into true material/texture/tone parameters rather than another camera-facing screen bridge.

## Inputs

- S488 gap gallery: `build/shots/s488_mitsuba_low_frequency_native_screen_card_sweep/gap_gallery/gap_summary_gallery.json`
- S488 gallery: `build/shots/s488_mitsuba_low_frequency_native_screen_card_sweep/gap_gallery/gallery/index.html`
- S487 LF3 preview: `build/shots/s487_mitsuba_low_frequency_parity_sweep/lf3_proxy_close_target_gap/renderer_target_gap_summary.json`
- S485 LRS4 native baseline: `build/shots/s485_mitsuba_light_response_sweep/lrs4_sparse_spec/target_gap/renderer_target_gap_summary.json`

## Ranking

| Rank | Candidate | Mean MAD | Max MAD | Max Gap | Decision |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | S478 `p4_soft_wide` proxy | `19.079715470679012` | `23.9488554526749` | `176` | current visual gate |
| 2 | S487 `lf3_proxy_close` preview | `19.144350646219134` | `23.95285943930041` | `214` | keep as direction |
| 3 | S485 `lrs4_sparse_spec` | `19.214833622685184` | `23.98198945473251` | `219` | current native baseline |
| 4 | S488 `sc4_sprite_mix` | `19.216166489840536` | `23.982440200617283` | `219` | reject |
| 5 | S488 `sc1_soft_card` | `19.214948479295266` | `23.98278806584362` | `219` | reject |
| 6 | S488 `sc3_broad_card` | `19.21498979230967` | `23.982888374485597` | `219` | reject |
| 7 | S488 `sc2_bright_card` | `19.215062371399178` | `23.983278677983538` | `219` | reject |

## Mechanism Checks

- `sc1_soft_card`: rectangle card, mask gain `0.35`, blur `4.0`, `0` sprites.
- `sc2_bright_card`: rectangle card, mask gain `0.55`, blur `2.0`, `0` sprites.
- `sc3_broad_card`: rectangle card, mask gain `0.45`, blur `8.0`, `0` sprites.
- `sc4_sprite_mix`: rectangle plus sprites, mask gain `0.65`, blur `2.0`, `768` sprites.
- All four candidates exported, validated, rendered, and produced target-gap galleries.
- The first `sc2` attempt failed because diffuse reflectance used a value above `1.0`; it was corrected and rerun with reflectance clamped to the Mitsuba-valid range.

## Interpretation

S487 worked because it applied bounded low-frequency color correction directly to the rendered image. S488 reduces that correction into an opacity-only screen card and fixed reflectance/sprite response, which loses too much color and sign information. It also reintroduces the old screen-card limitation documented by earlier S397/S425 paths.

The useful part of S487 should stay alive, but the representation must change.

## Next

Implement S489 as a true parity texture/tone asset rather than a screen card. The next candidate should preserve per-frame low-frequency RGB correction and dark-region damping, then consume it through a render-data shader/material path or a renderer-native post-tonemap texture stage before comparing against S478, S487 LF3 preview, and S485 LRS4.
