# PF-FLIP Phase B — 희소 2상 (phase-field FLIP on sparse blocks) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`).

**Goal:** Phase 2의 2상 phase-field FLIP(Eq.7 φ, cubic 커널 Eq.6, 가변계수 β=1/ρ Poisson Eq.8)을 Phase A의 희소 인프라(`SparseMacGrid2D`) 위로 포팅한다. 검증 2축: **(a) 동등성** — 희소 Rayleigh-Taylor가 dense `Sim2DTP`처럼 뒤집힌다, **(b) 희소성** — 자유표면이 있는 버블 탱크 씬에서 빈 공간(headspace) 블록이 끝까지 할당되지 않는다. **payoff: 논문의 핵심 솔버(2상)가 논문의 자료구조(희소) 위에서 돈다.**

**Architecture:** 검증된 dense 2상 모듈을 희소 저장으로 미러링. **β는 저장하지 않고 면 raw 밀도에서 즉석 계산** — dense가 매 스텝 `bu[idx]=betaFromPhi(phiFromRawDensity(mu[idx]))`로 전 면을 채우는 것과 수학적으로 동일하며(질량 0 면 → φ=0 → β=1/ρ_g), 비활성 블록의 `get()`=0 기본값 문제를 원천 회피한다. 압력은 Phase A 패턴(유체셀 열거 CG + **면당 1회 갱신 face-sweep 투영** + `pf.clear()` 라이브 지표)에 dense `pressure2d_vc.cpp`의 두 정교화(**BC-aware 발산**, **순수 Neumann 핀**)를 이식. RT는 전 도메인이 입자로 차므로(순수 Neumann, 핀 경유) 희소성 게이트가 불가능 — 희소성은 **자유표면+2상 버블 씬**(물웅덩이+기포+빈 headspace)으로 시연한다. 2상에서 "빈 공간이 없는" 씬의 진짜 메모리 절감은 SPEC-2(narrow-band air)의 몫임을 명시.

**Tech Stack:** 기존 C++17/CMake/doctest. branch `feat/phaseB-sparse-twophase`(from main). 재사용: `phasefield.h`(PhaseParams/φ/β), `particles2d_tp.h`, `calibrateRhoTilde0_2d`(transfer2d_tp.h — 내부에서 자체 dense 8×8을 만들므로 그대로 호출 가능), Phase A의 `SparseMacGrid2D<8>`/`sparse_ops2d` 패턴.

**Scope:** 2D 2상 on sparse, 밀도비 100:1. **이월:** 3D 희소·다해상도·멀티스레드·halo·narrow-band air(SPEC-2)·c_div·escaped particles·1000:1.

---

## File Structure (신규)
| 파일 | 책임 |
|---|---|
| `src/driver/sparse_ops2d_tp.h`/`.cpp` | 2상 희소 ops: 정규화 cubic P2G(타입별 질량), VC 압력(β 즉석계산+Neumann 핀+BC-aware 발산), 타입별 α G2P, RK2 이류 |
| `src/driver/sparse_sim2d_tp.h`/`.cpp` | `SparseSim2DTP` 드라이버 + RT/버블탱크 씬 |
| `src/driver/viz_sparse_tp.h` | 상별 색(액체 파랑/기체 호박색) + 활성블록 오버레이 PPM |
| `apps/run_sparse_bubble.cpp` | 버블 탱크 러너 (max active blocks 출력) |
| `tests/test_sparse_transfer_tp.cpp` | cubic 운동량 보존 + φ 위상분리 + 스플랫 희소성 |
| `tests/test_sparse_vc.cpp` | 희소 VC 투영: Dirichlet 발산제거 + 순수 Neumann 정수압(핀 경유) |
| `tests/test_sparse_sim_tp.cpp` | 희소 RT 뒤집힘 (dense test_rt 미러) |
| `tests/test_sparse_bubble.cpp` | 버블 상승 + **희소성 게이트** (headspace 비할당) |

**규약:** Phase A와 동일 MAC/블록(B=8). marker float(0=AIR,1=FLUID,2=SOLID). 입자 타입 0=liquid, 1=gas, `m_p=ρ_type·V_p`(Vp=1). 커널 Eq.6 `w=(max(1−d²/r²,0))³`, KR=1.5셀, **per-particle 2-pass 정규화**(partition-of-unity → 운동량 정확 보존, dense `transfer2d_tp.cpp`와 동일). 함수명은 `sp*_tp`/`spProjectStepVC`로 기존 심볼과 충돌 없음. 핀 셀은 열거 순서상 첫 유체셀 — dense(행우선 첫 셀)와 셀이 다를 수 있으나 **널공간 상수만 고정하므로 수학적으로 동등**(디버깅 시 쫓지 말 것).

---

## Task 1: 2상 희소 P2G/G2P (정규화 cubic, 타입별)

**Files:** Create `src/driver/sparse_ops2d_tp.h`, `src/driver/sparse_ops2d_tp.cpp`, `tests/test_sparse_transfer_tp.cpp`; Modify `CMakeLists.txt` (cpp→`pfflip2d`, test→`unit_tests`).

