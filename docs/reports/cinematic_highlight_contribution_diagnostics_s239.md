# S239 Highlight Contribution Diagnostics

## Status

Passed.

This diagnostic uses existing rendered frame directories only; no simulation or Blender render was rerun.

## Artifacts

- Diagnostic sheet: `build\shots\s239_highlight_contribution_diagnostics\diagnostic_sheet.png`
- Summary JSON: `build\shots\s239_highlight_contribution_diagnostics\diagnostic_summary.json`
- Mask directory: `build\shots\s239_highlight_contribution_diagnostics\masks`

## Thresholds

- Tail percentile: `0.95`
- Minimum tail luminance: `80`
- Gain/loss delta threshold: `4`
- Mean active tail threshold: `91.4375`

## Aggregate

- Gain ratio: `0.031143391927083333`
- Loss ratio: `0.0`
- Net gain ratio: `0.031143391927083333`
- Mean gain luma delta: `12.647490145835157`
- Mean loss luma delta: `None`
- Strongest gain luma delta: `25`
- Strongest loss luma delta: `0`

## Finding

S239 visualizes where the S238 accepted highlight-material response adds or loses upper-tail luminance against S230.

## Decision

Keep the S238 accepted highlight-material response. The diagnostic finds `0.031143391927083333` aggregate upper-tail gain ratio and `0.0` aggregate loss ratio, with gain concentrated in glint/reflection strip regions.

## Next

Move to a non-highlight visual pass next. S240 should target water/foam readability or renderer contribution masks rather than more broad highlight recovery.
