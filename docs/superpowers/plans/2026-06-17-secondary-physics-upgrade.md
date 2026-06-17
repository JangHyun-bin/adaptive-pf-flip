# Secondary Particle Physics Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade secondary droplet/bubble lifecycle from simple advection/removal into a more physical opt-in model with dt-based drag, droplet gravity scaling, bubble buoyancy, and reabsorption-to-primary volume coupling.

**Architecture:** Extend the shared `src/driver/secondary_particles3d.h` helper so sparse and multires 3D TP simulations receive identical behavior. Keep existing defaults compatible. Add opt-in fields on `SparseSim3DTP` and `MRSim3DTP`, then propagate them through validators and the paired bench so the new physics can be gated without affecting default `ctest` runtime.

**Tech Stack:** C++17/MSVC, doctest, existing sparse/MR 3D TP validators and paired benchmark.

---

## File Structure

- Modify `src/driver/secondary_particles3d.h`
  - Add `droplet_gravity_scale`, `droplet_drag`, `bubble_drag`, and optional reabsorbed particle outputs.
  - Add stats for dragged particles and reabsorbed-to-primary particles/volumes.
- Modify `src/driver/sparse_sim3d_tp.h/.cpp`
  - Add sim knobs and counters.
  - Append reabsorbed particles back into `particles` only when `secondary_reabsorb_to_primary` is enabled.
- Modify `src/driver/multires_sim3d_tp.h/.cpp`
  - Mirror sparse knobs/counters.
- Modify `apps/validate_sparse3d_tp.cpp`, `apps/validate_multires3d_tp.cpp`, `apps/bench_multires_sparse3d_tp.cpp`
  - Add CLI knobs and printed metrics for drag, gravity scale, and primary reinjection.
- Modify `tests/test_secondary_particles3d.cpp`, `tests/test_sparse_sim3d_tp.cpp`, `tests/test_multires_sim3d_tp.cpp`
  - Add focused tests for dt-based drag/buoyancy and opt-in primary volume coupling.
- Modify `README.md` and `docs/superpowers/plans/2026-06-17-spec4-render-cache-sequence.md`
  - Add S35 status and roadmap note.

## Task 1: Shared Helper Tests And Physics

**Files:**
- Modify: `tests/test_secondary_particles3d.cpp`
- Modify: `src/driver/secondary_particles3d.h`

- [x] **Step 1: Add a failing helper test**

Add a test where a droplet near the low-x boundary and a bubble near the high-x boundary stay outside the reabsorb band. Configure:
- `velocity_damping = 1.0`
- `droplet_gravity_scale = 0.5`
- `droplet_drag = 1.0`
- `bubble_drag = 0.0`
- `gravity = -10.0`
- `bubble_buoyancy_scale = 0.25`
- `dt = 0.1`

Expected:
- droplet `vx` is multiplied by `exp(-0.1)`
- droplet `vy` includes half gravity and drag
- bubble `vy` increases by `0.25`
- drag stats count one dragged droplet and zero dragged bubbles.

- [x] **Step 2: Implement minimal helper behavior**

Apply per-set acceleration, legacy `velocity_damping`, and new `exp(-drag * dt)` damping. Keep defaults equivalent to prior behavior by defaulting new drag coefficients to `0.0` and droplet gravity scale to `1.0`.

## Task 2: Primary Reabsorption Coupling

**Files:**
- Modify: `tests/test_sparse_sim3d_tp.cpp`
- Modify: `tests/test_multires_sim3d_tp.cpp`
- Modify: `src/driver/sparse_sim3d_tp.h/.cpp`
- Modify: `src/driver/multires_sim3d_tp.h/.cpp`

- [x] **Step 1: Add sparse and MR tests**

Create one reabsorbed droplet with volume multiplier `2.0`, enable `secondary_reabsorb_to_primary`, run one step, and assert:
- secondary container is empty
- primary liquid particle count increases by one
- primary liquid volume increases by `2.0`
- reabsorbed-to-primary count and volume counters report the same addition.

