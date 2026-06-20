# S367 Mitsuba Secondary Shadow Sweep

## Goal

Test whether the remaining renderer-target gap is caused by the SV1 visibility
layer being too bright and fog-like. Keep the accepted camera/background/render
baseline fixed and compare dark secondary visibility layers against the current
SV1-cache baseline.

## Changes

- Extend `tools/composite_mitsuba_secondary_layer.py` with a bounded
  `--blend-mode shadow` option.
- Preserve default alpha behavior for existing SV1-style composites.
- Add shadow color and alpha scale controls for diagnostic occlusion layers.
- Generate two shadow candidates:
  - `SO1-shadow`: soft dark layer with the same coverage as SV1.
  - `SO2-shadow`: smaller, sharper, darker particle layer.

## Results

Summary:
`build/shots/s367_mitsuba_secondary_shadow_sweep_summary/secondary_shadow_sweep_summary.json`

Visual review:
`build/shots/s367_mitsuba_secondary_shadow_review/gallery/index.html`

Public preview:
`https://louis-bowl-viii-predictions.trycloudflare.com/index.html`

Ranking:

| Rank | Candidate | Mean target MAD | Max target MAD | Max diff |
| ---: | --- | ---: | ---: | ---: |
| 1 | `SV1-cache` | 19.103672839506174 | 23.72217142489712 | 170 |
| 2 | `SO1-shadow` | 19.272146910365226 | 24.144057998971192 | 170 |
| 3 | `SO2-shadow` | 19.309630272633747 | 24.19077160493827 | 170 |

## Decision

Reject shadow-only secondary compositing for now. The visual read confirms the
target has darker secondary detail than SV1-cache, but replacing the layer with a
pure shadow layer removes too much bright water/spray response and loses the
hard target-gap gate.

## Next

Move to a target-trained visibility profile or renderer/material integration
that can preserve the bright crest highlights while adding darker particle
detail.
