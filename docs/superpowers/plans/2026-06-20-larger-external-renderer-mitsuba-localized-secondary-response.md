# Larger External Renderer: Mitsuba Localized Secondary Response

Status: complete

## Goal

Replace S413 whole-frame material scaling with a renderer-side localized
secondary response: only secondary shapes whose projected positions hit a mask
should use modified material settings.

## Result

S414 added a localized secondary response patcher and tested LR1/LR3/LR4. The
mechanism works, but the candidates are rejected.

- Public compare gallery:
  `https://italia-mart-wallet-sides.trycloudflare.com/index.html`
- Summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_summary_s414.md`
- Sweep:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_localized_secondary_sweep_summary_s414.md`

Best localized candidate max target MAD is `23.989165380658438`, still worse
than SS1 `23.951853137860084` and far behind S409 `SF12_H18`
`23.687431841563786`.

## Code Change

- Added `tools/localize_mitsuba_secondary_material_response.py`.

The tool projects existing secondary XML shapes to screen space, samples a
source-response mask, and rewrites only matching shapes to localized BSDFs. It
also supports a source-luma gate; LR3 reduced the selected shape count from
`5200` to `980`.

## Validation

- `python -m py_compile tools\localize_mitsuba_secondary_material_response.py`
- XML validation for LR1, LR3, LR4
- Mitsuba render for LR1, LR3, LR4
- Target-gap reports for LR1, LR3, LR4
- Sweep summary across previous native candidates
- Published compare gallery with HTTP `200`

## Decision

Keep the localized BSDF patcher, reject localized secondary attenuation as the
next visual strategy. It changes the right part of the renderer path but the
wrong response class.

## Next

S415 should apply localization to source-highlight/light or water/volume
texture response instead of secondary attenuation.
