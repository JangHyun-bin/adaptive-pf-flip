# PF-FLIP Phase A — 희소 FLIP 통합 (2D 단상이 희소격자 위에서) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`).

**Goal:** Phase 3에서 만든 `SparseBlockGrid2D`를 실제 FLIP 솔버에 연결한다 — 2D 단상 dam-break가 **활성 블록만 할당하며**(희소 저장) 돌아가고, 균일격자 결과와 동등함을 검증한다. **payoff: "큰 도메인을 적은 메모리로"** = MSBG의 실제 가치 실현.

**Architecture:** MAC 필드(u,v,질량,p,marker)를 각각 `SparseBlockGrid2D`로 저장한 `SparseMacGrid2D`. P2G 스플랫이 `ref()`로 쓰며 **입자가 닿는 블록만 자동 활성화** → 희소성 공짜. 압력 CG는 **유체 셀만 열거**해서 풀고, 이웃은 `get()`(비활성=0=AIR Dirichlet)로 접근. 검증된 Phase 0 알고리즘(bilinear P2G, CG, RK2)을 희소 저장 위에 재구성. 단상·단일해상도부터.

**Tech Stack:** 기존 C++17/CMake/doctest. branch `feat/phaseA-sparse-flip`(from main). 참고: 검증된 Phase 0 솔버가 `src/{transfer,pressure,advect,driver}2d.*`에 있음.

**Scope:** 2D 단상 dam-break on sparse grid. **이월:** 2상/3D/다해상도/halo 최적화/실제 멀티스레드.

---

## File Structure (신규)
| 파일 | 책임 |
|---|---|
| `src/grid/sparse_block_grid2d.h` | (Phase 3, +clear() 추가) |
| `src/grid/sparse_mac_grid2d.h` | MAC 필드 묶음(u/v/질량/p/marker) + 접근자 + 유체셀 열거 |
| `src/driver/sparse_sim2d.h`/`.cpp` | 희소 FLIP 스텝(p2g/mark/div/CG/project/g2p/advect) + dam-break |
| `src/driver/viz_sparse.h` | 입자 + 활성블록 오버레이 viz |
| `apps/run_sparse_dambreak.cpp` | 러너(활성블록 비율 출력) |
| `tests/test_sparse_mac.cpp`, `test_sparse_pressure.cpp`, `test_sparse_sim.cpp` | 검증 |

**규약:** B=블록변(테스트 8). 좌표/인덱스는 Phase 0과 동일 MAC. 단상: m_p=1, ρ=1. marker float(0=AIR,1=FLUID,2=SOLID).

---

## Task 1: SparseMacGrid2D + SparseBlockGrid2D::clear()

**Files:** Modify `src/grid/sparse_block_grid2d.h` (add `clear()`); Create `src/grid/sparse_mac_grid2d.h`, `tests/test_sparse_mac.cpp`; Modify `CMakeLists.txt`.

**STEP A:** `sparse_block_grid2d.h`의 struct에 메서드 추가 (블록 전부 해제 = 스텝 간 리셋):
```cpp
  void clear() { std::fill(blockmap.begin(), blockmap.end(), -1); pool.clear(); }
```

