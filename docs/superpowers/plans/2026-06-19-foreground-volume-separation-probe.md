# S228 Foreground Volume Separation Probe

## Goal

Improve foreground water-body separation without changing secondary direct thinning or broad accepted-preset behavior.

## Scope

- Add `dam_break_foreground_volume_separation_probe`.
- Inherit from `dam_break_water_mesh_smoothing`.
- Adjust only bounded rim/volume/metadata emission controls.
- Compare against the accepted S224 16-frame baseline.

## Preset Changes

- Water rim strength: `0.72`.
- Water rim width: `0.26`.
- Metadata depth attenuation water emission: low depth `1.08`, high depth `0.72`.
- Water volume scattering: alpha `0.30`, emission `0.40`.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 2`, `stable: 14`.
- Stable ratio: `0.875`.
- Blocked labels: `0`.
- Direct secondary counts: match S224 accepted on all `16` frames.
- Mean luminance delta versus S224 accepted: `+0.6793684895833394`.
- Minimum contrast delta: `0.0`.
- Nonblank ratio delta: `0.0`.
- Mean bright ratio delta: `-6.510416666666654e-06`.
- Mean highlight ratio delta: `-3.2552083333333407e-06`.

## Decision

S228 is a promotion candidate, not yet the accepted preset. The visual read of the foreground water body improves, but the small bright/highlight ratio drop should be checked over the 32-frame S227 motion window before promotion.

## Next

Run S229 as a 32-frame foreground-volume motion review, then either fold S228 into `dam_break_water_mesh_smoothing` or keep it opt-in.