- [ ] **Step 1: 실패 테스트** `tests/test_sparse_transfer_tp.cpp`:
```cpp
#include "doctest.h"
#include "grid/sparse_mac_grid2d.h"
#include "driver/sparse_ops2d_tp.h"
#include "transfer/transfer2d_tp.h"   // calibrateRhoTilde0_2d
#include "physics/phasefield.h"
TEST_CASE("sparse tp p2g: momentum conserved (normalized cubic)") {
  SparseMacGrid2D<8> g(6,6,1.0); PhaseParams pp; double Vp=1.0;
  Particles2DTP ps; ps.add({3.0,2.5},{4.0,0.0},0);   // liquid, m_p=rho_l*Vp=1
  spP2G_tp(g, ps, pp, Vp);
  double mom=0; for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i) mom += g.gu(i,j)*g.gmu(i,j);
  CHECK(mom == doctest::Approx(4.0).epsilon(1e-6));
}
TEST_CASE("sparse tp p2g: phase separation phi_liq~1 / phi_gas~0") {
  SparseMacGrid2D<8> g(8,8,1.0); PhaseParams pp; double Vp=1.0;
  Particles2DTP ps;
  for(int j=1;j<4;++j)for(int i=1;i<7;++i)for(int s=0;s<4;++s) ps.add({i+0.25+0.5*(s%2), j+0.25+0.5*(s/2)},{0,0},0);
  for(int j=4;j<7;++j)for(int i=1;i<7;++i)for(int s=0;s<4;++s) ps.add({i+0.25+0.5*(s%2), j+0.25+0.5*(s/2)},{0,0},1);
  pp.rho_tilde_0 = calibrateRhoTilde0_2d(pp, Vp);
  spP2G_tp(g, ps, pp, Vp);
  CHECK(phiFromRawDensity(g.gmu(4,2), pp) > 0.8);
  CHECK(phiFromRawDensity(g.gmu(4,5), pp) < 0.2);
}
TEST_CASE("sparse tp p2g: splat activates only touched blocks") {
  SparseMacGrid2D<8> g(64,64,1.0); PhaseParams pp; double Vp=1.0;
  Particles2DTP ps;
  for(int s=0;s<32;++s) ps.add({16.0+0.2*(s%8), 16.0+0.2*(s/8)},{1.0,0.0},0);  // confined near (16,16)
  spP2G_tp(g, ps, pp, Vp);
  CHECK(g.muf.activeBlockCount() > 0);
  CHECK(g.muf.activeBlockCount() < g.muf.totalBlocks());
}
TEST_CASE("sparse tp g2p: typed alpha blend (FLIP vs PIC per phase)") {
  SparseMacGrid2D<8> g(4,4,1.0), saved(4,4,1.0);
  for(int j=0;j<4;++j)for(int i=0;i<=4;++i){ g.u(i,j)=5.0f; saved.u(i,j)=2.0f; }
  Particles2DTP ps; ps.add({2.0,2.0},{10.0,0.0},0); ps.add({2.0,2.0},{10.0,0.0},1);
  spG2P_tp(g, ps, saved, 1.0, 0.0);   // liquid pure FLIP, gas pure PIC
  CHECK(ps.vel[0].x == doctest::Approx(13.0));  // 10 + (5-2)
  CHECK(ps.vel[1].x == doctest::Approx(5.0));   // grid velocity
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인** (`driver/sparse_ops2d_tp.h` 없음)
- [ ] **Step 3: 구현** `src/driver/sparse_ops2d_tp.h`:
```cpp
#pragma once
template<int B> struct SparseMacGrid2D;
struct Particles2DTP;
struct PhaseParams;
// two-phase sparse FLIP ops: typed masses m_p = rho_type*Vp; face beta = 1/rho(phi(raw)) computed on the fly
void spP2G_tp(SparseMacGrid2D<8>& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp);
void spProjectStepVC(SparseMacGrid2D<8>& g, const PhaseParams& pp, double dt, int cg_iters, double cg_tol);
void spG2P_tp(const SparseMacGrid2D<8>& g, Particles2DTP& ps, const SparseMacGrid2D<8>& saved, double aL, double aG);
void spAdvect_tp(Particles2DTP& ps, const SparseMacGrid2D<8>& g, double dt);
```
`src/driver/sparse_ops2d_tp.cpp` (Task 1 분량 — `spProjectStepVC`는 Task 2에서 이 파일에 추가):
```cpp
#include "driver/sparse_ops2d_tp.h"
#include "grid/sparse_mac_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <cmath>

// Eq.6 cubic kernel on squared distance; KR in cells (dense transfer2d_tp.cpp mirror)
static inline double kern(double d2, double r){ double q=d2/(r*r), t=1.0-q; return (t>0.0)? t*t*t : 0.0; }
static const double KR = 1.5;

// normalized 2-pass splat (partition of unity per particle) into u-field, ref()-activating writes
static void splatUK(SparseMacGrid2D<8>& g,double gx,double gy,double mom,double m){
  const int W=g.nx+1, H=g.ny;
  int rad=(int)std::ceil(KR); int i0=(int)std::floor(gx), j0=(int)std::floor(gy);
  double wsum=0;
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double dx=gx-ii,dy=gy-jj; wsum+=kern(dx*dx+dy*dy,KR); }
  if(wsum<=0.0) return;
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double dx=gx-ii,dy=gy-jj; double w=kern(dx*dx+dy*dy,KR)/wsum; if(w<=0.0) continue;
    g.u(ii,jj)+=(float)(w*mom); g.mu(ii,jj)+=(float)(w*m); }
}
// same for v-field
static void splatVK(SparseMacGrid2D<8>& g,double gx,double gy,double mom,double m){
  const int W=g.nx, H=g.ny+1;
  int rad=(int)std::ceil(KR); int i0=(int)std::floor(gx), j0=(int)std::floor(gy);
  double wsum=0;
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double dx=gx-ii,dy=gy-jj; wsum+=kern(dx*dx+dy*dy,KR); }
  if(wsum<=0.0) return;
  for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double dx=gx-ii,dy=gy-jj; double w=kern(dx*dx+dy*dy,KR)/wsum; if(w<=0.0) continue;
    g.v(ii,jj)+=(float)(w*mom); g.mv(ii,jj)+=(float)(w*m); }
}

