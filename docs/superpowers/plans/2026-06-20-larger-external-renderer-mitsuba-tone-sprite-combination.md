# S349 Mitsuba Tone Background Plus Screen Sprites

## Goal

Check whether the S347 sprite-mode secondary mask path helps after the S348
native tone/background correction.

## Scope

- Use S348 TB6 as the base export.
- Add S347 SC4-style screen sprites with
  `tools/add_mitsuba_secondary_screen_cards.py`.
- Render the resulting TS1 candidate.
- Compare TS1 against:
  - S341 C3 bridge through the S344 native replacement gate.
  - S335 secondary-pass contract gate.

## Command

```powershell
python tools\add_mitsuba_secondary_screen_cards.py `
  build\shots\s348_mitsuba_tone_bg_tb6\mitsuba_export.json `
  build\shots\s341_mitsuba_depth_aware_composite_c3\depth_aware_secondary_composite_summary.json `
  build\shots\s349_mitsuba_tone_bg_screen_sprites_ts1 `
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

## Outputs

- Export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_tone_bg_screen_sprites_ts1_export_s349.md`
- Render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_tone_bg_screen_sprites_ts1_render_s349.md`
- S335 contract gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_tone_bg_screen_sprites_ts1_candidate_gap_s349.md`
- C3 bridge gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_ts1_s349.md`

## Results

| Candidate | Mean target MAD | Max target MAD | Mean native-to-C3 MAD | Max native-to-C3 MAD |
| --- | ---: | ---: | ---: | ---: |
| S348 TB6 | `19.411650913065845` | `24.390221193415638` | `13.710569621270576` | `22.76778034979424` |
| S349 TS1 | `19.41354994534465` | `24.39063721707819` | `13.712686471193416` | `22.768213091563787` |

TS1 is slightly worse than TB6 on both mean and max target MAD.

## Decision

Do not keep the S347 sprite overlay on top of the tone-calibrated baseline.
TB6 remains the best native Mitsuba baseline.

## Next

Continue from TB6. The next attempt should tune native water/secondary material
or use a post-render bridge update from TB6, not simply add the current
screen-sprite mask path.
