# S199 Water Mesh Component Metadata And Island Filter

## Goal

Turn S198's OBJ-level component finding into reconstruction metadata and an
explicit, opt-in island filtering path.

## Scope

- Keep default reconstruction geometry unchanged.
- Add component metadata to every reconstructed water mesh frame.
- Add an optional `--min-component-face-ratio` filter for explicit island
  pruning probes.
- Pass component options through `run_cinematic_shot.py`.
- Validate with a metadata-only probe and a filter probe.

## Result

S199 passed.

The default metadata path reproduced the S198 component warning:

- max component count: `2`
- minimum largest-component face ratio: `0.767793241`
- removed faces: `0`

The explicit filter probe with `--min-component-face-ratio 0.3` removed the
secondary island in the first probe frame:

- max component count: `1`
- minimum largest-component face ratio: `1`
- removed faces: `4672`

## Verification

- `python -m py_compile tools\reconstruct_water.py tools\run_cinematic_shot.py`
- `python tools\reconstruct_water.py --help`
- `python tools\run_cinematic_shot.py --help`
- Metadata-only reconstruction probe on S168 sequence
- Explicit island-filter reconstruction probe on S168 sequence
- `python tools\analyze_water_mesh_quality.py ...` on both probe outputs
- `git diff --check`

## Next

S200 should run a conservative visual island-filter probe and compare it against
S191. Start with a much lower threshold than `0.3`, because the second component
can be physically meaningful water, not just noise.
