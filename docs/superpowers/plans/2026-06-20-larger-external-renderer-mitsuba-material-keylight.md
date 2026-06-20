# S370 Mitsuba Material Key Light Sweep

## Goal

Use the S369 region diagnosis to test whether renderer-side water/material
response can recover the missing crest highlights without more visibility-only
tuning.

## Changes

- Extend `tools/export_external_renderer_mitsuba_xml.py` with optional water
  material controls:
  - `--water-int-ior`
  - `--water-ext-ior`
  - `--water-specular-transmittance`
- Add optional rectangular area key light controls:
  - `--key-light-radiance`
  - `--key-light-position`
  - `--key-light-target`
  - `--key-light-scale`
- Keep default XML output unchanged unless the new options are passed.

## Candidates

- `KL1`: mild front key light plus lower water roughness.
- `KL2`: stronger/narrower key light plus lower water roughness.
- `KL3`: very weak key light after `KL1`/`KL2` over-lifted the scene.
- `KL4`/`KL5`: one-frame off-camera smoke checks to test whether visible panel
  placement caused the failure.

## Results

Summary:
`build/shots/s370_mitsuba_material_keylight_sweep_summary/material_keylight_sweep_summary.json`

Visual review:
`build/shots/s370_mitsuba_material_keylight_review/gallery/index.html`

Public preview:
`https://protocols-educators-george-stickers.trycloudflare.com/index.html`

Ranking:

| Rank | Candidate | Mean target MAD | Max target MAD | Max diff |
| ---: | --- | ---: | ---: | ---: |
| 1 | `SV1-cache` | 19.103672839506174 | 23.72217142489712 | 170 |
| 2 | `KL3` | 109.67923394097222 | 140.33243569958847 | 240 |
| 3 | `KL1` | 109.67945400913067 | 140.33249035493827 | 240 |
| 4 | `KL2` | 110.30775487075617 | 140.94324395576132 | 239 |

## Decision

Reject the area key-light approach for now. It boosts highlights, but it also
raises the full water body and background far beyond the target, causing a much
larger global gap. Moving the rectangle off-camera did not produce a usable
bounded highlight-only response in the smoke checks.

## Next

Use a bounded highlight-response control that is masked by water/crest evidence,
or move deeper into renderer-native surface reconstruction/material normals.
Do not continue broad key-light sweeps.
