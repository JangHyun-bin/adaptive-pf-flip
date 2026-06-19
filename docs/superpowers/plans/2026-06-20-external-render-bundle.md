# S273 Accepted External Render Bundle

## Goal

Turn the accepted S269/S271 handoff baseline into a frame-level input manifest
for external renderer prototypes and larger-shot reruns.

## Scope

- Add `tools/build_bridge_external_render_bundle.py`.
- Read `lsfs_bridge_cinematic_handoff_manifest`.
- Resolve the accepted sequence and render-data summary from the handoff
  sources.
- Reuse the bridge renderer's source-window resampling rule.
- Emit one bundle frame per accepted output frame with camera, particles,
  phase-cell, water-mesh, surface-quality, and render-data references.
- Default to `size_only` frame asset fingerprints to avoid hashing multi-GB
  particle CSV input on every run; expose `--hash-frame-files` for stronger
  validation when needed.

## Validation

- Script compile:
  `python -m py_compile tools/build_bridge_external_render_bundle.py`
- Bundle generation:
  `python tools/build_bridge_external_render_bundle.py --handoff-manifest build/shots/s271_accepted_handoff/handoff_manifest.json --out build/shots/s273_external_render_bundle/external_render_bundle.json --report docs/reports/cinematic_external_render_bundle_s273.md --title "S273 Accepted External Render Bundle" --next "Use this bundle as the frame-level accepted input list for external renderer prototypes and larger-shot reruns."`
- JSON validation:
  `python -m json.tool build/shots/s273_external_render_bundle/external_render_bundle.json`

## Result

- Bundle schema: `lsfs_bridge_external_render_bundle`
- Version: `1`
- Frame count: `32`
- Source window: `8..55`
- Asset hash mode: `size_only`
- Missing assets: `0`
- Particle CSV input: `1.28 GB`
- Phase-cell CSV input: `33.66 MB`
- Water mesh OBJ input: `53.39 MB`
- Sampled sequence frames: first `8`, middle `32`, last `55`

## Decision

Use S273 as the accepted frame-level external-render input list. It gives the
next renderer or larger-shot runner a deterministic source mapping without
requiring it to understand the bridge renderer internals.

## Next

Use the S273 bundle to drive an external renderer prototype, larger-shot dry
run, or large-scale benchmark input-size gate.
