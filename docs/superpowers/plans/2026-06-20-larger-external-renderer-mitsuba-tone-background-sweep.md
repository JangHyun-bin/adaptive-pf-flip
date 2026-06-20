# S348 Mitsuba Tone Background Sweep

## Goal

Calibrate the native Mitsuba background/tone before spending more iterations on
secondary geometry. S347 showed that secondary sprite placement only produced a
tiny metric change, while the native render was still much brighter than both
the accepted target and the validated C3 bridge.

## Scope

- Keep the S345 MB2 secondary settings fixed.
- Sweep only background radiance while keeping camera, water alpha, proxy,
  mist, halo, and billboard settings pinned.
- Render seven candidates, TB1 through TB7.
- Compare every candidate against:
  - the S341 C3 bridge through the S344 native replacement gate.
  - the S335 secondary-pass contract gate.

## Fixed Settings

- camera position: `18,20,58`
- camera target: `18,8,14`
- camera fov: `34`
- water alpha: `0.014`
- secondary proxy limit: `384`
- secondary proxy radius: `0.095`
- secondary opacity: `0.12`
- secondary halo opacity: `0.06`
- secondary halo radius scale: `3.0`
- secondary mist opacity: `0.026`
- secondary mist radius scale: `5.2`
- secondary mist shells: `1`
- secondary billboard opacity: `0.18`
- secondary billboard radius scale: `4.0`
- secondary billboard aspect: `1.4`

## Background Candidates

| Candidate | Background radiance |
| --- | --- |
| TB1 | `0.08,0.12,0.17` |
| TB2 | `0.10,0.12,0.14` |
| TB3 | `0.06,0.075,0.09` |
| TB4 | `0.09,0.11,0.13` |
| TB5 | `0.085,0.102,0.122` |
| TB6 | `0.080,0.096,0.115` |
| TB7 | `0.075,0.090,0.108` |

## Outputs

Each candidate has export, render, S335 contract gap, and S344 C3 bridge gap
reports:

- `docs/reports/cinematic_larger_external_renderer_mitsuba_tone_bg_tb*_export_s348.md`
- `docs/reports/cinematic_larger_external_renderer_mitsuba_tone_bg_tb*_render_s348.md`
- `docs/reports/cinematic_larger_external_renderer_mitsuba_tone_bg_tb*_candidate_gap_s348.md`
- `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_tb*_s348.md`

## Results

| Candidate | Mean target MAD | Max target MAD | Mean native-to-C3 MAD | Max native-to-C3 MAD |
| --- | ---: | ---: | ---: | ---: |
| S347 SC4 | `37.13381309477881` | `66.33893840020576` | `40.2254558899177` | `61.848001543209875` |
| TB1 | `16.39866785622428` | `32.140062371399175` | `16.804846563143006` | `27.432226080246913` |
| TB2 | `16.95466579861111` | `31.891748971193415` | `13.282437065972223` | `27.063974408436213` |
| TB3 | `24.183378584747942` | `34.51135030864197` | `18.47231240354938` | `32.89957690329218` |
| TB4 | `17.635921103395063` | `28.016278935185184` | `12.977909834747942` | `23.152771347736625` |
| TB5 | `18.48948760609568` | `25.238513374485596` | `13.144793917181069` | `20.340931712962963` |
| TB6 | `19.411650913065845` | `24.390221193415638` | `13.710569621270576` | `22.76778034979424` |
| TB7 | `20.494666923868312` | `26.986793981481483` | `14.567937483924897` | `25.367307098765433` |
| S341 C3 bridge | `11.423722591949588` | `14.571005658436214` | n/a | n/a |

TB1 has the best mean target MAD, but TB6 has the best max target MAD. The S344
replacement gate is driven by both mean and max, with max target MAD being the
current hard limiter, so TB6 is the best native replacement baseline from this
sweep.

## Decision

Use TB6 as the current best native Mitsuba baseline. It moves max target MAD
from S347 SC4 `66.33893840020576` down to `24.390221193415638`, which is the
largest native-render improvement so far. It still does not beat the S335
contract max `18.040229552469135` or the S341 C3 bridge max
`14.571005658436214`.

## Next

Continue from TB6. The next pass should combine the calibrated TB6 background
with secondary/sprite tuning or a post-render bridge check, instead of going
back to the brighter S345/S347 native baselines.
