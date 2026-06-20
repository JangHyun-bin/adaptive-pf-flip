# S368 Mitsuba Secondary Mixed/Dual Visibility Sweep

## Goal

Test whether the remaining target gap can be reduced by splitting secondary
visibility behavior by channel instead of applying a uniform light or shadow
layer.

## Changes

- Extend `tools/composite_mitsuba_secondary_layer.py` with channel-aware
  `mixed` and `dual` blend modes.
- `mixed` replaces selected channels with a shadow tint while leaving the other
  channels in the original light SV1 style.
- `dual` adds a shadow pass for selected channels and then restores a bounded
  light pass on top, preserving crest highlights better than shadow-only.

## Candidates

- `MX1`/`MX2`: spray and bubble as shadow channels.
- `MX3`: spray-only shadow channel.
- `DV1`/`DV3`/`DV4`/`DV5`: spray-only dual detail at different strengths.
- `DV2`: spray and bubble dual detail.

## Results

Summary:
`build/shots/s368_mitsuba_secondary_mixed_dual_sweep_summary/secondary_mixed_dual_sweep_summary.json`

Visual review:
`build/shots/s368_mitsuba_secondary_mixed_dual_review/gallery/index.html`

Public preview:
`https://lawn-regardless-petroleum-gospel.trycloudflare.com/index.html`

Ranking:

| Rank | Candidate | Mean target MAD | Max target MAD | Max diff |
| ---: | --- | ---: | ---: | ---: |
| 1 | `SV1-cache` | 19.103672839506174 | 23.72217142489712 | 170 |
| 2 | `DV4` | 19.10481328768004 | 23.72891139403292 | 170 |
| 3 | `DV5` | 19.106409223894033 | 23.73129822530864 | 170 |
| 4 | `DV3` | 19.10643928433642 | 23.739014917695474 | 170 |
| 5 | `DV1` | 19.11315915959362 | 23.742681327160494 | 170 |

## Decision

Keep `SV1-cache` as the current metric baseline. Dual spray detail almost ties
the baseline, but still does not beat the hard max target MAD gate. This makes
the next lever more likely to be renderer/material response or an automated
target-fit visibility profile, not more hand-tuned visibility-only variants.

## Next

Move to a target-fit profile harness or renderer/material response pass that can
alter water/background/secondary integration together rather than only swapping
the screen-space visibility layer.
