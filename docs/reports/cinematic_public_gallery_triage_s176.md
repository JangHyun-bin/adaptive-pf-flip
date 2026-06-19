# S176 Public Gallery Triage

Date: 2026-06-19

## Status

Passed.

Reviewed the S175 public gallery and selected the next visible render pass.

## Public Gallery

- URL: `https://yearly-whereas-generated-alfred.trycloudflare.com`
- Local URL: `http://127.0.0.1:8822`
- Publish report: `docs/reports/cinematic_gallery_publish_s175.md`
- Gallery report: `docs/reports/cinematic_metadata_depth_gallery_s175.md`
- Comparison report: `docs/reports/cinematic_metadata_depth_comparison_s174.md`

HTTP checks from the publish manifest:

- `https://yearly-whereas-generated-alfred.trycloudflare.com/index.html`: HTTP `200`, `5536` bytes
- `https://yearly-whereas-generated-alfred.trycloudflare.com/assets/shot.gif`: HTTP `200`, `23891985` bytes

## Evidence

S174 comparison showed the S173 metadata-depth pass moved in the intended
direction:

- Mean luminance delta: `-2.1279213686342615`
- Minimum contrast delta: `1.0`
- Mean bright ratio delta: `-0.0002721113040123457`
- Mean highlight ratio delta: `-0.000015944492669753106`
- Mean nonblank ratio delta: `0.0`

Visual read from the gallery:

- Water-surface readability and ripple cues survived the metadata attenuation.
- Late-frame secondary density is lower without disappearing.
- The remaining most visible non-photoreal cue is the long, nearly parallel
  horizontal glint/reflection strips across the water surface.
- Because S173 lowered secondary clutter, the regularity of these strips is now
  easier to notice.

## Selected Next Pass

S177: surface reflection/glint breakup.

Target:

- Reduce the uniform, ruler-straight ribbon read in `water_surface_glint_pass`
  and `water_reflection_pass`.
- Preserve the current depth attenuation and ripple readability.
- Use bounded jitter/taper/length variation rather than changing simulation.

Implementation direction:

- Add a renderer pass or preset option for per-strip breakup:
  - small deterministic frame/strip jitter,
  - length and width variation,
  - optional segmented/tapered strips,
  - lower alpha for far/deep metadata frames if sidecar data is present.
- Add preset `dam_break_surface_reflection_breakup` extending
  `dam_break_metadata_depth_attenuation`.
- Compare S177 against S173 using `tools/compare_cinematic_frames.py`.

Acceptance:

- 8-frame probe and 36-frame warm-cache render pass.
- Visual QA remains nonblank with contrast no worse than S173.
- Comparison shows reflection/glint changes concentrated on the water surface,
  not broad exposure or camera drift.
