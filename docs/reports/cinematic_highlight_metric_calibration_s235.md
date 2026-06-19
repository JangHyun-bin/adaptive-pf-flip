# S235 Highlight Metric Calibration

## Status

Passed.

S235 extends `tools/compare_cinematic_frames.py` with optional
`calibration_deltas` while preserving the existing `metric_deltas` summary. The
new fields are computed directly from rendered PNG pairs and do not require a
simulation or Blender rerun.

## Artifacts

- S231 calibration summary:
  `build/shots/s235_highlight_metric_calibration/s231_vs_s230eq/comparison_summary.json`
- S232 calibration summary:
  `build/shots/s235_highlight_metric_calibration/s232_vs_s230eq/comparison_summary.json`
- S234 calibration summary:
  `build/shots/s235_highlight_metric_calibration/s234_vs_s230eq/comparison_summary.json`
- S233 calibration summary:
  `build/shots/s235_highlight_metric_calibration/s233_vs_s230/comparison_summary.json`

## Added Metrics

- `luma_p95`, `luma_p99`, `luma_p995`
- `upper_mid_ratio` for luminance `>= 200`
- `near_highlight_ratio` for luminance `>= 235`
- `specular_ratio` for luminance `>= 250`
- pair-derived mean `contrast`

## Calibration Findings

| Case | Legacy highlight delta | Luma p99 delta | Luma p99.5 delta | Near-highlight delta | Specular delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| S231 16f | `0.0` | `+2.25` | `+2.5625` | `0.0` | `0.0` |
| S232 16f | `0.0` | `+8.375` | `+9.8125` | `0.0` | `0.0` |
| S234 16f | `0.0` | `+3.9375` | `+4.9375` | `0.0` | `0.0` |
| S233 32f | `-4.069010416666625e-07` | `+8.53125` | `+9.875` | `-1.3563368055555643e-07` | `-1.3563368055555643e-07` |

The older aggregate `highlight_ratio` is too thresholded to describe the visible
overlay changes: S232/S233 visibly recover upper-tail brightness, and the new
percentile metrics capture that. The strict near-highlight/specular ratios still
show no useful positive signal, which means the current strip overlays brighten
the high luma tail but rarely push additional pixels above the hard highlight
thresholds.

## Decision

Keep S232/S233 as opt-in visual probes and use the S235 calibration metrics for
future highlight tuning. Promotion should not depend only on legacy
`highlight_ratio`; it should require non-negative coverage/count gates plus a
positive upper-tail percentile signal and visual review.

## Next

S236 should either tune the actual water/glint material response or add a
water/overlay contribution mask. More overlay-only strip density is unlikely to
be the right lever now that the percentile metrics show upper-tail recovery but
hard-threshold ratios remain capped.
