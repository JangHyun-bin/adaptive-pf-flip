# Larger External Renderer: Mitsuba Residual-Filtered Sidecar

Status: complete

## Goal

Move residual evidence off the camera-facing screen-card path and into the
native 3D secondary sidecar path.

## Scope

- Add `tools/filter_mitsuba_secondary_sidecar_by_mask.py`.
- Read a source `lsfs_mitsuba_secondary_3d_sidecar`.
- Read a mask-source compatible summary with per-frame `layer_repo_path`.
- Keep only sidecar particles whose projected NDC position lands inside the
  residual alpha mask.
- Validate the filtered sidecar and export/render a native Mitsuba candidate
  using S357 SS1 settings with only the sidecar replaced.

## Validation

- `python -m py_compile tools\filter_mitsuba_secondary_sidecar_by_mask.py`
- Filtered sidecar: `ready`, `8` frames, `865 / 2877` particles retained
- Sidecar validation: `passed`, `0` failed checks
- Mitsuba export: `ready`, `8` frames, `0` failures
- Mitsuba render: `ready`, `8` frames, `0` render failures
- Target-gap and C1E-gap comparison

## Result

The filter is useful evidence plumbing, but filtering out non-residual
secondary particles is not a good replacement for SS1.

- Retention ratio: `0.30066041014946127`
- S398 max target MAD: `23.988987911522635`
- S398 mean target MAD: `19.222541875643003`
- SS1 max target MAD: `23.951853137860084`
- SS1 mean target MAD: `19.146412117412552`

## Decision

Keep the sidecar filtering tool. Do not use a filtered-only sidecar as the next
visual baseline because it removes the broad secondary contribution that SS1 was
already preserving.

## Next

Use the filtered set as a boost layer, not a replacement layer: preserve the
full SS1 sidecar and add boosted/duplicated residual particles or a separate
residual material pass.
