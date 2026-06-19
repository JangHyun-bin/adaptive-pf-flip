# S247 Water Body Contribution Diagnostics

## Status

Passed.

This diagnostic uses existing rendered frame directories only; no simulation or Blender render was rerun.

## Artifacts

- Diagnostic sheet: `build\shots\s247_water_body_contribution_diagnostics\diagnostic_sheet.png`
- Summary JSON: `build\shots\s247_water_body_contribution_diagnostics\diagnostic_summary.json`
- Mask directory: `build\shots\s247_water_body_contribution_diagnostics\masks`

## Thresholds

- Tail percentile: `0.95`
- Minimum tail luminance: `80`
- Gain/loss delta threshold: `4`
- Mean active tail threshold: `92.5`

## Aggregate

- Gain ratio: `0.0022139485677083333`
- Loss ratio: `0.0017569986979166666`
- Net gain ratio: `0.00045694986979166665`
- Mean gain luma delta: `10.267281407078043`
- Mean loss luma delta: `9.951799090238987`
- Strongest gain luma delta: `174`
- Strongest loss luma delta: `173`

## Visual Read

Unlike the foam/readability diagnostic, the water-body pass produces a mixed
upper-tail redistribution. Gain and loss both appear across the water surface,
which is expected for a material/scattering change rather than a localized
overlay-density change. The net ratio remains positive, and the S246 acceptance
comparison preserves contrast, coverage, and `luma_p99.5`.

This does not invalidate S246, but it does raise the value of better external
review artifacts before starting another subtle visual pass.

## Finding

S247 visualizes where the S246 accepted water-body thickness tuning adds or loses upper-tail luminance against S242.

## Next

Prioritize the render-export/review schema next, then return to secondary mist
readability with clearer external inspection artifacts.
