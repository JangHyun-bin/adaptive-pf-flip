# PF-FLIP Phase 0 — 2D 단상 FLIP 코어 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 균일 2D MAC 격자 위에서 동작하는 단상(single-phase) FLIP/PIC 유체 솔버를 TDD로 구축하고 2D dam-break로 검증한다. (SPEC-1 Phase 0 = 이후 phase-field 2상·MSBG 통합의 토대)

**Architecture:** MAC staggered 격자(속도=면, 압력=셀중심). P2G 질량·운동량 전송 → 중력 → 압력투영(CG) → FLIP/PIC 혼합 G2P → RK2 이류. 모듈은 단일 책임·독립 테스트. MSBG 교체는 Phase 3.

**Tech Stack:** C++17, CMake, doctest(단일 헤더), 자체 Vec2. (MSBG/TBB는 Phase 3에서 도입.)

---

## File Structure

| 파일 | 책임 |
|---|---|
| `CMakeLists.txt` | 빌드·테스트(CTest) |
| `external/doctest.h` | 단일 헤더 테스트 프레임워크 |
| `src/math/vec2.h` | 2D 벡터 수학 (header-only) |
| `src/grid/uniform_grid2d.h`/`.cpp` | MAC 격자: 면속도·셀압력·질량누적·마커 |
| `src/particles/particles2d.h` | 입자 컨테이너 |
| `src/transfer/transfer2d.h`/`.cpp` | P2G/G2P + bilinear 샘플 |
| `src/pressure/pressure2d.h`/`.cpp` | 발산·Poisson CG·투영 |
| `src/advect/advect2d.h`/`.cpp` | RK2 이류 |
| `src/driver/sim2d.h`/`.cpp` | 스텝 루프, dam-break 씬 |
| `tests/*.cpp` | 모듈별 회귀 테스트 |

**MAC 규약:** `u`(x-면) 크기 `(nx+1)*ny`, idx `i+(nx+1)*j`, i∈[0,nx], j∈[0,ny). `v`(y-면) 크기 `nx*(ny+1)`, idx `i+nx*j`. `p`/`marker`(셀) 크기 `nx*ny`. u-면(i,j) 중심 world `(ox+i·dx, oy+(j+0.5)·dx)`; v-면(i,j) 중심 `(ox+(i+0.5)·dx, oy+j·dx)`.

---

## Task 1: 프로젝트 스켈레톤 + 테스트 하니스

**Files:** Create `CMakeLists.txt`, `external/doctest.h`, `tests/test_main.cpp`, `tests/test_sanity.cpp`, `.gitignore`; stub `.cpp`들.

- [ ] **Step 1: git 초기화 + 디렉토리 생성**

Run (PowerShell):
```powershell
cd D:/HB/Rhizome/lsfs
if (-not (Test-Path .git)) { git init }
New-Item -ItemType Directory -Force external,src/math,src/grid,src/particles,src/transfer,src/pressure,src/advect,src/driver,tests,apps | Out-Null
```

