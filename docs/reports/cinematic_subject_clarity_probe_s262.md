# S262 Subject Clarity Probe

## Status

Passed as a 16-frame subject-clarity probe. Promote to S263 32-frame motion
review before acceptance.

This comparison uses existing rendered frame directories and bridge summaries only; no simulation was rerun.

## Artifacts

- Comparison sheet: `build\shots\s262_subject_clarity_probe\comparison_s260_16f\comparison_sheet.png`

## Metric Deltas

- Mean luminance: left `74.98091688368055`, right `74.41484944661458`, delta `-0.5660674370659677`
- Minimum contrast: left `153.0`, right `177.0`, delta `24.0`
- Mean bright ratio: left `0.00025010850694444446`, right `0.00021728515625`, delta `-3.282335069444445e-05`
- Mean highlight ratio: left `0.0001296657986111111`, right `0.000126953125`, delta `-2.7126736111111015e-06`
- Mean nonblank ratio: left `1.0`, right `1.0`, delta `0.0`

## Calibration Deltas

- Mean luma p95: left `97.0625`, right `94.5625`, delta `-2.5`
- Mean luma p99: left `112.3125`, right `107.375`, delta `-4.9375`
- Mean luma p99.5: left `118.1875`, right `111.9375`, delta `-6.25`
- Mean upper-mid ratio: left `0.00010091145833333333`, right `9.711371527777778e-05`, delta `-3.797743055555553e-06`
- Mean near-highlight ratio: left `5.208333333333334e-05`, right `5.154079861111111e-05`, delta `-5.425347222222257e-07`
- Mean specular ratio: left `2.2243923611111112e-05`, right `2.197265625e-05`, delta `-2.7126736111111286e-07`
- Mean frame contrast: left `206.0`, right `207.3125`, delta `1.3125`

## Metadata Attenuation

- Status: `active`
- Water alpha multiplier: `{'max': 1.28, 'min': 0.88}`
- Water emission multiplier: `{'max': 1.08, 'min': 0.72}`
- Secondary particle cap scale: `{'max': 1.0, 'min': 0.72}`

## Visual Finding

S262 tests lower glint/reflection clutter with slightly stronger water body volume/detail against the accepted S260 camera/look.

The surface-quality gate passed with `normal_rough: 2`, `stable: 14`, stable
ratio `0.875`, and blocked labels `0`. Effective glint count drops from `166`
to `137`, reflection count from `56` to `46`, and volume scatter alpha rises
from `0.3456` to `0.3672`.

Compared with the S260 16-frame reference, S262 keeps nonblank coverage
unchanged, raises minimum contrast by `24.0`, and reduces bright/highlight
ratios. The upper luma tail also drops (`luma_p99.5 -6.25`), so this is a
cleaner but calmer look that needs full-window review before promotion.

## Next

Run S263 as a 32-frame motion review for `dam_break_subject_clarity_probe`.
