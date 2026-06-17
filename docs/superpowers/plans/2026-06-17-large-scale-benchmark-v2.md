# Large-Scale Benchmark V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the large-scale 3D two-phase benchmark so it measures simulation, render-cache export, cache validation, preview rendering, and memory-proxy costs in one CSV.

**Architecture:** Keep `apps/bench_large_scale3d_tp.cpp` as the single CSV runner. The runner still defaults to simulation-only metrics, but `--render-cache-prefix PATH` enables per-row SPEC-4 cache export, Python cache validation, and preview timing. The render cache work happens after each simulation row completes, so default `ctest` remains unchanged and slow cinematic work stays opt-in.

**Tech Stack:** C++17/MSVC, CMake, doctest, existing `render_cache3d.h`, Python `tools/validate_render_cache.py`, Python `tools/render_cache_preview.py`.

---

## File Structure

- Modify `apps/bench_large_scale3d_tp.cpp`
  - Add render-cache CLI options.
  - Add liquid/gas count fields.
  - Add cache export/validate/preview timings.
  - Add cache bytes and total memory proxy fields.
- Modify `README.md`
  - Add S36 status row.
  - Add one large-scale v2 quickstart command.
- Modify `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`
  - Mark S36 as done after validation.
- Modify `docs/superpowers/plans/2026-06-17-large-scale-benchmark-v2.md`
  - Check off tasks after implementation.

## Task 1: Plan And CSV Contract

**Files:**
- Create: `docs/superpowers/plans/2026-06-17-large-scale-benchmark-v2.md`

- [x] **Step 1: Define S36 scope**

The runner must keep existing CSV fields and append these columns:

```text
liquid_particles_start,liquid_particles_end,gas_particles_start,gas_particles_end,
render_cache_enabled,render_cache_manifest,render_cache_frames,render_cache_bytes,
render_cache_export_ms,render_cache_validate_ms,render_cache_preview_ms,
render_cache_tools_status,total_memory_proxy_bytes
```

- [x] **Step 2: Define new CLI**

Add these options:

```text
--render-cache-prefix PATH
--render-cache-every N
--render-cache-preview-scale N
--python EXE
--skip-render-cache-tools
```

## Task 2: Implement Runner Metrics

**Files:**
- Modify: `apps/bench_large_scale3d_tp.cpp`

- [x] **Step 1: Add helper functions**

Add helpers for:
- particle count by phase
- path-safe row cache prefixes
- file size lookup
- quoted command arguments
- timed external tool invocation

- [x] **Step 2: Add render-cache row fields**

Extend `Row` with particle-count breakdown and render-cache timing fields.

- [x] **Step 3: Export cache after simulation**

When `--render-cache-prefix` is non-empty, write one JSONL cache frame plus one manifest for each row:

```text
<prefix>_<variant>_<solver>_000.jsonl
<prefix>_<variant>_<solver>_manifest.json
<prefix>_<variant>_<solver>_preview/
```

- [x] **Step 4: Time validator and preview**

Unless `--skip-render-cache-tools` is passed, time:

```powershell
python tools\validate_render_cache.py <manifest> --allow-empty-secondary
python tools\render_cache_preview.py <manifest> <preview-dir> <scale>
```

Set `render_cache_tools_status` to `ok`, `fail`, `skipped`, or `disabled`.

## Task 3: Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md`
- Modify: `docs/superpowers/plans/2026-06-17-large-scale-benchmark-v2.md`

- [x] **Step 1: Add README status**

Add:

```markdown
| **S36** | **Large-scale benchmark v2** - large-scale CSV runner now records per-phase counts, render-cache export bytes/time, cache validation time, preview time, and total memory proxy. | done |
```

- [x] **Step 2: Add README quickstart**

Add:

```powershell
.\build\Release\bench_large_scale3d_tp.exe --nx 16 --ny 24 --nz 16 --steps 4 --solver baseline --csv build/large_scale3d_tp_v2.csv --render-cache-prefix build/large_scale3d_tp_v2 --render-cache-every 4 --render-cache-preview-scale 4
```

- [x] **Step 3: Mark roadmap S36 complete**

Update S36 in `docs/superpowers/plans/2026-06-17-cinematic-hyperreal-roadmap.md` to note the landing commit message.

## Task 4: Verification

**Files:**
- Validate generated build artifacts under `build/`

- [x] **Step 1: Build Release targets**

Run:

```powershell
cmake --build build --config Release --target bench_large_scale3d_tp export_render_cache3d
```

- [x] **Step 2: Run S36 smoke**

Run:

```powershell
.\build\Release\bench_large_scale3d_tp.exe --nx 16 --ny 24 --nz 16 --steps 4 --solver baseline --csv build/large_scale3d_tp_v2.csv --render-cache-prefix build/large_scale3d_tp_v2 --render-cache-every 4 --render-cache-preview-scale 4
```

Expected:
- `status=ok`
- CSV exists.
- CSV header contains `render_cache_export_ms`.
- At least one `_manifest.json` exists under `build/`.
- At least one `_preview/cache_preview.gif` exists under `build/`.

- [x] **Step 3: Run full project checks**

Run:

```powershell
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Task 5: Commit

**Files:**
- Stage only S36 source and docs.

- [x] **Step 1: Commit and push**

Run:

```powershell
git add README.md apps\bench_large_scale3d_tp.cpp docs\superpowers\plans\2026-06-17-cinematic-hyperreal-roadmap.md docs\superpowers\plans\2026-06-17-large-scale-benchmark-v2.md
git commit -m "test: extend large scale render benchmarks"
git push origin main
```
