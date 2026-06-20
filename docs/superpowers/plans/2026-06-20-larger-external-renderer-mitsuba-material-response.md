# Larger External Renderer: Mitsuba Material Response MR1

Status: complete

## Goal

Replace the rejected S411 camera-plane insertion idea with an export/material
response candidate that modifies actual Mitsuba scene data.

## Result

S412 added a reusable material-response patcher and tested `MR1`. The tool and
validation loop work, but `MR1` is rejected.

- Public compare gallery:
  `https://barcelona-prevent-respect-sticker.trycloudflare.com/index.html`
- Summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr1_summary_s412.md`
- Sweep:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_material_response_mr1_sweep_summary_s412.md`

`MR1` max target MAD is `23.990219907407408`, worse than SS1
`23.951853137860084`, S411 `23.988294110082304`, S409 `SF12_H18`
`23.687431841563786`, and S401 CR21 `23.552905092592592`.

## Code Change

- Added `tools/modulate_mitsuba_material_response.py`.

The tool consumes the S410 channel/highlight mask sources and patches a Mitsuba
XML export with material/light response parameters. It creates a new
`lsfs_mitsuba_xml_export` manifest, so downstream render/target-gap/gallery
tools work unchanged.

## Validation

- `python -m py_compile tools\modulate_mitsuba_material_response.py`
- `python tools/validate_mitsuba_xml_export.py ...`
- Rendered MR1 with `build/s319_mitsuba_venv/Scripts/python.exe`
- Computed target gap and sweep ranking
- Built visual compare gallery
- Published gallery with Cloudflare quick tunnel and verified HTTP `200`

## Decision

Keep the patcher, reject `MR1`. The failure is not a runtime/export failure; it
is a candidate-design failure. Broad per-frame key-light/material modulation
does not recover the localized source-response behavior.

## Next

Run MR2 as a bounded localized response test. Start by removing broad key-light
lift and using the material patcher for a smaller spray/foam attenuation or AOV
localized response probe.
