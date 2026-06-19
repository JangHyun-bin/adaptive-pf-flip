# S167 S165 Public Gallery Visual Triage

Generated UTC: `2026-06-19T05:12:00Z`

## Summary

- Public gallery: `https://england-susan-dos-swimming.trycloudflare.com`
- Local gallery: `http://127.0.0.1:8820`
- Reviewed shot: `dam_break_source_slab_deemphasis`
- Baseline comparison: S162 `dam_break_establishing_scale_composition`
- Selected next milestone: S168 water depth and foreground separation pass.

## Publish Evidence

S166 publish checks passed:

| Target | Status | Bytes |
| --- | ---: | ---: |
| `http://127.0.0.1:8820/` | 200 | 8150 |
| `http://127.0.0.1:8820/assets/shot.gif` | 200 | 25819124 |
| `https://england-susan-dos-swimming.trycloudflare.com/` | 200 | 8150 |
| `https://england-susan-dos-swimming.trycloudflare.com/assets/shot.gif` | 200 | 25819124 |

## Gate Evidence

S165 full gate passed:

| Metric | Value |
| --- | ---: |
| Frames | 36 |
| Grid | `36 x 44 x 28` |
| Visual mean luminance | 89.45182385103202 |
| Visual mean bright ratio | 0.002005901572145062 |
| Visual min contrast | 186.0 |
| Temporal highlight max peak delta | 138 |
| Camera min target distance | 26.10153252205701 |
| Secondary mean inside ratio | 0.9185529911257326 |
| Secondary mean depth span | 13.85923744136715 |
| Ripple mean edge value | 34.58111849221724 |

All visual, temporal, focus, secondary-depth, secondary-framing,
ripple-readability, and camera-stability gates passed.

## Visual Findings

- S165 clearly reduces the dominant ceiling-like source slab visible in S162.
  The source is now cropped/lowered enough that the first read is the impact
  pool, falling spray/foam, and broad water surface rather than a top slab.
- A thin upper water band remains in late frames. This is still visible, but it
  is no longer the dominant blocker.
- The stronger glint/reflection pass restores visual QA brightness without
  triggering temporal highlight or ripple highlight limits.
- The current larger remaining artifact is depth readability: foreground,
  midground, and background water often merge into one flat blue sheet. This
  limits the shot's cinematic scale more than the residual source band.

## Decision

Proceed with S168: water depth and foreground separation pass.

The next pass should tune render-side depth cues before changing the source
shape again:

- Strengthen foreground/midground separation with a bounded depth/tint pass.
- Keep S165 source scene, source window, camera, grid, and secondary settings.
- Preserve S165 QA gates and compare against S165 review artifacts.
- Avoid another source-window crop unless the depth pass exposes a stronger
  late-frame upper-band issue.