- [x] **Step 2: Implement coupling**

Collect reabsorbed droplets/bubbles in the shared helper, then append them to `sim.particles` after lifecycle advancement only when `secondary_reabsorb_to_primary` is true.

## Task 3: CLI Metrics

**Files:**
- Modify: `apps/validate_sparse3d_tp.cpp`
- Modify: `apps/validate_multires3d_tp.cpp`
- Modify: `apps/bench_multires_sparse3d_tp.cpp`

- [x] **Step 1: Add CLI knobs**

Add:
- `--secondary-droplet-gravity-scale S`
- `--secondary-droplet-drag S`
- `--secondary-bubble-drag S`
- `--secondary-reabsorb-to-primary`

- [x] **Step 2: Print metrics**

Print:
- `secondary_droplets_dragged_total`
- `secondary_bubbles_dragged_total`
- `secondary_droplets_reabsorbed_to_primary_total`
- `secondary_bubbles_reabsorbed_to_primary_total`
- `secondary_droplet_volume_reabsorbed_to_primary_total`
- `secondary_bubble_volume_reabsorbed_to_primary_total`

- [x] **Step 3: Preserve gates**

Existing secondary lifecycle gates should still pass. Add invalid CLI checks for negative drag and negative gravity scale.

## Task 4: Docs And Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-17-spec4-render-cache-sequence.md`

- [x] **Step 1: Add S35 docs**

Add S35 to README and add one sparse validator command with drag/reabsorb-to-primary controls.

- [x] **Step 2: Run targeted tests**

Run:

```powershell
cmake --build build --config Debug --target unit_tests
.\build\Debug\unit_tests.exe --test-case="*secondary*"
.\build\Debug\unit_tests.exe --test-case="sparse 3D secondary*"
.\build\Debug\unit_tests.exe --test-case="multires 3D secondary*"
```

- [x] **Step 3: Run runner smokes**

Run:

```powershell
cmake --build build --config Release --target validate_sparse3d_tp validate_multires3d_tp bench_multires_sparse3d_tp
.\build\Release\validate_sparse3d_tp.exe --scenario bubble --steps 4 --secondary-lifecycle --secondary-droplet-drag 1 --secondary-bubble-drag 0.5 --secondary-droplet-gravity-scale 0.5 --secondary-reabsorb-to-primary
.\build\Release\validate_multires3d_tp.exe --scenario bubble --steps 4 --secondary-lifecycle --secondary-droplet-drag 1 --secondary-bubble-drag 0.5 --secondary-droplet-gravity-scale 0.5 --secondary-reabsorb-to-primary
.\build\Release\bench_multires_sparse3d_tp.exe --steps 3 --secondary-lifecycle --secondary-droplet-drag 1 --secondary-bubble-drag 0.5 --secondary-droplet-gravity-scale 0.5 --secondary-reabsorb-to-primary
```

- [x] **Step 4: Full checks**

Run:

```powershell
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Task 5: Commit

**Files:**
- Stage all modified source, app, test, README, and plan files.

- [x] **Step 1: Commit and push**

Run:

```powershell
git add README.md src\driver\secondary_particles3d.h src\driver\sparse_sim3d_tp.h src\driver\sparse_sim3d_tp.cpp src\driver\multires_sim3d_tp.h src\driver\multires_sim3d_tp.cpp apps\validate_sparse3d_tp.cpp apps\validate_multires3d_tp.cpp apps\bench_multires_sparse3d_tp.cpp tests\test_secondary_particles3d.cpp tests\test_sparse_sim3d_tp.cpp tests\test_multires_sim3d_tp.cpp docs\superpowers\plans\2026-06-17-spec4-render-cache-sequence.md docs\superpowers\plans\2026-06-17-secondary-physics-upgrade.md
git commit -m "feat: upgrade secondary particle physics"
git push origin main
```
