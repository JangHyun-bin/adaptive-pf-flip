# S453 Mitsuba Target Residual Decision

Generated UTC: `2026-06-20T14:30:00+00:00`

## Decision

Promote the S453 residual analyzer as the next calibration bridge. S452 showed that small hand-tuned response sweeps are close to saturated; S453 now measures the remaining positive target residual directly and emits a ranked local response request table for the next candidate.

Do not treat the residual output as a final render preset. It is a diagnostic feed: the next step should consume the request table and generate a target-driven local response candidate.

## Evidence

- Analyzer: `tools/analyze_mitsuba_target_residual.py`
- Residual report: `docs/reports/cinematic_larger_external_renderer_mitsuba_sw2_target_residual_s453.md`
- Residual summary: `build/shots/s453_mitsuba_sw2_target_residual/target_residual_analysis.json`
- Overlay GIF: `build/shots/s453_mitsuba_sw2_target_residual/residual_overlay.gif`
- Representative overlay: `build/shots/s453_mitsuba_sw2_target_residual/overlays/frame_0007.png`

## Results

| Metric | Value |
| --- | ---: |
| Frames analyzed | `8` |
| Requests emitted | `16` |
| Selected pixels | `42754` |
| Mean selected residual | `73.78343546802638` |
| Max residual | `169` |
| Overlay GIF bytes | `3007264` |

## Top Residual Request

| Field | Value |
| --- | --- |
| Frame | `7` |
| Output frame | `47` |
| BBox | `[302, 224, 623, 296]` |
| Weighted center px | `[442.0399803382632, 255.9590047483448]` |
| Screen radius px | `61.052508279449` |
| Area px | `11710` |
| Mean residual | `96.59530315969258` |
| Max residual | `168` |
| Suggested radiance scalar | `1.1364153312905008` |

## Interpretation

The strongest residual is not random sensor noise or a tiny isolated artifact. It is a broad upper water highlight band in the late frame, which matches the visual failure mode from S452: compact highlights remain under-powered compared with the target.

This makes the next step more concrete than another manual radiance/radius sweep. S454 should convert residual requests into local Mitsuba response geometry or material response controls, then render and score that candidate against SS1, GL3, and the S452 sweep leader.

## Next

Build an S454 target-driven response candidate that consumes `target_residual_analysis.json`, places local response controls from the ranked residual requests, and runs the existing validate/render/target-gap/gallery path.
