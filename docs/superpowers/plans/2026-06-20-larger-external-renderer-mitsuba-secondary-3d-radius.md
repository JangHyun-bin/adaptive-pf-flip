# S355 Mitsuba Secondary 3D Radius Scale Pass

## Goal

Test whether the S354 sidecar import path can beat the MW7 no-secondary control
by shrinking the native sphere footprint while keeping sidecar positions and
opacity.

## Scope

- Add `--secondary-3d-radius-scale` to
  `tools/export_external_renderer_mitsuba_xml.py`.
- Default remains `1.0`, preserving S354 behavior.
- Render three sidecar radius candidates:
  - SR1: radius scale `0.5`
  - SR2: radius scale `0.35`
  - SR3: radius scale `0.2`
- Compare against MW7 and S354 SI3.

## Outputs

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_radius_sweep_summary_s355.md`
- Per-candidate export reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_radius_sr*_export_s355.md`
- Per-candidate render reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_radius_sr*_render_s355.md`
- Per-candidate S335 contract gaps:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_radius_sr*_candidate_gap_s355.md`
- Per-candidate S350 C1E bridge gaps:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_radius_sr*_c1e_gap_s355.md`

## Results

| Candidate | Mean target MAD | Max target MAD | Max contract MAD | Mean native-to-C1E MAD | Max native-to-C1E MAD |
| --- | ---: | ---: | ---: | ---: | ---: |
| MW7 | `19.146286` | `23.951993` | `25.512461` | `13.605084` | `22.125309` |
| SI3 | `19.147658` | `23.953638` | `25.508993` | `13.601172` | `22.126016` |
| SR1 | `19.146779` | `23.953122` | `25.510377` | `13.603568` | `22.125786` |
| SR2 | `19.146437` | `23.952629` | `25.511336` | `13.604281` | `22.125488` |
| SR3 | `19.146341` | `23.952147` | `25.512204` | `13.604854` | `22.125505` |

Shrinking the sidecar spheres monotonically approaches MW7, but does not beat
MW7's max target MAD. SR3 is the best radius-scale candidate, still slightly
worse than MW7 by the hard max target gate.

## Decision

Keep `--secondary-3d-radius-scale` because it is useful control plumbing for
future sidecar import tests. Do not keep shrinking sphere proxies as the main
quality path.

The next sidecar step should change representation, not only size:

- channel-specific color/opacity,
- depth attenuation from sidecar camera depth,
- billboard or volume shells generated from sidecar records,
- then a measured replacement attempt against S350 C1E and S335.
