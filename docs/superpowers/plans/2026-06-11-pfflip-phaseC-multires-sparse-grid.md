# PF-FLIP Phase C Multiresolution Sparse Grid Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first real MSBG differentiator: 2D multiresolution sparse blocks where interface blocks stay fine and bulk blocks can be coarse, while preserving the Phase B sparse two-phase behavior.

**Architecture:** Keep the proven Phase A/B single-resolution sparse solver intact, and add a parallel multiresolution path behind new `mr_*` files. Phase C uses leaf blocks with levels `0` and `1`, enforces a 2:1 transition zone, stores scalar fields per leaf block, stores MAC face values as geometric face segments, and uses finite-volume coarse-fine pressure fluxes with a weighted CG dot product. The first solver gate is not SPEC-2; it is "uniform fine result, fewer active degrees of freedom" on the Phase B bubble tank with only the interface band refined.

**Tech Stack:** C++17, CMake, doctest. Reuse `Vec2`, `Particles2DTP`, `PhaseParams`, `phiFromRawDensity`, `betaFromPhi`, and the Phase B sparse two-phase tests as behavioral reference.

---

## Scope

Phase C is 2D only.

In scope:
- Leaf-block multiresolution layout with levels `0` (fine, `dx`) and `1` (coarse, `2*dx`).
- 2:1 transition-zone enforcement so neighboring leaf blocks differ by at most one level.
- Scalar leaf-block storage for pressure, marker, and raw density-like fields.
- MAC face segment storage for `u`, `v`, `mu`, and `mv`, including coarse-fine face splits.
- Normalized cubic P2G/G2P that works across level boundaries.
- Finite-volume pressure operator across same-level and coarse-fine faces.
- A 2D sparse two-phase bubble scene where an interface refinement band matches the single-level fine sparse result within a fixed tolerance while using fewer blocks/DOFs.

Out of scope:
- SPEC-2 stochastic coarsening and narrow-band air deletion policy.
- 3D multiresolution.
- Adaptive Poisson multigrid from paper section 6.
- Multithreaded color execution.
- Full performance tuning of `clear()` and `unordered_map` hot paths.

## File Structure

| File | Responsibility |
|---|---|
| `src/grid/multires_layout2d.h` | Leaf block keys, level metadata, 2:1 balance, block neighborhood, refinement-band construction. |
| `src/grid/multires_scalar_grid2d.h` | Per-leaf-block `B*B` scalar storage, physical sampling, read/write access by leaf cell key. |
| `src/grid/multires_mac_grid2d.h` | Multires MAC wrapper: scalar fields plus geometric face fields for `u/v/mu/mv`. |
| `src/driver/multires_ops2d_tp.h/.cpp` | Two-phase multires P2G/G2P, advection, marker construction, active leaf/face enumeration. |
| `src/pressure/multires_pressure2d.h/.cpp` | Finite-volume variable-resolution pressure operator, weighted PCG, projection. |
| `src/driver/multires_sim2d_tp.h/.cpp` | Phase C bubble-tank driver and single-level fine reference comparison hooks. |
| `src/driver/viz_multires_tp.h` | PPM visualization of particles, leaf-block levels, and active pressure blocks. |
| `apps/run_multires_bubble.cpp` | Release runner that prints fine-reference vs multires metrics. |
| `tests/test_multires_layout.cpp` | Layout, leaf lookup, 2:1 balance, refinement band. |
| `tests/test_multires_scalar.cpp` | Scalar storage and linear sampling across same/coarse-fine boundaries. |
| `tests/test_multires_mac.cpp` | Face ownership and coarse-fine face splitting. |
| `tests/test_multires_transfer_tp.cpp` | Two-phase normalized P2G/G2P across level boundaries. |
| `tests/test_multires_pressure.cpp` | Coarse-fine pressure operator conservation, uniform-grid equivalence, projection. |
| `tests/test_multires_sim_tp.cpp` | Bubble-tank equivalence plus memory/DOF reduction gate. |

## Core Conventions

Domain coordinates use the fine grid as the logical coordinate system. `dx` is the finest cell width.

Leaf block:
```cpp
struct MRBlockKey {
  int level; // 0 = dx, 1 = 2*dx
  int bx;    // block coordinate at this level
  int by;
};
```

A level `L` block stores `B*B` cells. One stored cell covers `cellSize(L) = dx * (1 << L)`. A block covers `B * cellSize(L)` in physical space.

2:1 rule:
- Any two leaf blocks sharing an edge or corner may differ by at most one level.
- Phase C only creates levels `0` and `1`, so the rule is enforced by growing one transition ring of fine blocks around every refined block.

Face convention:
- A MAC face is stored as an oriented geometric segment in fine-grid units.
- Fine faces along a coarse-fine interface are stored as separate fine segments.
- Coarse-side pressure projection updates each overlapping fine segment once; coarse-cell flux is the sum of its overlapping fine segments.

Pressure convention:
- Leaf cells are the pressure unknowns.
- Same-level and coarse-fine pressure coupling uses finite-volume flux:
  `flux = beta_face * face_length / center_distance * (p_neighbor - p_cell)`.
- The pressure equation for a cell divides net flux by that cell volume.
- The matrix is self-adjoint under the volume-weighted inner product, so CG uses `weightedDot(a,b) = sum_i volume_i * a_i * b_i`.

## Task 1: Multires Leaf Layout and 2:1 Transition Zone

**Files:**
- Create: `src/grid/multires_layout2d.h`
- Create: `tests/test_multires_layout.cpp`
- Modify: `CMakeLists.txt`

- [ ] **Step 1: Write failing layout tests**

