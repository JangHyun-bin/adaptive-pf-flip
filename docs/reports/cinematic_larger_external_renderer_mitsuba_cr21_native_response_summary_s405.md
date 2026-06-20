# S405 CR21 Native Response Migration Summary

Generated UTC: `2026-06-20T08:40:00Z`

Public comparison URL: `https://decades-monitors-application-watch.trycloudflare.com/index.html`

## Goal

Move the CR21 target-free source/dark-secondary response one step closer to a
renderer-side/native candidate, without using target images at runtime.

## Changes

- Added `classify_response_pixels()` to
  `tools/apply_mitsuba_source_region_response.py`.
- Added `tools/build_mitsuba_source_response_mask_source.py`.
- Exported CR21 evidence masks:
  - highlight mask source
  - dark-secondary mask source
  - response-union mask source
- Built and rendered three renderer-side candidates:
  - `NH1_HighlightSprites`
  - `NU1_UnionSoftCard`
  - `NHD1_HighlightDarkCard`
- Published a Target/C1E/SS1/NH1/NU1/NHD1/CR21 comparison gallery.

## Mask Coverage

| Mask | Mean Coverage | Max Coverage |
| --- | ---: | ---: |
| `highlight` | 0.003991849922839506 | 0.014924768518518518 |
| `dark-secondary` | 0.0024090952932098765 | 0.0077083333333333335 |
| `response-union` | 0.006400945216049383 | 0.01949652777777778 |

## Target Gap Ranking

| Candidate | Mean Target MAD | Max Target MAD | Max Diff |
| --- | ---: | ---: | ---: |
| `S401_CR21_Profile` | 18.657217962319958 | 23.552905092592592 | 182 |
| `SS1_Native` | 19.146412117412552 | 23.951853137860084 | 170 |
| `NH1_HighlightSprites` | 19.222958220807612 | 23.98830825617284 | 226 |
| `NHD1_HighlightDarkCard` | 19.222967705118315 | 23.988318544238684 | 226 |
| `NU1_UnionSoftCard` | 19.222715486754115 | 23.988894675925927 | 226 |

## Validation

- `python -m py_compile tools\apply_mitsuba_source_region_response.py tools\build_mitsuba_source_response_mask_source.py`
- CR21 refactor parity against S401: `8` frames, max diff `0`, mean channel abs diff `0.0`
- Mask source generation: `ready`, `8` frames each
- Native candidate exports: `ready`, `8` frames each, `0` missing references
- Native candidate renders: `ready`, `8` frames each, `0` render failures
- Target-gap comparisons: `ready`, `8` frames each
- C1E replacement comparisons: `ready`, decision `native_candidate_needs_work`
- S405 public gallery:
  - public `index.html`: HTTP `200`
  - public `assets/comparison.gif`: HTTP `200`

## Decision

Do not promote `NH1`, `NU1`, or `NHD1`. The CR21 evidence masks are narrow and
useful, but mapping them through screen-space sprites/cards does not reproduce
the CR21 response. The candidates remain in the same failed native band as
earlier screen-card and sidecar-count experiments.

Keep the new mask-source tool. It gives the next pass an explicit, target-free
source/secondary response contract without re-running target analysis.

## Next

S406 should move away from screen-space cards and into material/AOV response:

- use the S405 CR21 masks as evidence/diagnostics, not as the final render
  mechanism;
- drive secondary material, water surface, or source-region AOV behavior from
  the mask/particle metadata;
- keep SS1 as native baseline and S401 CR21 as visual reference;
- compare every candidate through the same target-gap, C1E-gap, and comparison
  gallery flow.
