# S356 Mitsuba Secondary 3D Depth Material Pass

## Goal

Make the S353/S354 sidecar secondary import beat the MW7 no-secondary control
by changing representation, not just shrinking sphere radius.

S355 showed that radius shrink alone approaches MW7 but does not pass it. S356
adds channel-specific sidecar opacity and depth-based radius falloff.

## Scope

- Extend `tools/export_external_renderer_mitsuba_xml.py` with:
  - `--secondary-3d-channel-opacity`
  - `--secondary-3d-depth-radius-falloff`
- Preserve defaults so earlier S354/S355 commands are unchanged.
- Render five sidecar depth/material candidates SD1-SD5.
- Compare each candidate against:
  - MW7 no-secondary control,
  - S335 secondary contract,
  - S350 C1E bridge.

## Candidate Shape

All candidates use:

- S353 sidecar: `build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d_sidecar.json`
- camera: `18,20,58 -> 18,8,14`
- FOV: `34`
- background: `0.080,0.096,0.115`
- water alpha: `0.014`
- proxy limit: `1024`

Key variations:

| Candidate | Radius scale | Depth falloff | Channel opacity |
| --- | ---: | ---: | --- |
| SD1 | `0.35` | `0.6` | `spray=0.005, foam=0.03, bubble=0.02, droplet=0.005` |
| SD2 | `0.2` | `0.6` | `spray=0.002, foam=0.02, bubble=0.012, droplet=0.002` |
| SD3 | `0.35` | `0.8` | `spray=0.001, foam=0.045, bubble=0.025, droplet=0.001` |
| SD4 | `0.2` | `0.8` | `spray=0.001, foam=0.015, bubble=0.01, droplet=0.001` |
| SD5 | `0.15` | `0.7` | `spray=0.0015, foam=0.018, bubble=0.011, droplet=0.0015` |

## Outputs

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_depth_sweep_summary_s356.md`
- Per-candidate export reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_depth_sd*_export_s356.md`
- Per-candidate render reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_depth_sd*_render_s356.md`
- Per-candidate S335 contract gaps:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_depth_sd*_candidate_gap_s356.md`
- Per-candidate S350 C1E bridge gaps:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_depth_sd*_c1e_gap_s356.md`

## Results

| Candidate | Mean target MAD | Max target MAD | Max contract MAD | Mean native-to-C1E MAD | Max native-to-C1E MAD |
| --- | ---: | ---: | ---: | ---: | ---: |
| MW7 | `19.146286` | `23.951993` | `25.512461` | `13.605084` | `22.125309` |
| SR3 | `19.146341` | `23.952147` | `25.512204` | `13.604854` | `22.125505` |
| SD1 | `19.146315` | `23.952164` | `25.512177` | `13.604844` | `22.125510` |
| SD2 | `19.146308` | `23.951948` | `25.512539` | `13.605036` | `22.125335` |
| SD3 | `19.146252` | `23.952159` | `25.512200` | `13.604848` | `22.125487` |
| SD4 | `19.146287` | `23.951929` | `25.512539` | `13.605083` | `22.125309` |
| SD5 | `19.146269` | `23.951959` | `25.512466` | `13.605060` | `22.125321` |

SD4 is the first sidecar-import candidate to beat MW7 by max target MAD:
`23.95192901234568` versus MW7 `23.951992669753086`.

The improvement is extremely small and not yet a visible quality jump. It is
still useful because it proves the sidecar path can add native secondary data
without worsening the hard max-target gate.

## Decision

Keep the S356 controls and treat SD4 as the current sidecar-import metric
baseline. Do not call this visually solved yet.

## Next

Preserve SD4's hard-gate behavior while making secondary more visible:

- add optional sidecar billboard/soft shell representation,
- keep channel-specific opacity and depth falloff,
- compare against S350 C1E and S335 after every visual increase.