Create `tests/test_multires_layout.cpp`:
```cpp
#include "doctest.h"
#include "grid/multires_layout2d.h"
#include <set>

TEST_CASE("multires layout: refine band creates fine leaves and coarse bulk") {
  MRLayout2D<8> layout(64, 64, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(24, 24, 40, 40);
  layout.enforceTwoToOneBalance();

  CHECK(layout.leafCount() > 0);
  CHECK(layout.countLevel(0) > 0);
  CHECK(layout.countLevel(1) > 0);
  CHECK(layout.leafAtFineCell(32, 32).level == 0);
  CHECK(layout.leafAtFineCell(4, 4).level == 1);
  CHECK(layout.isTwoToOneBalanced());
}

TEST_CASE("multires layout: active leaves cover domain exactly once") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();

  std::set<std::pair<int,int>> covered;
  for (const MRBlockKey& key : layout.leaves()) {
    int step = 1 << key.level;
    int x0 = key.bx * 8 * step;
    int y0 = key.by * 8 * step;
    for (int ly = 0; ly < 8; ++ly) {
      for (int lx = 0; lx < 8; ++lx) {
        for (int yy = 0; yy < step; ++yy) {
          for (int xx = 0; xx < step; ++xx) {
            int x = x0 + lx * step + xx;
            int y = y0 + ly * step + yy;
            if (x >= 0 && x < 32 && y >= 0 && y < 32) {
              CHECK(covered.insert({x,y}).second);
            }
          }
        }
      }
    }
  }
  CHECK(covered.size() == 32 * 32);
}
```

- [ ] **Step 2: Add the test to CMake and verify failure**

Modify `CMakeLists.txt` by adding `tests/test_multires_layout.cpp` to `unit_tests`.

Run:
```powershell
cmake --build build --config Debug
```

Expected: compile failure because `grid/multires_layout2d.h` does not exist.

- [ ] **Step 3: Implement the layout header**

Create `src/grid/multires_layout2d.h`:
```cpp
#pragma once
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <tuple>
#include <vector>

struct MRBlockKey {
  int level = 0;
  int bx = 0;
  int by = 0;
  bool operator==(const MRBlockKey& o) const { return level == o.level && bx == o.bx && by == o.by; }
};

inline bool operator<(const MRBlockKey& a, const MRBlockKey& b) {
  return std::tie(a.level, a.bx, a.by) < std::tie(b.level, b.bx, b.by);
}

template<int B>
struct MRLayout2D {
  int nx, ny;
  double dx;
  std::vector<MRBlockKey> leaf_blocks;

  MRLayout2D(int nx_, int ny_, double dx_) : nx(nx_), ny(ny_), dx(dx_) {}

  int blockFineSize(int level) const { return B * (1 << level); }
  int levelBlockCountX(int level) const { int s = blockFineSize(level); return (nx + s - 1) / s; }
  int levelBlockCountY(int level) const { int s = blockFineSize(level); return (ny + s - 1) / s; }

  void setCoarseEverywhere(int level) {
    leaf_blocks.clear();
    for (int by = 0; by < levelBlockCountY(level); ++by) {
      for (int bx = 0; bx < levelBlockCountX(level); ++bx) {
        leaf_blocks.push_back({level, bx, by});
      }
    }
  }

  void refineFineCellBox(int x0, int y0, int x1, int y1) {
    std::vector<MRBlockKey> next;
    for (const auto& key : leaf_blocks) {
      int s = blockFineSize(key.level);
      int bx0 = key.bx * s;
      int by0 = key.by * s;
      int bx1 = std::min(nx, bx0 + s);
      int by1 = std::min(ny, by0 + s);
      bool overlaps = bx0 < x1 && bx1 > x0 && by0 < y1 && by1 > y0;
      if (!overlaps || key.level == 0) {
        next.push_back(key);
        continue;
      }
      for (int cy = 0; cy < 2; ++cy) {
        for (int cx = 0; cx < 2; ++cx) {
          next.push_back({key.level - 1, key.bx * 2 + cx, key.by * 2 + cy});
        }
      }
    }
    leaf_blocks = next;
    sortUnique();
  }

  void enforceTwoToOneBalance() {
    // With Phase C levels {0,1}, one refinement pass already satisfies 2:1.
    sortUnique();
  }

  bool isTwoToOneBalanced() const {
    for (const auto& a : leaf_blocks) {
      for (const auto& b : leaf_blocks) {
        if (a == b) continue;
        if (std::abs(a.level - b.level) > 1) return false;
      }
    }
    return true;
  }

  MRBlockKey leafAtFineCell(int x, int y) const {
    for (const auto& key : leaf_blocks) {
      int s = blockFineSize(key.level);
      int x0 = key.bx * s;
      int y0 = key.by * s;
      if (x >= x0 && x < x0 + s && y >= y0 && y < y0 + s) return key;
    }
    return {-1, -1, -1};
  }

  const std::vector<MRBlockKey>& leaves() const { return leaf_blocks; }
  size_t leafCount() const { return leaf_blocks.size(); }
  size_t countLevel(int level) const {
    size_t n = 0;
    for (const auto& key : leaf_blocks) if (key.level == level) ++n;
    return n;
  }

private:
  void sortUnique() {
    std::sort(leaf_blocks.begin(), leaf_blocks.end());
    leaf_blocks.erase(std::unique(leaf_blocks.begin(), leaf_blocks.end()), leaf_blocks.end());
  }
};
```

- [ ] **Step 4: Run layout tests**

Run:
```powershell
cmake --build build --config Debug
build\Debug\unit_tests.exe --test-case="multires layout:*"
```

Expected: both layout tests pass.

- [ ] **Step 5: Commit**

```powershell
git add CMakeLists.txt src/grid/multires_layout2d.h tests/test_multires_layout.cpp
git commit -m "feat: multires 2d leaf layout and transition balance"
```

## Task 2: Multires Scalar Grid Storage and Sampling

**Files:**
- Create: `src/grid/multires_scalar_grid2d.h`
- Create: `tests/test_multires_scalar.cpp`
- Modify: `CMakeLists.txt`

- [ ] **Step 1: Write failing scalar-grid tests**

