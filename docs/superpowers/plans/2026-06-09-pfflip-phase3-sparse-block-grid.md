# PF-FLIP Phase 3 — 미니멀 희소 블록 격자 (MSBG 개념 자체구현) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`).

**Goal:** 논문의 MSBG 자료구조를 *개념적으로* 우리 깨끗한 MSVC/CMake C++로 재구현한다 — 트리리스 + 큰 블록 + dense 평면 블록배열 + 블록풀 + 8-color. (실제 MSBG는 GCC/Make/POSIX 의존으로 이 머신에서 빌드/링크 불가 — 조사 결론.) 2D 단일해상도부터. **payoff: 균일격자와 동일한 결과를 희소 저장(활성 블록만)으로 얻음을 검증.**

**Architecture:** 도메인을 B×B 블록으로 분할. 블록 포인터의 **dense 평면 배열**(`bid = bx + nbx*by`). 블록은 **on-demand로 풀에서 할당**(활성 영역만 메모리). 셀 접근은 블록+로컬 인덱스. 이웃 스텐실은 bounds-checked `get()`(비활성=0)으로 투명 처리(halo는 후속 성능 최적화). **4-color**(2D) 블록 채색으로 lock-free 병렬 쓰기. 단일해상도·단일채널(float)부터; 다해상도·다채널은 Phase 3b.

**Tech Stack:** 기존 C++17/CMake/doctest. branch `feat/phase3-sparse-grid`(from main). `__sync_*`/`__attribute__` 대신 `<atomic>`/`alignas` (MSVC-clean).

**Scope (정직):** 단일해상도 희소 블록 격자 + 동등성/희소성 검증. **이월:** 다해상도(MSBG 차별점)·halo 최적화·8-color 병렬 splat의 실제 멀티스레딩·FLIP 솔버를 희소격자 위로 완전 포팅 → Phase 3b/4.

---

## File Structure (신규)
| 파일 | 책임 |
|---|---|
| `src/grid/sparse_block_grid2d.h` | 희소 블록 격자(블록풀+dense 인덱스, 셀 접근, 활성/희소) |
| `src/grid/block_color.h` | 4-color(2D) 블록 채색 + 색별 분할 |
| `tests/test_sparse_grid.cpp` | 할당·접근·희소성 |
| `tests/test_sparse_stencil.cpp` | 활성블록 순회 + Laplacian이 균일격자와 일치 |
| `tests/test_block_color.cpp` | 동색 블록 비인접(lock-free 안전) |
| `tests/test_sparse_splat.cpp` | 입자 스플랫 → 활성블록만 + 균일 결과 일치(희소성 payoff) |

**규약:** 블록 변 `B`(테스트 8, 운영 16). `nbx=(nx+B-1)/B`, `nby=(ny+B-1)/B`. `bid=bx+nbx*by`. 로컬 idx `lx+B*ly`. `get(i,j)`=비활성 블록이면 0(균일격자의 0과 동일 의미). `ref(i,j)`=쓰기 시 블록 활성화 후 참조.

---

## Task 1: SparseBlockGrid2D (블록풀 + dense 인덱스)

**Files:** Create `src/grid/sparse_block_grid2d.h`, `tests/test_sparse_grid.cpp`; Modify `CMakeLists.txt`.

- [ ] **Step 1: 실패 테스트** `tests/test_sparse_grid.cpp`:
```cpp
#include "doctest.h"
#include "grid/sparse_block_grid2d.h"
TEST_CASE("sparse grid allocate/access/sparsity") {
  SparseBlockGrid2D<8> g(64, 32, 1.0);      // 8x4 = 32 blocks total
  CHECK(g.nbx == 8); CHECK(g.nby == 4);
  CHECK(g.activeBlockCount() == 0);
  CHECK(g.get(10, 5) == doctest::Approx(0.0));     // inactive -> 0
  g.ref(10, 5) = 3.5;                               // activates one block
  CHECK(g.get(10, 5) == doctest::Approx(3.5));
  CHECK(g.activeBlockCount() == 1);                 // only one block allocated
  g.ref(11, 6) = 1.0;                               // same block (10/8==11/8==1, 5/8==6/8==0)
  CHECK(g.activeBlockCount() == 1);
  g.ref(40, 20) = 2.0;                              // different block
  CHECK(g.activeBlockCount() == 2);
  CHECK(g.blockActive(1, 0));
  CHECK(!g.blockActive(0, 0));
}
```
- [ ] **Step 2: CMake에 `tests/test_sparse_grid.cpp` 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/grid/sparse_block_grid2d.h`:
```cpp
#pragma once
#include <vector>
#include <cstddef>

