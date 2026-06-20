# Larger External Renderer: Mitsuba Residual-Augmented Sidecar

Status: complete

## Goal

Test the next sidecar strategy after S398: preserve the full SS1 secondary 3D
sidecar and add boosted duplicates only for residual-mask-selected particles.

## Scope

- Extend `tools/filter_mitsuba_secondary_sidecar_by_mask.py` with `--mode augment`.
- Preserve the original sidecar rows in augment mode.
- Duplicate residual-mask-selected rows with configurable radius scaling.
- Build RA1 with radius scale `1.7` and `1` duplicate per selected particle.
- Export/render RA1 with S357 SS1 settings, using a larger proxy limit so the
  augmented rows are not sampled away.

## Validation

- `python -m py_compile tools\filter_mitsuba_secondary_sidecar_by_mask.py`
- RA1 sidecar: `ready`, `8` frames, `3742` output particles
- RA1 validation: `passed`, `0` failed checks
- RA1 Mitsuba export: `ready`, `8` frames, `0` failures
- RA1 Mitsuba render: `ready`, `8` frames, `0` render failures
- RA1 target-gap and C1E-gap comparison

## Result

Augment mode works, but a simple residual particle radius boost is still not a
metric improvement.

- Mask-selected particles: `865 / 2877`
- Output particles: `3742`
- Output/source ratio: `1.3006604101494612`
- RA1 max target MAD: `23.98904320987654`
- RA1 mean target MAD: `19.22306568287037`
- SS1 max target MAD: `23.951853137860084`
- SS1 mean target MAD: `19.146412117412552`

## Decision

Keep augment mode as useful sidecar tooling. Do not continue tuning only sidecar
particle count/radius for this CR21 replacement problem.

## Next

Shift the renderer work toward BSDF/lighting/surface representation. The recent
screen-card, filtered-sidecar, and augmented-sidecar tests all fail in the same
metric band, which points away from quantity/radius controls and toward material
response, water surface transport, and target-free perceptual gates.
