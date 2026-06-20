# S342 Mitsuba Depth-Aware Secondary Composite Validation

## Goal

Add a dedicated validation gate for the S341
`lsfs_mitsuba_depth_aware_secondary_composite` bridge before packaging or
publishing it as the current visual baseline.

## Scope

- Add `tools/validate_mitsuba_depth_aware_secondary_composite.py`.
- Validate the S341 C3 composite summary without regenerating the render
  frames.
- Check schema/version/status, source manifests, gallery files, required
  frame assets, composite hashes, target/contract MAD gates, output-frame
  ordering, and native-weight bounds.
- Keep the composite summary gallery metadata stable by marking its
  self-referential JSON entry with `hash_policy: self_referential_json`.

## Commands

```powershell
python tools\build_mitsuba_depth_aware_secondary_composite.py `
  build\shots\s338_mitsuba_secondary_mist_m1\actual_render\mitsuba_render.json `
  build\shots\s335_mitsuba_secondary_pass_contract\secondary_pass_contract.json `
  build\shots\s341_mitsuba_depth_aware_composite_c3 `
  --native-base-strength 0.14 `
  --secondary-native-strength 0.02 `
  --mask-blur-radius 2.5 `
  --mask-gain 1.35 `
  --max-target-mean-abs-diff 24 `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c3_s341.md `
  --title "S341 Mitsuba Depth-Aware Composite C3"
```

```powershell
python tools\validate_mitsuba_depth_aware_secondary_composite.py `
  build\shots\s341_mitsuba_depth_aware_composite_c3\depth_aware_secondary_composite_summary.json `
  --out build\shots\s342_mitsuba_depth_aware_composite_validation\validation.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_depth_aware_composite_validation_s342.md `
  --title "S342 Mitsuba Depth-Aware Composite Validation"
```

## Outputs

- Validator:
  `tools/validate_mitsuba_depth_aware_secondary_composite.py`
- Validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_validation_s342.md`
- Validation JSON:
  `build/shots/s342_mitsuba_depth_aware_composite_validation/validation.json`
- Validated composite:
  `build/shots/s341_mitsuba_depth_aware_composite_c3/depth_aware_secondary_composite_summary.json`

## Results

The validation run passed `129` checks with `0` failures and `0` skipped
checks. The validated C3 composite keeps the S341 bridge metrics unchanged:

- Mean target MAD: `11.423722591949588`
- Max target MAD: `14.571005658436214`
- Max contract MAD: `8.268018904320988`
- S335 contract max target MAD: `18.040229552469135`
- Mean native weight: `0.13702558967259743`

## Decision

S342 accepts S341 C3 as a validated depth-aware post-render bridge. The next
step should package or publish the C3 gallery for visual review, then continue
toward a renderer-native depth/secondary pass that can replace the post-render
bridge rather than only matching it.
