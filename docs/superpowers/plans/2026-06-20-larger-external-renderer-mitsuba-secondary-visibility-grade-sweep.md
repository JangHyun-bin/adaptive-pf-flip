# S364 Mitsuba Secondary Visibility Grade Sweep

## Goal

Test whether a restrained global post-grade can close the remaining visual gap
after S363 without changing the SV1-cache secondary visibility contract.

This pass intentionally uses global grade parameters only. It does not copy
target pixels or use target-image local masks.

## Changes

- Extended `tools/compare_mitsuba_renderer_target_gap.py` with
  `--actual-grade-summary`.
- Ran three grade candidates over the S362 SV1-cache composite:
  - `G1`: previous restrained cinematic grade baseline,
  - `G2`: cooler/darker grade,
  - `G3`: warmer/lighter grade.
- Ranked the grade candidates against the ungraded `SV1-cache` baseline.

## Result

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_visibility_grade_sweep_summary_s364.md`

| Candidate | Mean Target MAD | Max Target MAD | Decision |
| --- | ---: | ---: | --- |
| `SV1-cache` | `19.103672839506174` | `23.72217142489712` | keep baseline |
| `G3` | `20.5120418595679` | `31.732736625514402` | reject |
| `G1` | `18.76499035493827` | `36.446965663580244` | reject; max gate breaks |
| `G2` | `19.972234278549383` | `46.3463850308642` | reject |

Global post-grade does not solve the remaining visual gap. `G1` improves mean
MAD slightly, but the hard max target gate regresses from `23.72217142489712` to
`36.446965663580244`, which is not acceptable.

## Next

Keep `SV1-cache` as the active visual baseline. Move tone matching into
renderer-facing background/camera/material parameters rather than broad
post-grade tuning.