void spP2G_tp(SparseMacGrid2D<8>& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp){
  g.uf.clear(); g.vf.clear(); g.muf.clear(); g.mvf.clear();
  for(size_t k=0;k<ps.size();++k){
    double rho=(ps.type[k]==0)? pp.rho_l : pp.rho_g; double mp=rho*Vp;
    double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    splatUK(g, px, py-0.5, mp*ps.vel[k].x, mp);
    splatVK(g, px-0.5, py, mp*ps.vel[k].y, mp);
  }
  // normalize: face velocity = momentum / raw mass, over active mass blocks only
  for(int b: g.muf.activeBlocks()){ int bx,by; g.muf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>g.nx||j>=g.ny) continue;
      float m=g.gmu(i,j); if(m>0) g.u(i,j)=g.gu(i,j)/m; } }
  for(int b: g.mvf.activeBlocks()){ int bx,by; g.mvf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>=g.nx||j>g.ny) continue;
      float m=g.gmv(i,j); if(m>0) g.v(i,j)=g.gv(i,j)/m; } }
}

// clamped bilinear samplers on sparse fields (file-local; Phase A sparse_ops2d.cpp mirror)
static float sU(const SparseMacGrid2D<8>& g,double px,double py){ int i0=(int)std::floor(px),j0=(int)std::floor(py-0.5); double fx=px-i0,fy=(py-0.5)-j0;
  auto v=[&](int i,int j){ return g.gu(std::max(0,std::min(g.nx,i)),std::max(0,std::min(g.ny-1,j))); };
  return (float)((1-fx)*(1-fy)*v(i0,j0)+fx*(1-fy)*v(i0+1,j0)+(1-fx)*fy*v(i0,j0+1)+fx*fy*v(i0+1,j0+1)); }
static float sV(const SparseMacGrid2D<8>& g,double px,double py){ int i0=(int)std::floor(px-0.5),j0=(int)std::floor(py); double fx=(px-0.5)-i0,fy=py-j0;
  auto v=[&](int i,int j){ return g.gv(std::max(0,std::min(g.nx-1,i)),std::max(0,std::min(g.ny,j))); };
  return (float)((1-fx)*(1-fy)*v(i0,j0)+fx*(1-fy)*v(i0+1,j0)+(1-fx)*fy*v(i0,j0+1)+fx*fy*v(i0+1,j0+1)); }

void spG2P_tp(const SparseMacGrid2D<8>& g, Particles2DTP& ps, const SparseMacGrid2D<8>& saved, double aL, double aG){
  for(size_t k=0;k<ps.size();++k){
    double a=(ps.type[k]==0)? aL : aG;
    double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    double un=sU(g,px,py), vn=sV(g,px,py);
    double du=un-sU(saved,px,py), dv=vn-sV(saved,px,py);
    double pic_x=un, pic_y=vn, flip_x=ps.vel[k].x+du, flip_y=ps.vel[k].y+dv;
    ps.vel[k].x=a*flip_x+(1-a)*pic_x; ps.vel[k].y=a*flip_y+(1-a)*pic_y;
  }
}
void spAdvect_tp(Particles2DTP& ps, const SparseMacGrid2D<8>& g, double dt){
  double lox=0.5*g.dx,hix=(g.nx-0.5)*g.dx,loy=0.5*g.dx,hiy=(g.ny-0.5)*g.dx;
  for(size_t k=0;k<ps.size();++k){ double px=ps.pos[k].x/g.dx,py=ps.pos[k].y/g.dx;
    double u1=sU(g,px,py),v1=sV(g,px,py); double mx=ps.pos[k].x+0.5*dt*u1,my=ps.pos[k].y+0.5*dt*v1;
    double u2=sU(g,mx/g.dx,my/g.dx),v2=sV(g,mx/g.dx,my/g.dx);
    ps.pos[k].x=std::max(lox,std::min(hix,ps.pos[k].x+dt*u2));
    ps.pos[k].y=std::max(loy,std::min(hiy,ps.pos[k].y+dt*v2)); }
}
```
> 주: 운동량 테스트 epsilon은 1e-6 (float 면 저장 — dense의 1e-9는 double 필드 기준). `splatUK/splatVK`의 wsum은 **in-bounds 노드만** 합산 — dense `splatK`와 동일한 경계 처리.
- [ ] **Step 4: 빌드·테스트 PASS** — `cmake -S . -B build; cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure`
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: sparse two-phase P2G/G2P (normalized cubic, typed alpha)"`

---

## Task 2: 희소 가변계수 압력 (β 즉석계산 + Neumann 핀 + BC-aware 발산)

**Files:** Modify `src/driver/sparse_ops2d_tp.cpp` (add `spProjectStepVC`); Create `tests/test_sparse_vc.cpp`; Modify `CMakeLists.txt` (test 추가).

