# S336 Mitsuba Secondary Pass Contract Validation

## Goal

Add a repeatable validation gate for the S335 Mitsuba secondary-pass contract.
The validator should prove that the contract's source hashes, review artifacts,
frame assets, frame mapping, secondary-pass semantics, and overlay-diff gates
still match the checked contract before the next renderer-native secondary pass
uses it as a target.

## Scope

- Add `tools/validate_mitsuba_secondary_pass_contract.py`.
- Validate `lsfs_mitsuba_secondary_pass_contract` schema/version/status.
- Validate source JSON files and schemas when a schema is recorded.
- Validate gallery artifacts, frame assets, sizes, and SHA256 hashes.
- Validate required frame roles:
  - `actual`
  - `secondary_layer`
  - `overlay`
  - `overlay_graded`
  - `target`
  - `diff`
  - `strip`
- Validate frame metrics and output-frame ordering.
- Keep real HTTP checks optional with `--check-public`, because quick tunnel
  URLs are session-lifetime artifacts.

## Commands

```powershell
python tools\validate_mitsuba_secondary_pass_contract.py `
  build\shots\s335_mitsuba_secondary_pass_contract\secondary_pass_contract.json `
  --out build\shots\s336_mitsuba_secondary_pass_contract_validation\validation.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_pass_contract_validation_s336.md `
  --title "S336 Mitsuba Secondary Pass Contract Validation"
```

Optional live public check, only when the inherited tunnel is active:

```powershell
python tools\validate_mitsuba_secondary_pass_contract.py `
  build\shots\s335_mitsuba_secondary_pass_contract\secondary_pass_contract.json `
  --check-public `
  --timeout 20 `
  --out build\shots\s336_mitsuba_secondary_pass_contract_validation\validation.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_pass_contract_validation_s336.md `
  --title "S336 Mitsuba Secondary Pass Contract Validation"
```

## Outputs

- Validation JSON:
  `build/shots/s336_mitsuba_secondary_pass_contract_validation/validation.json`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_pass_contract_validation_s336.md`
- Validator:
  `tools/validate_mitsuba_secondary_pass_contract.py`

## Acceptance

- Validation status is `passed`.
- Total checks are `187`.
- Failed checks are `0`.
- Default skipped checks are `2`, corresponding to optional public HTTP probes.
- Contract status remains `ready`.
- Missing frame assets remain `0`.
- Max overlay mean absolute diff remains under `20.0`.
- All recorded frame artifact hashes match.

## Next

Use this validator as the regression gate while replacing the S334/S335
screen-space overlay hybrid with a renderer-native Mitsuba secondary pass.
