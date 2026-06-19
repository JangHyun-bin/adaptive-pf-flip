# S280 External Bundle Preview Benchmark

## Goal

Run a bounded larger preview benchmark through the S273/S277 external-bundle
path after S279 preflight passes.

## Scope

- Add `tools/run_external_bundle_preview_benchmark.py`.
- Require an optional preflight gate before running the benchmark.
- Render preview frames from the external bundle.
- Assemble a GIF.
- Build a preview gallery.
- Record step timings, occupancy, GIF size, and gallery metadata in a JSON
  summary and checked-in Markdown report.

## Validation

- Script compile:
  `python -m py_compile tools/run_external_bundle_preview_benchmark.py`
- Benchmark run:
  `python tools/run_external_bundle_preview_benchmark.py --bundle build/shots/s273_external_render_bundle/external_render_bundle.json --preflight-gate build/shots/s279_external_bundle_benchmark_gate/benchmark_gate.json --out-dir build/shots/s280_external_bundle_preview_benchmark --frames 24 --width 1280 --height 720 --min-occupancy 0.01 --secondary-channel all --fps 8 --keyframes 8 --summary build/shots/s280_external_bundle_preview_benchmark/benchmark_summary.json --report docs/reports/cinematic_external_bundle_preview_benchmark_s280.md --next "Use S280 as the bounded larger preview benchmark for the external-bundle path; next publish the S280 gallery if this higher-resolution preview should replace S278."`
- JSON validation:
  `python -m json.tool build/shots/s280_external_bundle_preview_benchmark/benchmark_summary.json`
  `python -m json.tool build/shots/s280_external_bundle_preview_benchmark/preview/render_summary.json`
  `python -m json.tool build/shots/s280_external_bundle_preview_benchmark/gallery/gallery_manifest.json`
- Visual inspection:
  `build/shots/s280_external_bundle_preview_benchmark/gallery/assets/keyframe_07.png`

## Result

- Status: `passed`
- Frames: `24`
- Resolution: `1280 x 720`
- Minimum occupancy: `0.056202256944444445`
- Required minimum occupancy: `0.01`
- GIF size: `903.32 KB`
- Gallery assets: `9`
- Total elapsed: `70.72s`
- Render elapsed: `69.25s`
- GIF assembly elapsed: `1.28s`
- Gallery build elapsed: `0.20s`

## Decision

S280 passes as the bounded larger preview benchmark for the external-bundle
path. It is still a lightweight preview, not a photoreal render, but it proves
the S273/S277 pipeline can handle a higher-resolution motion review at modest
runtime.

## Next

Publish the S280 gallery if the 24-frame 1280 x 720 benchmark should replace
the S278 lightweight handoff endpoint.