dense `pressure2d_vc.cpp`의 미러: 면 β=1/ρ(φ(raw)), AIR=Dirichlet 0, SOLID=Neumann 제외, **유체셀 중 AIR 이웃이 하나도 없으면 첫 열거 셀을 identity row로 핀**. 발산은 BC-aware(솔리드 인접 면=0). 투영은 Phase A의 face-sweep(면당 1회, 유체 비인접 면 skip).

- [ ] **Step 1: 실패 테스트** `tests/test_sparse_vc.cpp`:
```cpp
#include "doctest.h"
#include "grid/sparse_mac_grid2d.h"
#include "driver/sparse_ops2d_tp.h"
#include "physics/phasefield.h"
#include <cmath>
TEST_CASE("sparse VC projection removes divergence (uniform liquid beta, Dirichlet air)") {
  SparseMacGrid2D<8> g(32,32,1.0); PhaseParams pp;
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    int c=(i==0||i==g.nx-1||j==0||j==g.ny-1)?2 : ((i>=10&&i<20&&j>=10&&j<20)?1:0);
    if(c!=0) g.setCell(i,j,c);
  }
  // packed-liquid raw density (=rho_l*rho_tilde_0=1) on blob faces -> beta ~ 1/rho_l
  for(int j=10;j<20;++j)for(int i=10;i<=20;++i) g.mu(i,j)=1.0f;
  for(int j=10;j<=20;++j)for(int i=10;i<20;++i) g.mv(i,j)=1.0f;
  for(int j=10;j<20;++j)for(int i=10;i<=20;++i) g.u(i,j)=(float)i;   // divergent
  spProjectStepVC(g, pp, 1.0, 500, 1e-9);
  double mx=0; for(int j=10;j<20;++j)for(int i=10;i<20;++i){
    double d=(g.gu(i+1,j)-g.gu(i,j)+g.gv(i,j+1)-g.gv(i,j)); mx=std::max(mx,std::abs(d)); }
  CHECK(mx < 1e-4);
  CHECK(g.pf.activeBlockCount() == 4);   // blob [10,20)^2 -> p-blocks {1,2}x{1,2} only
}
TEST_CASE("sparse VC hydrostatic two-phase column, pure Neumann (pin engaged): residual |v| bounded") {
  SparseMacGrid2D<8> g(6,16,1.0); PhaseParams pp;
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    int c=(i==0||i==g.nx-1||j==0||j==g.ny-1)?2:1;     // ALL interior FLUID -> no AIR anywhere
    g.setCell(i,j,c);
  }
  // face raw densities: heavy (packed liquid, raw=1 -> beta~1) below j=8, light (gas, raw=0.01 -> beta=100) above
  for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i) g.mu(i,j)=(j<8)?1.0f:0.01f;
  for(int j=0;j<=g.ny;++j)for(int i=0;i<g.nx;++i) g.mv(i,j)=(j<8)?1.0f:0.01f;
  double dt=0.1, gc=-9.81;
  for(int j=1;j<g.ny;++j)for(int i=0;i<g.nx;++i) g.v(i,j)=g.gv(i,j)+(float)(dt*gc);
  spProjectStepVC(g, pp, dt, 1000, 1e-10);
  double mv=0; for(int j=2;j<g.ny-1;++j)for(int i=1;i<g.nx-1;++i) mv=std::max(mv,std::abs((double)g.gv(i,j)));
  CHECK(mv < 0.5);   // hydrostatic balance held (free-fall would be ~0.981)
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인** (`spProjectStepVC` 미정의 링크 에러)
- [ ] **Step 3: 구현** — `src/driver/sparse_ops2d_tp.cpp`에 추가 (`spP2G_tp` 아래):
```cpp
static std::vector<int> fluidCellsTP(const SparseMacGrid2D<8>& g){
  std::vector<int> cells;
  for(int b: g.mkf.activeBlocks()){ int bx,by; g.mkf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly;
      if(g.inBounds(i,j) && g.cell(i,j)==1) cells.push_back(i + g.nx*j); } }
  return cells;
}
void spProjectStepVC(SparseMacGrid2D<8>& g, const PhaseParams& pp, double dt, int cg_iters, double cg_tol){
  g.pf.clear();                                 // p-blocks track LIVE fluid (sparsity metric/viz read pf)
  auto cells = fluidCellsTP(g);
  int N=(int)cells.size(); if(N==0) return;
  std::unordered_map<int,int> idx; idx.reserve(N*2);
  for(int t=0;t<N;++t) idx[cells[t]]=t;
  auto isFluid=[&](int i,int j){ return g.inBounds(i,j) && g.cell(i,j)==1; };
  auto isSolid=[&](int i,int j){ return !g.inBounds(i,j) || g.cell(i,j)==2; };
  auto isAir  =[&](int i,int j){ return g.inBounds(i,j) && g.cell(i,j)==0; };
  // face beta on the fly from raw face density (== dense per-face bu/bv computation)
  auto bU=[&](int i,int j){ return betaFromPhi(phiFromRawDensity((double)g.gmu(i,j),pp),pp); };
  auto bV=[&](int i,int j){ return betaFromPhi(phiFromRawDensity((double)g.gmv(i,j),pp),pp); };
  // pure-Neumann pin (dense findPinCell mirror): pin first enumerated fluid cell iff no fluid cell touches AIR
  int pc=-1;
  { bool dirichlet=false; const int di[4]={1,-1,0,0},dj[4]={0,0,1,-1};
    for(int t=0;t<N && !dirichlet;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx;
      for(int n=0;n<4;++n) if(isAir(i+di[n],j+dj[n])){ dirichlet=true; break; } }
    if(!dirichlet) pc=cells[0]; }
  double scale=dt/(g.dx*g.dx);
  // rhs = -divergence, BC-aware: solid-adjacent face velocities count as 0 (dense divergenceVC mirror)
  std::vector<double> x(N,0),r(N),z(N),pd(N),Ap(N);
  for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx;
    if(cells[t]==pc){ r[t]=0.0; continue; }
    double uR=isSolid(i+1,j)?0.0:(double)g.gu(i+1,j), uL=isSolid(i-1,j)?0.0:(double)g.gu(i,j);
    double vT=isSolid(i,j+1)?0.0:(double)g.gv(i,j+1), vB=isSolid(i,j-1)?0.0:(double)g.gv(i,j);
    r[t]=-((uR-uL)+(vT-vB))/g.dx; }
  auto diagOf=[&](int i,int j){
    double d=0; struct F{int ni,nj;double b;};
    F fs[4]={ {i+1,j,bU(i+1,j)},{i-1,j,bU(i,j)},{i,j+1,bV(i,j+1)},{i,j-1,bV(i,j)} };
    for(auto& f:fs) if(!isSolid(f.ni,f.nj)) d+=f.b;
    return scale*d; };
  auto applyA=[&](const std::vector<double>& xx,std::vector<double>& out){
    for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx;
      if(cells[t]==pc){ out[t]=xx[t]; continue; }            // identity row pins pressure
      double diag=0,off=0; struct F{int ni,nj;double b;};
      F fs[4]={ {i+1,j,bU(i+1,j)},{i-1,j,bU(i,j)},{i,j+1,bV(i,j+1)},{i,j-1,bV(i,j)} };
      for(auto& f:fs){ if(isSolid(f.ni,f.nj)) continue; diag+=f.b;
        int nc=f.ni+g.nx*f.nj;
        if(isFluid(f.ni,f.nj) && nc!=pc) off+=f.b*xx[idx[nc]]; }
      out[t]=scale*(diag*xx[t]-off); } };
  auto prec=[&](const std::vector<double>& in,std::vector<double>& o){
    for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx;
      double d=(cells[t]==pc)?1.0:diagOf(i,j); o[t]=(d>0)?in[t]/d:0.0; } };
  auto dotp=[&](const std::vector<double>& a,const std::vector<double>& b){ double s=0; for(int t=0;t<N;++t) s+=a[t]*b[t]; return s; };
  double res0=0; for(int t=0;t<N;++t) res0=std::max(res0,std::abs(r[t])); if(res0<cg_tol) return;
  prec(r,z); pd=z; double rz=dotp(r,z),res=res0;
  for(int it=0;it<cg_iters;++it){ applyA(pd,Ap); double pAp=dotp(pd,Ap); if(std::abs(pAp)<1e-30) break;
    double al=rz/pAp; for(int t=0;t<N;++t){x[t]+=al*pd[t];r[t]-=al*Ap[t];}
    res=0; for(int t=0;t<N;++t) res=std::max(res,std::abs(r[t])); if(res<cg_tol) break;
    prec(r,z); double rzn=dotp(r,z),be=rzn/rz; rz=rzn; for(int t=0;t<N;++t) pd[t]=z[t]+be*pd[t]; }
  for(int t=0;t<N;++t){ int i=cells[t]%g.nx,j=cells[t]/g.nx; g.p(i,j)=(float)x[t]; }
  // project with face beta: single-touch face sweeps (Phase A corrected pattern + dense projectVC beta)
  double s=dt/g.dx;
  // NOTE: dense index sweep, sparse writes (skip = no block activation); sparsifying the sweep = Phase 3b/4
  for(int j=0;j<g.ny;++j)for(int i=1;i<g.nx;++i){
    bool lf=isFluid(i-1,j), rf=isFluid(i,j);
    if(!lf&&!rf) continue;
    if(isSolid(i-1,j)||isSolid(i,j)){ g.u(i,j)=0.0f; continue; }
    double pl=lf?(double)g.gp(i-1,j):0.0, pr=rf?(double)g.gp(i,j):0.0;
    g.u(i,j)=g.gu(i,j)-(float)(s*bU(i,j)*(pr-pl));
  }
  for(int j=1;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    bool bf=isFluid(i,j-1), tf=isFluid(i,j);
    if(!bf&&!tf) continue;
    if(isSolid(i,j-1)||isSolid(i,j)){ g.v(i,j)=0.0f; continue; }
    double pb=bf?(double)g.gp(i,j-1):0.0, pt=tf?(double)g.gp(i,j):0.0;
    g.v(i,j)=g.gv(i,j)-(float)(s*bV(i,j)*(pt-pb));
  }
}
```
> 핀 셀의 p는 identity row + rhs 0으로 0에 고정 — 투영에서 특별 처리 불필요(dense와 동일). `fluidCellsTP`는 Phase A `fluidCells`의 file-local 복제(static, ODR 무해) — 공용화는 Phase 3b 정리 항목.
- [ ] **Step 4: 빌드·테스트 PASS** (발산<1e-4 + pf 블록 4개 + 정수압 잔류 |v|<0.5). 실패 시 디버그(β 부호/면 인덱스/핀 rhs). **테스트 약화 금지.**
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: sparse variable-coefficient pressure (on-the-fly beta, Neumann pin, BC-aware div)"`

