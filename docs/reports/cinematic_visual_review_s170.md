# S170 S168 Public Gallery Visual Triage

Generated UTC: `2026-06-19T06:04:00Z`

## Summary

- Public gallery: `https://vendor-continuing-substantial-giving.trycloudflare.com`
- Local gallery: `http://127.0.0.1:8821`
- Reviewed shot: `dam_break_water_depth_foreground_separation`
- Baseline comparison: S165 `dam_break_source_slab_deemphasis`
- Selected next milestone: S171 render-data and depth export milestone.

## Publish Evidence

S169 publish checks passed:

| Target | Status | Bytes |
| --- | ---: | ---: |
| `http://127.0.0.1:8821/` | 200 | 8161 |
| `http://127.0.0.1:8821/assets/shot.gif` | 200 | 24468261 |
| `https://vendor-continuing-substantial-giving.trycloudflare.com/` | 200 | 8161 |
| `https://vendor-continuing-substantial-giving.trycloudflare.com/assets/shot.gif` | 200 | 24468261 |

## Gate Evidence

S168 full gate passed:

| Metric | Value |
| --- | ---: |
| Frames | 36 |
| Grid | `36 x 44 x 28` |
| Visual mean luminance | 86.9082305832851 |
| Visual mean bright ratio | 0.0012959044656635802 |
| Visual min contrast | 184.0 |
| Temporal highlight max peak delta | 159 |
| Camera min target distance | 26.10153252205701 |
| Secondary mean inside ratio | 0.9185529911257326 |
| Secondary mean depth span | 13.85923744136715 |
| Ripple mean edge value | 28.55730614920156 |

All visual, temporal, focus, secondary-depth, secondary-framing,
ripple-readability, and camera-stability gates passed.

## Visual Findings

- S168 gives a modestly deeper foreground and midground read than S165, and it
  keeps the S165 source-slab improvement intact.
- The improvement is real but small. The current renderer-side knobs are now
  producing diminishing returns compared with the time cost of full cinematic
  gates.
- The remaining visible limitations are not one preset away:
  - coarse sparse phase-cell mesh thickness still creates broad sheet-like water
    forms,
  - the late-frame upper water band still exists,
  - depth/volume/secondary information is still flattened into a single Blender
    bridge representation.
- More glint/reflection tuning risks trading one artifact for another: line-heavy
  highlights can pass QA while still reading as artificial surface strokes.

## Decision

Proceed with S171: render-data and depth export milestone.

The next pass should improve the data contract before further look-dev:

- Export richer per-frame water volume/depth metadata alongside the current mesh
  and secondary channels.
- Preserve existing gallery/report flows.
- Add a validation/inspection report that proves the new data exists and can be
  consumed by later render passes.
- Keep S168 as the current published visual baseline.
