# S461 Mitsuba Signed Target Gap Decision

Generated UTC: `2026-06-20T15:20:00+00:00`

## Decision

Promote the signed target-gap analyzer as the S461 bridge from material/tone plateau to frame-aware response tuning.

The next render candidate should focus on bounded `highlight` brighten requests, especially late frames `47` and `40`. The `channel_band` region should not be globally brightened: its signed luma is negative, so it is already too bright relative to target in that source region.

## Evidence

- Analyzer: `tools/analyze_mitsuba_signed_target_gap.py`
- Analysis report: `docs/reports/cinematic_larger_external_renderer_mitsuba_mt8_signed_target_gap_s461.md`
- Analysis summary: `build/shots/s461_mitsuba_mt8_signed_target_gap/signed_target_gap_analysis.json`
- Gallery: `build/shots/s461_mitsuba_mt8_signed_target_gap/gallery/index.html`
- Visual GIF: `build/shots/s461_mitsuba_mt8_signed_target_gap/gallery/assets/signed_gap.gif`
- Base candidate: `build/shots/s460_mitsuba_material_tone_refine_sweep/mt8_secondary_light_target_gap/renderer_target_gap_summary.json`

## Region Findings

| Region | Coverage | Mean Abs Luma | Signed Luma | Positive Pixels | Positive Mean | Negative Pixels | Negative Mean Abs | Interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `all` | `1.000000` | `17.685456` | `5.040850` | `2316049` | `19.402234` | `1103111` | `23.098458` | Full-frame target remains slightly brighter on average, but this is too broad for direct response. |
| `highlight` | `0.003992` | `102.519436` | `102.507081` | `16546` | `102.568530` | `4` | `22.814100` | Main missing-light region; safe next target for localized brighten response. |
| `channel_band` | `0.000452` | `27.816061` | `-22.850127` | `218` | `18.806948` | `1346` | `34.777228` | Do not globally brighten; this region mostly needs dimming or exclusion. |

## Top Requests

| Rank | Output | Region | Direction | Score | Mean Abs | Max Abs | Area | BBox | Strength |
| ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| 1 | `47` | `highlight` | `brighten` | `5793.591` | `103.224` | `168.191` | `3578` | `[329, 229, 606, 257]` | `0.6072` |
| 2 | `40` | `highlight` | `brighten` | `5007.930` | `99.588` | `167.123` | `4131` | `[322, 226, 552, 275]` | `0.5858` |
| 3 | `47` | `highlight` | `brighten` | `4354.012` | `103.941` | `167.979` | `1993` | `[309, 260, 442, 291]` | `0.6114` |
| 4 | `47` | `highlight` | `brighten` | `2852.131` | `100.432` | `130.522` | `916` | `[302, 243, 391, 271]` | `0.5908` |
| 5 | `0` | `highlight` | `brighten` | `2530.639` | `131.791` | `158.374` | `393` | `[441, 139, 478, 159]` | `0.7752` |

## Interpretation

S460 proved that small scalar material/tone changes are saturated. S461 now shows why: the remaining visual miss is local and signed. The highlight-source mask has a strong positive target gap, while the channel-band mask has a negative signed gap. A single global brightness/material push would improve one region while hurting the other.

The S462 candidate should therefore consume the S461 signed request list and apply a bounded, frame-aware highlight response. It should start with the late-frame requests for outputs `47` and `40`, cap max luma delta, and re-run the target-gap comparison against `SS1_Native`, `S459_mt4_balanced`, and `S460_mt8_secondary_light`.

## Next

S462 should build a response candidate from `signed_target_gap_analysis.json`: apply only `highlight`/`brighten` requests, keep channel-band excluded from brightening, and require max absolute gap to stay at or below `177` before promotion.