// Treeless sparse block grid: dense flat array of block slots, blocks allocated on demand.
// Single-resolution, scalar float. B = block edge length (compile-time).
template<int B>
struct SparseBlockGrid2D {
  int nx, ny, nbx, nby;
  double dx, ox = 0.0, oy = 0.0;
  std::vector<int> blockmap;                  // bid -> pool index, or -1 (inactive)
  std::vector<std::vector<float>> pool;       // active block data (B*B each)

  SparseBlockGrid2D(int nx_, int ny_, double dx_)
    : nx(nx_), ny(ny_), nbx((nx_+B-1)/B), nby((ny_+B-1)/B), dx(dx_),
      blockmap((size_t)((nx_+B-1)/B)*((ny_+B-1)/B), -1) {}

  static constexpr int blockVol() { return B*B; }
  int bid(int bx, int by) const { return bx + nbx*by; }
  bool inBlockRange(int bx, int by) const { return bx>=0 && bx<nbx && by>=0 && by<nby; }
  bool blockActive(int bx, int by) const { return inBlockRange(bx,by) && blockmap[bid(bx,by)]>=0; }
  size_t activeBlockCount() const { size_t c=0; for(int m: blockmap) if(m>=0) ++c; return c; }
  size_t totalBlocks() const { return blockmap.size(); }

  int activateBlock(int bx, int by) {
    int b = bid(bx,by);
    if (blockmap[b] < 0) { blockmap[b] = (int)pool.size(); pool.emplace_back(blockVol(), 0.0f); }
    return blockmap[b];
  }
  // write access (activates block)
  float& ref(int i, int j) {
    int bx=i/B, by=j/B, pi=activateBlock(bx,by);
    return pool[pi][(i%B) + B*(j%B)];
  }
  // read access (inactive -> 0)
  float get(int i, int j) const {
    if (i<0||i>=nx||j<0||j>=ny) return 0.0f;
    int bx=i/B, by=j/B, m=blockmap[bid(bx,by)];
    if (m<0) return 0.0f;
    return pool[m][(i%B) + B*(j%B)];
  }
  // list of active block ids
  std::vector<int> activeBlocks() const {
    std::vector<int> v; for(size_t b=0;b<blockmap.size();++b) if(blockmap[b]>=0) v.push_back((int)b); return v;
  }
  void blockCoords(int b, int& bx, int& by) const { bx = b % nbx; by = b / nbx; }
};
```
- [ ] **Step 4: 빌드·테스트 PASS** — `cmake -S . -B build; cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure`
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: SparseBlockGrid2D (treeless block pool + dense index)"`

---

## Task 2: 활성블록 순회 + 스텐실(Laplacian) 균일격자 동등성

**Files:** Create `tests/test_sparse_stencil.cpp`; Modify `CMakeLists.txt`. (구현은 Task 1 헤더의 `get/ref/activeBlocks`로 충분 — 본 태스크는 스텐실 연산이 균일격자와 일치함을 검증.)

희소격자의 `get()`은 비활성 이웃을 0으로 돌려주므로, 활성 영역 내부에서 5-점 Laplacian이 균일격자(0 패딩)와 정확히 일치해야 한다.

