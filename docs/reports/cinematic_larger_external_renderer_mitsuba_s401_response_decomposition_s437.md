# S437 Mitsuba S401 Response Decomposition

Generated UTC: `2026-06-20T12:42:31.477998+00:00`
Summary JSON: `build/reports/s437_mitsuba_s401_response_decomposition/response_decomposition_summary.json`
Status: `ready`

## Score Context

- `S401_CR21_Profile` rank `1` max-gap MAD `23.552905092592592`
- `SS1_Native` rank `3` max-gap MAD `23.951853137860084`
- `S433_SurfaceContactFoamSCF3` rank `4` max-gap MAD `23.98888374485597`
- `S414_LR4_ChannelBand` rank `5` max-gap MAD `23.989165380658438`

## Decomposition

| Region | Mask Kind | Mean Coverage | Top Channel | Precision | Recall | F1 | Decision |
| --- | --- | ---: | --- | ---: | ---: | ---: | --- |
| `S401_CR21_highlight` | `highlight` | 0.003991849922839506 | `spray_density_ge_8` | 0.004530027110469938 | 0.03926306251887647 | 0.008122867747216355 | `keep-as-light-or-response-reference` |
| `S401_CR21_dark_primary` | `dark-secondary-primary` | 0.001956741898148148 | `spray_density_ge_32` | 0.043784227331918155 | 0.6049291435613062 | 0.08165811382898205 | `representation-needed` |
| `S401_CR21_channel_band` | `channel-band` | 0.0004523533950617284 | `foam_or_bubble` | 0.019573244453158188 | 0.6385927505330491 | 0.03798230874100377 | `representation-needed` |

## Decisions

### S401_CR21_highlight

- Decision: `keep-as-light-or-response-reference`
- Native cause: `not explained by secondary channels`
- Reason: Highlight mask coverage is 0.003992, but best secondary overlap F1 is only 0.008123.

### S401_CR21_dark_primary

- Decision: `representation-needed`
- Native cause: `not explained by current secondary/material channels`
- Reason: Best channel `spray_density_ge_32` has weak F1 0.081658; another low-level overlay is unlikely to close this response.

### S401_CR21_channel_band

- Decision: `representation-needed`
- Native cause: `not explained by current secondary/material channels`
- Reason: Best channel `foam_or_bubble` has weak F1 0.037982; another low-level overlay is unlikely to close this response.

## Overall

S401 CR21 should remain an upper-bound response reference for now; its decomposed masks do not clear secondary-channel portability gates.
Weak or nonsecondary regions: `S401_CR21_highlight`, `S401_CR21_dark_primary`, `S401_CR21_channel_band`.
Portable regions: `none`.
The next implementation path should change the primary water surface/volume or isolate a physical highlight/light response, not add more broad secondary overlays.

## Next

Do not port S401 CR21 wholesale. Use it as an upper-bound reference, then either build a physical highlight/light-response probe or move to a higher-fidelity primary water surface/volume export.
