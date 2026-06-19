# S243 Foam Readability Contribution Diagnostics

## Status

Passed.

This diagnostic uses existing rendered frame directories only; no simulation or Blender render was rerun.

## Artifacts

- Diagnostic sheet: `build\shots\s243_foam_readability_contribution_diagnostics\diagnostic_sheet.png`
- Summary JSON: `build\shots\s243_foam_readability_contribution_diagnostics\diagnostic_summary.json`
- Mask directory: `build\shots\s243_foam_readability_contribution_diagnostics\masks`

## Thresholds

- Tail percentile: `0.95`
- Minimum tail luminance: `80`
- Gain/loss delta threshold: `4`
- Mean active tail threshold: `91.9375`

## Aggregate

- Gain ratio: `0.00255615234375`
- Loss ratio: `0.0001691351996527778`
- Net gain ratio: `0.0023870171440972224`
- Mean gain luma delta: `12.237818422405875`
- Mean loss luma delta: `9.786910598893563`
- Strongest gain luma delta: `55`
- Strongest loss luma delta: `39`

## Visual Read

The diagnostic sheet concentrates the S242 gain in contact foam and ripple
speckles, most visibly through the middle of the accepted motion window. Loss is
present but small and scattered; the aggregate gain ratio is roughly fifteen
times the aggregate loss ratio.

This is consistent with the S242 acceptance comparison: the pass improves local
foam/ripple readability without broad exposure, coverage, contrast, or hard
highlight drift.

## Finding

S243 visualizes where the S242 accepted foam/readability tuning adds or loses upper-tail luminance against S238.

## Next

Move to water-body thickness/refraction next. Foam/readability is now accepted,
and the main water volume is the next largest visual gap.
