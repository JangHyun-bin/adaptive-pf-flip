# Larger External Renderer: Mitsuba SF12 H18 Renderer-Native Inputs

Status: complete

## Goal

Convert the accepted S409 split response into explicit renderer-migration
inputs rather than another post-composite grade.

## Result

S410 produced two source-response mask sources:

- `SF12_H18_Highlight`:
  `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`
- `SF12_ChannelBand`:
  `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`

It also published an expanded AOV package with `Source Highlight` and
`Target Highlight` panels:

- `https://isbn-brussels-raise-luxury.trycloudflare.com/index.html`

## Code Changes

- `tools/build_mitsuba_source_response_mask_source.py` now accepts
  `--channel-mask-channels` and records classifier settings.
- `tools/build_mitsuba_screen_evidence_aov_package.py` now includes source and
  target highlight panels and coverage metadata.

## Validation

- `python -m py_compile tools\build_mitsuba_source_response_mask_source.py`
- `python -m py_compile tools\build_mitsuba_screen_evidence_aov_package.py`
- Highlight mask source: `ready`, `8` frames
- Channel-band mask source: `ready`, `8` frames
- AOV package: `ready`, `8` frames, `11` AOVs
- Public AOV package `index.html`: HTTP `200`
- Public AOV package `assets/screen_evidence_aov.gif`: HTTP `200`

## Next

S411 should consume the S410 mask sources in a conservative renderer-native
candidate. The target is not another grade; it is a material/export/light
response candidate that can be compared against S409 `SF12_H18`, SS1, and S401
CR21.