- [ ] **Step 1: 실패 테스트** `tests/test_sparse_stencil.cpp`:
```cpp
#include "doctest.h"
#include "grid/sparse_block_grid2d.h"
#include <vector>
#include <cmath>
TEST_CASE("sparse 5-point Laplacian matches uniform reference in active region") {
  const int NX=24, NY=24, B=8;
  SparseBlockGrid2D<B> g(NX,NY,1.0);
  std::vector<float> uni(NX*NY, 0.0f);
  // fill a quadratic bump in [4,20)x[4,20)
  for(int j=4;j<20;++j)for(int i=4;i<20;++i){ float v=(float)(i*i + 2*j); g.ref(i,j)=v; uni[i+NX*j]=v; }
  auto lap=[&](auto getter,int i,int j){ return getter(i+1,j)+getter(i-1,j)+getter(i,j+1)+getter(i,j-1)-4*getter(i,j); };
  auto ug=[&](int i,int j)->float{ if(i<0||i>=NX||j<0||j>=NY) return 0.f; return uni[i+NX*j]; };
  auto sg=[&](int i,int j)->float{ return g.get(i,j); };
  double maxdiff=0;
  for(int j=5;j<19;++j)for(int i=5;i<19;++i) maxdiff=std::max(maxdiff,(double)std::abs(lap(ug,i,j)-lap(sg,i,j)));
  CHECK(maxdiff < 1e-5);
  // sparsity: only blocks covering [4,20) are active -> at most 3x3=9 of the 9 blocks (NX/B=3)
  CHECK(g.activeBlockCount() <= 9);
}
TEST_CASE("iterate active blocks covers all written cells") {
  SparseBlockGrid2D<8> g(32,32,1.0);
  g.ref(3,3)=1; g.ref(20,20)=2;
  int seen=0;
  for(int b: g.activeBlocks()){ int bx,by; g.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx, j=by*8+ly; if(g.get(i,j)!=0.f) ++seen; } }
  CHECK(seen == 2);
}
```
- [ ] **Step 2: CMake 추가 → 빌드·테스트 실행** (구현 추가 없이 PASS 기대; 만약 `get/ref/activeBlocks/blockCoords` 시그니처 불일치로 실패하면 Task 1 헤더를 맞춤)
- [ ] **Step 3: (필요시) 헤더 보정** — 없으면 생략.
- [ ] **Step 4: 빌드·테스트 PASS**
- [ ] **Step 5: Commit** — `git add -A; git commit -m "test: sparse stencil matches uniform + active-block iteration"`

---

## Task 3: 4-color 블록 채색 (lock-free 병렬 안전성)

**Files:** Create `src/grid/block_color.h`, `tests/test_block_color.cpp`; Modify `CMakeLists.txt`.

2D에서 동색 블록이 서로 4-이웃(상하좌우)이 아니도록 `color(bx,by) = (bx&1) + 2*(by&1)` (4색). 같은 색 블록은 메모리가 겹치지 않아 lock 없이 병렬 쓰기 가능(논문 8-color의 2D 버전).

- [ ] **Step 1: 실패 테스트** `tests/test_block_color.cpp`:
```cpp
#include "doctest.h"
#include "grid/sparse_block_grid2d.h"
#include "grid/block_color.h"
TEST_CASE("4-color: same-color blocks are never 4-neighbors") {
  SparseBlockGrid2D<8> g(64,64,1.0);
  for(int by=0;by<g.nby;++by)for(int bx=0;bx<g.nbx;++bx) g.activateBlock(bx,by);
  auto buckets = partitionByColor4(g);         // vector<vector<int>> size 4
  CHECK(buckets.size()==4);
  for(int c=0;c<4;++c){
    for(int b: buckets[c]){ int bx,by; g.blockCoords(b,bx,by);
      // none of the 4-neighbors share color c
      int nb[4][2]={{bx+1,by},{bx-1,by},{bx,by+1},{bx,by-1}};
      for(auto& n: nb){ if(g.inBlockRange(n[0],n[1])) CHECK(color4(n[0],n[1])!=c); } }
  }
  // all blocks partitioned exactly once
  size_t tot=0; for(auto& v: buckets) tot+=v.size();
  CHECK(tot == g.activeBlockCount());
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/grid/block_color.h`:
```cpp
#pragma once
#include <vector>
#include "grid/sparse_block_grid2d.h"
inline int color4(int bx, int by){ return (bx & 1) + 2*(by & 1); }
template<int B>
std::vector<std::vector<int>> partitionByColor4(const SparseBlockGrid2D<B>& g){
  std::vector<std::vector<int>> buckets(4);
  for(int b: g.activeBlocks()){ int bx,by; g.blockCoords(b,bx,by); buckets[color4(bx,by)].push_back(b); }
  return buckets;
}
```
- [ ] **Step 4: 빌드·테스트 PASS**
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: 4-color block coloring (lock-free parallel safety)"`

---

## Task 4: 입자 스플랫 — 활성블록만 + 균일 결과 일치 (희소성 payoff)

