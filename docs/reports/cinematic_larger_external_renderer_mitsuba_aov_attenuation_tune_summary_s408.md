# S408 AOV Attenuation Tune Summary

Generated UTC: `2026-06-20T08:56:00Z`

Public comparison URL: `https://avoiding-ipod-settled-involve.trycloudflare.com/index.html`

## Goal

Tune around S407 `SF18_SprayFoam`, keeping the same target-free spray/foam AOV
mask and only changing attenuation strength/max delta.

## Candidates

| Candidate | Channel Mask | Luma Band | Strength | Max Delta |
| --- | --- | --- | ---: | ---: |
| `SF12_SprayFoam` | `spray,foam` | `0..95` | 0.12 | 18 |
| `SF18_SprayFoam` | `spray,foam` | `0..95` | 0.18 | 24 |
| `SF22_SprayFoam` | `spray,foam` | `0..95` | 0.22 | 30 |
| `SF26_SprayFoam` | `spray,foam` | `0..95` | 0.26 | 34 |

## Target Gap Ranking

| Candidate | Mean Target MAD | Max Target MAD | Max Diff |
| --- | ---: | ---: | ---: |
| `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| `SF12_SprayFoam` | 19.120776588220163 | 23.755951646090534 | 170 |
| `SF18_SprayFoam` | 19.135082706404322 | 23.77382137345679 | 170 |
| `SF22_SprayFoam` | 19.14672389403292 | 23.785713734567903 | 170 |
| `SF26_SprayFoam` | 19.16045307677469 | 23.798092849794237 | 172 |
| `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |

## Validation

- Candidate generation: `ready`, `8` frames each
- Target-gap comparisons: `ready`, `8` frames each
- S408 public gallery:
  - public `index.html`: HTTP `200`
  - public `assets/comparison.gif`: HTTP `200`

## Decision

Promote `SF12_SprayFoam` as the current tuned AOV attenuation probe. It improves
over S407 `SF18` and over SS1 on both mean and max target MAD, while staying
less heavy than the stronger attenuation candidates.

`S401_CR21_Profile` is still the best overall target-free visual response, but
SF12 is the best response based on secondary-channel AOV evidence.

## Next

S409 should handle source highlights separately. S406 showed highlights are not
explained by secondary channels, and S408 only improves the dark/secondary
attenuation portion. The next pass should keep SF12 as the dark-secondary probe
and add a bounded, target-free source-highlight response that does not rely on
secondary material.