- [ ] **Step 1: 실패 테스트** `tests/test_sparse_mac.cpp`:
```cpp
#include "doctest.h"
#include "grid/sparse_mac_grid2d.h"
TEST_CASE("sparse MAC: splat activates only touched blocks; access; clear") {
  SparseMacGrid2D<8> g(64,64,1.0);                 // 8x8=64 cell-blocks
  CHECK(g.uf.activeBlockCount()==0);
  g.u(10,5) = 2.0f;  g.mu(10,5) = 1.0f;            // touches one u-block
  CHECK(g.gu(10,5)==doctest::Approx(2.0f));
  CHECK(g.uf.activeBlockCount()==1);
  g.setCell(10,5,1);                                // FLUID
  CHECK(g.cell(10,5)==1);
  CHECK(g.cell(60,60)==0);                          // inactive -> AIR(0)
  g.clearAll();
  CHECK(g.uf.activeBlockCount()==0);
  CHECK(g.gu(10,5)==doctest::Approx(0.0f));
}
```
- [ ] **Step 2: STEP A 적용 + CMake에 test 추가 → 빌드 FAIL 확인 (sparse_mac_grid2d.h 없음). 기존 40 테스트는 clear() 추가 후에도 PASS 확인.**
- [ ] **Step 3: 구현** `src/grid/sparse_mac_grid2d.h`:
```cpp
#pragma once
#include "grid/sparse_block_grid2d.h"
#include <vector>
// MAC grid backed by sparse block fields. Single-phase scalar.
template<int B>
struct SparseMacGrid2D {
  int nx, ny; double dx, ox=0.0, oy=0.0;
  SparseBlockGrid2D<B> uf, vf, muf, mvf, pf, mkf;   // u(nx+1,ny) v(nx,ny+1) masses, p & marker(nx,ny)
  SparseMacGrid2D(int nx_,int ny_,double dx_)
    : nx(nx_), ny(ny_), dx(dx_),
      uf(nx_+1,ny_,dx_), vf(nx_,ny_+1,dx_),
      muf(nx_+1,ny_,dx_), mvf(nx_,ny_+1,dx_),
      pf(nx_,ny_,dx_), mkf(nx_,ny_,dx_) {}
  float& u(int i,int j){ return uf.ref(i,j); }
  float& v(int i,int j){ return vf.ref(i,j); }
  float& mu(int i,int j){ return muf.ref(i,j); }
  float& mv(int i,int j){ return mvf.ref(i,j); }
  float& p(int i,int j){ return pf.ref(i,j); }
  float gu(int i,int j) const { return uf.get(i,j); }
  float gv(int i,int j) const { return vf.get(i,j); }
  float gmu(int i,int j) const { return muf.get(i,j); }
  float gmv(int i,int j) const { return mvf.get(i,j); }
  float gp(int i,int j) const { return pf.get(i,j); }
  void setCell(int i,int j,int c){ mkf.ref(i,j)=(float)c; }
  int cell(int i,int j) const { return (int)(mkf.get(i,j)+0.5f); }   // inactive -> 0 (AIR)
  bool inBounds(int i,int j) const { return i>=0&&i<nx&&j>=0&&j<ny; }
  void clearAll(){ uf.clear(); vf.clear(); muf.clear(); mvf.clear(); pf.clear(); mkf.clear(); }
  size_t activeCellBlocks() const { return pf.activeBlockCount(); }
  size_t totalCellBlocks()  const { return pf.totalBlocks(); }
};
```
- [ ] **Step 4: 빌드·테스트 PASS** — `cmake -S . -B build; cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure`
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: SparseMacGrid2D (MAC fields on sparse block grid) + clear()"`

---

## Task 2: 희소 P2G + 발산 + 압력 CG + 투영

**Files:** Create `src/driver/sparse_ops2d.h`, `src/driver/sparse_ops2d.cpp`, `tests/test_sparse_pressure.cpp`; Modify `CMakeLists.txt`.

핵심: P2G는 `ref()`로 활성블록만 켜고, 압력 CG는 **유체 셀 열거 + dense 벡터**로 푼다(이웃은 `get()`). 단상 ρ=1, scale=dt/(dx²).

