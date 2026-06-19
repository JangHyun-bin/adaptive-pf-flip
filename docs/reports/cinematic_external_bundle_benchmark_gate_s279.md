# S279 External Bundle Benchmark Gate

Generated UTC: `2026-06-19T20:06:28.725728+00:00`
Gate JSON: `build/shots/s279_external_bundle_benchmark_gate/benchmark_gate.json`
Status: `passed`
Checks: `13`
Failures: `0`

## Bundle

- Bundle: `build/shots/s273_external_render_bundle/external_render_bundle.json`
- Accepted preset: `dam_break_water_mesh_smoothing`
- Frames: `32`
- Source window: `8..55`
- Missing assets: `0`
- Quality labels: `{'normal_rough': 3, 'stable': 29}`

## Input Footprint

- Camera JSON: `104.74 KB`
- Particle CSV: `1.28 GB`
- Phase-cell CSV: `33.66 MB`
- Water mesh OBJ: `53.39 MB`
- Total current input: `1.37 GB`
- Projected 64-frame input: `2.74 GB`
- Projected 24-frame preview sample input: `1.03 GB`

## Preview

- Preview: `build/shots/s277_external_bundle_motion_preview/preview/render_summary.json`
- Frames: `16`
- Resolution: `960 x 540`
- Min occupancy: `0.05804398148148148`
- Secondary pixels: `2252..4126`

## Publish

- Status: `running`
- Public URL: `https://concord-extensions-dial-conduct.trycloudflare.com`

## Checks

| Check | Status | Expected | Actual | Detail |
| --- | --- | --- | --- | --- |
| bundle_schema | `passed` | `lsfs_bridge_external_render_bundle` | `lsfs_bridge_external_render_bundle` | bundle schema |
| bundle_frame_count | `passed` | `32` | `32` | minimum bundle frame count |
| bundle_missing_assets | `passed` | `0` | `0` | missing asset count |
| bundle_sequence_monotonic | `passed` | `True` | `True` | sequence frame order is monotonic |
| bundle_water_mesh_faces | `passed` | `1000` | `17720` | minimum water mesh face count |
| preview_frame_count | `passed` | `16` | `16` | minimum preview frame count |
| preview_occupancy | `passed` | `0.01` | `0.05804398148148148` | minimum preview occupancy |
| preview_resolution_width | `passed` | `960` | `960` | minimum preview width |
| preview_resolution_height | `passed` | `540` | `540` | minimum preview height |
| publish_status | `passed` | `running` | `running` | publish status |
| publish_recorded_checks | `passed` | `0` | `0` | recorded publish checks are 2xx |
| public_index_live | `passed` | `2xx` | `200` | HTTP 200 |
| public_gif_live | `passed` | `2xx` | `200` | HTTP 200, 393813 bytes |

## Next

Use S279 as the larger-shot readiness gate for the S273/S277 external-bundle path; next run a bounded larger-shot dry-run or benchmark only after this gate passes.
