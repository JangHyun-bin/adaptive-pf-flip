# S239 Highlight Contribution Diagnostics

## Goal

Make the accepted S238 highlight-material change inspectable as an image-space
upper-tail gain/loss mask before moving to the next visual pass.

## Scope

- Add `tools/highlight_contribution_diagnostics.py`.
- Compare existing S230 accepted foreground-volume frames against existing S238
  accepted highlight-material frames.
- Do not rerun simulation or Blender.
- Emit per-frame masks, a diagnostic sheet, JSON summary, and a Markdown report.

## Results

- Tool compile: passed.
- Frame pairs: `32`.
- Tail percentile: `0.95`.
- Minimum tail luminance: `80`.
- Gain/loss delta threshold: `4`.
- Mean active tail threshold: `91.4375`.
- Aggregate gain ratio: `0.031143391927083333`.
- Aggregate loss ratio: `0.0`.
- Net gain ratio: `0.031143391927083333`.
- Mean gain luma delta: `12.647490145835157`.
- Strongest gain luma delta: `25`.

## Decision

S239 confirms that the accepted S238 highlight response adds upper-tail luminance
without measurable upper-tail loss against S230. The mask sheet shows the gain
is concentrated in the water glint/reflection strip regions rather than broadly
lifting the whole frame.

## Next

Use S238 as the accepted water-highlight baseline. S240 should move to a
non-highlight visual pass, preferably water/foam readability or a targeted
contribution-mask renderer, instead of continuing broad highlight recovery.
