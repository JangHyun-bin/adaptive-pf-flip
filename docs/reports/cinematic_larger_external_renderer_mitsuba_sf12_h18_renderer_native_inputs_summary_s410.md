# S410 SF12 H18 Renderer-Native Inputs Summary

Generated UTC: `2026-06-20T09:14:00Z`

Public AOV package URL:
`https://isbn-brussels-raise-luxury.trycloudflare.com/index.html`

## Goal

Move the accepted S409 split response closer to renderer-native controls by
packaging the two masks that define the current target-free response:

- `SF12` spray/foam channel-band dark attenuation
- `H18` nonsecondary source-highlight response

## Code Changes

- `tools/build_mitsuba_source_response_mask_source.py`
  - Added `--channel-mask-channels`.
  - Records response classifier settings in the summary/report.
- `tools/build_mitsuba_screen_evidence_aov_package.py`
  - Adds `Source Highlight` and `Target Highlight` AOV panels.
  - Records highlight thresholds in settings.
  - Adds highlight coverage to per-frame records.

## Mask Sources

| Source | Mask Kind | Max Coverage | Mean Coverage | Key Settings |
| --- | --- | ---: | ---: | --- |
| `SF12_H18_Highlight` | `highlight` | 0.014924768518518518 | 0.003991849922839506 | source luma `>=120`, alpha `<=3` |
| `SF12_ChannelBand` | `channel-band` | 0.0132445987654321 | 0.00808641975308642 | channels `spray,foam`, luma `0..95`, strength `0.12`, max delta `18` |

## AOV Package

- Frames: `8`
- AOVs per frame: `11`
- GIF bytes: `7228091`
- Public `index.html`: HTTP `200`
- Public `assets/screen_evidence_aov.gif`: HTTP `200`

The package now shows `Target`, `Actual`, `Layer Alpha`, `Source Luma`,
`Source Highlight`, `Target Highlight`, `DS6 Mask`, `Target Dark Diagnostic`,
`Water Mask`, `Contact Mask`, and `Overlay`.

## Decision

Keep `SF12_H18` as the accepted split-response migration target. S410 does not
claim a new renderer-native render yet; it turns the accepted post-composite
behavior into explicit, inspectable source masks and AOV evidence so the next
pass can replace the grade with renderer/export controls.

## Next

S411 should build a renderer-native candidate that consumes these two inputs.
Start with a conservative material/export response: use the `SF12_ChannelBand`
mask for secondary dark attenuation and the `SF12_H18_Highlight` mask as a
bounded highlight/emission or light-response control. Compare against S409
`SF12_H18`, SS1, and S401 CR21 before promoting it.
