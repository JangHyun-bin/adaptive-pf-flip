# S352 Mitsuba No-Secondary Background Sweep

## Goal

After S351 showed that disabling current native secondary proxies improves the
target/C1E max error, test whether the MW7 no-secondary-proxy control benefits
from a different background radiance.

## Scope

- Keep MW7 camera, water alpha, and secondary proxy limit `0`.
- Sweep only background radiance around the TB6 value.
- Compare every candidate against:
  - the S335 secondary-pass contract,
  - the S350 C1E depth-aware bridge.

## Candidates

| Candidate | Background radiance |
| --- | --- |
| MW7 | `0.080,0.096,0.115` |
| NB1 | `0.075,0.090,0.108` |
| NB2 | `0.070,0.084,0.101` |
| NB3 | `0.085,0.102,0.122` |
| NB4 | `0.078,0.094,0.112` |

## Outputs

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_no_secondary_bg_sweep_summary_s352.md`
- Per-candidate export reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_no_secondary_bg_nb*_export_s352.md`
- Per-candidate render reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_no_secondary_bg_nb*_render_s352.md`
- Per-candidate S335 contract gaps:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_no_secondary_bg_nb*_candidate_gap_s352.md`
- Per-candidate S350 C1E bridge gaps:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_no_secondary_bg_nb*_c1e_gap_s352.md`

## Results

| Candidate | Mean target MAD | Max target MAD | Max contract MAD | Mean native-to-C1E MAD | Max native-to-C1E MAD |
| --- | ---: | ---: | ---: | ---: | ---: |
| MW7 | `19.14628649048354` | `23.951992669753086` | `25.512461419753087` | `13.605083670910494` | `22.125309284979423` |
| NB1 | `20.204336` | `26.554997` | `22.875340` | `14.371923` | `24.723611` |
| NB2 | `21.420919` | `29.266413` | `23.116985` | `15.439318` | `27.431411` |
| NB3 | `18.250665` | `25.934545` | `28.061110` | `13.145886` | `21.145738` |
| NB4 | `19.541565` | `24.949338` | `24.501301` | `13.861291` | `23.120024` |

NB3 improves mean target MAD and native-to-C1E max MAD, but it worsens the hard
max-target gate from MW7 `23.951992669753086` to `25.934545`. NB1, NB2, and
NB4 also worsen max target MAD.

## Decision

Keep MW7's TB6 background as the no-secondary-proxy control baseline. More
background tuning is not the next high-leverage path.

The current best native control is still far from S350 C1E max target MAD
`14.389824459876543`. The next meaningful renderer step is to replace the
sampled proxy-secondary representation with depth-aware 3D secondary data,
not to keep tuning background radiance.

## Next

Start a depth-aware 3D secondary export path for Mitsuba. The first slice should
be schema-first and renderer-safe:

- emit per-frame secondary world positions, radius, type, velocity, and depth
  metadata into a compact sidecar,
- validate sidecar bounds and camera projection,
- add a native Mitsuba import/proxy pass that consumes that sidecar instead of
  sampled screen-space or low-fidelity proxy settings.