---

## Task 3: SparseSim2DTP 드라이버 + 희소 RT 동등성

**Files:** Create `src/driver/sparse_sim2d_tp.h`, `src/driver/sparse_sim2d_tp.cpp`, `tests/test_sparse_sim_tp.cpp`; Modify `CMakeLists.txt`.

스텝(dense `Sim2DTP::step()` 미러): `markCells(입자→FLUID, 테두리→SOLID) → spP2G_tp → saved=복사 → 중력(mv>0 활성블록) → 벽 BC → spProjectStepVC → spG2P_tp(αL,αG) → spAdvect_tp`. β는 spProjectStepVC 내부에서 즉석 계산되므로 드라이버에 β 채널 갱신 단계가 없다(dense와의 구조적 차이 — 수학은 동일).

- [ ] **Step 1: 실패 테스트** `tests/test_sparse_sim_tp.cpp` (dense `test_rt.cpp` 미러):
```cpp
#include "doctest.h"
#include "driver/sparse_sim2d_tp.h"
#include <cmath>
TEST_CASE("sparse two-phase Rayleigh-Taylor overturns (heavy over light)") {
  SparseSim2DTP sim(32,48,1.0);
  sim.initRayleighTaylor();
  auto meanY=[&](unsigned char t){ double s=0;int n=0; for(size_t k=0;k<sim.particles.size();++k) if(sim.particles.type[k]==t){s+=sim.particles.pos[k].y;++n;} return n?s/n:0.0; };
  double hy0=meanY(0), gy0=meanY(1);
  CHECK(hy0 > gy0);                 // heavy starts on top
  size_t n0=sim.particles.size();
  for(int s=0;s<80;++s) sim.step();
  CHECK(sim.particles.size()==n0);
  bool fin=true; for(size_t k=0;k<sim.particles.size();++k) if(!std::isfinite(sim.particles.pos[k].x)||!std::isfinite(sim.particles.pos[k].y)) fin=false;
  CHECK(fin);
  CHECK(meanY(0) < hy0);            // heavy sank
  CHECK(meanY(1) > gy0);            // light rose
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/driver/sparse_sim2d_tp.h`:
```cpp
#pragma once
#include "grid/sparse_mac_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"
struct SparseSim2DTP {
  SparseMacGrid2D<8> grid; Particles2DTP particles; PhaseParams phase;
  double dt=0.02, gravity=-9.81, Vp=1.0;
  double alpha_liquid=0.95, alpha_gas=0.95;
  int cg_iters=400; double cg_tol=1e-7;
  SparseSim2DTP(int nx,int ny,double dx) : grid(nx,ny,dx) {}
  void initRayleighTaylor();
  void initBubbleTank();
  void step();
};
```
`src/driver/sparse_sim2d_tp.cpp` (`initBubbleTank`는 Task 4에서 채움 — 여기서는 선언만 있고 정의 없으면 링크 에러가 나므로 **빈 stub 정의**를 두고 Task 4에서 본문 작성):
```cpp
#include "driver/sparse_sim2d_tp.h"
#include "driver/sparse_ops2d_tp.h"
#include "transfer/transfer2d_tp.h"   // calibrateRhoTilde0_2d
#include <cmath>
#include <algorithm>

static void seedCell(Particles2DTP& ps,int i,int j,double dx,unsigned char t){
  for(int s=0;s<4;++s){ double x=(i+0.25+0.5*(s%2))*dx, y=(j+0.25+0.5*(s/2))*dx; ps.add({x,y},{0,0},t); }
}
void SparseSim2DTP::initRayleighTaylor(){
  phase.rho_tilde_0 = calibrateRhoTilde0_2d(phase, Vp);
  int mid=grid.ny/2;
  for(int j=1;j<grid.ny-1;++j)for(int i=1;i<grid.nx-1;++i){
    double pert = 1.0*std::cos(2*3.14159265*i/grid.nx);
    bool heavy = (double)j > (mid + pert);
    seedCell(particles,i,j,grid.dx, heavy?0:1);
  }
}
void SparseSim2DTP::initBubbleTank(){ /* Task 4 */ }
static void markCells(SparseMacGrid2D<8>& g, const Particles2DTP& ps){
  g.mkf.clear();
  for(int j=0;j<g.ny;++j){ g.setCell(0,j,2); g.setCell(g.nx-1,j,2); }
  for(int i=0;i<g.nx;++i){ g.setCell(i,0,2); g.setCell(i,g.ny-1,2); }
  for(size_t k=0;k<ps.size();++k){ int i=(int)(ps.pos[k].x/g.dx),j=(int)(ps.pos[k].y/g.dx);
    if(g.inBounds(i,j) && g.cell(i,j)!=2) g.setCell(i,j,1); }
}
void SparseSim2DTP::step(){
  markCells(grid, particles);
  spP2G_tp(grid, particles, phase, Vp);
  SparseMacGrid2D<8> saved = grid;                 // FLIP snapshot (pre-forces)
  for(int b: grid.mvf.activeBlocks()){ int bx,by; grid.mvf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>=grid.nx||j>grid.ny) continue;
      if(grid.gmv(i,j)>0) grid.v(i,j)=grid.gv(i,j)+(float)(dt*gravity); } }
  for(int j=0;j<grid.ny;++j){ grid.u(0,j)=0; grid.u(1,j)=0; grid.u(grid.nx-1,j)=0; grid.u(grid.nx,j)=0; }
  for(int i=0;i<grid.nx;++i){ grid.v(i,0)=0; grid.v(i,1)=0; grid.v(i,grid.ny-1)=0; grid.v(i,grid.ny)=0; }
  spProjectStepVC(grid, phase, dt, cg_iters, cg_tol);
  spG2P_tp(grid, particles, saved, alpha_liquid, alpha_gas);
  spAdvect_tp(particles, grid, dt);
}
```
- [ ] **Step 4: 빌드·테스트 PASS** (희소 RT 뒤집힘: heavy↓ light↑ + 유한 + count). RT는 순수 Neumann(전 도메인 입자)이라 **핀 경로가 실전 검증**됨. 실패 시 디버그. **테스트 약화 금지.**
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: SparseSim2DTP two-phase driver + sparse Rayleigh-Taylor"`