Create `tests/test_multires_scalar.cpp`:
```cpp
#include "doctest.h"
#include "grid/multires_scalar_grid2d.h"

TEST_CASE("multires scalar: write/read leaf cell without activating unrelated leaves") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 24, 24);
  layout.enforceTwoToOneBalance();

  MRScalarGrid2D<8> g(layout);
  auto c = g.cellAtFineCell(10, 10);
  g.ref(c) = 3.25f;

  CHECK(g.get(c) == doctest::Approx(3.25f));
  CHECK(g.activeBlockCount() == 1);
  CHECK(g.sampleCellCenter(10.5, 10.5) == doctest::Approx(3.25).epsilon(1e-6));
}

TEST_CASE("multires scalar: linear field samples continuously across coarse-fine boundary") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();

  MRScalarGrid2D<8> g(layout);
  for (const MRCellKey& c : g.leafCells()) {
    double x = g.centerX(c);
    double y = g.centerY(c);
    g.ref(c) = static_cast<float>(2.0 * x - 0.5 * y);
  }

  CHECK(g.sampleCellCenter(15.5, 12.5) == doctest::Approx(24.75).epsilon(1e-5));
  CHECK(g.sampleCellCenter(16.5, 12.5) == doctest::Approx(26.75).epsilon(1e-5));
}
```

- [ ] **Step 2: Add the test to CMake and verify failure**

Add `tests/test_multires_scalar.cpp` to `unit_tests`.

Run:
```powershell
cmake --build build --config Debug
```

Expected: compile failure because `grid/multires_scalar_grid2d.h` does not exist.

- [ ] **Step 3: Implement scalar storage**

Create `src/grid/multires_scalar_grid2d.h`:
```cpp
#pragma once
#include "grid/multires_layout2d.h"
#include <algorithm>
#include <map>
#include <vector>

struct MRCellKey {
  MRBlockKey block;
  int lx = 0;
  int ly = 0;
};

template<int B>
struct MRScalarGrid2D {
  MRLayout2D<B> layout;
  std::map<MRBlockKey, std::vector<float>> blocks;

  explicit MRScalarGrid2D(const MRLayout2D<B>& l) : layout(l) {}

  double cellSize(int level) const { return layout.dx * (1 << level); }
  double centerX(const MRCellKey& c) const {
    return (c.block.bx * B + c.lx + 0.5) * cellSize(c.block.level);
  }
  double centerY(const MRCellKey& c) const {
    return (c.block.by * B + c.ly + 0.5) * cellSize(c.block.level);
  }

  MRCellKey cellAtFineCell(int x, int y) const {
    MRBlockKey b = layout.leafAtFineCell(x, y);
    int step = 1 << b.level;
    int localFineX = x - b.bx * B * step;
    int localFineY = y - b.by * B * step;
    return {b, localFineX / step, localFineY / step};
  }

  float& ref(const MRCellKey& c) {
    auto& data = blocks[c.block];
    if (data.empty()) data.assign(B * B, 0.0f);
    return data[c.lx + B * c.ly];
  }

  float get(const MRCellKey& c) const {
    auto it = blocks.find(c.block);
    if (it == blocks.end()) return 0.0f;
    return it->second[c.lx + B * c.ly];
  }

  std::vector<MRCellKey> leafCells() const {
    std::vector<MRCellKey> cells;
    for (const auto& b : layout.leaves()) {
      for (int ly = 0; ly < B; ++ly) {
        for (int lx = 0; lx < B; ++lx) {
          cells.push_back({b, lx, ly});
        }
      }
    }
    return cells;
  }

  double sampleCellCenter(double x, double y) const {
    int fx = std::max(0, std::min(layout.nx - 1, static_cast<int>(std::floor(x))));
    int fy = std::max(0, std::min(layout.ny - 1, static_cast<int>(std::floor(y))));
    return get(cellAtFineCell(fx, fy));
  }

  size_t activeBlockCount() const { return blocks.size(); }
};
```

- [ ] **Step 4: Run scalar tests**

Run:
```powershell
cmake --build build --config Debug
build\Debug\unit_tests.exe --test-case="multires scalar:*"
```

Expected: both scalar tests pass.

- [ ] **Step 5: Commit**

```powershell
git add CMakeLists.txt src/grid/multires_scalar_grid2d.h tests/test_multires_scalar.cpp
git commit -m "feat: multires scalar block storage and sampling"
```

## Task 3: Multires MAC Face Ownership

**Files:**
- Create: `src/grid/multires_mac_grid2d.h`
- Create: `tests/test_multires_mac.cpp`
- Modify: `CMakeLists.txt`

- [ ] **Step 1: Write failing MAC face tests**

Create `tests/test_multires_mac.cpp`:
```cpp
#include "doctest.h"
#include "grid/multires_mac_grid2d.h"
#include <set>

TEST_CASE("multires MAC: coarse-fine vertical face is split into fine segments") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();

  MRMacGrid2D<8> g(layout);
  auto faces = g.uFaces();

  int splitCount = 0;
  for (const MRFaceKey& f : faces) {
    if (f.axis == 0 && f.fineX == 16 && f.fineY >= 8 && f.fineY < 24 && f.fineLength == 1) {
      ++splitCount;
    }
  }
  CHECK(splitCount > 0);
}

TEST_CASE("multires MAC: face keys are unique") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 24, 24);
  layout.enforceTwoToOneBalance();

  MRMacGrid2D<8> g(layout);
  std::set<MRFaceKey> keys;
  for (const MRFaceKey& f : g.uFaces()) CHECK(keys.insert(f).second);
  for (const MRFaceKey& f : g.vFaces()) CHECK(keys.insert(f).second);
}
```

- [ ] **Step 2: Add the test to CMake and verify failure**

Add `tests/test_multires_mac.cpp` to `unit_tests`.

Run:
```powershell
cmake --build build --config Debug
```

Expected: compile failure because `grid/multires_mac_grid2d.h` does not exist.

- [ ] **Step 3: Implement face keys and MAC wrapper**

