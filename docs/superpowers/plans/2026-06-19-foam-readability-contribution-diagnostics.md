# S243 Foam Readability Contribution Diagnostics

## Goal

Verify that the accepted S242 foam/readability change adds visible energy in the
intended foam and ripple regions without creating a broad exposure shift.

## Scope

- Reuse existing S238 and S242 accepted frame directories.
- Generate upper-tail gain/loss masks with
  `tools/highlight_contribution_diagnostics.py`.
- Inspect aggregate gain/loss ratios and the diagnostic sheet.
- Use the result to choose the next visual pass.

## Results

- Frames: `32`
- Tail percentile: `0.95`
- Minimum tail luminance: `80`
- Gain/loss threshold: `4`
- Mean active tail threshold: `91.9375`
- Gain ratio: `0.00255615234375`
- Loss ratio: `0.0001691351996527778`
- Net gain ratio: `0.0023870171440972224`
- Mean gain luma delta: `12.237818422405875`
- Mean loss luma delta: `9.786910598893563`
- Strongest gain luma delta: `55`
- Strongest loss luma delta: `39`

## Artifacts

- Report:
  `docs/reports/cinematic_foam_readability_contribution_diagnostics_s243.md`
- Diagnostic sheet:
  `build/shots/s243_foam_readability_contribution_diagnostics/diagnostic_sheet.png`
- Summary:
  `build/shots/s243_foam_readability_contribution_diagnostics/diagnostic_summary.json`
- Masks:
  `build/shots/s243_foam_readability_contribution_diagnostics/masks/`

## Decision

S242 is a bounded readability improvement. The diagnostic sheet shows the gain
clustered around contact foam and ripple speckles, especially in the middle of
the motion window, while loss is much smaller and scattered. This supports
keeping S242 as the accepted baseline.

## Next

Move to the next non-highlight pass. The recommended next target is water-body
thickness/refraction because foam/readability is now accepted and the remaining
scene still lacks stronger depth cues in the main water volume.