---

## Task 4: 버블 탱크 (자유표면 + 2상) — 희소성 게이트

**Files:** Modify `src/driver/sparse_sim2d_tp.cpp` (`initBubbleTank` 본문); Create `tests/test_sparse_bubble.cpp`; Modify `CMakeLists.txt`.

씬: 물웅덩이(하단 절반, liquid) + 그 안의 원형 기포(gas) + **빈 headspace(입자 없음 = 진짜 AIR)**. AIR가 있으므로 Dirichlet 경로. 기포는 β 대비(1 vs 100)에서 창발하는 부력으로 상승. headspace 셀-블록은 끝까지 비할당 → **2상에서도 희소성 payoff**.

- [ ] **Step 1: 실패 테스트** `tests/test_sparse_bubble.cpp`:
```cpp
#include "doctest.h"
#include "driver/sparse_sim2d_tp.h"
#include <cmath>
#include <algorithm>
TEST_CASE("sparse bubble tank: gas rises by buoyancy, headspace blocks never allocated") {
  SparseSim2DTP sim(48,48,1.0);    // 6x6=36 cell-blocks
  sim.initBubbleTank();            // water rows [1,24), gas bubble circle, empty above
  size_t n0=sim.particles.size(); CHECK(n0>0);
  auto meanY=[&](unsigned char t){ double s=0;int n=0; for(size_t k=0;k<sim.particles.size();++k) if(sim.particles.type[k]==t){s+=sim.particles.pos[k].y;++n;} return n?s/n:0.0; };
  double gy0=meanY(1); CHECK(gy0>0.0);
  size_t maxActive=0;
  for(int s=0;s<60;++s){ sim.step(); maxActive=std::max(maxActive,sim.grid.activeCellBlocks()); }
  CHECK(sim.particles.size()==n0);
  bool fin=true; for(size_t k=0;k<sim.particles.size();++k) if(!std::isfinite(sim.particles.pos[k].x)||!std::isfinite(sim.particles.pos[k].y)) fin=false;
  CHECK(fin);
  CHECK(meanY(1) > gy0 + 0.5);                       // bubble rose
  CHECK(maxActive > 0);
  CHECK(maxActive < sim.grid.totalCellBlocks());     // headspace stayed unallocated (sparsity)
}
```
- [ ] **Step 2: CMake 추가 → 빌드·테스트 실행 → 새 테스트 FAIL 확인** (`initBubbleTank` stub이 입자를 안 만들어 `n0>0` FAIL — 올바른 이유)
- [ ] **Step 3: 구현** — `sparse_sim2d_tp.cpp`의 stub을 본문으로 교체:
```cpp
void SparseSim2DTP::initBubbleTank(){
  phase.rho_tilde_0 = calibrateRhoTilde0_2d(phase, Vp);
  int wl = grid.ny/2;                                  // water level: liquid rows [1, wl)
  double cx = grid.nx*0.5, cy = wl*0.375, r = grid.nx*0.09375;   // 48x48 -> cx=24, cy=9, r=4.5
  for(int j=1;j<wl;++j)for(int i=1;i<grid.nx-1;++i){
    double dxc=(i+0.5)-cx, dyc=(j+0.5)-cy;
    bool gas = (dxc*dxc+dyc*dyc) < r*r;
    seedCell(particles,i,j,grid.dx, gas?1:0);          // bubble=gas, pool=liquid; above wl: EMPTY (AIR)
  }
}
```
- [ ] **Step 4: 빌드·테스트 PASS** (기포 상승 ≥0.5셀 + maxActive ∈ (0, 36)). headspace는 입자/유체셀이 없어 pf 블록이 비활성으로 남는 게 게이트의 핵심. 실패 시 디버그(부력 방향: heavy β小·light β大, AIR Dirichlet). **테스트 약화 금지.**
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: bubble-tank scene (free surface + two-phase) with sparsity gate"`

