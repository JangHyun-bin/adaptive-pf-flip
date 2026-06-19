# S247 Water Body Contribution Diagnostics

## Goal

Inspect where the accepted S246 water-body thickness/refraction tuning changes
upper-tail luminance against the S242 foam/readability baseline.

## Scope

- Reuse existing S242 and S246 accepted frame directories.
- Generate upper-tail gain/loss masks with
  `tools/highlight_contribution_diagnostics.py`.
- Use the result to decide whether the next pass should continue visual tuning
  or first improve external review/export artifacts.

## Results

- Frames: `32`
- Tail percentile: `0.95`
- Minimum tail luminance: `80`
- Gain/loss threshold: `4`
- Mean active tail threshold: `92.5`
- Gain ratio: `0.0022139485677083333`
- Loss ratio: `0.0017569986979166666`
- Net gain ratio: `0.00045694986979166665`
- Mean gain luma delta: `10.267281407078043`
- Mean loss luma delta: `9.951799090238987`
- Strongest gain luma delta: `174`
- Strongest loss luma delta: `173`

## Artifacts

- Report:
  `docs/reports/cinematic_water_body_contribution_diagnostics_s247.md`
- Diagnostic sheet:
  `build/shots/s247_water_body_contribution_diagnostics/diagnostic_sheet.png`
- Summary:
  `build/shots/s247_water_body_contribution_diagnostics/diagnostic_summary.json`
- Masks:
  `build/shots/s247_water_body_contribution_diagnostics/masks/`

## Decision

Keep S246 accepted. The water-body pass redistributes upper-tail energy more
than the foam/readability pass, but the net gain remains positive and the
accepted S246 comparison already preserved contrast, coverage, and `luma_p99.5`.
The mixed gain/loss pattern means future visual changes should be reviewed with
clearer external artifacts rather than relying only on local frame sheets.

## Next

Prioritize the render-export/review schema next, then return to secondary mist
readability with a stronger baseline for external inspection.
