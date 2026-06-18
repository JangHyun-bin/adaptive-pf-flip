# Ripple Readability Diagnostics

## Goal

Add a diagnostic review artifact that makes subtle contact-region ripple and surface-line changes easier to inspect than full-frame or normal focus sheets alone.

## Scope

- Add `ripple_readability_review` as an opt-in renderer review config.
- Generate `review/ripple_readability_sheet.png` from focus-region crops.
- Generate `review/ripple_readability_manifest.json` with edge/highlight metrics.
- Add a gate for frame count, mean edge strength, edge nonzero ratio, and highlight ratio.
- Add `dam_break_ripple_readability_diagnostics` as an inherited S90 preset.
- Preserve existing contact sheet, focus sheet, focus comparison, temporal diff, and visual QA artifacts.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\run_cinematic_shot.py --preset dam_break_ripple_readability_diagnostics --out build\shots\s91_ripple_readability_diagnostics --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s91.md --compare-review-manifest build\shots\s90_ripple_placement_focus_tuning\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S91 generated:

- `build/shots/s91_ripple_readability_diagnostics/shot.gif`
- `build/shots/s91_ripple_readability_diagnostics/review/contact_sheet.png`
- `build/shots/s91_ripple_readability_diagnostics/review/focus_sheet.png`
- `build/shots/s91_ripple_readability_diagnostics/review/ripple_readability_sheet.png`
- `build/shots/s91_ripple_readability_diagnostics/review/ripple_readability_manifest.json`
- `docs/reports/cinematic_gate_s91.md`

The final gate passes ripple readability QA with mean edge strength `35.3016`, mean edge nonzero ratio `0.371383`, and max highlight ratio `0.0010111`. Existing visual, temporal, focus, camera, and secondary framing gates pass.

## Next

S92 should compare ripple/contact diagnostic sheets across nearby milestones.