---

## Task 5: 2상 희소 viz + 버블 러너 (시연)

**Files:** Create `src/driver/viz_sparse_tp.h`, `apps/run_sparse_bubble.cpp`; Modify `CMakeLists.txt`.

- [ ] **Step 1: viz** `src/driver/viz_sparse_tp.h` — 활성블록(암녹) + 액체(파랑) + 기체(호박색 — dense의 암색 대신; 기포가 주인공인 데모라 가시성 우선, 의도된 팔레트 변경):
```cpp
#pragma once
#include <string>
#include <vector>
#include <fstream>
#include "driver/sparse_sim2d_tp.h"
inline void writeSparseTPPPM(const SparseSim2DTP& sim,const std::string& path,int scale=8){
  int W=sim.grid.nx*scale,H=sim.grid.ny*scale; std::vector<unsigned char> img(W*H*3,16);
  for(int b: sim.grid.pf.activeBlocks()){ int bx,by; sim.grid.pf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>=sim.grid.nx||j>=sim.grid.ny) continue;
      int px=i*scale,py=H-1-j*scale; for(int yy=0;yy<scale;++yy)for(int xx=0;xx<scale;++xx){ int X=px+xx,Y=py-yy; if(X<0||X>=W||Y<0||Y>=H)continue; int o=(X+W*Y)*3; img[o]=24;img[o+1]=40;img[o+2]=28; } } }
  for(size_t k=0;k<sim.particles.size();++k){ int px=(int)(sim.particles.pos[k].x/sim.grid.dx*scale),py=H-1-(int)(sim.particles.pos[k].y/sim.grid.dx*scale);
    if(px<0||px>=W||py<0||py>=H) continue; int o=(px+W*py)*3;
    if(sim.particles.type[k]==0){ img[o]=60;img[o+1]=140;img[o+2]=230; } else { img[o]=235;img[o+1]=160;img[o+2]=60; } }
  std::ofstream f(path,std::ios::binary); f<<"P6\n"<<W<<" "<<H<<"\n255\n"; f.write((const char*)img.data(),img.size());
}
```
- [ ] **Step 2: 러너** `apps/run_sparse_bubble.cpp`:
```cpp
#include "driver/sparse_sim2d_tp.h"
#include "driver/viz_sparse_tp.h"
#include <algorithm>
#include <cstdio>
int main(){ SparseSim2DTP sim(96,96,1.0);   // 12x12=144 blocks; water rows [1,48), bubble r=9
  sim.initBubbleTank();
  size_t maxActive=0;
  for(int s=0;s<200;++s){ sim.step(); maxActive=std::max(maxActive,sim.grid.activeCellBlocks());
    if(s%5==0){ char n[64]; std::snprintf(n,sizeof(n),"spb_%03d.ppm",s/5); writeSparseTPPPM(sim,n); } }
  std::printf("done: %zu particles, max active blocks %zu/%zu\n", sim.particles.size(), maxActive, sim.grid.totalCellBlocks());
  return 0; }
```
CMake: `add_executable(run_sparse_bubble apps/run_sparse_bubble.cpp)` + `target_link_libraries(run_sparse_bubble pfflip2d)`.
- [ ] **Step 3: 빌드·실행** — 러너는 Release로(`cmake --build build --config Release --target run_sparse_bubble`), 리포 루트에서 실행 → `spb_###.ppm` 40프레임 + "max active blocks X/144" 출력(기대: X≈72 — 물 영역 절반만). 대표 프레임 4장을 PNG로 변환(리포 밖 임시 폴더)해 controller 육안 확인: **기포가 떠오르고, 활성블록이 하단 절반에만 있으며, headspace는 끝까지 검정**.
- [ ] **Step 4: 전체 Debug 스위트 PASS 재확인 후 Commit** — `git add src/driver/viz_sparse_tp.h apps/run_sparse_bubble.cpp CMakeLists.txt; git commit -m "feat: sparse two-phase viz + bubble runner (active-block overlay)"`

