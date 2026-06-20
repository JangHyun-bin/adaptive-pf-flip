# Larger External Renderer: Mitsuba SF12 H18 Split Native Candidate

Status: complete

## Goal

Use the S410 `SF12_ChannelBand` and `SF12_H18_Highlight` mask sources in a
Mitsuba-rendered candidate and compare it against S409 `SF12_H18`, SS1, and
S401 CR21.

## Result

S411 rendered successfully but is rejected.

- Public compare gallery:
  `https://thereby-talented-jerry-acute.trycloudflare.com/index.html`
- Summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_h18_split_native_summary_s411.md`
- Sweep report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_h18_split_native_sweep_summary_s411.md`

S411 target gap:

- Mean gap MAD: `19.222873344264404`
- Max gap MAD: `23.988294110082304`
- Max gap: `226`

This is worse than SS1 native max gap MAD `23.951853137860084`, S409
`SF12_H18` max gap MAD `23.687431841563786`, and S401 CR21 max gap MAD
`23.552905092592592`.

## What Was Tested

S411 converted S410 masks into camera-plane native XML additions:

- `SF12_ChannelBand` became a low-reflectance dark card.
- `SF12_H18_Highlight` became bounded highlight sprites.

This kept the test target-free and renderer-side, but the mechanism behaves like
the rejected S405 screen-card family. It does not recover the split source
response in a real material/light path.

## Validation

- Channel dark-card export: `ready`, `8` frames
- Split native export: `ready`, `8` frames, `512` sprites
- Mitsuba render: `ready`, `8` frames, `0` failures
- Target gap: `ready`
- Sweep summary: `ready`
- Compare gallery: `ready`
- Public compare `index.html`: HTTP `200`
- Public compare `assets/comparison.gif`: HTTP `200`

## Decision

Do not promote S411. Keep the S410 mask sources and S411 render/export reports
as evidence, but stop trying to migrate the split response through camera-plane
cards or sprites.

## Next

S412 should implement an export/material-side modulation path. The next
candidate should affect water or participating-media response through Mitsuba
scene data, not through a screen-space insert.
