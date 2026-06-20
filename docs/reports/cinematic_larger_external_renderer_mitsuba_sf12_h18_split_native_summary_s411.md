# S411 SF12 H18 Split Native Candidate Summary

Generated UTC: `2026-06-20T09:24:00Z`

Public compare URL:
`https://thereby-talented-jerry-acute.trycloudflare.com/index.html`

## Goal

Consume the two S410 renderer-migration mask sources in a Mitsuba render input
and test whether a conservative native candidate can replace the accepted S409
`SF12_H18` post-composite response.

## Inputs

S411 used both S410 mask sources:

- `SF12_ChannelBand`:
  `build/shots/s410_mitsuba_sf12_channel_band_mask_source/source_response_mask_source_summary.json`
- `SF12_H18_Highlight`:
  `build/shots/s410_mitsuba_sf12_h18_highlight_mask_source/source_response_mask_source_summary.json`

The channel-band pass added a dark screen card over the S357 SS1 export:

- Card mode: `rectangle`
- Card distance: `18`
- Mask gain: `0.20`
- Mask blur radius: `0.6`
- Reflectance: `0.012,0.015,0.018`

The highlight pass added bounded screen sprites:

- Sprite limit per frame: `64`
- Sprite threshold: `16`
- Sprite stride: `2`
- Sprite radius pixels: `3.8`
- Sprite radiance: `2.6,3.2,3.8`
- Sprite alpha scale: `0.55`
- Sprite alpha power: `1.15`

## Render Runtime

The render must use the project Mitsuba runtime:

- `build/s319_mitsuba_venv/Scripts/python.exe`

The default `python` currently resolves to a Miniconda Python without Mitsuba,
so direct `python tools/render_mitsuba_xml_export.py ...` fails with
`No module named 'mitsuba'`. This is an environment selection issue, not a
scene/export failure.

## Result

The S411 candidate rendered successfully but should not be promoted.

| Rank | Candidate | Mean Gap MAD | Max Gap MAD | Max Gap |
| ---: | --- | ---: | ---: | ---: |
| 1 | `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| 2 | `S409_SF12_H18` | 18.756908677340533 | 23.687431841563786 | 170 |
| 3 | `SF12_SprayFoam` | 19.120776588220163 | 23.755951646090534 | 170 |
| 4 | `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |
| 5 | `S411_SplitNative` | 19.222873344264404 | 23.988294110082304 | 226 |

The compare gallery shows the same failure mode as S405: the screen-card/sprite
candidate remains visually close to SS1 and does not reproduce the S409/S401
source-response behavior.

## Artifacts

- Channel dark-card export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_channel_dark_card_export_s411.md`
- Split native export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_h18_split_native_export_s411.md`
- Mitsuba render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_h18_split_native_render_s411.md`
- Target-gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_h18_split_native_target_gap_s411.md`
- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_h18_split_native_sweep_summary_s411.md`
- Compare report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_h18_split_native_compare_s411.md`
- Publish report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_sf12_h18_split_native_compare_publish_s411.md`

## Validation

- Built channel dark-card export: `ready`, `8` frames
- Built split native export: `ready`, `8` frames, `512` sprites
- Rendered Mitsuba frames: `ready`, `8` frames, `0` failures
- Target gap computed for S411: max gap MAD
  `23.988294110082304`
- Sweep ranked S411 below SS1
- Compare gallery built: `ready`, `8` frames, `6` columns
- Public compare `index.html`: HTTP `200`
- Public compare `assets/comparison.gif`: HTTP `200`

## Decision

Do not promote S411. It proves that the S410 masks can be consumed by the native
XML path, but it also confirms that camera-plane cards/sprites are the wrong
migration mechanism for the accepted split response.

## Next

S412 should move the response into real renderer/export controls: water
material modulation, volume/surface response, or light-response metadata. Avoid
another camera-plane card/sprite migration pass unless it is only used as a
diagnostic.
