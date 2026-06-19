# S179 Public Gallery Triage

Date: 2026-06-19

## Status

Passed.

Reviewed the S178 public gallery and selected the next visible render target.

## Public Gallery

- URL: `https://alloy-mailman-right-gay.trycloudflare.com`
- Local URL: `http://127.0.0.1:8823`
- Publish report: `docs/reports/cinematic_gallery_publish_s178.md`
- S177 gate report: `docs/reports/cinematic_surface_reflection_breakup_s177.md`
- S177 comparison report:
  `docs/reports/cinematic_surface_reflection_breakup_comparison_s177.md`

HTTP checks from the publish manifest:

- `https://alloy-mailman-right-gay.trycloudflare.com/index.html`: HTTP `200`, `5514` bytes
- `https://alloy-mailman-right-gay.trycloudflare.com/assets/shot.gif`: HTTP `200`, `24084190` bytes

## Keep/Tune Decision

Keep the S177 strip breakup bounds for now.

Evidence:

- Mean bright ratio delta vs S173: `-0.0007917691454475309`
- Minimum contrast delta vs S173: `0.0`
- Mean nonblank ratio delta vs S173: `0.0`
- The comparison diff is concentrated on the water-surface strip regions, which
  matches the S177 target.

Remaining issue:

- The long uniform ribbon read is reduced, but secondary particles still read
  too much like tan/gold beads suspended over the water instead of mist, foam,
  bubbles, and spray.
- Once the surface strips are less dominant, the secondary material/shape issue
  becomes the next most visible non-photoreal cue.

## Selected Next Pass

S180: secondary material and de-beading pass.

Target:

- Reduce amber/bead-like direct secondary particles.
- Make spray/foam read softer and more mist-like.
- Preserve secondary visibility and S173/S177 water-depth improvements.

Implementation direction:

- Add a preset extending `dam_break_surface_reflection_breakup`.
- Lower direct bubble/droplet alpha and radius scales.
- Shift spray/foam material toward cooler white/blue mist.
- Increase soft pass contribution slightly while keeping late-frame cap
  attenuation active.
- Compare S180 against S177 with `tools/compare_cinematic_frames.py`.

Acceptance:

- 8-frame probe and 36-frame warm-cache render pass.
- Nonblank ratio remains `1.0`; contrast no worse than S177.
- Bright/highlight ratios do not spike.
- Comparison diff is concentrated in secondary particles and mist, not camera
  or global exposure.
