# Secondary Render Integration Review

## Goal

Check spray, foam, and bubble secondary layers against the S102 water volume scattering baseline without changing the underlying simulation or render material stack.

## Scope

- Add `dam_break_secondary_render_integration_review` as an inherited S102 preset.
- Include `bubble` in `renderer.secondary_depth_review.channels`.
- Keep water volume scattering, water material, camera, cache schema, and secondary render materials unchanged.
- Use the existing secondary depth review and comparison sheets to inspect spray/foam/bubble integration.
- Preserve visual QA, temporal highlight QA, focus review QA, ripple readability QA, secondary depth review QA, and comparison artifacts.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python tools\run_cinematic_shot.py --preset dam_break_secondary_render_integration_review --out build\shots\s103_secondary_render_integration_review --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s103.md --compare-review-manifest build\shots\s102_water_volume_scattering\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S103 generated:

- `build/shots/s103_secondary_render_integration_review/shot.gif`
- `build/shots/s103_secondary_render_integration_review/review/contact_sheet.png`
- `build/shots/s103_secondary_render_integration_review/review/secondary_depth_sheet.png`
- `build/shots/s103_secondary_render_integration_review/review/secondary_depth_comparison_sheet.png`
- `docs/reports/cinematic_gate_s103.md`

The full gate passed with bubble-inclusive secondary depth review:

- channels: `bubble`, `foam`, `spray`
- active particles mean: `192.0`
- crop particles mean: `191.75`
- crop ratio mean: `0.9987`
- depth span mean: `10.2681`
- normalized depth span mean: `0.3955`
- visual QA mean luminance: `101.3397`
- focus review min contrast: `72.0`

The comparison sheet shows the S102 spray/foam review next to the S103 bubble/foam/spray review, giving a direct check that bubble markers remain in-frame under the water volume scattering baseline.

## Next

S104 should run a larger-grid cinematic benchmark that keeps the S103 render/review stack passing while exposing runtime and visual cost beyond the current `28 x 34 x 22` gate.
