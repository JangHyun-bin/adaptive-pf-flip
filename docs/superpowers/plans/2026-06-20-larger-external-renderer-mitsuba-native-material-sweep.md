# S351 Mitsuba Native Material And Secondary Sweep

## Goal

Test whether the S348 TB6 native Mitsuba baseline can be improved by changing
native water roughness and secondary proxy material strength, without adding
more post-render blending.

## Scope

- Keep the TB6 camera and background fixed.
- Sweep water roughness first, then progressively attenuate native secondary
  proxies.
- Add a no-secondary-proxy control to separate water/background error from
  proxy-secondary error.
- Compare every candidate against:
  - the S335 secondary-pass contract,
  - the S350 C1E depth-aware bridge.

## Fixed Baseline

- camera position: `18,20,58`
- camera target: `18,8,14`
- camera fov: `34`
- background radiance: `0.080,0.096,0.115`
- baseline water alpha: `0.014`
- baseline secondary proxy limit: `384`
- baseline secondary proxy radius: `0.095`

## Candidate Set

| Candidate | Change from TB6 |
| --- | --- |
| MW1 | water alpha `0.010` |
| MW2 | water alpha `0.018` |
| MW3 | lower secondary opacity, halo, mist, and billboard strength |
| MW4 | stronger secondary attenuation |
| MW5 | stronger secondary attenuation |
| MW6 | near-off secondary opacity with proxies still emitted |
| MW7 | secondary proxy limit `0` no-secondary-proxy control |

## Outputs

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_material_sweep_summary_s351.md`
- Per-candidate export reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_material_mw*_export_s351.md`
- Per-candidate render reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_material_mw*_render_s351.md`
- Per-candidate S335 contract gaps:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_material_mw*_candidate_gap_s351.md`
- Per-candidate S350 C1E bridge gaps:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_material_mw*_c1e_gap_s351.md`
- Baseline S350 C1E bridge gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_native_material_tb6_c1e_gap_s351.md`

## Results

| Candidate | Mean target MAD | Max target MAD | Mean contract MAD | Max contract MAD | Mean native-to-C1E MAD | Max native-to-C1E MAD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TB6 | `19.411650913065845` | `24.390221193415638` | `13.6738766718107` | `24.992857767489712` | `13.654164` | `22.504146` |
| MW1 | `19.425247` | `24.386404` | `13.757055` | `25.014654` | `13.758078` | `22.531492` |
| MW2 | `19.395520` | `24.386285` | `13.754828` | `24.993894` | `13.761021` | `22.543230` |
| MW3 | `19.403970` | `24.373263` | `13.673490` | `25.024372` | `13.650160` | `22.487575` |
| MW4 | `19.396669` | `24.353510` | `13.674214` | `25.054030` | `13.646612` | `22.467953` |
| MW5 | `19.392399` | `24.339938` | `13.678026` | `25.087172` | `13.645543` | `22.455222` |
| MW6 | `19.392558` | `24.332458` | `13.685104` | `25.111525` | `13.648679` | `22.447433` |
| MW7 | `19.14628649048354` | `23.951992669753086` | `13.649256044238683` | `25.512461419753087` | `13.605083670910494` | `22.125309284979423` |

MW7 is the best target/C1E candidate: it lowers TB6 max target MAD from
`24.390221193415638` to `23.951992669753086`, and lowers max native-to-C1E MAD
from `22.504146` to `22.125309284979423`.

The tradeoff is clear: MW7 increases max contract MAD from `24.992857767489712`
to `25.512461419753087`. Removing the current secondary proxies helps the
target/C1E metric but moves away from the S335 overlay contract.

## Decision

Do not keep tuning the current sphere/halo/mist/billboard secondary proxies as
the native replacement path. They are useful visual placeholders, but the sweep
shows they add mismatch against the accepted target and C1E bridge.

Use MW7 as the next native water/background control baseline. The next native
renderer work should export secondary particles as a depth-aware 3D data layer
or volume-aware secondary representation, not as screen-space or simple sampled
sphere proxies.

## Next

Run a small no-secondary-proxy background sweep around MW7, then implement a
proper depth-aware 3D secondary cache/export path for native Mitsuba instead of
more proxy opacity tuning.
