# S436 Mitsuba Current Visual Decision Gallery

Generated UTC: `2026-06-20T12:38:39.823813+00:00`
Summary JSON: `build/reports/s436_mitsuba_current_visual_decision_gallery/gap_summary_gallery.json`
Gallery: `build/reports/s436_mitsuba_current_visual_decision_gallery/gallery/index.html`
Best candidate: `S401_CR21_Profile`
Best max gap MAD: `23.552905092592592`

## Scope

S436 refreshes the current-best visual decision bundle after S429-S435. The
candidate set intentionally includes the score leader, the best true-native
baseline, and the recent native renderer-side attempts that tried to explain or
replace the remaining residual response.

Included candidates:

- `S401_CR21_Profile`: current score leader and non-native response profile.
- `S409_SF12_H18`: strongest source-highlight variant.
- `SS1_Native`: best true-native baseline in the current renderer path.
- `S414_LR4_ChannelBand`: localized secondary material attenuation path.
- `S429_PhaseBillboardPB1`: phase-volume billboard proxy path.
- `S432_TetraSoftTS1`: soft tetra water mesh replacement path.
- `S433_SurfaceContactFoamSCF3`: surface-contact foam patch path.
- `S430_WaterTransmittanceWT1`: water transmittance sweep negative control.

## Ranking

| Rank | Candidate | Status | Frames | Mean Gap MAD | Max Gap MAD | Max Gap | GIF |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `S401_CR21_Profile` | `ready` | 8 | 18.657217962319958 | 23.552905092592592 | 182 | `build/reports/s436_mitsuba_current_visual_decision_gallery/gallery/assets/S401_CR21_Profile/shot.gif` |
| 2 | `S409_SF12_H18` | `ready` | 8 | 18.756908677340533 | 23.687431841563786 | 170 | `build/reports/s436_mitsuba_current_visual_decision_gallery/gallery/assets/S409_SF12_H18/shot.gif` |
| 3 | `SS1_Native` | `ready` | 8 | 19.146412117412552 | 23.951853137860084 | 170 | `build/reports/s436_mitsuba_current_visual_decision_gallery/gallery/assets/SS1_Native/shot.gif` |
| 4 | `S433_SurfaceContactFoamSCF3` | `ready` | 8 | 19.22623191550926 | 23.98888374485597 | 226 | `build/reports/s436_mitsuba_current_visual_decision_gallery/gallery/assets/S433_SurfaceContactFoamSCF3/shot.gif` |
| 5 | `S414_LR4_ChannelBand` | `ready` | 8 | 19.222742091049383 | 23.989165380658438 | 226 | `build/reports/s436_mitsuba_current_visual_decision_gallery/gallery/assets/S414_LR4_ChannelBand/shot.gif` |
| 6 | `S429_PhaseBillboardPB1` | `ready` | 8 | 19.302463027263375 | 24.143501157407407 | 230 | `build/reports/s436_mitsuba_current_visual_decision_gallery/gallery/assets/S429_PhaseBillboardPB1/shot.gif` |
| 7 | `S432_TetraSoftTS1` | `ready` | 8 | 19.427301633230453 | 24.167265303497942 | 227 | `build/reports/s436_mitsuba_current_visual_decision_gallery/gallery/assets/S432_TetraSoftTS1/shot.gif` |
| 8 | `S430_WaterTransmittanceWT1` | `ready` | 8 | 20.39433232060185 | 26.585197402263375 | 229 | `build/reports/s436_mitsuba_current_visual_decision_gallery/gallery/assets/S430_WaterTransmittanceWT1/shot.gif` |

## Next

S401 CR21 remains the score leader; SS1 remains the best true-native baseline. Recent native add-ons from S414 and S429-S433 did not beat SS1, so the next work should stop broad low-level patch sweeps and move to response decomposition or a higher-fidelity water/volume representation.

## Decision

The S429-S435 line closed the low-level native add-on path for now. Surface
contact foam, phase billboards, channel-band attenuation, water transmittance,
camera framing, and soft tetra replacement all produced measurable artifacts but
did not improve the score beyond `SS1_Native`, and none approached
`S401_CR21_Profile`.

The next useful step is not another broad parameter sweep over small renderer
patches. The next step should either:

- decompose the S401 residual into highlight, dark-primary, and channel-band
  masks and only port the parts that have a plausible physical/native cause; or
- move up a representation level with a better water volume/surface export that
  can change the primary water body instead of adding secondary overlays.