**Files:** Create `tests/test_sparse_splat.cpp`; Modify `CMakeLists.txt`. (스플랫 헬퍼는 테스트 내 인라인 — 데이터구조 검증이 목적.)

논문 MSBG의 핵심 가치 = **같은 결과를 희소 저장으로**. 좁은 영역에 입자를 뿌려 (a) 활성 블록이 전체의 일부만(희소성), (b) 활성 영역의 스플랫 결과가 균일격자와 일치함을 검증.

- [ ] **Step 1: 실패 테스트** `tests/test_sparse_splat.cpp`:
```cpp
#include "doctest.h"
#include "grid/sparse_block_grid2d.h"
#include <vector>
#include <cmath>
TEST_CASE("particle splat: sparse storage + matches uniform in active region") {
  const int NX=128, NY=128, B=8;       // 16x16 = 256 blocks
  SparseBlockGrid2D<B> g(NX,NY,1.0);
  std::vector<float> uni(NX*NY,0.0f);
  // particles confined to a small disk around (30,30) radius ~6
  struct P{double x,y;}; std::vector<P> ps;
  for(int n=0;n<400;++n){ double a=0.0173*n, r=6.0*((n*37)%100)/100.0; ps.push_back({30+r*std::cos(a),30+r*std::sin(a)}); }
  auto splat=[&](auto setter){ for(auto& p: ps){ int i=(int)p.x,j=(int)p.y; double fx=p.x-i,fy=p.y-j;
    setter(i,j,(float)((1-fx)*(1-fy))); setter(i+1,j,(float)(fx*(1-fy))); setter(i,j+1,(float)((1-fx)*fy)); setter(i+1,j+1,(float)(fx*fy)); } };
  splat([&](int i,int j,float w){ if(i>=0&&i<NX&&j>=0&&j<NY) uni[i+NX*j]+=w; });
  splat([&](int i,int j,float w){ if(i>=0&&i<NX&&j>=0&&j<NY) g.ref(i,j)+=w; });
  // (a) sparsity: far fewer than all 256 blocks active (disk near one corner)
  CHECK(g.activeBlockCount() < 16);
  CHECK(g.activeBlockCount() > 0);
  // (b) equivalence: sparse matches uniform everywhere
  double maxdiff=0; for(int j=0;j<NY;++j)for(int i=0;i<NX;++i) maxdiff=std::max(maxdiff,(double)std::abs(g.get(i,j)-uni[i+NX*j]));
  CHECK(maxdiff < 1e-6);
  // memory proof: pool holds only active blocks
  CHECK(g.pool.size() == g.activeBlockCount());
}
```
- [ ] **Step 2: CMake 추가 → 빌드·테스트 실행** (Task1~2 구현으로 PASS 기대)
- [ ] **Step 3: (필요시) 보정** — 없으면 생략.
- [ ] **Step 4: 빌드·테스트 PASS** (희소성 <16/256 블록 + 균일 동등 maxdiff<1e-6)
- [ ] **Step 5: Commit** — `git add -A; git commit -m "test: sparse splat matches uniform with sparse storage (MSBG payoff)"`

---

## Self-Review
- **Coverage:** 희소 블록 격자(T1), 스텐실 동등성(T2), 4-color(T3), 스플랫 희소성+동등(T4). MSBG 개념(트리리스·dense인덱스·블록풀·색채색) 자체구현. ✅
- **Placeholder scan:** 전 step 코드/명령. 없음. ✅
- **Type consistency:** `SparseBlockGrid2D<B>`(`ref/get/activateBlock/blockActive/activeBlocks/blockCoords/activeBlockCount/inBlockRange/nbx/nby/pool`), `color4/partitionByColor4`. 일관. ✅
- **게이트:** 희소성(활성블록 ≪ 전체) + 균일격자 동등(maxdiff<1e-6) — MSBG의 "같은 결과, 희소 저장"을 직접 증명.
- **MSVC-clean:** `__sync_*`/`__attribute__` 없음. 표준 C++17만.

## 다음 (Phase 3b / 4)
- 다해상도(MSBG 차별점): 블록별 해상도 레벨 + 전이존
- halo 교환(성능)·실제 멀티스레드 색별 splat
- FLIP 솔버(transfer/pressure/advect)를 `IGrid` 추상화로 희소격자 위에 완전 포팅