---

## Self-Review
- **Coverage:** 2상 P2G/G2P cubic(T1) · 가변계수 압력+핀+BC-aware(T2) · 드라이버+RT 동등성(T3) · 자유표면 버블+희소성 게이트(T4) · viz/러너 시연(T5). Eq.6/7/8 전부 희소 위에서. ✅
- **Placeholder:** 전 step 실제 코드/명령. `initBubbleTank` stub은 Task 3에 명시적 빈 정의 + Task 4에서 본문 교체로 처리(TBD 아님). ✅
- **Type consistency:** `spP2G_tp/spProjectStepVC/spG2P_tp/spAdvect_tp(SparseMacGrid2D<8>, Particles2DTP, PhaseParams)`, `SparseSim2DTP(grid/particles/phase/dt/gravity/Vp/alpha_liquid/alpha_gas/cg_iters/cg_tol/initRayleighTaylor/initBubbleTank/step)`, `writeSparseTPPPM`, 기존 `calibrateRhoTilde0_2d/phiFromRawDensity/betaFromPhi/Particles2DTP` 재사용 — 전 태스크 일관. ✅
- **검증 관문:** 운동량 1e-6 + 위상분리(T1) · 발산<1e-4+pf=4블록 + 정수압<0.5(핀 실전)(T2) · RT 뒤집힘(T3) · 기포 상승+headspace 비할당(T4) · 육안+X/144(T5).
- **Phase A 교훈 선반영:** face-sweep 투영(면당 1회) · `pf.clear()` 라이브 지표 · 러너 max 추적 라벨 · 운동량 epsilon float 보정 · 명시적 `#include <algorithm>`.
- **정직성:** RT는 활성≈전체(전 도메인 입자)라 희소성 게이트가 원리적으로 불가 — 희소성은 버블 씬이 담당. 2상 전역 씬의 메모리 절감은 SPEC-2(narrow-band air) 이월임을 Architecture에 명시.