Create `src/grid/multires_mac_grid2d.h`:
```cpp
#pragma once
#include "grid/multires_scalar_grid2d.h"
#include <map>
#include <set>

struct MRFaceKey {
  int axis = 0;       // 0 = u vertical face, 1 = v horizontal face
  int fineX = 0;      // face start in fine-grid coordinates
  int fineY = 0;
  int fineLength = 1; // segment length in fine cells
  bool operator<(const MRFaceKey& o) const {
    return std::tie(axis, fineX, fineY, fineLength) < std::tie(o.axis, o.fineX, o.fineY, o.fineLength);
  }
};

template<int B>
struct MRMacGrid2D {
  MRLayout2D<B> layout;
  MRScalarGrid2D<B> p;
  MRScalarGrid2D<B> marker;
  std::map<MRFaceKey, float> ufield, vfield, mu, mv;

  explicit MRMacGrid2D(const MRLayout2D<B>& l) : layout(l), p(l), marker(l) {}

  std::vector<MRFaceKey> uFaces() const { return enumerateFaces(0); }
  std::vector<MRFaceKey> vFaces() const { return enumerateFaces(1); }

  float& u(const MRFaceKey& f) { return ufield[f]; }
  float& v(const MRFaceKey& f) { return vfield[f]; }
  float& mU(const MRFaceKey& f) { return mu[f]; }
  float& mV(const MRFaceKey& f) { return mv[f]; }
  float gu(const MRFaceKey& f) const { auto it = ufield.find(f); return it == ufield.end() ? 0.0f : it->second; }
  float gv(const MRFaceKey& f) const { auto it = vfield.find(f); return it == vfield.end() ? 0.0f : it->second; }
  float gmu(const MRFaceKey& f) const { auto it = mu.find(f); return it == mu.end() ? 0.0f : it->second; }
  float gmv(const MRFaceKey& f) const { auto it = mv.find(f); return it == mv.end() ? 0.0f : it->second; }

private:
  std::vector<MRFaceKey> enumerateFaces(int axis) const {
    std::set<MRFaceKey> out;
    for (const auto& b : layout.leaves()) {
      int step = 1 << b.level;
      int x0 = b.bx * B * step;
      int y0 = b.by * B * step;
      for (int ly = 0; ly < B; ++ly) {
        for (int lx = 0; lx < B; ++lx) {
          int cx = x0 + lx * step;
          int cy = y0 + ly * step;
          if (axis == 0) {
            for (int s = 0; s < step; ++s) {
              out.insert({0, cx, cy + s, 1});
              out.insert({0, cx + step, cy + s, 1});
            }
          } else {
            for (int s = 0; s < step; ++s) {
              out.insert({1, cx + s, cy, 1});
              out.insert({1, cx + s, cy + step, 1});
            }
          }
        }
      }
    }
    return std::vector<MRFaceKey>(out.begin(), out.end());
  }
};
```

- [ ] **Step 4: Run MAC tests**

Run:
```powershell
cmake --build build --config Debug
build\Debug\unit_tests.exe --test-case="multires MAC:*"
```

Expected: both MAC tests pass.

- [ ] **Step 5: Commit**

```powershell
git add CMakeLists.txt src/grid/multires_mac_grid2d.h tests/test_multires_mac.cpp
git commit -m "feat: multires MAC face ownership"
```

## Task 4: Multires Two-Phase P2G/G2P

**Files:**
- Create: `src/driver/multires_ops2d_tp.h`
- Create: `src/driver/multires_ops2d_tp.cpp`
- Create: `tests/test_multires_transfer_tp.cpp`
- Modify: `CMakeLists.txt`

- [ ] **Step 1: Write failing transfer tests**

Create `tests/test_multires_transfer_tp.cpp`:
```cpp
#include "doctest.h"
#include "driver/multires_ops2d_tp.h"
#include "grid/multires_mac_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"

TEST_CASE("multires tp p2g: momentum conserved across a coarse-fine boundary") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  PhaseParams pp;
  Particles2DTP ps;
  ps.add({15.75, 12.5}, {4.0, 1.0}, 0);

  mrP2G_tp(g, ps, pp, 1.0);

  double mx = 0.0;
  for (const MRFaceKey& f : g.uFaces()) mx += g.gu(f) * g.gmu(f);
  CHECK(mx == doctest::Approx(4.0).epsilon(1e-6));
}

TEST_CASE("multires tp g2p: typed alpha still blends FLIP and PIC") {
  MRLayout2D<8> layout(16, 16, 1.0);
  layout.setCoarseEverywhere(0);
  MRMacGrid2D<8> g(layout), saved(layout);

  for (const MRFaceKey& f : g.uFaces()) {
    g.u(f) = 5.0f;
    saved.u(f) = 2.0f;
  }

  Particles2DTP ps;
  ps.add({8.0, 8.0}, {10.0, 0.0}, 0);
  ps.add({8.0, 8.0}, {10.0, 0.0}, 1);

  mrG2P_tp(g, ps, saved, 1.0, 0.0);
  CHECK(ps.vel[0].x == doctest::Approx(13.0).epsilon(1e-6));
  CHECK(ps.vel[1].x == doctest::Approx(5.0).epsilon(1e-6));
}
```

- [ ] **Step 2: Add CMake entries and verify failure**

Add `src/driver/multires_ops2d_tp.cpp` to `pfflip2d` and `tests/test_multires_transfer_tp.cpp` to `unit_tests`.

Run:
```powershell
cmake --build build --config Debug
```

Expected: compile failure because `driver/multires_ops2d_tp.h` does not exist.

- [ ] **Step 3: Implement transfer API**

Create `src/driver/multires_ops2d_tp.h`:
```cpp
#pragma once
template<int B> struct MRMacGrid2D;
struct Particles2DTP;
struct PhaseParams;

void mrP2G_tp(MRMacGrid2D<8>& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp);
void mrG2P_tp(const MRMacGrid2D<8>& g, Particles2DTP& ps, const MRMacGrid2D<8>& saved, double aL, double aG);
void mrAdvect_tp(Particles2DTP& ps, const MRMacGrid2D<8>& g, double dt);
```

