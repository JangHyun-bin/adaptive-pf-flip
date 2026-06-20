# S416 Mitsuba Water Patch Summary

Generated UTC: `2026-06-20T10:10:00Z`

Public compare URL:
`https://full-fuji-tone-vii.trycloudflare.com/index.html`

## Goal

Turn the S415 point-emitter water-highlight idea into a broader water-surface
patch response without adding a new tool. This reuses
`tools/add_mitsuba_water_mask_highlights.py` with larger emitter radii, lower
emitter counts, and stricter spacing so the result is less speckled.

## Code Change

No code change.

S416 only generated and evaluated new Mitsuba export/render candidates from the
existing S415 water-highlight tool.

## Candidates

| Candidate | Emitters | Source Luma Gate | Radius | Radiance | Max Gap MAD |
| --- | ---: | --- | ---: | --- | ---: |
| `WP1` | 101 | `120..255` | 0.14 | `0.80,1.00,1.25` | 23.985679655349795 |
| `WP2` | 53 | `145..255` | 0.18 | `1.20,1.45,1.75` | 23.9812795781893 |
| `WP3` | 43 | `145..255` | 0.26 | `1.55,1.85,2.20` | 23.983085133744854 |
| `WP4` | 60 | `145..255` | 0.22 | `1.35,1.60,1.95` | 23.97967785493827 |
| `WP5` | 61 | `145..255` | 0.25 | `1.45,1.72,2.05` | 23.981273148148148 |

## Result

WP4 is the best native water-patch candidate in this sweep, but it should not
be promoted over SS1 yet.

| Rank | Candidate | Mean Gap MAD | Max Gap MAD | Max Gap |
| ---: | --- | ---: | ---: | ---: |
| 1 | `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| 2 | `S409_SF12_H18` | 18.756908677340533 | 23.687431841563786 | 170 |
| 3 | `SF12_SprayFoam` | 19.120776588220163 | 23.755951646090534 | 170 |
| 4 | `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |
| 5 | `S416_WP4` | 19.31142160172325 | 23.97967785493827 | 255 |
| 6 | `S416_WP5` | 19.361695441100824 | 23.981273148148148 | 255 |
| 7 | `S416_WP2` | 19.254283854166665 | 23.9812795781893 | 253 |
| 8 | `S416_WP3` | 19.341100742669752 | 23.983085133744854 | 255 |
| 9 | `S416_WP1` | 19.24947064686214 | 23.985679655349795 | 253 |
| 10 | `S415_WH4` | 19.225447048611112 | 23.98679526748971 | 234 |

Visual review shows WP4 is broader than WH4, so the direction is useful. It
still does not reproduce the connected highlight/dark-water response in
S409/S401, and it retains visible emitter speckling in the later frames.

## Artifacts

- WP1 export/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp1_export_s416.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp1_render_s416.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp1_target_gap_s416.md`
- WP2 export/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp2_export_s416.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp2_render_s416.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp2_target_gap_s416.md`
- WP3 export/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp3_export_s416.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp3_render_s416.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp3_target_gap_s416.md`
- WP4 export/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp4_export_s416.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp4_render_s416.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp4_target_gap_s416.md`
- WP5 export/render/target:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp5_export_s416.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp5_render_s416.md`,
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_wp5_target_gap_s416.md`
- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_sweep_summary_s416.md`
- Compare report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_compare_s416.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_water_patch_compare_publish_s416.md`

## Validation

- WP1/WP2/WP3/WP4/WP5 XML validation: each `ready`, `8` parsed, `0` failures, `0` warnings
- WP1/WP2/WP3/WP4/WP5 Mitsuba render: each `ready`, `8` frames, `0` failures
- WP1/WP2/WP3/WP4/WP5 target gap: each `ready`
- Sweep summary: `ready`
- Compare gallery: `ready`
- Public compare `index.html`: HTTP `200`
- Public compare `assets/comparison.gif`: HTTP `200`

## Decision

Keep WP4 as the best native water-patch probe so far, but do not promote it as
the final renderer-native replacement. The patch response is better than WH4,
but it remains worse than SS1 and far behind the accepted S409/S401
screen-evidence response.

## Next

S417 should either combine WP4 with the accepted SF12 dark attenuation, or move
the same water/highlight evidence into a true renderer-side texture or volume
mask instead of discrete emitters.
