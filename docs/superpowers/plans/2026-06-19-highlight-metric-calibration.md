# S235 Highlight Metric Calibration

## Goal

Make highlight tuning decisions less dependent on a single hard-threshold
`highlight_ratio` metric.

## Scope

- Extend `tools/compare_cinematic_frames.py` with additive calibration metrics.
- Keep the existing `metric_deltas` fields unchanged.
- Generate calibration comparison summaries from existing S231/S232/S233/S234
  rendered frames.
- Document whether overlay-only highlight probes are being hidden by the legacy
  aggregate metric.

## Results

- Tool compile: passed.
- S231/S232/S234 16-frame calibration summaries: generated.
- S233 32-frame calibration summary: generated.
- S232 upper-tail luminance deltas: `luma_p99 +8.375`, `luma_p995 +9.8125`.
- S233 upper-tail luminance deltas: `luma_p99 +8.53125`, `luma_p995 +9.875`.
- Strict near-highlight/specular deltas remain flat or slightly negative.

## Decision

The legacy hard-threshold `highlight_ratio` is too coarse for the current visual
tuning loop. Upper-tail percentile metrics should be used alongside the existing
coverage, contrast, and direct secondary count gates.

## Next

Run S236 as a material/specular or contribution-mask pass. Avoid more broad
overlay density until the renderer can separate water/glint contribution or
push true specular highlights instead of just raising upper-tail luminance.
