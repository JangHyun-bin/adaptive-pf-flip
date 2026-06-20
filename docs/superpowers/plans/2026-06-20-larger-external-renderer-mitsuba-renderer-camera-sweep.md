# S366 Mitsuba Renderer Camera Sweep

## Goal

After S364/S365 ruled out broad post-grade and background-only tuning, test
whether small renderer-facing camera/framing changes improve the SV1-cache path.

Because camera changes alter screen projection, this pass regenerates the SV1
visibility profile for each camera candidate instead of reusing the S360 RGBA
cache directly.

## Candidates

- Baseline: `SV1-cache` from S362.
- `CF1`: camera target lowered to `18,7.2,14`, FOV `34`.
- `CF2`: camera target stays `18,8,14`, FOV narrowed to `32`.

## Result

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_renderer_camera_sweep_summary_s366.md`
- Visual review:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_renderer_camera_review_s366.md`
- Public quick-tunnel preview:
  `https://dare-sell-aquarium-third.trycloudflare.com/index.html`

| Candidate | Mean Target MAD | Max Target MAD | Decision |
| --- | ---: | ---: | --- |
| `SV1-cache` | `19.103672839506174` | `23.72217142489712` | keep baseline |
| `CF2` | `19.448651379243827` | `24.04738297325103` | close, reject |
| `CF1` | `19.653690441743827` | `24.0534754372428` | close, reject |

The visual review confirms the metric result: camera-only changes adjust scale
and projected secondary mass slightly, but they do not solve the remaining
target/C1E look gap.

## Next

Stop camera-only tuning. Move to material/secondary integration: keep the
S357/S362 camera/background baseline and improve how the water/material response
and secondary visibility integrate in the renderer-facing path.
