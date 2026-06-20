# Larger External Renderer: Mitsuba Material Response MR2

Status: complete

## Goal

Use the S412 material-response patcher for a narrower no-key-light experiment:
secondary spray/foam attenuation only.

## Result

MR2 is rejected. It removes MR1's broad key-light lift and is marginally better
than MR1, but it is still worse than SS1 and S411.

- Public compare gallery:
  `https://zinc-birth-deleted-wales.trycloudflare.com/index.html`
- Summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr2_summary_s413.md`
- Sweep:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr2_sweep_summary_s413.md`

MR2 max target MAD is `23.98916859567901`. SS1 remains better at
`23.951853137860084`, and S409 `SF12_H18` remains much better at
`23.687431841563786`.

## Validation

- Exported `8` MR2 XML scenes with `0` key lights
- XML validation parsed `8` scenes with `0` failures and `0` warnings
- Rendered `8` frames with the project Mitsuba runtime
- Computed target gap and sweep ranking
- Built and published a visual compare gallery, verified HTTP `200`

## Decision

Whole-frame secondary material scaling is not sufficient. It changes the right
class of geometry, but not the right localized region.

## Next

S414 should introduce localized response data into the renderer path: a native
projection mask, per-particle material grouping, or texture/volume mask that can
drive only the S410 evidence regions.