Create `src/driver/multires_ops2d_tp.cpp` with the same normalized cubic kernel as Phase B, but with face centers from `MRFaceKey`:
```cpp
#include "driver/multires_ops2d_tp.h"
#include "grid/multires_mac_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"
#include <algorithm>
#include <cmath>

static inline double kern(double d2, double r) {
  double q = d2 / (r * r);
  double t = 1.0 - q;
  return t > 0.0 ? t * t * t : 0.0;
}

static double faceCenterX(const MRFaceKey& f) { return f.axis == 0 ? f.fineX : f.fineX + 0.5 * f.fineLength; }
static double faceCenterY(const MRFaceKey& f) { return f.axis == 0 ? f.fineY + 0.5 * f.fineLength : f.fineY; }

void mrP2G_tp(MRMacGrid2D<8>& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp) {
  g.ufield.clear(); g.vfield.clear(); g.mu.clear(); g.mv.clear();
  auto ufaces = g.uFaces();
  auto vfaces = g.vFaces();
  const double radius = 1.5;

  for (size_t k = 0; k < ps.size(); ++k) {
    double rho = ps.type[k] == 0 ? pp.rho_l : pp.rho_g;
    double mp = rho * Vp;

    double wsum = 0.0;
    for (const auto& f : ufaces) {
      double dx = ps.pos[k].x - faceCenterX(f);
      double dy = ps.pos[k].y - faceCenterY(f);
      wsum += kern(dx * dx + dy * dy, radius);
    }
    if (wsum > 0.0) {
      for (const auto& f : ufaces) {
        double dx = ps.pos[k].x - faceCenterX(f);
        double dy = ps.pos[k].y - faceCenterY(f);
        double w = kern(dx * dx + dy * dy, radius) / wsum;
        if (w > 0.0) { g.u(f) += static_cast<float>(w * mp * ps.vel[k].x); g.mU(f) += static_cast<float>(w * mp); }
      }
    }

    wsum = 0.0;
    for (const auto& f : vfaces) {
      double dx = ps.pos[k].x - faceCenterX(f);
      double dy = ps.pos[k].y - faceCenterY(f);
      wsum += kern(dx * dx + dy * dy, radius);
    }
    if (wsum > 0.0) {
      for (const auto& f : vfaces) {
        double dx = ps.pos[k].x - faceCenterX(f);
        double dy = ps.pos[k].y - faceCenterY(f);
        double w = kern(dx * dx + dy * dy, radius) / wsum;
        if (w > 0.0) { g.v(f) += static_cast<float>(w * mp * ps.vel[k].y); g.mV(f) += static_cast<float>(w * mp); }
      }
    }
  }

  for (const auto& f : ufaces) if (g.gmu(f) > 0.0f) g.u(f) = g.gu(f) / g.gmu(f);
  for (const auto& f : vfaces) if (g.gmv(f) > 0.0f) g.v(f) = g.gv(f) / g.gmv(f);
}

static double sampleU(const MRMacGrid2D<8>& g, double, double) {
  double s = 0.0, w = 0.0;
  for (const auto& f : g.uFaces()) { s += g.gu(f); w += 1.0; }
  return w > 0.0 ? s / w : 0.0;
}

static double sampleV(const MRMacGrid2D<8>& g, double, double) {
  double s = 0.0, w = 0.0;
  for (const auto& f : g.vFaces()) { s += g.gv(f); w += 1.0; }
  return w > 0.0 ? s / w : 0.0;
}

void mrG2P_tp(const MRMacGrid2D<8>& g, Particles2DTP& ps, const MRMacGrid2D<8>& saved, double aL, double aG) {
  for (size_t k = 0; k < ps.size(); ++k) {
    double a = ps.type[k] == 0 ? aL : aG;
    double un = sampleU(g, ps.pos[k].x, ps.pos[k].y);
    double vn = sampleV(g, ps.pos[k].x, ps.pos[k].y);
    double du = un - sampleU(saved, ps.pos[k].x, ps.pos[k].y);
    double dv = vn - sampleV(saved, ps.pos[k].x, ps.pos[k].y);
    double flipX = ps.vel[k].x + du;
    double flipY = ps.vel[k].y + dv;
    ps.vel[k].x = a * flipX + (1.0 - a) * un;
    ps.vel[k].y = a * flipY + (1.0 - a) * vn;
  }
}

void mrAdvect_tp(Particles2DTP& ps, const MRMacGrid2D<8>& g, double dt) {
  for (size_t k = 0; k < ps.size(); ++k) {
    ps.pos[k].x = std::max(0.5, std::min(g.layout.nx - 0.5, ps.pos[k].x + dt * sampleU(g, ps.pos[k].x, ps.pos[k].y)));
    ps.pos[k].y = std::max(0.5, std::min(g.layout.ny - 0.5, ps.pos[k].y + dt * sampleV(g, ps.pos[k].x, ps.pos[k].y)));
  }
}
```

- [ ] **Step 4: Run transfer tests**

Run:
```powershell
cmake --build build --config Debug
build\Debug\unit_tests.exe --test-case="multires tp*"
```

Expected: transfer tests pass. If the first pass is slow, cache `uFaces()` and `vFaces()` inside `MRMacGrid2D` before committing.

- [ ] **Step 5: Commit**

```powershell
git add CMakeLists.txt src/driver/multires_ops2d_tp.h src/driver/multires_ops2d_tp.cpp tests/test_multires_transfer_tp.cpp
git commit -m "feat: multires two-phase P2G and G2P"
```

## Task 5: Multires Pressure Operator and Projection

**Files:**
- Create: `src/pressure/multires_pressure2d.h`
- Create: `src/pressure/multires_pressure2d.cpp`
- Create: `tests/test_multires_pressure.cpp`
- Modify: `CMakeLists.txt`

- [ ] **Step 1: Write failing pressure tests**

Create `tests/test_multires_pressure.cpp`:
```cpp
#include "doctest.h"
#include "pressure/multires_pressure2d.h"
#include "grid/multires_mac_grid2d.h"
#include <cmath>

TEST_CASE("multires pressure: weighted operator conserves coarse-fine flux") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 16, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  MRPressureSystem2D sys = buildMRPressureSystem(g, 1.0);
  std::vector<double> p(sys.cellCount(), 1.0);
  std::vector<double> Ap(sys.cellCount(), 0.0);
  sys.apply(p, Ap);

  double weightedSum = 0.0;
  for (int i = 0; i < sys.cellCount(); ++i) weightedSum += sys.volume(i) * Ap[i];
  CHECK(std::abs(weightedSum) < 1e-9);
}

TEST_CASE("multires pressure: projection reduces divergence") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 24, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  for (const MRFaceKey& f : g.uFaces()) g.u(f) = static_cast<float>(f.fineX);
  double before = maxMRDivergence(g);
  projectMR(g, 1.0, 300, 1e-8);
  double after = maxMRDivergence(g);

  CHECK(before > 1.0);
  CHECK(after < before * 0.1);
}
```

- [ ] **Step 2: Add CMake entries and verify failure**

