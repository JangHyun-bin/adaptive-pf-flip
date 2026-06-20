# S369 Mitsuba Target Gap Region Analysis

## Goal

After S367/S368 showed that visibility-only secondary tuning no longer beats
`SV1-cache`, split the remaining target gap by image region to decide the next
renderer/material lever.

## Changes

- Add `tools/analyze_mitsuba_target_gap_regions.py`.
- The tool compares a target preview summary with an actual secondary composite
  summary.
- It uses the secondary visibility layer alpha as a mask and reports:
  - all pixels
  - secondary-mask pixels
  - nonsecondary pixels
  - target highlight pixels
  - dark target pixels inside the secondary mask
- It writes JSON, CSV, and a visual gallery with target/actual/diff/mask strips.

## Results

Summary:
`build/shots/s369_mitsuba_target_gap_regions_sv1/target_gap_region_summary.json`

CSV:
`build/shots/s369_mitsuba_target_gap_regions_sv1/target_gap_regions.csv`

Visual review:
`build/shots/s369_mitsuba_target_gap_regions_sv1/gallery/index.html`

Public preview:
`https://combining-contractor-furthermore-hire.trycloudflare.com/index.html`

Aggregate region metrics for `SV1-cache`:

| Region | Coverage | Mean MAD | Target luma | Actual luma | Signed luma |
| --- | ---: | ---: | ---: | ---: | ---: |
| `all` | 1.000000 | 19.103673 | 91.288041 | 86.521458 | -4.766584 |
| `secondary` | 0.045091 | 21.578829 | 92.635703 | 92.790421 | 0.154718 |
| `nonsecondary` | 0.954909 | 18.986796 | 91.224405 | 86.225437 | -4.998968 |
| `highlight` | 0.006155 | 99.553962 | 235.043558 | 134.834664 | -100.208894 |
| `secondary_dark_target` | 0.003533 | 51.263450 | 24.401817 | 75.794614 | 51.392797 |

## Decision

The dominant next issue is not only secondary visibility. The nonsecondary
region covers most pixels and is still too dark by about 5 luma on average. The
highlight region is tiny but extremely wrong: actual is about 100 luma darker
than target. The dark secondary target region is the opposite: actual is about
51 luma too bright.

## Next

Run a renderer/material response pass that boosts water/crest highlights while
separately suppressing bright visibility contribution over target-dark secondary
detail. Avoid more global post-grade or visibility-only sweeps unless they are
driven by these region metrics.
