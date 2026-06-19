# S279 External Bundle Benchmark Gate

## Goal

Turn the S273/S277 external-bundle path into an enforceable readiness gate
before running larger-shot or benchmark work.

## Scope

- Add `tools/validate_external_bundle_benchmark_gate.py`.
- Validate the external render bundle schema, frame count, missing assets,
  monotonic source sampling, and minimum water mesh face count.
- Validate the S277 preview frame count, resolution, and occupancy gate.
- Validate the S278 publish manifest and live public `index.html`/`shot.gif`.
- Record current input footprint and projected larger-frame input sizes.
- Emit a JSON gate result under `build/` and a checked-in Markdown report.

## Validation

- Script compile:
  `python -m py_compile tools/validate_external_bundle_benchmark_gate.py`
- Gate run:
  `python tools/validate_external_bundle_benchmark_gate.py --bundle build/shots/s273_external_render_bundle/external_render_bundle.json --preview-summary build/shots/s277_external_bundle_motion_preview/preview/render_summary.json --publish-manifest build/shots/s278_external_bundle_motion_preview_publish/publish_manifest.json --out build/shots/s279_external_bundle_benchmark_gate/benchmark_gate.json --report docs/reports/cinematic_external_bundle_benchmark_gate_s279.md --check-public --timeout-seconds 30 --project-frames 64 --project-preview-frames 24 --next "Use S279 as the larger-shot readiness gate for the S273/S277 external-bundle path; next run a bounded larger-shot dry-run or benchmark only after this gate passes."`
- JSON validation:
  `python -m json.tool build/shots/s279_external_bundle_benchmark_gate/benchmark_gate.json`

## Result

- Gate schema: `lsfs_external_bundle_benchmark_gate`
- Status: `passed`
- Checks: `13`
- Failures: `0`
- Bundle frames: `32`
- Missing assets: `0`
- Quality labels: `normal_rough: 3`, `stable: 29`
- Current input footprint: `1.37 GB`
- Projected 64-frame input footprint: `2.74 GB`
- Projected 24-frame preview sample footprint: `1.03 GB`
- S277 preview minimum occupancy: `0.05804398148148148`
- Public preview URL: `https://concord-extensions-dial-conduct.trycloudflare.com`

## Decision

Use S279 as the larger-shot readiness gate for the external-bundle path. A
larger-shot or benchmark job should not consume S273/S277 unless this gate
passes.

## Next

Run a bounded larger-shot dry-run or benchmark using the S273/S277 path, with
S279 as the preflight gate.