- [ ] **Step 1: 실패 테스트** `tests/test_sparse_pressure.cpp`:
```cpp
#include "doctest.h"
#include "grid/sparse_mac_grid2d.h"
#include "driver/sparse_ops2d.h"
#include <cmath>
TEST_CASE("sparse projection removes divergence in fluid blob") {
  SparseMacGrid2D<8> g(32,32,1.0);
  // fluid blob [10,20)x[10,20); solid border ring of cells
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    int c = (i==0||i==g.nx-1||j==0||j==g.ny-1)?2 : ((i>=10&&i<20&&j>=10&&j<20)?1:0);
    if(c!=0) g.setCell(i,j,c);
  }
  // divergent u field on the fluid faces
  for(int j=10;j<20;++j)for(int i=10;i<=20;++i) g.u(i,j)=(float)i;
  spProjectStep(g, 1.0, 500, 1e-9);            // divergence -> solvePressure -> project
  // post divergence in fluid ~0
  double mx=0; for(int j=10;j<20;++j)for(int i=10;i<20;++i){
    double d=(g.gu(i+1,j)-g.gu(i,j)+g.gv(i,j+1)-g.gv(i,j)); mx=std::max(mx,std::abs(d)); }
  CHECK(mx < 1e-4);
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/driver/sparse_ops2d.h`:
```cpp
#pragma once
template<int B> struct SparseMacGrid2D;
struct Particles2D;
// single-phase sparse FLIP ops (m_p=1, rho=1)
void spP2G(SparseMacGrid2D<8>& g, const Particles2D& ps);
void spProjectStep(SparseMacGrid2D<8>& g, double dt, int cg_iters, double cg_tol);
void spG2P(const SparseMacGrid2D<8>& g, Particles2D& ps, const SparseMacGrid2D<8>& saved, double alpha);
void spAdvect(Particles2D& ps, const SparseMacGrid2D<8>& g, double dt);
```
`src/driver/sparse_ops2d.cpp`:
```cpp
#include "driver/sparse_ops2d.h"
#include "grid/sparse_mac_grid2d.h"
#include "particles/particles2d.h"
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <cmath>

static void splatU(SparseMacGrid2D<8>& g,double gx,double gy,double mom,double m){
  int i0=(int)std::floor(gx), j0=(int)std::floor(gy); double fx=gx-i0,fy=gy-j0;
  double w[2][2]={{(1-fx)*(1-fy),fx*(1-fy)},{(1-fx)*fy,fx*fy}};
  for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di){ int ii=i0+di,jj=j0+dj;
    if(ii<0||ii>g.nx||jj<0||jj>=g.ny) continue; g.u(ii,jj)+=(float)(w[dj][di]*mom); g.mu(ii,jj)+=(float)(w[dj][di]*m); } }
static void splatV(SparseMacGrid2D<8>& g,double gx,double gy,double mom,double m){
  int i0=(int)std::floor(gx), j0=(int)std::floor(gy); double fx=gx-i0,fy=gy-j0;
  double w[2][2]={{(1-fx)*(1-fy),fx*(1-fy)},{(1-fx)*fy,fx*fy}};
  for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di){ int ii=i0+di,jj=j0+dj;
    if(ii<0||ii>=g.nx||jj<0||jj>g.ny) continue; g.v(ii,jj)+=(float)(w[dj][di]*mom); g.mv(ii,jj)+=(float)(w[dj][di]*m); } }

void spP2G(SparseMacGrid2D<8>& g, const Particles2D& ps){
  g.uf.clear(); g.vf.clear(); g.muf.clear(); g.mvf.clear();
  const double mp=1.0;
  for(size_t k=0;k<ps.size();++k){ double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    splatU(g,px,py-0.5,mp*ps.vel[k].x,mp); splatV(g,px-0.5,py,mp*ps.vel[k].y,mp); }
  // normalize: iterate active u/v mass blocks
  for(int b: g.muf.activeBlocks()){ int bx,by; g.muf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>g.nx||j>=g.ny) continue;
      float m=g.gmu(i,j); if(m>0) g.u(i,j)=g.gu(i,j)/m; } }
  for(int b: g.mvf.activeBlocks()){ int bx,by; g.mvf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>=g.nx||j>g.ny) continue;
      float m=g.gmv(i,j); if(m>0) g.v(i,j)=g.gv(i,j)/m; } }
}

static std::vector<int> fluidCells(const SparseMacGrid2D<8>& g){
  std::vector<int> cells;
  for(int b: g.mkf.activeBlocks()){ int bx,by; g.mkf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly;
      if(g.inBounds(i,j) && g.cell(i,j)==1) cells.push_back(i + g.nx*j); } }
  return cells;
}
void spProjectStep(SparseMacGrid2D<8>& g, double dt, int cg_iters, double cg_tol){
  auto cells = fluidCells(g);
  int N=(int)cells.size(); if(N==0) return;
  std::unordered_map<int,int> idx; idx.reserve(N*2);
  for(int t=0;t<N;++t) idx[cells[t]]=t;
  auto isFluid=[&](int i,int j){ return g.inBounds(i,j) && g.cell(i,j)==1; };
  auto isSolid=[&](int i,int j){ return !g.inBounds(i,j) || g.cell(i,j)==2; };
  double scale=dt/(g.dx*g.dx);
  // rhs b = -divergence at fluid cells
  std::vector<double> bvec(N), x(N,0),r(N),z(N),pd(N),Ap(N);
  for(int t=0;t<N;++t){ int i=cells[t]%g.nx, j=cells[t]/g.nx;
    double d=(g.gu(i+1,j)-g.gu(i,j)+g.gv(i,j+1)-g.gv(i,j))/g.dx; bvec[t]=-d; r[t]=bvec[t]; }
  auto diagOf=[&](int i,int j){ double d=0; const int di[4]={1,-1,0,0},dj[4]={0,0,1,-1};
    for(int n=0;n<4;++n) if(!isSolid(i+di[n],j+dj[n])) d+=1.0; return scale*d; };
  auto applyA=[&](const std::vector<double>& xx,std::vector<double>& out){
    const int di[4]={1,-1,0,0},dj[4]={0,0,1,-1};
    for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx; double diag=0,off=0;
      for(int n=0;n<4;++n){ int ni=i+di[n],nj=j+dj[n]; if(isSolid(ni,nj)) continue; diag+=1.0;
        if(isFluid(ni,nj)) off+=xx[idx[ni+g.nx*nj]]; }
      out[t]=scale*(diag*xx[t]-off); } };
  auto prec=[&](const std::vector<double>& in,std::vector<double>& o){ for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx; double d=diagOf(i,j); o[t]=(d>0)?in[t]/d:0.0; } };
  auto dotp=[&](const std::vector<double>& a,const std::vector<double>& b){ double s=0; for(int t=0;t<N;++t) s+=a[t]*b[t]; return s; };
  double res0=0; for(int t=0;t<N;++t) res0=std::max(res0,std::abs(r[t])); if(res0<cg_tol) return;
  prec(r,z); pd=z; double rz=dotp(r,z),res=res0;
  for(int it=0;it<cg_iters;++it){ applyA(pd,Ap); double pAp=dotp(pd,Ap); if(std::abs(pAp)<1e-30) break;
    double al=rz/pAp; for(int t=0;t<N;++t){x[t]+=al*pd[t];r[t]-=al*Ap[t];}
    res=0; for(int t=0;t<N;++t) res=std::max(res,std::abs(r[t])); if(res<cg_tol) break;
    prec(r,z); double rzn=dotp(r,z),be=rzn/rz; rz=rzn; for(int t=0;t<N;++t) pd[t]=z[t]+be*pd[t]; }
  // write pressure into sparse p-field
  for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx; g.p(i,j)=(float)x[t]; }
  // project u,v on faces adjacent to fluid
  double s=dt/g.dx;
  for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx;
    // left/right u faces, bottom/top v faces around this fluid cell
    // u(i,j): between (i-1,j)&(i,j); u(i+1,j): between (i,j)&(i+1,j)
    if(!isSolid(i-1,j)&&!isSolid(i,j)){ double pl=isFluid(i-1,j)?g.gp(i-1,j):0.0, pr=g.gp(i,j); g.u(i,j)=g.gu(i,j)-(float)(s*(pr-pl)); } else g.u(i,j)=0.0f;
    if(!isSolid(i,j)&&!isSolid(i+1,j)){ double pl=g.gp(i,j), pr=isFluid(i+1,j)?g.gp(i+1,j):0.0; g.u(i+1,j)=g.gu(i+1,j)-(float)(s*(pr-pl)); } else g.u(i+1,j)=0.0f;
    if(!isSolid(i,j-1)&&!isSolid(i,j)){ double pb=isFluid(i,j-1)?g.gp(i,j-1):0.0, pt=g.gp(i,j); g.v(i,j)=g.gv(i,j)-(float)(s*(pt-pb)); } else g.v(i,j)=0.0f;
    if(!isSolid(i,j)&&!isSolid(i,j+1)){ double pb=g.gp(i,j), pt=isFluid(i,j+1)?g.gp(i,j+1):0.0; g.v(i,j+1)=g.gv(i,j+1)-(float)(s*(pt-pb)); } else g.v(i,j+1)=0.0f; }
}
// g2p/advect (Phase 0 mirror, sparse get sampling)
static float sU(const SparseMacGrid2D<8>& g,double px,double py){ int i0=(int)std::floor(px),j0=(int)std::floor(py-0.5); double fx=px-i0,fy=(py-0.5)-j0;
  auto v=[&](int i,int j){ return g.gu(std::max(0,std::min(g.nx,i)),std::max(0,std::min(g.ny-1,j))); };
  return (float)((1-fx)*(1-fy)*v(i0,j0)+fx*(1-fy)*v(i0+1,j0)+(1-fx)*fy*v(i0,j0+1)+fx*fy*v(i0+1,j0+1)); }
static float sV(const SparseMacGrid2D<8>& g,double px,double py){ int i0=(int)std::floor(px-0.5),j0=(int)std::floor(py); double fx=(px-0.5)-i0,fy=py-j0;
  auto v=[&](int i,int j){ return g.gv(std::max(0,std::min(g.nx-1,i)),std::max(0,std::min(g.ny,j))); };
  return (float)((1-fx)*(1-fy)*v(i0,j0)+fx*(1-fy)*v(i0+1,j0)+(1-fx)*fy*v(i0,j0+1)+fx*fy*v(i0+1,j0+1)); }
void spG2P(const SparseMacGrid2D<8>& g, Particles2D& ps, const SparseMacGrid2D<8>& saved, double alpha){
  for(size_t k=0;k<ps.size();++k){ double px=(ps.pos[k].x-g.ox)/g.dx,py=(ps.pos[k].y-g.oy)/g.dx;
    double un=sU(g,px,py),vn=sV(g,px,py); double du=un-sU(saved,px,py),dv=vn-sV(saved,px,py);
    double pic_x=un,pic_y=vn, flip_x=ps.vel[k].x+du, flip_y=ps.vel[k].y+dv;
    ps.vel[k].x=alpha*flip_x+(1-alpha)*pic_x; ps.vel[k].y=alpha*flip_y+(1-alpha)*pic_y; } }
void spAdvect(Particles2D& ps, const SparseMacGrid2D<8>& g, double dt){
  double lox=0.5*g.dx,hix=(g.nx-0.5)*g.dx,loy=0.5*g.dx,hiy=(g.ny-0.5)*g.dx;
  for(size_t k=0;k<ps.size();++k){ double px=ps.pos[k].x/g.dx,py=ps.pos[k].y/g.dx;
    double u1=sU(g,px,py),v1=sV(g,px,py); double mx=ps.pos[k].x+0.5*dt*u1,my=ps.pos[k].y+0.5*dt*v1;
    double u2=sU(g,mx/g.dx,my/g.dx),v2=sV(g,mx/g.dx,my/g.dx);
    ps.pos[k].x=std::max(lox,std::min(hix,ps.pos[k].x+dt*u2));
    ps.pos[k].y=std::max(loy,std::min(hiy,ps.pos[k].y+dt*v2)); } }
```
> 주: `Particles2D`는 Phase 0의 것(`pos,vel` Vec2, `size`, `add`). `splatU`가 face 인덱스 i를 0..nx까지 쓰므로 경계 체크에 유의.
- [ ] **Step 4: 빌드·테스트 PASS** (희소 투영 후 유체 발산 < 1e-4). 실패 시 디버그(부호·이웃·face 경계). 테스트 약화 금지.
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: sparse single-phase FLIP ops (P2G, CG pressure, project, G2P, advect)"`

