# S406 CR21 Mask Channel Join Summary

Generated UTC: `2026-06-20T08:45:00Z`

Public AOV URL: `https://almost-supplied-consulting-graph.trycloudflare.com/index.html`

## Goal

Determine whether the S405 CR21 response masks are explained by projected
secondary channels, before spending another renderer pass on material changes.

## Inputs

- Highlight mask source:
  `build/shots/s405_mitsuba_cr21_highlight_mask_source/source_response_mask_source_summary.json`
- Dark-secondary mask source:
  `build/shots/s405_mitsuba_cr21_dark_secondary_mask_source/source_response_mask_source_summary.json`
- Response-union mask source:
  `build/shots/s405_mitsuba_cr21_response_union_mask_source/source_response_mask_source_summary.json`
- Mitsuba export:
  `build/shots/s357_mitsuba_secondary_3d_soft_ss1/mitsuba_export.json`

## Results

| Mask | Best Candidate | Precision | Recall | F1 | Candidate Coverage |
| --- | --- | ---: | ---: | ---: | ---: |
| `Highlight` | `spray_density_ge_8` | 0.004530 | 0.039263 | 0.008123 | 0.034599 |
| `DarkSecondary` | `all_secondary_channels_density_ge_8` | 0.099769 | 0.906983 | 0.179764 | 0.046142 |
| `ResponseUnion` | `all_secondary_channels_density_ge_8` | 0.093692 | 0.448808 | 0.155021 | 0.046142 |

## Decision

The CR21 highlight mask is not explained by secondary channels. Treat it as a
source/water response problem, not a spray/foam material problem.

The dark-secondary and response-union masks are loosely explained by broad
secondary density, especially all-channel and spray/foam density. Precision is
low, so directly changing all secondary material will likely repeat the S394/S395
failure. The useful interpretation is local attenuation around secondary density,
not brighter or larger secondary particles.

## Next

S407 should build a bounded attenuation/AOV candidate:

- use `DarkSecondary` / `ResponseUnion` as diagnostics;
- avoid source-highlight changes through secondary material;
- test local spray/foam density attenuation against the target and C1E gates;
- if the attenuation candidate also lands in the S396/S405 failed band, move
  away from screen/material proxies toward a true water/source transport model.
