# S407 AOV Attenuation Summary

Generated UTC: `2026-06-20T08:50:00Z`

Public comparison URL: `https://battery-sister-radius-career.trycloudflare.com/index.html`

## Goal

Test a bounded target-free local attenuation pass based on S406 channel evidence,
without using target images at runtime.

## Change

`tools/apply_mitsuba_source_region_response.py` now supports
`--channel-mask-channels`, allowing channel-band response to use only selected
projected secondary channels such as `spray,foam`.

Default behavior remains unchanged: all four secondary channels are selected,
and the S401 CR21 profile still reproduces pixel-identical output.

## Candidates

| Candidate | Channel Mask | Luma Band | Strength | Max Delta |
| --- | --- | --- | ---: | ---: |
| `AD18_AllDensity` | `spray,foam,bubble,droplet` | `0..95` | 0.18 | 24 |
| `SF18_SprayFoam` | `spray,foam` | `0..95` | 0.18 | 24 |
| `SF32_SprayFoam` | `spray,foam` | `0..95` | 0.32 | 40 |

## Target Gap Ranking

| Candidate | Mean Target MAD | Max Target MAD | Max Diff |
| --- | ---: | ---: | ---: |
| `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| `SF18_SprayFoam` | 19.135082706404322 | 23.77382137345679 | 170 |
| `AD18_AllDensity` | 19.14884677211934 | 23.784441872427983 | 170 |
| `SF32_SprayFoam` | 19.184116431970164 | 23.816592078189302 | 178 |
| `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |

## Validation

- `python -m py_compile tools\apply_mitsuba_source_region_response.py`
- CR21 channel option parity against S401: `8` frames, max diff `0`, mean channel abs diff `0.0`
- Candidate generation: `ready`, `8` frames each
- Target-gap comparisons: `ready`, `8` frames each
- S407 public gallery:
  - public `index.html`: HTTP `200`
  - public `assets/comparison.gif`: HTTP `200`

## Decision

Promote `SF18_SprayFoam` as the next target-free AOV attenuation probe. It is
still weaker than the CR21 profile, but it is the first bounded AOV/material
direction in this branch that improves over SS1 on both mean and max target MAD.

Do not promote `SF32`; it over-attenuates. Do not use all-channel attenuation as
the main direction; it is less targeted than spray/foam while offering no visual
advantage.

## Next

S408 should tune around `SF18_SprayFoam` rather than returning to broad material
sweeps:

- test a narrow strength/max-delta sweep around `0.14..0.24`;
- keep `spray,foam` channel masking;
- handle source highlights separately, since S406 showed highlights are not
  explained by secondary channels;
- compare against SS1, SF18, and CR21 with the same public-gallery flow.
