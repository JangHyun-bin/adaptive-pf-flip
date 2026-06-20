# S347 Mitsuba Secondary Screen Sprites

## Goal

Make the S346 renderer-side screen-card path visibly affect the native Mitsuba
output without relying on a single full-frame rectangle whose material response
is too weak or too opaque.

## Scope

- Extend `tools/add_mitsuba_secondary_screen_cards.py` with `--card-mode
  sprites`.
- Sample bright pixels from each secondary mask.
- Project those samples onto the same camera-facing plane used by S346.
- Emit small Mitsuba `disk` shapes with area-emitter radiance instead of one
  textured rectangle.
- Keep the original rectangle mode for compatibility.
- Render two sprite candidates:
  - SC3: moderate sprite count/radius/radiance.
  - SC4: stronger sprite stress test.
- Compare both against the S335 contract gate and S344 C3 bridge gate.

## Commands

SC3:

```powershell
python tools\add_mitsuba_secondary_screen_cards.py `
  build\shots\s345_mitsuba_secondary_mist_billboard_mb2\mitsuba_export.json `
  build\shots\s341_mitsuba_depth_aware_composite_c3\depth_aware_secondary_composite_summary.json `
  build\shots\s347_mitsuba_secondary_screen_sprites_sc3 `
  --frames 8 `
  --card-mode sprites `
  --card-distance 18 `
  --mask-gain 8.0 `
  --mask-blur-radius 2.0 `
  --sprite-limit 512 `
  --sprite-threshold 24 `
  --sprite-radius-pixels 7.0 `
  --sprite-radiance 10.0,13.0,16.0
```

SC4:

```powershell
python tools\add_mitsuba_secondary_screen_cards.py `
  build\shots\s345_mitsuba_secondary_mist_billboard_mb2\mitsuba_export.json `
  build\shots\s341_mitsuba_depth_aware_composite_c3\depth_aware_secondary_composite_summary.json `
  build\shots\s347_mitsuba_secondary_screen_sprites_sc4 `
  --frames 8 `
  --card-mode sprites `
  --card-distance 18 `
  --mask-gain 8.0 `
  --mask-blur-radius 2.0 `
  --sprite-limit 1024 `
  --sprite-threshold 18 `
  --sprite-stride 1 `
  --sprite-radius-pixels 11.0 `
  --sprite-radiance 42.0,52.0,64.0 `
  --sprite-alpha-scale 1.15 `
  --sprite-alpha-power 0.9
```

Both candidates were rendered with `tools/render_mitsuba_xml_export.py` at
`--frames 8 --spp 4 --write-png`.

## Outputs

- Updated tool:
  `tools/add_mitsuba_secondary_screen_cards.py`
- SC3 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_sprites_sc3_export_s347.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_sprites_sc3_render_s347.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_sprites_sc3_candidate_gap_s347.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_sc3_s347.md`
- SC4 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_sprites_sc4_export_s347.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_sprites_sc4_render_s347.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_sprites_sc4_candidate_gap_s347.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_sc4_s347.md`

## Results

| Candidate | Mean target MAD | Max target MAD | Mean native-to-C3 MAD | Max native-to-C3 MAD | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| S345 MB2 | `37.13389178240741` | `66.33950488683128` | `40.225236062885806` | `61.84939814814815` | `native_candidate_needs_work` |
| S347 SC3 | `37.13424913194444` | `66.33931455761316` | `40.225885497042185` | `61.84857381687243` | `native_candidate_needs_work` |
| S347 SC4 | `37.13381309477881` | `66.33893840020576` | `40.2254558899177` | `61.848001543209875` | `native_candidate_needs_work` |
| S341 C3 bridge | `11.423722591949588` | `14.571005658436214` | n/a | n/a | validated bridge |

SC4 emits `8192` screen sprites across `8` frames and is the current best
native Mitsuba candidate by max target MAD. The improvement over MB2 is real
but tiny: max target MAD improves from `66.33950488683128` to
`66.33893840020576`.

## Decision

Sprite mode is useful infrastructure: it creates renderer-native mask-guided
secondary marks without a full-screen card. It is not enough to close the visual
gap. The remaining error is dominated by native tone/background and broader
render target mismatch rather than only secondary mask geometry.

## Next

Start native tone/background calibration. Use S344 as the gate, but tune the
base Mitsuba render toward the C3/target tone before spending more iterations
on secondary sprite placement.