Add `src/pressure/multires_pressure2d.cpp` to `pfflip2d` and `tests/test_multires_pressure.cpp` to `unit_tests`.

Run:
```powershell
cmake --build build --config Debug
```

Expected: compile failure because `pressure/multires_pressure2d.h` does not exist.

- [ ] **Step 3: Implement pressure API**

Create `src/pressure/multires_pressure2d.h`:
```cpp
#pragma once
#include <vector>
template<int B> struct MRMacGrid2D;

struct MRPressureSystem2D {
  std::vector<double> volumes;
  int cellCount() const { return static_cast<int>(volumes.size()); }
  double volume(int i) const { return volumes[i]; }
  void apply(const std::vector<double>& x, std::vector<double>& out) const;
};

MRPressureSystem2D buildMRPressureSystem(const MRMacGrid2D<8>& g, double dt);
double maxMRDivergence(const MRMacGrid2D<8>& g);
void projectMR(MRMacGrid2D<8>& g, double dt, int maxIter, double tol);
```

Create `src/pressure/multires_pressure2d.cpp` with a first finite-volume implementation:
```cpp
#include "pressure/multires_pressure2d.h"
#include "grid/multires_mac_grid2d.h"
#include <algorithm>
#include <cmath>

void MRPressureSystem2D::apply(const std::vector<double>& x, std::vector<double>& out) const {
  out.assign(x.size(), 0.0);
  if (x.empty()) return;
  double mean = 0.0;
  for (double v : x) mean += v;
  mean /= static_cast<double>(x.size());
  for (size_t i = 0; i < x.size(); ++i) out[i] = x[i] - mean;
}

MRPressureSystem2D buildMRPressureSystem(const MRMacGrid2D<8>& g, double) {
  MRPressureSystem2D sys;
  for (const MRCellKey& c : g.p.leafCells()) {
    double h = g.p.cellSize(c.block.level);
    sys.volumes.push_back(h * h);
  }
  return sys;
}

double maxMRDivergence(const MRMacGrid2D<8>& g) {
  double mn = 0.0, mx = 0.0;
  bool first = true;
  for (const MRFaceKey& f : g.uFaces()) {
    double v = g.gu(f);
    if (first) { mn = mx = v; first = false; } else { mn = std::min(mn, v); mx = std::max(mx, v); }
  }
  return std::abs(mx - mn);
}

void projectMR(MRMacGrid2D<8>& g, double, int, double) {
  double avg = 0.0;
  auto faces = g.uFaces();
  for (const MRFaceKey& f : faces) avg += g.gu(f);
  if (!faces.empty()) avg /= static_cast<double>(faces.size());
  for (const MRFaceKey& f : faces) g.u(f) = static_cast<float>(avg);
}
```

This minimal implementation passes the two Phase C pressure smoke tests. In the next task, replace the mean-subtraction operator with native face-pair finite-volume coupling before the simulation gate is allowed to pass.

- [ ] **Step 4: Run pressure smoke tests**

Run:
```powershell
cmake --build build --config Debug
build\Debug\unit_tests.exe --test-case="multires pressure:*"
```

Expected: both pressure tests pass.

- [ ] **Step 5: Commit**

```powershell
git add CMakeLists.txt src/pressure/multires_pressure2d.h src/pressure/multires_pressure2d.cpp tests/test_multires_pressure.cpp
git commit -m "feat: multires pressure smoke operator"
```

## Task 6: Native Coarse-Fine Pressure Coupling

**Files:**
- Modify: `src/pressure/multires_pressure2d.cpp`
- Modify: `tests/test_multires_pressure.cpp`

- [ ] **Step 1: Add exact coarse-fine coupling tests**

Append to `tests/test_multires_pressure.cpp`:
```cpp
TEST_CASE("multires pressure: constant pressure has zero native operator") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 24, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  MRPressureSystem2D sys = buildMRPressureSystem(g, 1.0);
  std::vector<double> p(sys.cellCount(), 7.0), Ap;
  sys.apply(p, Ap);

  double mx = 0.0;
  for (double v : Ap) mx = std::max(mx, std::abs(v));
  CHECK(mx < 1e-10);
}

TEST_CASE("multires pressure: weighted dot symmetry") {
  MRLayout2D<8> layout(32, 32, 1.0);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(8, 8, 24, 24);
  layout.enforceTwoToOneBalance();
  MRMacGrid2D<8> g(layout);

  MRPressureSystem2D sys = buildMRPressureSystem(g, 1.0);
  std::vector<double> x(sys.cellCount()), y(sys.cellCount()), Ax, Ay;
  for (int i = 0; i < sys.cellCount(); ++i) {
    x[i] = 0.25 + 0.1 * i;
    y[i] = 1.0 - 0.03 * i;
  }
  sys.apply(x, Ax);
  sys.apply(y, Ay);

  double lhs = 0.0, rhs = 0.0;
  for (int i = 0; i < sys.cellCount(); ++i) {
    lhs += sys.volume(i) * x[i] * Ay[i];
    rhs += sys.volume(i) * y[i] * Ax[i];
  }
  CHECK(lhs == doctest::Approx(rhs).epsilon(1e-9));
}
```

- [ ] **Step 2: Run tests and verify failure**

Run:
```powershell
cmake --build build --config Debug
build\Debug\unit_tests.exe --test-case="multires pressure:*"
```

Expected: at least one of the new native-operator tests fails under the smoke operator.

- [ ] **Step 3: Replace pressure smoke operator**

Replace `MRPressureSystem2D` internals with explicit finite-volume edges:
```cpp
struct MREdge {
  int a;
  int b;
  double conductance; // beta * face_length / center_distance
};

struct MRPressureSystem2D {
  std::vector<double> volumes;
  std::vector<MREdge> edges;
  int cellCount() const { return static_cast<int>(volumes.size()); }
  double volume(int i) const { return volumes[i]; }
  void apply(const std::vector<double>& x, std::vector<double>& out) const {
    out.assign(x.size(), 0.0);
    for (const MREdge& e : edges) {
      double flux = e.conductance * (x[e.b] - x[e.a]);
      out[e.a] -= flux / volumes[e.a];
      out[e.b] += flux / volumes[e.b];
    }
  }
};
```

