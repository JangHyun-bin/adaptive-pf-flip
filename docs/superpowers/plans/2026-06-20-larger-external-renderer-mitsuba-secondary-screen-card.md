# S346 Mitsuba Secondary Screen Card

## Goal

Move beyond proxy-only sphere/mist/billboard tuning by inserting renderer-side
bitmap opacity cards guided by the validated secondary mask.

## Scope

- Add `tools/add_mitsuba_secondary_screen_cards.py`.
- Take an existing `lsfs_mitsuba_xml_export` as a base.
- Take the S341 C3 depth-aware composite summary as the secondary-mask source.
- Build per-frame grayscale opacity textures from `secondary_layer_repo_path`.
- Insert a camera-facing Mitsuba rectangle with a bitmap `mask` BSDF into each
  base XML scene.
- Preserve output schema as `lsfs_mitsuba_xml_export` so the existing Mitsuba
  render tool can consume it.
- Render and compare two candidates:
  - SC1: weak mask gain.
  - SC2: stronger mask gain.

## Commands

SC1:

```powershell
python tools\add_mitsuba_secondary_screen_cards.py `
  build\shots\s345_mitsuba_secondary_mist_billboard_mb2\mitsuba_export.json `
  build\shots\s341_mitsuba_depth_aware_composite_c3\depth_aware_secondary_composite_summary.json `
  build\shots\s346_mitsuba_secondary_screen_card_sc1 `
  --frames 8 `
  --card-distance 18 `
  --card-scale 1.0 `
  --mask-gain 0.6 `
  --mask-blur-radius 1.5 `
  --reflectance 0.70,0.84,0.96
```

SC2:

```powershell
python tools\add_mitsuba_secondary_screen_cards.py `
  build\shots\s345_mitsuba_secondary_mist_billboard_mb2\mitsuba_export.json `
  build\shots\s341_mitsuba_depth_aware_composite_c3\depth_aware_secondary_composite_summary.json `
  build\shots\s346_mitsuba_secondary_screen_card_sc2 `
  --frames 8 `
  --card-distance 18 `
  --card-scale 1.0 `
  --mask-gain 8.0 `
  --mask-blur-radius 2.0 `
  --reflectance 0.78,0.90,1.0
```

Both exports were rendered with `tools/render_mitsuba_xml_export.py` at
`--frames 8 --spp 4 --write-png`, then compared with both the S335 contract
gap and the S344 C3 bridge replacement gate.

## Outputs

- Tool:
  `tools/add_mitsuba_secondary_screen_cards.py`
- SC1 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_card_sc1_export_s346.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_card_sc1_render_s346.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_card_sc1_candidate_gap_s346.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_sc1_s346.md`
- SC2 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_card_sc2_export_s346.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_card_sc2_render_s346.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_screen_card_sc2_candidate_gap_s346.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_sc2_s346.md`

## Results

| Candidate | Mean target MAD | Max target MAD | Mean native-to-C3 MAD | Max native-to-C3 MAD | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| S345 MB2 | `37.13389178240741` | `66.33950488683128` | `40.225236062885806` | `61.84939814814815` | `native_candidate_needs_work` |
| S346 SC1 | `37.133900704089505` | `66.33952031893004` | `40.22522456918724` | `61.84936728395062` | `native_candidate_needs_work` |
| S346 SC2 | `37.13389475630144` | `66.33952031893004` | `40.22522087191358` | `61.84936728395062` | `native_candidate_needs_work` |
| S341 C3 bridge | `11.423722591949588` | `14.571005658436214` | n/a | n/a | validated bridge |

SC2 successfully generated `8` secondary screen cards and `73.76 KB` of mask
textures with `0` missing references. The metric result is effectively tied
with MB2, which means the current card depth/material setup does not yet move
the native render toward C3.

## Decision

S346 establishes the renderer-side bitmap mask-card pipeline, but the first
placement/material settings do not improve the native replacement gap. Keep the
tool; do not treat SC1/SC2 as visual improvements.

## Next

Tune the screen-card model itself: card depth, facing direction, material or
emissive response, alpha orientation, and possibly depth-sorted multi-card
placement. Continue using the S344 gate before accepting any native replacement.