---

## Task 3: SparseSim2D 드라이버 + dam-break 검증 (희소성 payoff)

**Files:** Create `src/driver/sparse_sim2d.h`, `src/driver/sparse_sim2d.cpp`, `tests/test_sparse_sim.cpp`; Modify `CMakeLists.txt`.

스텝: `clearAll → markCells(입자→FLUID, 경계→SOLID) → spP2G → saved=복사 → 중력(mv>0 면) → 벽 BC → spProjectStep → spG2P → spAdvect`.

- [ ] **Step 1: 실패 테스트** `tests/test_sparse_sim.cpp`:
```cpp
#include "doctest.h"
#include "driver/sparse_sim2d.h"
#include <cmath>
TEST_CASE("sparse dam-break: stable, count conserved, falls+spreads, SPARSE storage") {
  SparseSim2D sim(64,64,1.0);     // 8x8=64 cell-blocks total
  sim.initDamBreak();
  size_t n0=sim.particles.size(); CHECK(n0>0);
  double mx0=0,my0=0; for(size_t k=0;k<n0;++k){mx0+=sim.particles.pos[k].x;my0+=sim.particles.pos[k].y;} mx0/=n0;my0/=n0;
  size_t maxActive=0;
  for(int s=0;s<60;++s){ sim.step(); maxActive=std::max(maxActive,sim.grid.activeCellBlocks()); }
  CHECK(sim.particles.size()==n0);
  bool fin=true; double mx1=0,my1=0; for(size_t k=0;k<sim.particles.size();++k){ if(!std::isfinite(sim.particles.pos[k].x)||!std::isfinite(sim.particles.pos[k].y)) fin=false; mx1+=sim.particles.pos[k].x;my1+=sim.particles.pos[k].y;} mx1/=sim.particles.size();my1/=sim.particles.size();
  CHECK(fin); CHECK(my1<my0); CHECK(mx1>mx0);
  // SPARSITY payoff: never all 64 blocks active (fluid occupies a fraction)
  CHECK(maxActive < sim.grid.totalCellBlocks());
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/driver/sparse_sim2d.h`:
```cpp
#pragma once
#include "grid/sparse_mac_grid2d.h"
#include "particles/particles2d.h"
struct SparseSim2D {
  SparseMacGrid2D<8> grid; Particles2D particles;
  double dt=0.05, alpha=0.95, gravity=-9.81; int cg_iters=200; double cg_tol=1e-6;
  SparseSim2D(int nx,int ny,double dx) : grid(nx,ny,dx) {}
  void initDamBreak();
  void step();
};
```
`src/driver/sparse_sim2d.cpp`:
```cpp
#include "driver/sparse_sim2d.h"
#include "driver/sparse_ops2d.h"
#include <vector>
void SparseSim2D::initDamBreak(){
  int wc=grid.nx*4/10,hr=grid.ny*7/10;
  for(int j=1;j<hr;++j)for(int i=1;i<wc;++i)for(int sj=0;sj<2;++sj)for(int si=0;si<2;++si){
    double x=(i+0.25+0.5*si)*grid.dx,y=(j+0.25+0.5*sj)*grid.dx; particles.add({x,y},{0,0}); }
}
static void markCells(SparseMacGrid2D<8>& g, const Particles2D& ps){
  g.mkf.clear();
  for(int j=0;j<g.ny;++j){ g.setCell(0,j,2); g.setCell(g.nx-1,j,2); }
  for(int i=0;i<g.nx;++i){ g.setCell(i,0,2); g.setCell(i,g.ny-1,2); }
  for(size_t k=0;k<ps.size();++k){ int i=(int)(ps.pos[k].x/g.dx),j=(int)(ps.pos[k].y/g.dx);
    if(g.inBounds(i,j) && g.cell(i,j)!=2) g.setCell(i,j,1); }
}
void SparseSim2D::step(){
  markCells(grid, particles);
  spP2G(grid, particles);
  SparseMacGrid2D<8> saved = grid;                 // copy for FLIP delta
  // gravity on active v-faces with mass
  for(int b: grid.mvf.activeBlocks()){ int bx,by; grid.mvf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>=grid.nx||j>grid.ny) continue;
      if(grid.gmv(i,j)>0) grid.v(i,j)=grid.gv(i,j)+(float)(dt*gravity); } }
  // wall BC: zero normal velocity at the solid-interface faces (cols/rows 0,1,nx-1,nx ; 0,1,ny-1,ny)
  for(int j=0;j<grid.ny;++j){ grid.u(0,j)=0; grid.u(1,j)=0; grid.u(grid.nx-1,j)=0; grid.u(grid.nx,j)=0; }
  for(int i=0;i<grid.nx;++i){ grid.v(i,0)=0; grid.v(i,1)=0; grid.v(i,grid.ny-1)=0; grid.v(i,grid.ny)=0; }
  spProjectStep(grid, dt, cg_iters, cg_tol);
  spG2P(grid, particles, saved, alpha);
  spAdvect(particles, grid, dt);
}
```
- [ ] **Step 4: 빌드·테스트 PASS** (dam-break 안정·count보존·낙하·확산 + **활성블록 < 전체 = 희소성**). 60스텝이 느리면 32×32로 줄여도 됨(테스트는 64×64로 작성). 실패 시 디버그.
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: SparseSim2D single-phase FLIP dam-break on sparse grid"`

