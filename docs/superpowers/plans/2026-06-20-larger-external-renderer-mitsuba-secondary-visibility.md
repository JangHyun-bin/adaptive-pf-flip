# S359 Mitsuba Secondary Visibility Bridge

## Goal

Use the S358 visual review result to test whether a bounded screen-space
secondary visibility bridge can make SS1 visibly closer to the accepted target
without breaking the hard target-gap gate.

This is a diagnostic bridge, not the final renderer-native solution. The goal is
to find a controlled appearance target that can later be moved into a
renderer-facing cache/pass.

## Changes

- Extended `tools/compare_mitsuba_renderer_target_gap.py` with
  `--actual-composite-summary`.
- This lets the existing target-gap comparison pipeline read
  `lsfs_mitsuba_secondary_composite` outputs directly.
- Generated SS1 baseline recheck and three S359 visibility candidates:
  `SV1`, `SV2`, and `SV3`.

## Results

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_visibility_sweep_summary_s359.md`
- Best candidate: `SV1`
- SV1 public quick-tunnel preview:
  `https://reductions-kde-panels-wrote.trycloudflare.com/index.html`

| Candidate | Mean Target MAD | Max Target MAD | Note |
| --- | ---: | ---: | --- |
| `SV1` | `19.103672839506174` | `23.72217142489712` | best bounded bridge |
| `SV3` | `19.159634291409464` | `23.830943287037037` | sharper, worse gate |
| `SV2` | `19.110620177469137` | `23.900221836419753` | stronger, worse gate |
| `SS1` | `19.146412117412552` | `23.951853137860084` | native baseline |

SV1 improves max target MAD by about `0.22968171296296397` over SS1 while
making the secondary mass visibly easier to inspect. Stronger visibility
settings start to lose the hard gate again.

## Next

Port the SV1 visibility profile into a renderer-facing secondary cache/pass
instead of treating the screen-space bridge as final output. Keep the comparison
pipeline and public preview package as the acceptance gate.
