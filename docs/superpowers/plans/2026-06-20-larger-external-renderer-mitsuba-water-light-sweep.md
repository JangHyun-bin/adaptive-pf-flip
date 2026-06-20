# Larger External Renderer: Mitsuba Water/Light Sweep

Status: complete

## Goal

After S396-S399 ruled out screen-card and secondary sidecar quantity/radius as
the next improvement axis, test whether basic water BSDF and lighting controls
move the native Mitsuba render toward the target.

## Scope

All candidates preserve the S357 SS1 camera, sidecar, secondary material, and
billboard settings. Only water/light parameters change.

- `WA006`: water roughdielectric alpha `0.006`
- `WA028`: water roughdielectric alpha `0.028`
- `WT72`: water alpha `0.014`, specular transmittance `0.72,0.86,1.0`
- `KL1`: water alpha `0.014`, low key light `0.35,0.42,0.50`

## Validation

For each candidate:

- Mitsuba XML export: `ready`, `8` frames, `0` failures
- Mitsuba render: `ready`, `8` frames, `0` render failures
- Target-gap comparison
- C1E bridge-gap comparison

Sweep summary:

- `docs/reports/cinematic_larger_external_renderer_mitsuba_water_light_sweep_summary_s400.md`
- `build/shots/s400_mitsuba_water_light_sweep/native_gap_sweep_summary.json`

## Result

SS1 remains the native baseline.

| Candidate | Mean Target MAD | Max Target MAD | Max Diff |
| --- | ---: | ---: | ---: |
| SS1 | 19.146412 | 23.951853 | 170 |
| KL1 | 19.222774 | 23.988706 | 226 |
| WA006 | 19.235980 | 23.990508 | 226 |
| WA028 | 19.209452 | 24.001433 | 223 |
| WT72 | 21.136788 | 27.907769 | 231 |

## Decision

Do not promote any S400 candidate. Water specular transmittance reduction is
especially harmful for this target. Low key light has the least bad result of
the tested variants, but it still falls into the same failed native band as the
recent secondary-sidecar experiments.

## Next

Keep SS1 as the native baseline. The next useful branch is not broad scalar
water/light tuning; move toward a stronger BSDF/model change or a calibrated
post-render tone/grade bridge that can reproduce CR21-like frame-local response
without using the target image at runtime.
