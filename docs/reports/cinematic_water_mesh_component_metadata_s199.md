# S199 Water Mesh Component Metadata And Island Filter

## Status

Passed.

## Implementation

- `tools/reconstruct_water.py`
  - Adds per-frame water mesh component metadata:
    `component_count`, `largest_component_face_ratio`,
    `largest_component_vertex_ratio`, top component face/vertex ratios, and
    pre-filter component ratios.
  - Adds `--component-detail-limit`.
  - Adds optional `--min-component-face-ratio`; default `0.0` preserves existing
    geometry and only records metadata.
  - Includes component options in the reconstruction fingerprint.
- `tools/run_cinematic_shot.py`
  - Passes component options through to `reconstruct_water.py`.
  - Reports max component count, minimum largest-component ratio, and removed
    face count in shot reports.

## Validation

Metadata-only probe:

```powershell
python tools\reconstruct_water.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\shots\s199_component_metadata_probe --frames 4 --threshold 0.02 --surface-mode tetra --implicit-iso 0.45 --implicit-blur-iterations 0 --smooth-iterations 0 --smooth-alpha 0.18 --write-normals --component-detail-limit 4
```

Result:

- `component_count_max=2`
- `largest_component_face_ratio_min=0.767793241`
- `component_filter_removed_faces=0`
- Quality analyzer status: `warning`

Filter probe:

```powershell
python tools\reconstruct_water.py build\shots\s168_water_depth_foreground_separation\converted\sequence.json build\shots\s199_component_filter_probe --frames 4 --threshold 0.02 --surface-mode tetra --implicit-iso 0.45 --implicit-blur-iterations 0 --smooth-iterations 0 --smooth-alpha 0.18 --write-normals --component-detail-limit 4 --min-component-face-ratio 0.3
```

Result:

- `component_count_max=1`
- `largest_component_face_ratio_min=1`
- `component_filter_removed_faces=4672`
- Quality analyzer status: `ok`

## Findings

The S198 warning is reproducible through the new reconstruction metadata. In
the first probe frame, the water mesh has two closed components:

- component 1: `15448` faces, ratio `0.7677932405566601`
- component 2: `4672` faces, ratio `0.23220675944333996`

The optional filter removes the smaller component when the threshold is `0.3`.
This proves the component/island path works, but `0.3` is intentionally too high
for production. The next render candidate should use a conservative threshold
or first expose component labels visually.

## Next

S200 should run a small visual probe with a conservative island threshold, then
compare it against S191. Do not replace the baseline until a gallery confirms
that removing or labeling islands improves water-body readability without
deleting physically meaningful separated water masses.
