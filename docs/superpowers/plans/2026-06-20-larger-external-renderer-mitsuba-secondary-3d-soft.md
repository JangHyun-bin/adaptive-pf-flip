# S357 Mitsuba Secondary 3D Soft Billboard Pass

## Goal

Try to make the S356 SD4 sidecar baseline more visibly present while preserving
the hard max-target gate.

## Scope

- Keep the S356 SD4 sidecar material/depth settings.
- Add low-opacity sidecar billboard or mist proxies using existing Mitsuba XML
  exporter controls.
- Measure against:
  - MW7 no-secondary control,
  - SD4,
  - S335 secondary contract,
  - S350 C1E bridge.

## Candidates

All candidates use SD4's base:

- sidecar: `build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d_sidecar.json`
- radius scale: `0.2`
- depth radius falloff: `0.8`
- channel opacity: `spray=0.001,foam=0.015,bubble=0.01,droplet=0.001`

| Candidate | Soft pass |
| --- | --- |
| SS1 | billboard opacity `0.002`, radius scale `2.2`, aspect `1.2` |
| SS2 | billboard opacity `0.004`, radius scale `3.0`, aspect `1.25` |
| SS3 | mist opacity `0.0015`, radius scale `3.0`, shells `1` |
| SS4 | billboard opacity `0.0015`, radius scale `2.0`, aspect `1.2` |
| SS5 | billboard opacity `0.0025`, radius scale `2.4`, aspect `1.2` |

## Outputs

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_soft_sweep_summary_s357.md`
- Per-candidate export reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_soft_ss*_export_s357.md`
- Per-candidate render reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_soft_ss*_render_s357.md`
- Per-candidate S335 contract gaps:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_soft_ss*_candidate_gap_s357.md`
- Per-candidate S350 C1E bridge gaps:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_soft_ss*_c1e_gap_s357.md`

## Results

| Candidate | Mean target MAD | Max target MAD | Max contract MAD | Mean native-to-C1E MAD | Max native-to-C1E MAD |
| --- | ---: | ---: | ---: | ---: | ---: |
| MW7 | `19.146286` | `23.951993` | `25.512461` | `13.605084` | `22.125309` |
| SD4 | `19.146287` | `23.951929` | `25.512539` | `13.605083` | `22.125309` |
| SS1 | `19.146412` | `23.951853` | `25.512155` | `13.605125` | `22.125238` |
| SS2 | `19.146712` | `23.952048` | `25.512479` | `13.605416` | `22.125438` |
| SS3 | `19.146580` | `23.952471` | `25.512038` | `13.604485` | `22.125564` |
| SS4 | `19.146413` | `23.951979` | `25.512487` | `13.605123` | `22.125369` |
| SS5 | `19.146570` | `23.952113` | `25.512300` | `13.605204` | `22.125508` |

SS1 is the best candidate by max target MAD. It improves over SD4
`23.95192901234568` to `23.951853137860084`, and also improves max
native-to-C1E MAD from `22.125309` to `22.125238`.

SS2 and SS5 show that a stronger billboard starts to harm the hard gate. SS3
mist improves mean native-to-C1E, but worsens max target MAD and max
native-to-C1E MAD.

## Decision

Use SS1 as the current sidecar-soft baseline. This is still a subtle visual
change, but it is the first soft sidecar pass that improves the hard max-target
gate over SD4 instead of trading it away.

## Next

Package a focused visual review for MW7, SD4, and SS1. The next tuning pass
should inspect actual frames before increasing secondary strength further.
