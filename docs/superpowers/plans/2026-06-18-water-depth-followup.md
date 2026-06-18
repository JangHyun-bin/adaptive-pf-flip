# Water Depth Followup

## Decision

Keep `dam_break_water_depth_focus_comparison` as the water-depth diagnostic crop.

## Rationale

S100 compared the S99 contact-region focus crop against a lower water-body crop. The lower crop shows the main water volume, rim cue, bottom attenuation, and late-frame depth band directly, while preserving the existing full-frame, temporal, ripple, secondary depth, and comparison gates.

The measured S100 focus crop is comfortably inside the diagnostic gate:

- frame count: `8`
- nonblank ratio min/mean/max: `1.0 / 1.0 / 1.0`
- contrast min/mean/max: `75.0 / 149.125 / 196.0`
- mean luminance min/mean/max: `74.5558 / 92.4267 / 116.9138`
- bright ratio mean: `0.0001196`

No additional crop or lighting retune is needed before the next rendering milestone.

## Result

S101 is a decision milestone only. It intentionally does not add a new render output.

## Next

S102 should add an opt-in water volume scattering or attenuation pass so the main water body reads less like a flat transparent slab, while preserving the S100 diagnostic gates.
