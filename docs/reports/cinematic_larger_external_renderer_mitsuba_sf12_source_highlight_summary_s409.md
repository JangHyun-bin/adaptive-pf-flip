# S409 SF12 Source Highlight Summary

Generated UTC: `2026-06-20T09:08:00Z`

Public comparison URL:
`https://angela-postcard-cooperation-hosting.trycloudflare.com/index.html`

## Goal

Keep the S408 `SF12_SprayFoam` spray/foam attenuation probe and add a separate
target-free source-highlight response. The highlight pass is constrained to
nonsecondary pixels with source luma `>= 120` and alpha `<= 3`.

## Candidates

| Candidate | Highlight Strength | Highlight Max Delta | SF12 Spray/Foam |
| --- | ---: | ---: | --- |
| `SF12_H15` | 0.45 | 55 | on |
| `SF12_H16` | 0.55 | 70 | on |
| `SF12_H17` | 0.70 | 90 | on |
| `SF12_H18` | 0.85 | 120 | on |
| `SF12_H19` | 1.00 | 255 | on |

All candidates keep the S408 channel-band settings:
`spray,foam`, source luma `0..95`, strength `0.12`, max delta `18`.

## Ranking

| Candidate | Mean Target MAD | Max Target MAD | Max Diff |
| --- | ---: | ---: | ---: |
| `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| `SF12_H19` | 18.72657222543724 | 23.68549704218107 | 182 |
| `SF12_H18` | 18.756908677340533 | 23.687431841563786 | 170 |
| `SF12_H17` | 18.816972173996913 | 23.698841306584363 | 170 |
| `SF12_H16` | 18.88112059542181 | 23.710983796296297 | 170 |
| `SF12_H15` | 18.92520190329218 | 23.71939236111111 | 170 |
| `SF12_SprayFoam` | 19.120776588220163 | 23.755951646090534 | 170 |
| `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |

## Validation

- Candidate generation: `ready`, `8` frames each
- Target-gap comparisons: `ready`, `8` frames each
- Visual compare gallery: `ready`, `8` frames, `8` columns
- Public `index.html`: HTTP `200`
- Public `assets/comparison.gif`: HTTP `200`

## Decision

Promote `SF12_H18` as the bounded source-highlight probe. `SF12_H19` is the
numeric best SF12 variant, but it is a saturated ceiling/reference pass. H18
keeps the same coverage and nearly the same target gap while avoiding the
unbounded highlight max delta.

`S401_CR21_Profile` remains the best overall target-free source-response
reference, but S409 splits its behavior into two more renderer-migratable
pieces: `SF12_SprayFoam` for spray/foam dark attenuation and `SF12_H18` for
nonsecondary source highlights.

## Next

S410 should migrate the accepted S409 split response toward renderer-native
controls. Start from `SF12_H18`, preserve `SF12` as the dark/secondary AOV
attenuation baseline, and test whether the nonsecondary highlight behavior can
be represented by material/export/light-response data instead of a
post-composite grade.
