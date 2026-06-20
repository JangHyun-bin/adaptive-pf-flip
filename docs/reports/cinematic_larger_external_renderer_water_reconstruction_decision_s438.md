# S438 Water Reconstruction Decision

Generated UTC: `2026-06-20T12:45:02+00:00`

## Scope

S438 compares the baseline water reconstruction used by the larger cinematic
shot against the S432 tetra-soft replacement. The goal is to decide whether the
next renderer step should be another smoothing/mesh-quality pass, or a different
primary-water representation diagnostic.

## Inputs

- Baseline quality report:
  `docs/reports/cinematic_larger_external_renderer_water_mesh_quality_s168_s438.md`
- Tetra-soft quality report:
  `docs/reports/cinematic_larger_external_renderer_water_mesh_quality_tetra_soft_s438.md`
- Tetra-soft render sweep:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_tetra_soft_sweep_summary_s432.md`
- S437 response decomposition:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_s401_response_decomposition_s437.md`

## Quality Comparison

| Metric | Baseline S168 | Tetra Soft S432 | Direction |
| --- | ---: | ---: | --- |
| Mean mesh risk score | 0.129409 | 0.101895 | better |
| Max mesh risk score | 0.178073 | 0.136406 | better |
| Mean sharp edge ratio | 0.008197 | 0.005849 | better |
| Mean normal discontinuity p95 | 0.071188 | 0.061880 | better |
| Mean face area CV | 0.600144 | 0.411145 | better |
| Mean largest component ratio | 0.968502 | 0.968060 | no meaningful change |
| Single dominant component gate | false | false | still failing |

## Render Result

Tetra-soft did improve mesh smoothness diagnostics, but it did not improve the
visual target gap:

- `SS1_Native`: max-gap MAD `23.951853137860084`
- `S432_TetraSoftTS1`: max-gap MAD `24.167265303497942`
- `S401_CR21_Profile`: max-gap MAD `23.552905092592592`

This means the current visual miss is not primarily solved by smoother tetra
surface reconstruction. The remaining issue is more likely screen-visible water
body placement, component/silhouette contribution, or volume/depth response.

## Decision

Do not spend the next step on another small smoothing sweep. The next useful
step should inspect water-body visibility in screen space:

- component visibility and largest-component contribution per frame;
- projected silhouette/depth overlap against the current gap frames;
- whether the secondary small component in early frames is visually important or
  just topology noise;
- whether a higher-level volume/surface export should preserve thickness and
  foreground separation instead of only improving triangle smoothness.

## Next

S439 should build a water component visibility and silhouette/depth diagnostic
bundle for the baseline and tetra-soft reconstructions before another Mitsuba
replacement render.
