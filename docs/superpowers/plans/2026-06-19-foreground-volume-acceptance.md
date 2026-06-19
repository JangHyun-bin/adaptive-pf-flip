# S230 Foreground Volume Acceptance

## Goal

Fold the S228/S229 foreground-volume separation settings into the accepted cinematic preset and verify parity against the probe.

## Scope

- Update `dam_break_water_mesh_smoothing`.
- Keep S228/S229 probe preset available for historical comparison.
- Render a 32-frame accepted-preset review over source indices `8..55`.
- Compare accepted output against S229 foreground-volume probe frames.

## Accepted Preset Changes

- Water rim strength: `0.72`.
- Water rim width: `0.26`.
- Metadata depth attenuation water emission: low depth `1.08`, high depth `0.72`.
- Water volume scattering: alpha `0.30`, emission `0.40`.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 3`, `stable: 29`.
- Stable ratio: `0.90625`.
- Blocked labels: `0`.
- Direct secondary counts: match S229 on all `32` frames.
- Mean luminance parity delta: `-1.2207031261368684e-06`.
- Minimum contrast delta: `0.0`.
- Bright ratio delta: `0.0`.
- Highlight ratio delta: `0.0`.
- Nonblank ratio delta: `0.0`.

## Decision

Keep the foreground-volume settings in the accepted `dam_break_water_mesh_smoothing` preset.

## Next

Start the next visual pass from S230 accepted. Practical candidates are highlight energy recovery, temporal glint polish, or a higher-resolution accepted gallery.
