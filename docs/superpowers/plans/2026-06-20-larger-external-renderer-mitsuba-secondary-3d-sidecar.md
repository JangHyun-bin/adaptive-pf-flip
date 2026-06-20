# S353 Mitsuba Secondary 3D Sidecar

## Goal

Create a renderer-safe depth-aware 3D secondary-particle sidecar before trying
another native Mitsuba secondary replacement.

S351 and S352 showed that the current sampled sphere/halo/mist/billboard
secondary proxies do not close the native target gap. The next path needs a
first-class 3D secondary data layer with camera projection and validation.

## Scope

- Add `tools/build_mitsuba_secondary_3d_sidecar.py`.
- Add `tools/validate_mitsuba_secondary_3d_sidecar.py`.
- Consume the S308 renderer-neutral adapter manifest.
- Read per-frame `particle_stream` CSV assets.
- Emit per-frame JSONL sidecars containing secondary particle:
  - channel,
  - kind,
  - index,
  - phase,
  - position,
  - velocity,
  - speed,
  - volume,
  - age,
  - radius,
  - camera depth and normalized screen projection.
- Keep the first run to `8` representative frames.

## Command

```powershell
python tools\build_mitsuba_secondary_3d_sidecar.py `
  build\shots\s308_larger_external_renderer_generic_adapter\adapter_manifest.json `
  build\shots\s353_mitsuba_secondary_3d_sidecar `
  --frames 8 `
  --base-radius 0.095 `
  --camera-position 18,20,58 `
  --camera-target 18,8,14 `
  --camera-fov 34 `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_3d_sidecar_s353.md `
  --title "S353 Mitsuba Secondary 3D Sidecar"
```

Validation:

```powershell
python tools\validate_mitsuba_secondary_3d_sidecar.py `
  build\shots\s353_mitsuba_secondary_3d_sidecar\secondary_3d_sidecar.json `
  --out build\shots\s353_mitsuba_secondary_3d_sidecar_validation\validation.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_3d_sidecar_validation_s353.md `
  --title "S353 Mitsuba Secondary 3D Sidecar Validation"
```

## Outputs

- Sidecar report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_sidecar_s353.md`
- Validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_sidecar_validation_s353.md`
- Build artifact sidecar:
  `build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d_sidecar.json`
- Per-frame JSONL files:
  `build/shots/s353_mitsuba_secondary_3d_sidecar/secondary_3d/frame_####_secondary_3d.jsonl`

## Results

| Metric | Value |
| --- | ---: |
| Frames | `8` |
| Sidecar JSONL files | `8` |
| Secondary particles | `2877` |
| In-front particles | `2877` |
| In-frame particles | `2877` |
| Missing references | `0` |
| Sidecar bytes | `1.11 MB` |
| Validation failed checks | `0` |

Channel totals:

| Channel | Count | In frame |
| --- | ---: | ---: |
| spray | `2052` | `2052` |
| foam | `548` | `548` |
| bubble | `277` | `277` |
| droplet | `0` | `0` |

## Decision

Use this sidecar as the data contract for the next native Mitsuba secondary
attempt. This is not yet a renderer-quality improvement; it is the missing
data bridge that lets the next step replace sampled proxy-secondary behavior
with camera-aware 3D secondary records.

## Next

Implement a Mitsuba import/proxy pass that consumes
`lsfs_mitsuba_secondary_3d_sidecar`, emits native secondary geometry from the
sidecar records, and compares the result against S350 C1E and S335.
