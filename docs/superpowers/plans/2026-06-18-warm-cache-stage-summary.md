# Warm Cache Stage Summary

## Goal

Make warm-cache reuse behavior inspectable from a shot summary without opening individual command logs.

## Scope

- Add `tools/summarize_shot_commands.py`.
- Read a `shot_summary.json`.
- Report export, validation, water reconstruction, and conversion reuse flags.
- Report each command's exit code, reuse state, elapsed time, and stdout log path.
- Keep this as a reporting tool; do not change simulation or render output.

## Command

```powershell
python tools\summarize_shot_commands.py build\s112_export_reuse_probe\shot_summary.json --out docs\reports\cinematic_warm_cache_summary_s113.md
```

## Result

S113 produced `docs/reports/cinematic_warm_cache_summary_s113.md`.

- Export cache reused: `True`.
- Validation reused: `True`.
- Water reconstruction reused: `True`.
- Converted sequence reused: `True`.
- Warm-cache total command time in the 2-frame probe: `1.17s`.
- Warm-cache reused command time: `536.75ms`.

## Next

S114 should target render-frame reuse because export, validation, reconstruction, and conversion now have opt-in warm-cache paths.