---

## Task 4: 희소 viz + 활성블록 비율 시연

**Files:** Create `src/driver/viz_sparse.h`, `apps/run_sparse_dambreak.cpp`; Modify `CMakeLists.txt`.

- [ ] **Step 1: viz** `src/driver/viz_sparse.h` — 입자(파랑) + 활성 셀블록 윤곽(어두운 녹색)을 PPM에 그림:
```cpp
#pragma once
#include <string>
#include <vector>
#include <fstream>
#include "driver/sparse_sim2d.h"
inline void writeSparsePPM(const SparseSim2D& sim,const std::string& path,int scale=8){
  int W=sim.grid.nx*scale,H=sim.grid.ny*scale; std::vector<unsigned char> img(W*H*3,16);
  // shade active blocks faintly
  for(int b: sim.grid.pf.activeBlocks()){ int bx,by; sim.grid.pf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>=sim.grid.nx||j>=sim.grid.ny) continue;
      int px=i*scale,py=H-1-j*scale; for(int yy=0;yy<scale;++yy)for(int xx=0;xx<scale;++xx){ int X=px+xx,Y=py-yy; if(X<0||X>=W||Y<0||Y>=H)continue; int o=(X+W*Y)*3; img[o]=24;img[o+1]=40;img[o+2]=28; } } }
  for(size_t k=0;k<sim.particles.size();++k){ int px=(int)(sim.particles.pos[k].x/sim.grid.dx*scale),py=H-1-(int)(sim.particles.pos[k].y/sim.grid.dx*scale);
    if(px<0||px>=W||py<0||py>=H) continue; int o=(px+W*py)*3; img[o]=60;img[o+1]=140;img[o+2]=230; }
  std::ofstream f(path,std::ios::binary); f<<"P6\n"<<W<<" "<<H<<"\n255\n"; f.write((const char*)img.data(),img.size());
}
```
- [ ] **Step 2: 러너** `apps/run_sparse_dambreak.cpp`:
```cpp
#include "driver/sparse_sim2d.h"
#include "driver/viz_sparse.h"
#include <cstdio>
int main(){ SparseSim2D sim(128,96,1.0);   // 16x12=192 blocks
  sim.initDamBreak();
  for(int s=0;s<160;++s){ sim.step(); if(s%5==0){ char n[64]; std::snprintf(n,sizeof(n),"sp_%03d.ppm",s/5); writeSparsePPM(sim,n); } }
  std::printf("done: %zu particles, max active blocks %zu/%zu\n", sim.particles.size(), sim.grid.activeCellBlocks(), sim.grid.totalCellBlocks());
  return 0; }
```
CMake: `add_executable(run_sparse_dambreak apps/run_sparse_dambreak.cpp)` + `target_link_libraries(run_sparse_dambreak pfflip2d)`.
- [ ] **Step 3: 빌드·실행** → sp_###.ppm 시퀀스 + "active blocks X/192" 출력. controller가 육안 확인(입자 dam-break + 활성블록이 유체 따라다님 = 희소).
- [ ] **Step 4: Commit** — `git add -A; git commit -m "feat: sparse dam-break viz + runner (active-block overlay)"`

---

## Self-Review
- **Coverage:** SparseMacGrid2D(T1), 희소 P2G/CG/투영(T2), 드라이버+dam-break+희소성(T3), viz(T4). ✅
- **Placeholder:** 전 step 코드/명령. 없음. ✅
- **Type consistency:** `SparseMacGrid2D<8>`(`u/v/mu/mv/p/gu../setCell/cell/clearAll/activeCellBlocks/uf/vf/muf/mvf/pf/mkf`), `spP2G/spProjectStep/spG2P/spAdvect`, `SparseSim2D`. 일관. `SparseBlockGrid2D::clear()` 추가. ✅
- **payoff 게이트:** dam-break가 (a)균일과 동등 거동(낙하·확산·안정·count보존), (b)**활성블록<전체(희소 저장)** — MSBG 가치 실현.
- **이월:** 2상·3D·다해상도 = 후속.
