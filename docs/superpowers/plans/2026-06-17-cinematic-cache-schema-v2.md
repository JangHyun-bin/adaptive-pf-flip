# Cinematic Cache Schema v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Keep S37 as one commit and push after verification.

**Goal:** Extend the 3D render cache with cinematic metadata while preserving existing v1 manifest/frame compatibility.

**Architecture:** Keep the existing `lsfs_cache3d_version: 1` and `lsfs_cache3d_manifest_version: 1` compatibility markers. Add `cache_schema_version: 2` and optional cinematic fields that readers can ignore by default. The validator only requires the v2 fields when `--require-cinematic` is passed.

**Tech Stack:** C++17 render cache writer, Python validator/preview tools, doctest.

## Scope

- Modify `src/driver/render_cache3d.h`
  - Add camera focal length and vertical FOV metadata.
  - Add per-frame world units, shutter interval, frame bounds, and a cinematic metadata section.
  - Add secondary channel counts and age ranges to the water summary.
  - Add manifest-level `cache_schema_version`, world units, bounds, and optional per-frame shutter metadata.
- Modify `tools/validate_render_cache.py`
  - Accept v1 data by default.
  - Add `--require-cinematic` to enforce v2 fields.
  - Validate camera focal/FOV metadata, world units, frame bounds, shutter interval, and secondary channel summaries.
- Modify `tools/render_cache_preview.py`
  - Keep accepting v1 manifests.
  - Accept manifests with optional v2 metadata without branching preview behavior.
- Modify `tests/test_render_cache3d.cpp`
  - Assert v2 schema fields are emitted by sparse/MR frame writers and manifests.
- Modify `README.md`
  - Add S37 status and a quickstart validation command.
- Modify `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`
  - Mark S37 as done after validation.

## Compatibility Rules

- Existing v1 manifests and JSONL frames must still validate without `--require-cinematic`.
- Existing preview behavior must not depend on v2-only fields.
- New writer output should include v2 fields by default because downstream S38 conversion will consume them.

## Verification

```powershell
cmake --build build --config Debug --target unit_tests
.\build\Debug\unit_tests.exe --test-case="*render cache*"
python -m py_compile tools\validate_render_cache.py tools\render_cache_preview.py
cmake --build build --config Release --target export_render_cache3d bench_large_scale3d_tp
.\build\Release\export_render_cache3d.exe --kind sparse --steps 2 --every 1 --out-prefix build\s37_sparse
python tools\validate_render_cache.py build\s37_sparse_manifest.json
python tools\validate_render_cache.py build\s37_sparse_manifest.json --require-cinematic
python tools\render_cache_preview.py build\s37_sparse_manifest.json build\s37_preview 4
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Commit

```powershell
git add README.md src\driver\render_cache3d.h tests\test_render_cache3d.cpp tools\validate_render_cache.py tools\render_cache_preview.py docs\superpowers\plans\2026-06-17-cinematic-cache-schema-v2.md docs\superpowers\plans\2026-06-17-cinematic-hyperreal-roadmap.md
git commit -m "feat: extend cinematic render cache schema"
git push origin main
```
