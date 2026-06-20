# S584 Mitsuba Renderer Scene Depth Material Sweep

Generated UTC: `2026-06-20T22:16:59.791189+00:00`
Summary JSON: `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/depth_material_sweep_summary.json`
Gallery: `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/gallery/index.html`
Status: `ready`
Selected candidate: `strength_1_0`

## Candidates

| Candidate | Strength | Feasible | Max Delta | Max Mean | Coverage | GIF |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `strength_0_35` | 0.35 | `True` | 2 | 0.12574138374485597 | 0.18644483024691358 | `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/candidates/strength_0_35/depth_material_sweep.gif` |
| `strength_0_65` | 0.65 | `True` | 3 | 0.2585140174897119 | 0.2705073302469136 | `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/candidates/strength_0_65/depth_material_sweep.gif` |
| `strength_0_85` | 0.85 | `True` | 4 | 0.33654128086419755 | 0.29575810185185186 | `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/candidates/strength_0_85/depth_material_sweep.gif` |
| `strength_1_0` | 1.0 | `True` | 5 | 0.4139242541152263 | 0.3287885802469136 | `build/shots/s584_mitsuba_renderer_scene_depth_material_sweep/candidates/strength_1_0/depth_material_sweep.gif` |

## Selected

- Label: `strength_1_0`
- Base strength: `1.0`
- Max absolute delta: `5`
- Max mean absolute delta: `0.4139242541152263`
- Max changed coverage: `0.3287885802469136`

## Next

Use the selected S584 candidate as the bounded target for a native renderer-side depth/material implementation, then compare it against S577 and S582 before promotion.