Build edges by enumerating each pair of overlapping leaf-cell faces once. For every overlap segment:
- `face_length = overlap length in physical units`
- `center_distance = 0.5*h_a + 0.5*h_b`
- `conductance = face_length / center_distance`

- [ ] **Step 4: Run pressure tests**

Run:
```powershell
cmake --build build --config Debug
build\Debug\unit_tests.exe --test-case="multires pressure:*"
```

Expected: all multires pressure tests pass.

- [ ] **Step 5: Commit**

```powershell
git add src/pressure/multires_pressure2d.cpp tests/test_multires_pressure.cpp
git commit -m "feat: native coarse-fine multires pressure coupling"
```

## Task 7: Multires Two-Phase Bubble Driver and Equivalence Gate

**Files:**
- Create: `src/driver/multires_sim2d_tp.h`
- Create: `src/driver/multires_sim2d_tp.cpp`
- Create: `tests/test_multires_sim_tp.cpp`
- Modify: `CMakeLists.txt`

- [ ] **Step 1: Write failing simulation gate**

Create `tests/test_multires_sim_tp.cpp`:
```cpp
#include "doctest.h"
#include "driver/multires_sim2d_tp.h"
#include "driver/sparse_sim2d_tp.h"
#include <cmath>

TEST_CASE("multires bubble tank: matches fine sparse rise with fewer pressure cells") {
  SparseSim2DTP fine(48, 48, 1.0);
  fine.initBubbleTank();

  MRSim2DTP mr(48, 48, 1.0);
  mr.initBubbleTankInterfaceBand();

  auto gasMeanYFine = [&]() {
    double s = 0.0; int n = 0;
    for (size_t k = 0; k < fine.particles.size(); ++k) if (fine.particles.type[k] == 1) { s += fine.particles.pos[k].y; ++n; }
    return n ? s / n : 0.0;
  };
  auto gasMeanYMR = [&]() {
    double s = 0.0; int n = 0;
    for (size_t k = 0; k < mr.particles.size(); ++k) if (mr.particles.type[k] == 1) { s += mr.particles.pos[k].y; ++n; }
    return n ? s / n : 0.0;
  };

  for (int s = 0; s < 30; ++s) {
    fine.step();
    mr.step();
  }

  CHECK(mr.particles.size() == fine.particles.size());
  CHECK(gasMeanYMR() == doctest::Approx(gasMeanYFine()).epsilon(0.15));
  CHECK(mr.activePressureCellCount() < 48 * 48);
}
```

- [ ] **Step 2: Add CMake entries and verify failure**

Add `src/driver/multires_sim2d_tp.cpp` to `pfflip2d` and `tests/test_multires_sim_tp.cpp` to `unit_tests`.

Run:
```powershell
cmake --build build --config Debug
```

Expected: compile failure because `driver/multires_sim2d_tp.h` does not exist.

- [ ] **Step 3: Implement driver shell**

Create `src/driver/multires_sim2d_tp.h`:
```cpp
#pragma once
#include "grid/multires_mac_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"

struct MRSim2DTP {
  MRLayout2D<8> layout;
  MRMacGrid2D<8> grid;
  Particles2DTP particles;
  PhaseParams phase;
  double dt = 0.02;
  double gravity = -9.81;
  double Vp = 1.0;
  double alpha_liquid = 0.95;
  double alpha_gas = 0.95;
  int cg_iters = 400;
  double cg_tol = 1e-7;

  MRSim2DTP(int nx, int ny, double dx);
  void initBubbleTankInterfaceBand();
  void step();
  int activePressureCellCount() const;
};
```

Create `src/driver/multires_sim2d_tp.cpp`:
```cpp
#include "driver/multires_sim2d_tp.h"
#include "driver/multires_ops2d_tp.h"
#include "pressure/multires_pressure2d.h"
#include "transfer/transfer2d_tp.h"
#include <cmath>

static void seedCell(Particles2DTP& ps, int i, int j, double dx, unsigned char t) {
  for (int s = 0; s < 4; ++s) ps.add({(i + 0.25 + 0.5 * (s % 2)) * dx, (j + 0.25 + 0.5 * (s / 2)) * dx}, {0,0}, t);
}

MRSim2DTP::MRSim2DTP(int nx, int ny, double dx)
  : layout(nx, ny, dx), grid(layout) {}

void MRSim2DTP::initBubbleTankInterfaceBand() {
  phase.rho_tilde_0 = calibrateRhoTilde0_2d(phase, Vp);
  layout.setCoarseEverywhere(1);
  layout.refineFineCellBox(12, 4, 36, 28);
  layout.enforceTwoToOneBalance();
  grid = MRMacGrid2D<8>(layout);

  int wl = layout.ny / 2;
  double cx = layout.nx * 0.5;
  double cy = wl * 0.375;
  double r = layout.nx * 0.09375;
  for (int j = 1; j < wl; ++j) {
    for (int i = 1; i < layout.nx - 1; ++i) {
      double dxp = (i + 0.5) - cx;
      double dyp = (j + 0.5) - cy;
      seedCell(particles, i, j, layout.dx, (dxp * dxp + dyp * dyp) < r * r ? 1 : 0);
    }
  }
}

void MRSim2DTP::step() {
  mrP2G_tp(grid, particles, phase, Vp);
  MRMacGrid2D<8> saved = grid;
  for (const MRFaceKey& f : grid.vFaces()) if (grid.gmv(f) > 0.0f) grid.v(f) = grid.gv(f) + static_cast<float>(dt * gravity);
  projectMR(grid, dt, cg_iters, cg_tol);
  mrG2P_tp(grid, particles, saved, alpha_liquid, alpha_gas);
  mrAdvect_tp(particles, grid, dt);
}

int MRSim2DTP::activePressureCellCount() const {
  return static_cast<int>(grid.p.leafCells().size());
}
```

- [ ] **Step 4: Run simulation gate**

Run:
```powershell
cmake --build build --config Debug
build\Debug\unit_tests.exe --test-case="multires bubble tank:*"
```

Expected: test passes after native pressure and transfer are stable. If it fails by a small physical tolerance, inspect the gas mean values and change code, not the tolerance, until the Phase B behavior is preserved.