- [ ] **Step 2: doctest 받기**

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/doctest/doctest/v2.4.11/doctest/doctest.h" -OutFile external/doctest.h
```
Expected: `external/doctest.h` (~250KB).

- [ ] **Step 3: 테스트 메인**

`tests/test_main.cpp`:
```cpp
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"
```

- [ ] **Step 4: `.gitignore`**
```
/build/
*.o
*.obj
*.ppm
```

- [ ] **Step 5: CMake**

`CMakeLists.txt`:
```cmake
cmake_minimum_required(VERSION 3.16)
project(pfflip2d CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
include_directories(external src)
enable_testing()
add_library(pfflip2d
  src/grid/uniform_grid2d.cpp
  src/transfer/transfer2d.cpp
  src/pressure/pressure2d.cpp
  src/advect/advect2d.cpp
  src/driver/sim2d.cpp)
add_executable(unit_tests
  tests/test_main.cpp
  tests/test_sanity.cpp)
target_link_libraries(unit_tests pfflip2d)
add_test(NAME unit_tests COMMAND unit_tests)
```

- [ ] **Step 6: sanity 테스트**

`tests/test_sanity.cpp`:
```cpp
#include "doctest.h"
TEST_CASE("harness works") { CHECK(1 + 1 == 2); }
```

- [ ] **Step 7: 빈 소스 stub (CMake 링크용)**

```powershell
foreach ($f in "src/grid/uniform_grid2d.cpp","src/transfer/transfer2d.cpp","src/pressure/pressure2d.cpp","src/advect/advect2d.cpp","src/driver/sim2d.cpp") { if (-not (Test-Path $f)) { New-Item -ItemType File $f | Out-Null } }
```

- [ ] **Step 8: 빌드·테스트**

```powershell
cmake -S . -B build; cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure
```
Expected: `unit_tests` PASS (1 case).

- [ ] **Step 9: Commit**
```powershell
git add -A; git commit -m "chore: scaffold pfflip2d with doctest harness"
```

---

## Task 2: Vec2 수학 타입

**Files:** Create `src/math/vec2.h`, `tests/test_vec2.cpp`; Modify `CMakeLists.txt`.

- [ ] **Step 1: 실패 테스트**

`tests/test_vec2.cpp`:
```cpp
#include "doctest.h"
#include "math/vec2.h"
TEST_CASE("vec2 ops") {
  Vec2 a{1.0,2.0}, b{3.0,4.0};
  CHECK((a+b).x == doctest::Approx(4.0));
  CHECK((b-a).y == doctest::Approx(2.0));
  CHECK((a*2.0).x == doctest::Approx(2.0));
  CHECK(dot(a,b) == doctest::Approx(11.0));
  CHECK(a.length() == doctest::Approx(std::sqrt(5.0)));
}
```

- [ ] **Step 2: CMake에 `tests/test_vec2.cpp` 추가 → 빌드 FAIL 확인**

`unit_tests` 소스 목록에 추가 후:
```powershell
cmake -S . -B build; cmake --build build --config Debug
```
Expected: FAIL (`vec2.h` 없음).

- [ ] **Step 3: 구현**

`src/math/vec2.h`:
```cpp
#pragma once
#include <cmath>
struct Vec2 {
  double x = 0.0, y = 0.0;
  Vec2 operator+(const Vec2& o) const { return {x+o.x, y+o.y}; }
  Vec2 operator-(const Vec2& o) const { return {x-o.x, y-o.y}; }
  Vec2 operator*(double s) const { return {x*s, y*s}; }
  Vec2& operator+=(const Vec2& o) { x+=o.x; y+=o.y; return *this; }
  double length() const { return std::sqrt(x*x + y*y); }
};
inline double dot(const Vec2& a, const Vec2& b) { return a.x*b.x + a.y*b.y; }
```

- [ ] **Step 4: 빌드·테스트 PASS**
```powershell
cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure
```

- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: add Vec2"`

---

## Task 3: UniformGrid2D (MAC 격자)

**Files:** Create `src/grid/uniform_grid2d.h`, `tests/test_grid.cpp`; Modify `CMakeLists.txt`. (`uniform_grid2d.cpp`는 헤더 전용이라 빈 채로 둠.)

- [ ] **Step 1: 실패 테스트**

`tests/test_grid.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid2d.h"
TEST_CASE("grid sizes and access") {
  UniformGrid2D g(4,3,0.5);
  CHECK(g.nx == 4); CHECK(g.ny == 3);
  CHECK(g.u_size() == (4+1)*3);
  CHECK(g.v_size() == 4*(3+1));
  CHECK(g.cell_size() == 4*3);
  g.u(2,1) = 7.0;  CHECK(g.u(2,1) == doctest::Approx(7.0));
  g.p(3,2) = -1.5; CHECK(g.p(3,2) == doctest::Approx(-1.5));
  g.clear();       CHECK(g.u(2,1) == doctest::Approx(0.0));
}
```

- [ ] **Step 2: CMake에 `tests/test_grid.cpp` 추가 → 빌드 FAIL 확인**

- [ ] **Step 3: 헤더 구현**

`src/grid/uniform_grid2d.h`:
```cpp
#pragma once
#include <vector>
#include <cstddef>
#include <algorithm>

enum class Cell : unsigned char { AIR = 0, FLUID = 1, SOLID = 2 };

struct UniformGrid2D {
  int nx, ny;
  double dx;
  double ox = 0.0, oy = 0.0;

  std::vector<double> ufield, vfield;   // 면 속도
  std::vector<double> mu, mv;           // 면 질량
  std::vector<double> pfield;           // 셀 압력
  std::vector<Cell> marker;             // 셀 타입

  UniformGrid2D(int nx_, int ny_, double dx_)
      : nx(nx_), ny(ny_), dx(dx_),
        ufield((nx_+1)*ny_, 0.0), vfield(nx_*(ny_+1), 0.0),
        mu((nx_+1)*ny_, 0.0), mv(nx_*(ny_+1), 0.0),
        pfield(nx_*ny_, 0.0), marker(nx_*ny_, Cell::AIR) {}

  size_t u_size() const { return ufield.size(); }
  size_t v_size() const { return vfield.size(); }
  size_t cell_size() const { return pfield.size(); }

  double& u(int i, int j) { return ufield[i + (nx+1)*j]; }
  double& v(int i, int j) { return vfield[i + nx*j]; }
  double& p(int i, int j) { return pfield[i + nx*j]; }
  Cell& cell(int i, int j) { return marker[i + nx*j]; }

  bool inBounds(int i, int j) const { return i>=0 && i<nx && j>=0 && j<ny; }

  void clear() {
    std::fill(ufield.begin(), ufield.end(), 0.0);
    std::fill(vfield.begin(), vfield.end(), 0.0);
    std::fill(mu.begin(), mu.end(), 0.0);
    std::fill(mv.begin(), mv.end(), 0.0);
    std::fill(pfield.begin(), pfield.end(), 0.0);
  }
};
```
> 벡터 멤버는 `ufield/vfield/pfield`(접근자 함수 `u/v/p`와 이름 충돌 회피). `mu/mv`는 P2G에서 채운다.

- [ ] **Step 4: 빌드·테스트 PASS**
```powershell
cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure
```

- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: UniformGrid2D MAC grid"`

---

## Task 4: Particles2D

**Files:** Create `src/particles/particles2d.h`, `tests/test_particles.cpp`; Modify `CMakeLists.txt`.

- [ ] **Step 1: 실패 테스트**

`tests/test_particles.cpp`:
```cpp
#include "doctest.h"
#include "particles/particles2d.h"
TEST_CASE("particles add/size") {
  Particles2D ps;
  CHECK(ps.size() == 0);
  ps.add({1.0,2.0}, {0.0,-1.0});
  ps.add({3.0,4.0}, {0.5,0.0});
  CHECK(ps.size() == 2);
  CHECK(ps.pos[1].x == doctest::Approx(3.0));
  CHECK(ps.vel[0].y == doctest::Approx(-1.0));
}
```

- [ ] **Step 2: CMake에 추가 → 빌드 FAIL 확인**

- [ ] **Step 3: 구현**

`src/particles/particles2d.h`:
```cpp
#pragma once
#include <vector>
#include "math/vec2.h"
struct Particles2D {
  std::vector<Vec2> pos, vel;
  size_t size() const { return pos.size(); }
  void add(const Vec2& p, const Vec2& vv) { pos.push_back(p); vel.push_back(vv); }
};
```

- [ ] **Step 4: 빌드·테스트 PASS**
```powershell
cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure
```

- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: Particles2D"`

---

## Task 5: P2G 전송

**Files:** Create `src/transfer/transfer2d.h`, `tests/test_p2g.cpp`; Modify `src/transfer/transfer2d.cpp`, `CMakeLists.txt`.

알고리즘: 입자(질량 `m_p=1`)를 인접 면에 bilinear 가중으로 운동량·질량 누적 → 면속도=운동량/질량. (Eq.6 cubic 커널은 Phase 2.)

- [ ] **Step 1: 실패 테스트**

`tests/test_p2g.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d.h"
#include "transfer/transfer2d.h"
TEST_CASE("p2g single particle at u-node gives its vx") {
  UniformGrid2D g(4,4,1.0);
  Particles2D ps; ps.add({2.0,1.5}, {3.0,-7.0});  // u-면(2,1) 중심=(2.0,1.5)
  p2g(g, ps);
  CHECK(g.u(2,1) == doctest::Approx(3.0));
  CHECK(g.mu[2 + (g.nx+1)*1] == doctest::Approx(1.0));
}
TEST_CASE("p2g conserves momentum across two u-nodes") {
  UniformGrid2D g(4,4,1.0);
  Particles2D ps; ps.add({2.5,1.5}, {4.0,0.0});   // 두 면에 50:50
  p2g(g, ps);
  double mom = g.u(2,1)*g.mu[2+5*1] + g.u(3,1)*g.mu[3+5*1];
  CHECK(mom == doctest::Approx(4.0));
}
```

- [ ] **Step 2: CMake에 추가 → 빌드 FAIL 확인**

- [ ] **Step 3: 헤더 + P2G 구현**

`src/transfer/transfer2d.h`:
```cpp
#pragma once
struct UniformGrid2D;
struct Particles2D;
void p2g(UniformGrid2D& g, const Particles2D& ps);
void g2p(const UniformGrid2D& g, Particles2D& ps,
         const UniformGrid2D& saved, double alpha);
double sampleU(const UniformGrid2D& g, double px, double py);
double sampleV(const UniformGrid2D& g, double px, double py);
```

`src/transfer/transfer2d.cpp`:
```cpp
#include "transfer/transfer2d.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d.h"
#include <algorithm>
#include <cmath>

static void splat(std::vector<double>& field, std::vector<double>& mass,
                  int stride_w, int w, int h, double gx, double gy,
                  double mom, double m) {
  int i0 = (int)std::floor(gx), j0 = (int)std::floor(gy);
  double fx = gx - i0, fy = gy - j0;
  double wgt[2][2] = {{(1-fx)*(1-fy), fx*(1-fy)}, {(1-fx)*fy, fx*fy}};
  for (int dj = 0; dj < 2; ++dj)
    for (int di = 0; di < 2; ++di) {
      int ii = i0+di, jj = j0+dj;
      if (ii < 0 || ii >= w || jj < 0 || jj >= h) continue;
      int idx = ii + stride_w*jj;
      field[idx] += wgt[dj][di]*mom;
      mass[idx]  += wgt[dj][di]*m;
    }
}

void p2g(UniformGrid2D& g, const Particles2D& ps) {
  std::fill(g.ufield.begin(), g.ufield.end(), 0.0);
  std::fill(g.vfield.begin(), g.vfield.end(), 0.0);
  std::fill(g.mu.begin(), g.mu.end(), 0.0);
  std::fill(g.mv.begin(), g.mv.end(), 0.0);
  const double m_p = 1.0;
  for (size_t k = 0; k < ps.size(); ++k) {
    double px = (ps.pos[k].x - g.ox)/g.dx;
    double py = (ps.pos[k].y - g.oy)/g.dx;
    splat(g.ufield, g.mu, g.nx+1, g.nx+1, g.ny, px, py-0.5, m_p*ps.vel[k].x, m_p);
    splat(g.vfield, g.mv, g.nx,   g.nx,   g.ny+1, px-0.5, py, m_p*ps.vel[k].y, m_p);
  }
  for (size_t i = 0; i < g.ufield.size(); ++i) if (g.mu[i] > 0.0) g.ufield[i] /= g.mu[i];
  for (size_t i = 0; i < g.vfield.size(); ++i) if (g.mv[i] > 0.0) g.vfield[i] /= g.mv[i];
}

double sampleU(const UniformGrid2D& g, double px, double py) {
  const std::vector<double>& f = g.ufield;
  int w = g.nx+1, h = g.ny, stride = g.nx+1;
  double gx = px, gy = py - 0.5;
  int i0 = (int)std::floor(gx), j0 = (int)std::floor(gy);
  double fx = gx-i0, fy = gy-j0;
  auto get = [&](int ii, int jj)->double {
    ii = std::max(0, std::min(w-1, ii)); jj = std::max(0, std::min(h-1, jj));
    return f[ii + stride*jj]; };
  return (1-fx)*(1-fy)*get(i0,j0) + fx*(1-fy)*get(i0+1,j0)
       + (1-fx)*fy*get(i0,j0+1) + fx*fy*get(i0+1,j0+1);
}
double sampleV(const UniformGrid2D& g, double px, double py) {
  const std::vector<double>& f = g.vfield;
  int w = g.nx, h = g.ny+1, stride = g.nx;
  double gx = px - 0.5, gy = py;
  int i0 = (int)std::floor(gx), j0 = (int)std::floor(gy);
  double fx = gx-i0, fy = gy-j0;
  auto get = [&](int ii, int jj)->double {
    ii = std::max(0, std::min(w-1, ii)); jj = std::max(0, std::min(h-1, jj));
    return f[ii + stride*jj]; };
  return (1-fx)*(1-fy)*get(i0,j0) + fx*(1-fy)*get(i0+1,j0)
       + (1-fx)*fy*get(i0,j0+1) + fx*fy*get(i0+1,j0+1);
}

void g2p(const UniformGrid2D& g, Particles2D& ps,
         const UniformGrid2D& saved, double alpha) {
  for (size_t k = 0; k < ps.size(); ++k) {
    double px = (ps.pos[k].x - g.ox)/g.dx;
    double py = (ps.pos[k].y - g.oy)/g.dx;
    double u_new = sampleU(g, px, py), v_new = sampleV(g, px, py);
    double du = u_new - sampleU(saved, px, py);
    double dv = v_new - sampleV(saved, px, py);
    Vec2 pic{u_new, v_new};
    Vec2 flip{ps.vel[k].x + du, ps.vel[k].y + dv};
    ps.vel[k] = flip*alpha + pic*(1.0 - alpha);
  }
}
```
> `g2p`와 `sampleU/sampleV`는 Task 6에서 테스트하지만, 컴파일 단위 분리를 피하려 여기서 함께 정의한다(헤더 선언은 위에 포함). Task 6은 테스트만 추가한다.

- [ ] **Step 4: 빌드·테스트 PASS**
```powershell
cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure
```

- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: P2G/G2P + bilinear sampling"`

---

## Task 6: G2P 동작 검증 (FLIP/PIC)

**Files:** Create `tests/test_g2p.cpp`; Modify `CMakeLists.txt`. (구현은 Task 5에 포함; 본 태스크는 동작 검증.)

- [ ] **Step 1: 실패 테스트**

`tests/test_g2p.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d.h"
#include "transfer/transfer2d.h"
TEST_CASE("g2p PIC (alpha=0) takes grid velocity") {
  UniformGrid2D g(4,4,1.0), saved(4,4,1.0);
  std::fill(g.ufield.begin(), g.ufield.end(), 5.0);
  std::fill(saved.ufield.begin(), saved.ufield.end(), 0.0);
  Particles2D ps; ps.add({2.0,2.0}, {1.0,1.0});
  g2p(g, ps, saved, 0.0);
  CHECK(ps.vel[0].x == doctest::Approx(5.0));
}
TEST_CASE("g2p FLIP (alpha=1) adds delta") {
  UniformGrid2D g(4,4,1.0), saved(4,4,1.0);
  std::fill(g.ufield.begin(), g.ufield.end(), 5.0);
  std::fill(saved.ufield.begin(), saved.ufield.end(), 2.0);
  Particles2D ps; ps.add({2.0,2.0}, {10.0,0.0});
  g2p(g, ps, saved, 1.0);
  CHECK(ps.vel[0].x == doctest::Approx(13.0));  // 10 + (5-2)
}
```

- [ ] **Step 2: CMake에 `tests/test_g2p.cpp` 추가 → 빌드·테스트 실행**
```powershell
cmake -S . -B build; cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure
```
Expected: PASS (구현은 Task 5에 이미 존재).

- [ ] **Step 3: Commit** — `git add -A; git commit -m "test: G2P FLIP/PIC behavior"`

---

## Task 7: 발산 계산

**Files:** Create `src/pressure/pressure2d.h`, `tests/test_divergence.cpp`; Modify `src/pressure/pressure2d.cpp`, `CMakeLists.txt`.

- [ ] **Step 1: 실패 테스트**

`tests/test_divergence.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "pressure/pressure2d.h"
TEST_CASE("divergence of linear u field") {
  UniformGrid2D g(2,2,0.5);
  for (int j=0;j<g.ny;++j) for (int i=0;i<=g.nx;++i) g.u(i,j) = (double)i;
  auto d = divergence(g);
  CHECK(d[0] == doctest::Approx(2.0));  // (u(i+1)-u(i))/dx = 1/0.5
  CHECK(d[3] == doctest::Approx(2.0));
}
```

- [ ] **Step 2: CMake에 추가 → 빌드 FAIL 확인**

- [ ] **Step 3: 헤더 + divergence 구현**

`src/pressure/pressure2d.h`:
```cpp
#pragma once
#include <vector>
struct UniformGrid2D;
std::vector<double> divergence(const UniformGrid2D& g);
double solvePressure(UniformGrid2D& g, const std::vector<double>& div,
                     double dt, double rho, int max_iter, double tol);
void project(UniformGrid2D& g, double dt, double rho);
```

`src/pressure/pressure2d.cpp`:
```cpp
#include "pressure/pressure2d.h"
#include "grid/uniform_grid2d.h"
#include <cmath>
#include <algorithm>

std::vector<double> divergence(const UniformGrid2D& g) {
  UniformGrid2D& gm = const_cast<UniformGrid2D&>(g);
  std::vector<double> d(g.nx*g.ny, 0.0);
  for (int j=0;j<g.ny;++j) for (int i=0;i<g.nx;++i) {
    double du = gm.u(i+1,j) - gm.u(i,j);
    double dv = gm.v(i,j+1) - gm.v(i,j);
    d[i + g.nx*j] = (du + dv)/g.dx;
  }
  return d;
}
```
> 접근자 `u/v`가 non-const라 `const_cast`. (const 접근자는 YAGNI — 후속에 필요시 추가.)

- [ ] **Step 4: 빌드·테스트 PASS**
```powershell
cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure
```

- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: MAC divergence"`

---

## Task 8: 압력 Poisson CG + 투영

**Files:** Create `tests/test_pressure.cpp`; Modify `src/pressure/pressure2d.cpp`, `CMakeLists.txt`.

선형계(유체 셀): `scale·(diag·p_c − Σ_fluidNbr p_n) = −div_c`, `scale = dt/(rho·dx²)`, `diag` = (SOLID 아닌 이웃 수). AIR 이웃은 `p=0`(Dirichlet). SOLID 이웃은 제외(Neumann). 행렬-프리 CG + 대각 전처리.

- [ ] **Step 1: 실패 테스트**

`tests/test_pressure.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "pressure/pressure2d.h"
#include <cmath>
TEST_CASE("projection removes divergence in fluid") {
  UniformGrid2D g(8,8,1.0);
  for (int j=0;j<g.ny;++j) for (int i=0;i<g.nx;++i)
    g.cell(i,j) = (i>=2&&i<6&&j>=2&&j<6) ? Cell::FLUID : Cell::AIR;
  for (int j=0;j<g.ny;++j){ g.cell(0,j)=Cell::SOLID; g.cell(g.nx-1,j)=Cell::SOLID; }
  for (int i=0;i<g.nx;++i){ g.cell(i,0)=Cell::SOLID; g.cell(i,g.ny-1)=Cell::SOLID; }
  for (int j=0;j<g.ny;++j) for (int i=0;i<=g.nx;++i) g.u(i,j) = (double)i;
  auto d0 = divergence(g);
  solvePressure(g, d0, 1.0, 1.0, 500, 1e-9);
  project(g, 1.0, 1.0);
  auto d1 = divergence(g);
  double maxdiv = 0.0;
  for (int j=0;j<g.ny;++j) for (int i=0;i<g.nx;++i)
    if (g.cell(i,j)==Cell::FLUID) maxdiv = std::max(maxdiv, std::abs(d1[i+g.nx*j]));
  CHECK(maxdiv < 1e-5);
}
```

- [ ] **Step 2: CMake에 추가 → 빌드 FAIL 확인** (`solvePressure`/`project` 미정의)

- [ ] **Step 3: CG + 투영 구현 (pressure2d.cpp에 추가)**

```cpp
namespace {
inline bool isFluid(UniformGrid2D& g, int i, int j) {
  return g.inBounds(i,j) && g.cell(i,j) == Cell::FLUID;
}
inline bool isSolid(UniformGrid2D& g, int i, int j) {
  return !g.inBounds(i,j) || g.cell(i,j) == Cell::SOLID;
}
void applyA(UniformGrid2D& g, double scale,
            const std::vector<double>& x, std::vector<double>& out) {
  const int di[4]={1,-1,0,0}, dj[4]={0,0,1,-1};
  for (int j=0;j<g.ny;++j) for (int i=0;i<g.nx;++i) {
    int c = i + g.nx*j; out[c] = 0.0;
    if (!isFluid(g,i,j)) continue;
    double diag=0.0, off=0.0;
    for (int n=0;n<4;++n){
      int ni=i+di[n], nj=j+dj[n];
      if (isSolid(g,ni,nj)) continue;
      diag += 1.0;
      if (isFluid(g,ni,nj)) off += x[ni + g.nx*nj];
    }
    out[c] = scale*(diag*x[c] - off);
  }
}
double diagOf(UniformGrid2D& g, double scale, int i, int j) {
  const int di[4]={1,-1,0,0}, dj[4]={0,0,1,-1}; double d=0.0;
  for (int n=0;n<4;++n) if (!isSolid(g,i+di[n],j+dj[n])) d+=1.0;
  return scale*d;
}
} // namespace

double solvePressure(UniformGrid2D& g, const std::vector<double>& div,
                     double dt, double rho, int max_iter, double tol) {
  int N = g.nx*g.ny;
  double scale = dt/(rho*g.dx*g.dx);
  std::vector<double> x(N,0.0), r(N,0.0), z(N,0.0), pdir(N,0.0), Ap(N,0.0);
  for (int j=0;j<g.ny;++j) for (int i=0;i<g.nx;++i) {
    int c=i+g.nx*j; r[c] = isFluid(g,i,j) ? -div[c] : 0.0;
  }
  auto precond = [&](const std::vector<double>& in, std::vector<double>& outv){
    for (int j=0;j<g.ny;++j) for (int i=0;i<g.nx;++i){
      int c=i+g.nx*j; double d = isFluid(g,i,j)? diagOf(g,scale,i,j):0.0;
      outv[c] = (d>0.0)? in[c]/d : 0.0; } };
  auto dotp = [&](const std::vector<double>& a, const std::vector<double>& b){
    double s=0.0; for (int k=0;k<N;++k) s+=a[k]*b[k]; return s; };

  double res0 = 0.0; for (int k=0;k<N;++k) res0 = std::max(res0, std::abs(r[k]));
  if (res0 < tol) { g.pfield = x; return res0; }
  precond(r, z); pdir = z;
  double rz = dotp(r, z), res = res0;
  for (int it=0; it<max_iter; ++it) {
    applyA(g, scale, pdir, Ap);
    double pAp = dotp(pdir, Ap);
    if (std::abs(pAp) < 1e-30) break;
    double alpha = rz/pAp;
    for (int k=0;k<N;++k){ x[k]+=alpha*pdir[k]; r[k]-=alpha*Ap[k]; }
    res=0.0; for (int k=0;k<N;++k) res=std::max(res,std::abs(r[k]));
    if (res < tol) break;
    precond(r, z);
    double rz_new = dotp(r, z), beta = rz_new/rz; rz = rz_new;
    for (int k=0;k<N;++k) pdir[k] = z[k] + beta*pdir[k];
  }
  g.pfield = x; return res;
}

void project(UniformGrid2D& g, double dt, double rho) {
  double scale = dt/(rho*g.dx);
  for (int j=0;j<g.ny;++j) for (int i=1;i<g.nx;++i) {
    if (isSolid(g,i-1,j) || isSolid(g,i,j)) { g.u(i,j)=0.0; continue; }
    bool lf=isFluid(g,i-1,j), rf=isFluid(g,i,j);
    if (lf||rf) {
      double pl = lf? g.p(i-1,j):0.0, pr = rf? g.p(i,j):0.0;
      g.u(i,j) -= scale*(pr-pl);
    }
  }
  for (int j=1;j<g.ny;++j) for (int i=0;i<g.nx;++i) {
    if (isSolid(g,i,j-1) || isSolid(g,i,j)) { g.v(i,j)=0.0; continue; }
    bool bf=isFluid(g,i,j-1), tf=isFluid(g,i,j);
    if (bf||tf) {
      double pb = bf? g.p(i,j-1):0.0, pt = tf? g.p(i,j):0.0;
      g.v(i,j) -= scale*(pt-pb);
    }
  }
}
```

- [ ] **Step 4: 빌드·테스트 PASS** (유체 셀 발산 < 1e-5)
```powershell
cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure
```

- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: pressure CG solver + projection"`

---

## Task 9: RK2 이류

**Files:** Create `src/advect/advect2d.h`, `tests/test_advect.cpp`; Modify `src/advect/advect2d.cpp`, `CMakeLists.txt`.

- [ ] **Step 1: 실패 테스트**

`tests/test_advect.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d.h"
#include "advect/advect2d.h"
#include <algorithm>
TEST_CASE("advect moves particle linearly in uniform field") {
  UniformGrid2D g(10,10,1.0);
  std::fill(g.ufield.begin(), g.ufield.end(), 2.0);
  Particles2D ps; ps.add({5.0,5.0}, {2.0,0.0});
  advect(ps, g, 0.5);
  CHECK(ps.pos[0].x == doctest::Approx(6.0));
  CHECK(ps.pos[0].y == doctest::Approx(5.0));
}
TEST_CASE("advect clamps to domain") {
  UniformGrid2D g(10,10,1.0);
  std::fill(g.ufield.begin(), g.ufield.end(), 100.0);
  Particles2D ps; ps.add({9.0,5.0}, {100.0,0.0});
  advect(ps, g, 1.0);
  CHECK(ps.pos[0].x <= 10.0 - 0.5);
}
```

- [ ] **Step 2: CMake에 추가 → 빌드 FAIL 확인**

- [ ] **Step 3: 구현**

`src/advect/advect2d.h`:
```cpp
#pragma once
struct UniformGrid2D;
struct Particles2D;
void advect(Particles2D& ps, const UniformGrid2D& g, double dt);
```
`src/advect/advect2d.cpp`:
```cpp
#include "advect/advect2d.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d.h"
#include "transfer/transfer2d.h"
#include <algorithm>

void advect(Particles2D& ps, const UniformGrid2D& g, double dt) {
  double lo_x = g.ox + 0.5*g.dx, hi_x = g.ox + (g.nx-0.5)*g.dx;
  double lo_y = g.oy + 0.5*g.dx, hi_y = g.oy + (g.ny-0.5)*g.dx;
  for (size_t k=0;k<ps.size();++k) {
    double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    double u1=sampleU(g,px,py), v1=sampleV(g,px,py);
    double mx=ps.pos[k].x+0.5*dt*u1, my=ps.pos[k].y+0.5*dt*v1;
    double mpx=(mx-g.ox)/g.dx, mpy=(my-g.oy)/g.dx;
    double u2=sampleU(g,mpx,mpy), v2=sampleV(g,mpx,mpy);
    double nx_=ps.pos[k].x+dt*u2, ny_=ps.pos[k].y+dt*v2;
    ps.pos[k].x = std::max(lo_x, std::min(hi_x, nx_));
    ps.pos[k].y = std::max(lo_y, std::min(hi_y, ny_));
  }
}
```

- [ ] **Step 4: 빌드·테스트 PASS**
```powershell
cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure
```

- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: RK2 advection with domain clamp"`

---

## Task 10: Sim 드라이버 + dam-break 통합 테스트

**Files:** Create `src/driver/sim2d.h`, `tests/test_sim.cpp`; Modify `src/driver/sim2d.cpp`, `CMakeLists.txt`.

스텝 순서: `markCells → p2g → saved=grid스냅샷 → 중력 → 솔리드 경계 → divergence → solvePressure → project → g2p(saved,alpha) → advect`.

- [ ] **Step 1: 실패 통합 테스트**

`tests/test_sim.cpp`:
```cpp
#include "doctest.h"
#include "driver/sim2d.h"
#include <cmath>
#include <algorithm>
TEST_CASE("dam break stable + particle count conserved") {
  Sim2D sim(32,32,1.0);
  sim.initDamBreak();
  size_t n0 = sim.particles.size();
  CHECK(n0 > 0);
  for (int s=0;s<60;++s) sim.step();
  CHECK(sim.particles.size() == n0);
  bool finite = true; double maxy = 0.0;
  for (size_t k=0;k<sim.particles.size();++k) {
    if (!std::isfinite(sim.particles.pos[k].x) || !std::isfinite(sim.particles.pos[k].y)) finite=false;
    maxy = std::max(maxy, sim.particles.pos[k].y);
  }
  CHECK(finite);
  CHECK(maxy < 32.0);
}
```

- [ ] **Step 2: CMake에 추가 → 빌드 FAIL 확인**

- [ ] **Step 3: 드라이버 구현**

`src/driver/sim2d.h`:
```cpp
#pragma once
#include "grid/uniform_grid2d.h"
#include "particles/particles2d.h"
struct Sim2D {
  UniformGrid2D grid;
  Particles2D particles;
  double dt=0.05, rho=1.0, alpha=0.95, gravity=-9.81;
  int cg_iters=200; double cg_tol=1e-6;
  Sim2D(int nx, int ny, double dx) : grid(nx,ny,dx) {}
  void initDamBreak();
  void step();
};
```
`src/driver/sim2d.cpp`:
```cpp
#include "driver/sim2d.h"
#include "transfer/transfer2d.h"
#include "pressure/pressure2d.h"
#include "advect/advect2d.h"

void Sim2D::initDamBreak() {
  int wcols = grid.nx*4/10, hrows = grid.ny*7/10;
  for (int j=1;j<hrows;++j) for (int i=1;i<wcols;++i)
    for (int sj=0;sj<2;++sj) for (int si=0;si<2;++si) {
      double x = grid.ox + (i + 0.25 + 0.5*si)*grid.dx;
      double y = grid.oy + (j + 0.25 + 0.5*sj)*grid.dx;
      particles.add({x,y}, {0.0,0.0});
    }
}

static void markCells(UniformGrid2D& g, const Particles2D& ps) {
  for (auto& c : g.marker) c = Cell::AIR;
  for (int j=0;j<g.ny;++j){ g.cell(0,j)=Cell::SOLID; g.cell(g.nx-1,j)=Cell::SOLID; }
  for (int i=0;i<g.nx;++i){ g.cell(i,0)=Cell::SOLID; g.cell(i,g.ny-1)=Cell::SOLID; }
  for (size_t k=0;k<ps.size();++k) {
    int i=(int)((ps.pos[k].x-g.ox)/g.dx), j=(int)((ps.pos[k].y-g.oy)/g.dx);
    if (g.inBounds(i,j) && g.cell(i,j)!=Cell::SOLID) g.cell(i,j)=Cell::FLUID;
  }
}

void Sim2D::step() {
  markCells(grid, particles);
  p2g(grid, particles);
  UniformGrid2D saved = grid;                 // 압력 전 스냅샷
  for (size_t idx=0; idx<grid.vfield.size(); ++idx)
    if (grid.mv[idx] > 0.0) grid.vfield[idx] += dt*gravity;
  for (int j=0;j<grid.ny;++j){ grid.u(0,j)=0; grid.u(1,j)=0; grid.u(grid.nx-1,j)=0; grid.u(grid.nx,j)=0; }
  for (int i=0;i<grid.nx;++i){ grid.v(i,0)=0; grid.v(i,1)=0; grid.v(i,grid.ny-1)=0; grid.v(i,grid.ny)=0; }
  auto div = divergence(grid);
  solvePressure(grid, div, dt, rho, cg_iters, cg_tol);
  project(grid, dt, rho);
  g2p(grid, particles, saved, alpha);
  advect(particles, grid, dt);
}
```

- [ ] **Step 4: 빌드·테스트 PASS** (60스텝: 입자 보존·유한·도메인 내)
```powershell
cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure
```

- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: 2D FLIP sim driver + dam-break integration test"`

---

## Task 11: PPM 시각화 + 육안 검증

**Files:** Create `src/driver/viz_ppm.h`, `apps/run_dambreak.cpp`; Modify `CMakeLists.txt`.

- [ ] **Step 1: PPM 라이터**

`src/driver/viz_ppm.h`:
```cpp
#pragma once
#include <string>
#include <vector>
#include <fstream>
#include "driver/sim2d.h"
inline void writePPM(const Sim2D& sim, const std::string& path, int scale=8) {
  int W = sim.grid.nx*scale, H = sim.grid.ny*scale;
  std::vector<unsigned char> img(W*H*3, 20);
  for (size_t k=0;k<sim.particles.size();++k) {
    int px=(int)((sim.particles.pos[k].x - sim.grid.ox)/sim.grid.dx*scale);
    int py=(int)((sim.particles.pos[k].y - sim.grid.oy)/sim.grid.dx*scale);
    py = H-1-py;
    if (px<0||px>=W||py<0||py>=H) continue;
    int o=(px+W*py)*3; img[o]=60; img[o+1]=140; img[o+2]=230;
  }
  std::ofstream f(path, std::ios::binary);
  f << "P6\n" << W << " " << H << "\n255\n";
  f.write((const char*)img.data(), img.size());
}
```

- [ ] **Step 2: 실행 앱**

`apps/run_dambreak.cpp`:
```cpp
#include "driver/sim2d.h"
#include "driver/viz_ppm.h"
#include <cstdio>
int main() {
  Sim2D sim(64,64,1.0);
  sim.initDamBreak();
  for (int s=0;s<120;++s) {
    sim.step();
    if (s%4==0) { char n[64]; std::snprintf(n,sizeof(n),"frame_%03d.ppm",s/4); writePPM(sim,n); }
  }
  std::printf("done: %zu particles\n", sim.particles.size());
  return 0;
}
```

- [ ] **Step 3: CMake에 앱 추가**
```cmake
add_executable(run_dambreak apps/run_dambreak.cpp)
target_link_libraries(run_dambreak pfflip2d)
```

- [ ] **Step 4: 빌드·실행**
```powershell
cmake -S . -B build; cmake --build build --config Debug; ./build/Debug/run_dambreak.exe
```
Expected: `frame_000.ppm`~`frame_029.ppm`, "done: N particles".

- [ ] **Step 5: 육안 검증** — `frame_000`(좌측 물기둥) → 후반(붕괴·우측 전파·바닥 정착)이면 PASS.

- [ ] **Step 6: Commit** — `git add -A; git commit -m "feat: PPM viz + dam-break runner"`

---

## Self-Review (작성자 점검)

- **Spec coverage:** Phase 0 요소 전부 커버 — MAC 격자(T3), P2G/G2P(T5–6, Eq.12·bilinear), 발산·압력·투영(T7–8, 표준 MGPCG=§6 대체), RK2 이류(T9), dam-break 검증(T10), 육안(T11). 점성(Eq.13)·2상·cubic 커널은 SPEC-1의 Phase 1/2 — 의도적 범위 외. ✅
- **Placeholder scan:** 모든 step에 실제 코드/명령. "TBD/적절히 처리" 없음. ✅
- **Type consistency:** 멤버 `ufield/vfield/mu/mv/pfield/marker`, 접근자 `u/v/p/cell`, 함수 `p2g/g2p/sampleU/sampleV/divergence/solvePressure/project/advect`가 전 태스크 일관. `g2p/sampleU/sampleV` 정의는 T5(헤더 선언 포함), T6은 테스트만. ✅

## 다음 PLAN
- **PLAN-1**: Phase 1 — 3D 확장 + 점성(Eq.13) + 속도 외삽
- **PLAN-2**: Phase 2 — phase-field 2상(Eq.7) + 가변계수 Poisson + cubic 커널(Eq.6) [★권장 정지선]
- **PLAN-3**: Phase 3 — 오픈 MSBG 통합(`IGrid` 교체)
