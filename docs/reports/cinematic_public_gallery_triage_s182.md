# S182 Public Gallery Triage

Date: 2026-06-19

## Status

Passed.

Reviewed the S181 public gallery and selected the next visible render target.

## Public Gallery

- URL: `https://message-kernel-pizza-increase.trycloudflare.com`
- Local URL: `http://127.0.0.1:8824`
- Publish report: `docs/reports/cinematic_gallery_publish_s181.md`
- S180 gate report: `docs/reports/cinematic_secondary_mist_debeading_s180.md`
- S180 comparison report:
  `docs/reports/cinematic_secondary_mist_debeading_comparison_s180.md`

Fresh HTTP checks:

- `https://message-kernel-pizza-increase.trycloudflare.com/index.html`: HTTP `200`, `5507` bytes
- `https://message-kernel-pizza-increase.trycloudflare.com/assets/shot.gif`: HTTP `200`, `24004938` bytes

## Keep/Tune Decision

Tune the S180 secondary de-beading further.

Evidence:

- Mean nonblank ratio remains `1.0`.
- Minimum contrast remains `185`.
- Mean luminance delta vs S177 is only `-0.38854730299962625`.
- Mean bright ratio delta vs S177 is only `0.000003315489969135839`.

Visual read:

- S180 is stable and keeps mist/foam visible.
- The direct secondary particles are smaller and cooler than S177, but several
  frames still read as many visible dot/sphere particles rather than continuous
  spray, foam, or mist.
- A pure material/radius preset is not enough; the renderer needs an explicit
  direct-secondary thinning control that does not remove the soft mist/streak
  passes.

## Selected Next Pass

S183: secondary direct visibility gating.

Target:

- Add a bounded renderer control for direct secondary spheres only.
- Keep soft spray/foam mist and streak passes active.
- Reduce bead-like direct secondary density with deterministic per-channel
  keep/dropout.
- Preserve S177 water-surface breakup and S180 material changes.

Implementation direction:

- Add `secondary_direct_pass` to the Blender bridge.
- Support per-channel keep ratios for `droplet`, `spray`, `foam`, and `bubble`.
- Apply it only in `add_secondary_particles`; do not affect
  `add_secondary_soft_pass` or `add_secondary_streak_pass`.
- Add a preset extending `dam_break_secondary_mist_debeading`.
- Compare S183 against S180 with `tools/compare_cinematic_frames.py`.

Acceptance:

- 8-frame probe and 36-frame warm-cache render pass.
- Nonblank ratio remains `1.0`; contrast no worse than S180.
- Bright/highlight ratios do not spike.
- Comparison diff is concentrated on direct secondary particles, not global
  exposure, camera, or water-surface strip regions.
