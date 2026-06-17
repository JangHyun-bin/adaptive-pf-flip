# Secondary Render Channels Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split secondary particles into explicit renderer-facing droplet, spray, foam, and bubble channels.

**Architecture:** Keep the existing primary/secondary particle containers unchanged. Add render-channel metadata at export time: each secondary particle receives a `render_channel`, and each frame receives a `secondary_channels` summary section. Readers stay backwards-compatible by accepting older caches without channel metadata, but when channel metadata exists the validator cross-checks it against particle records.

**Tech Stack:** C++17 render cache writer, doctest, Python validator/converter/preview tools, Pillow/numpy preview paths.

---

## Channel Contract

- `droplet`: ordinary secondary liquid escaped particle.
- `spray`: young or fast secondary liquid escaped particle.
- `foam`: older, slow secondary liquid candidate.
- `bubble`: secondary gas escaped particle.
- `water`: primary liquid particle render channel.
- `air`: primary gas particle render channel.

The cache writer emits one `render_channel` per particle. The `secondary_channels` section stores the four secondary channel counts and their total.

## Files

- Modify `src/driver/render_cache3d.h`
  - Add channel classification helpers.
  - Add `secondary_channels` JSONL section.
  - Add `render_channel` to particle records.
- Modify `tests/test_render_cache3d.cpp`
  - Assert non-zero foam/bubble channel summaries and per-particle `render_channel` output.
- Modify `tools/validate_render_cache.py`
  - Validate render channel names.
  - Cross-check `secondary_channels` counts against particle records.
  - Fail invalid channel names and negative channel counts.
- Modify `tools/convert_render_cache.py`
  - Preserve `render_channel` in particle CSV.
  - Include `secondary_channels` in per-frame camera JSON.
- Modify `tools/render_cache_preview.py`
  - Add `--secondary-channel all|droplet|spray|foam|bubble`.
- Modify `tools/cinematic_render_stub.py`
  - Add `--secondary-channel all|droplet|spray|foam|bubble`.
  - Use channel-specific colors and summary counts.
- Modify `README.md`
  - Add S40 status row and quickstart isolation command.
- Modify `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`
  - Mark S40 done and set S41 as next immediate action.

## Tasks

### Task 1: Writer Schema

- [ ] Add `render_channel` fields to JSONL particle records.
- [ ] Add one `secondary_channels` section per frame.
- [ ] Extend doctest assertions for foam and bubble channels.

### Task 2: Reader Validation

- [ ] Validate known channel names.
- [ ] Reject invalid channel names.
- [ ] Cross-check secondary channel summary counts.

### Task 3: Conversion and Preview

- [ ] Preserve channel data in converted particle CSV.
- [ ] Add secondary channel filtering to quick preview and cinematic preview.
- [ ] Include per-frame channel counts in cinematic preview summaries.

### Task 4: Verification

```powershell
cmake --build build --config Debug --target unit_tests
.\build\Debug\unit_tests.exe --test-case="*render cache*"
python -m py_compile tools\validate_render_cache.py tools\convert_render_cache.py tools\render_cache_preview.py tools\cinematic_render_stub.py
cmake --build build --config Release --target export_render_cache3d
.\build\Release\export_render_cache3d.exe --kind sparse --steps 2 --every 1 --out-prefix build\s40_sparse
python tools\validate_render_cache.py build\s40_sparse_manifest.json --require-cinematic
python tools\convert_render_cache.py build\s40_sparse_manifest.json build\s40_convert --require-cinematic
python tools\render_cache_preview.py build\s40_sparse_manifest.json build\s40_preview_channels 4 --secondary-channel foam --hide-primary-water
python tools\cinematic_render_stub.py build\s40_sparse_manifest.json build\s40_cinematic --frames 4 --width 640 --height 360 --secondary-channel foam --min-occupancy 0
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Commit

```powershell
git add README.md src\driver\render_cache3d.h tests\test_render_cache3d.cpp tools\validate_render_cache.py tools\convert_render_cache.py tools\render_cache_preview.py tools\cinematic_render_stub.py docs\superpowers\plans\2026-06-17-secondary-render-channels.md docs\superpowers\plans\2026-06-17-cinematic-hyperreal-roadmap.md
git commit -m "feat: add secondary render channels"
git push origin main
```
