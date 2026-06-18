# Secondary Mist Alpha Falloff

## Goal

Soften the visible circular edges of S68 billboard mist disks.

## Scope

- Keep the camera-facing billboard disk approach.
- Split each billboard into concentric radial rings.
- Assign decreasing alpha materials to the rings.
- Preserve the S65 visual QA gates and S68 render-cost range.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python - <<'PY'
import importlib.util
spec = importlib.util.spec_from_file_location('render_bridge_blender', 'tools/render_bridge_blender.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
compile(mod.BLENDER_DRIVER, 'BLENDER_DRIVER', 'exec')
PY
python tools\render_bridge_blender.py build\shots\s68_secondary_mist_quality\converted\sequence.json build\s69_mist_falloff_probe_dry --frames 4 --width 640 --height 360 --dry-run --render-preset dam_break_contact_closeup --preset-config configs\cinematic_presets.json
python tools\run_cinematic_shot.py --preset dam_break_contact_closeup --out build\shots\s69_secondary_mist_falloff --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s69.md --compare-review-manifest build\shots\s62_secondary_size_pass\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S69 generated:

- `build/shots/s69_secondary_mist_falloff/shot.gif`
- `build/shots/s69_secondary_mist_falloff/review/contact_sheet.png`
- `build/shots/s69_secondary_mist_falloff/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s69.md`

The falloff pass preserved visual QA and render cost, and it reduced the harshest disk-edge look. The mist still needs more aggressive tuning to remove the visible circular sprite character.

## Next

S70 should tune falloff more aggressively, likely with a lower outer alpha and a stronger center/inner transition.