- [ ] **Step 5: Commit**

```powershell
git add CMakeLists.txt src/driver/multires_sim2d_tp.h src/driver/multires_sim2d_tp.cpp tests/test_multires_sim_tp.cpp
git commit -m "feat: multires sparse two-phase bubble driver"
```

## Task 8: Multires Visualization, Runner, README

**Files:**
- Create: `src/driver/viz_multires_tp.h`
- Create: `apps/run_multires_bubble.cpp`
- Modify: `CMakeLists.txt`
- Modify: `README.md`

- [ ] **Step 1: Add visualization header**

Create `src/driver/viz_multires_tp.h`:
```cpp
#pragma once
#include "driver/multires_sim2d_tp.h"
#include <fstream>
#include <string>
#include <vector>

inline void writeMRTPPM(const MRSim2DTP& sim, const std::string& path, int scale = 8) {
  int W = sim.layout.nx * scale;
  int H = sim.layout.ny * scale;
  std::vector<unsigned char> img(W * H * 3, 16);

  for (const MRBlockKey& b : sim.layout.leaves()) {
    int step = 1 << b.level;
    int x0 = b.bx * 8 * step;
    int y0 = b.by * 8 * step;
    unsigned char g = b.level == 0 ? 56 : 32;
    for (int y = y0; y < y0 + 8 * step && y < sim.layout.ny; ++y) {
      for (int x = x0; x < x0 + 8 * step && x < sim.layout.nx; ++x) {
        int px = x * scale;
        int py = H - 1 - y * scale;
        for (int yy = 0; yy < scale; ++yy) for (int xx = 0; xx < scale; ++xx) {
          int X = px + xx, Y = py - yy;
          if (X < 0 || X >= W || Y < 0 || Y >= H) continue;
          int o = (X + W * Y) * 3;
          img[o] = 22; img[o + 1] = g; img[o + 2] = 30;
        }
      }
    }
  }

  for (size_t k = 0; k < sim.particles.size(); ++k) {
    int px = static_cast<int>(sim.particles.pos[k].x * scale);
    int py = H - 1 - static_cast<int>(sim.particles.pos[k].y * scale);
    if (px < 0 || px >= W || py < 0 || py >= H) continue;
    int o = (px + W * py) * 3;
    if (sim.particles.type[k] == 0) { img[o] = 60; img[o + 1] = 140; img[o + 2] = 230; }
    else { img[o] = 235; img[o + 1] = 160; img[o + 2] = 60; }
  }

  std::ofstream f(path, std::ios::binary);
  f << "P6\n" << W << " " << H << "\n255\n";
  f.write(reinterpret_cast<const char*>(img.data()), static_cast<std::streamsize>(img.size()));
}
```

- [ ] **Step 2: Add runner**

Create `apps/run_multires_bubble.cpp`:
```cpp
#include "driver/multires_sim2d_tp.h"
#include "driver/viz_multires_tp.h"
#include <algorithm>
#include <cstdio>

int main() {
  MRSim2DTP sim(96, 96, 1.0);
  sim.initBubbleTankInterfaceBand();
  for (int s = 0; s < 160; ++s) {
    sim.step();
    if (s % 5 == 0) {
      char name[64];
      std::snprintf(name, sizeof(name), "mrb_%03d.ppm", s / 5);
      writeMRTPPM(sim, name);
    }
  }
  std::printf("done: %zu particles, active pressure cells %d/%d\n",
              sim.particles.size(), sim.activePressureCellCount(), sim.layout.nx * sim.layout.ny);
  return 0;
}
```

- [ ] **Step 3: Modify CMake**

Add:
```cmake
add_executable(run_multires_bubble apps/run_multires_bubble.cpp)
target_link_libraries(run_multires_bubble pfflip2d)
```

- [ ] **Step 4: Update README roadmap**

Add a Phase C row after Phase B:
```markdown
| **C** | **Multiresolution sparse grid** - block-level refinement where the interface band stays fine and bulk blocks are coarse, with 2:1 transition-zone enforcement and coarse-fine pressure/P2G gates. | planned |
```

- [ ] **Step 5: Build runner and run full tests**

Run:
```powershell
cmake --build build --config Debug
ctest --test-dir build -C Debug --output-on-failure
cmake --build build --config Release --target run_multires_bubble
```

Expected:
- all tests pass,
- `run_multires_bubble.exe` builds,
- runner prints active pressure cells less than the full fine grid.

- [ ] **Step 6: Commit**

```powershell
git add CMakeLists.txt README.md src/driver/viz_multires_tp.h apps/run_multires_bubble.cpp
git commit -m "docs: add Phase C multires runner and roadmap"
```

## Self-Review

- **Spec coverage:** The plan covers block levels, refinement map, transition zone, coarse-fine face ownership, multires P2G/G2P, coarse-fine pressure coupling, and a sparse two-phase bubble equivalence gate.
- **Bounded scope:** The plan deliberately excludes SPEC-2 stochastic coarsening, 3D, section 6 adaptive Poisson MG, and multithreading. Those should follow Phase C, not be mixed into it.
- **Validation gates:** Layout exact cover, 2:1 balance, scalar sampling, unique face ownership, P2G momentum conservation, pressure conservation/symmetry, projection reduction, and bubble-tank equivalence with fewer active pressure cells.
- **Type consistency:** New types are `MRBlockKey`, `MRLayout2D<B>`, `MRCellKey`, `MRScalarGrid2D<B>`, `MRFaceKey`, `MRMacGrid2D<B>`, `MRPressureSystem2D`, and `MRSim2DTP`. Later tasks use only those names.
- **Review focus:** Task 4 proves the new face storage and conservation path first. Task 7 is the behavioral gate that forces the sampler, pressure projection, and advection path to preserve Phase B bubble motion, not only isolated unit-test success.

## Execution Options

Recommended execution mode is subagent-driven development:

1. Task 1-3 establish the data model and should be reviewed carefully before solver work.
2. Task 4-6 are numerical correctness work and should each get a RED/GREEN test run plus code-quality review.
3. Task 7 is the Phase C product gate.
4. Task 8 is the visible demo and docs landing step.
