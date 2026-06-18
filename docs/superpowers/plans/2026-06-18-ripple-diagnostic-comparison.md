# Ripple Diagnostic Comparison

## Goal

Add a side-by-side comparison artifact for ripple readability diagnostic sheets so subtle contact-region changes can be reviewed across nearby cinematic gates.

## Scope

- Load `ripple_readability_sheet` and `ripple_readability_manifest` from `lsfs_cinematic_review_pack` manifests when present.
- Generate `review/ripple_readability_comparison_sheet.png` from prior and current diagnostic sheets.
- Generate `review/ripple_readability_comparison_manifest.json` with source manifests and diagnostic artifacts.
- Preserve the existing full-frame comparison, focus comparison, and temporal diff paths.
- Run a full 36-frame gate against S91 to prove comparison artifacts are written.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\run_cinematic_shot.py --preset dam_break_ripple_readability_diagnostics --out build\shots\s92_ripple_diagnostic_comparison --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s92.md --compare-review-manifest build\shots\s91_ripple_readability_diagnostics\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S92 generated:

- `build/shots/s92_ripple_diagnostic_comparison/shot.gif`
- `build/shots/s92_ripple_diagnostic_comparison/review/contact_sheet.png`
- `build/shots/s92_ripple_diagnostic_comparison/review/ripple_readability_sheet.png`
- `build/shots/s92_ripple_diagnostic_comparison/review/ripple_readability_comparison_sheet.png`
- `build/shots/s92_ripple_diagnostic_comparison/review/ripple_readability_comparison_manifest.json`
- `docs/reports/cinematic_gate_s92.md`

The final gate compares `2` ripple diagnostic sources. Ripple readability QA, focus review QA, full-frame visual QA, temporal highlight QA, camera stability, and secondary framing QA pass.

## Next

S93 should tune contact foam and ripple integration while preserving diagnostic and temporal gates.
