# PF-FLIP Phase 2 ★ — 2상 Phase-Field (논문 코어) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`) syntax.

**Goal:** 단상 FLIP에 **논문의 핵심 — 표면 재구성 없는 2상(공기-물) phase-field**를 더한다. P2G raw 밀도를 위상장 φ로 재활용(Eq.7), cubic 커널(Eq.6), 공간 가변 계수 β=1/ρ 압력 Poisson(Eq.8), 상별 점성. 2D에서 Fig.7 곡선 · 정수압 평형 · **Rayleigh-Taylor 불안정성**으로 검증. (SPEC-1 Phase 2 = ★권장 정지선; 여기서 비로소 "논문다운" 2상 솔버)

**Architecture:** 기존 2D MAC FLIP 위에 2상 레이어 추가. 입자가 liquid/gas **타입**을 가지고 둘 다 격자에 splat → 면 raw 밀도 → Eq.7로 φ → ρ=lerp(ρ_g,ρ_l,φ) → β=1/ρ. 압력 Poisson은 면별 β로 가변계수화. 도메인은 free surface가 아니라 **양쪽 상이 채움**(공기 명시 해석). Phase 0 모듈은 보존, 2상 모듈은 `*_tp`(two-phase) 신규.

**Tech Stack:** 기존 C++17/CMake/doctest. branch `feat/phase2-twophase` (from main).

**Scope (정직):** 중간 밀도비(기본 100:1)로 표준 CG 수렴 범위에서 검증. 실제 1000:1·적응 Poisson(§6)·escaped droplet 변환·완전한 c_div 부피보존은 **SPEC-2/3로 이월**. Phase 2는 *2상 phase-field 코어 + 가변계수 투영*의 정성 정확성(위상 분리·정수압·RT)에 집중.

---

## File Structure (신규)
| 파일 | 책임 |
|---|---|
| `src/physics/phasefield.h` | Eq.7 위상장 변환 `phiFromRawDensity` + PhaseParams |
| `src/transfer/transfer2d_tp.h`/`.cpp` | cubic 커널(Eq.6) 타입별 P2G(raw 밀도) + G2P(상별 α) |
| `src/pressure/pressure2d_vc.h`/`.cpp` | 가변계수 β Poisson + 투영 |
| `src/driver/sim2d_tp.h`/`.cpp` | 2상 스텝 루프, RT/정수압/dam-break 씬 |
| `src/driver/viz_phase.h` | φ 컬러 viz (liquid/gas 구분) |
| `apps/run_rt2d.cpp` | Rayleigh-Taylor 러너 |
| `tests/test_*_tp.cpp` | 2상 회귀 테스트 |

**규약:** 면 raw 밀도는 기존 `mu/mv`(누적 질량) 재사용. `ρ̃_0`(packed liquid 기준 raw 밀도)는 1로 정규화되도록 입자 부피 `V_p`를 잡는다(아래 Task 2 calibration). 2상에서 marker: 입자(liquid OR gas) 있는 셀=FLUID, 빈 셀=AIR, 벽=SOLID. 압력은 모든 FLUID(양상)에서 풂.

---

## Task 1: 위상장 변환 (Eq.7) + Fig.7 검증

**Files:** Create `src/physics/phasefield.h`, `tests/test_phasefield.cpp`; Modify `CMakeLists.txt`.

Eq.7: `φ(ρ̃)=0` if `ρ̃<ρ̃_min`; else `min(sqrt(max(ρ̃−ρ̃_min,0)/(α_φ·ρ̃_0·ρ_l)),1)`, `ρ̃_min=η_φ·ρ_g·ρ̃_0`, `η_φ=log(ρ_l/ρ_g)`.

- [ ] **Step 1: 실패 테스트** `tests/test_phasefield.cpp`:
```cpp
#include "doctest.h"
#include "physics/phasefield.h"
#include <cmath>
TEST_CASE("Eq.7 phase field curve (Fig.7)") {
  PhaseParams pp;                  // rho_l=1, rho_g=0.01, alpha_phi=1, rho_tilde_0=1
  // gas-level raw density -> phi = 0 (below threshold)
  CHECK(phiFromRawDensity(pp.rho_g, pp) == doctest::Approx(0.0));
  // packed-liquid raw density (~rho_l) -> phi ~ 1
  CHECK(phiFromRawDensity(pp.rho_l, pp) == doctest::Approx(1.0).epsilon(0.02));
  // monotonic non-decreasing
  double prev=-1;
  for(double rt=0; rt<=1.0; rt+=0.05){ double f=phiFromRawDensity(rt,pp); CHECK(f>=prev-1e-12); CHECK(f>=0.0); CHECK(f<=1.0); prev=f; }
  // threshold rho_min = log(100)*0.01*1 ~ 0.0461; just below -> 0, just above -> >0
  double rmin = std::log(pp.rho_l/pp.rho_g)*pp.rho_g*pp.rho_tilde_0;
  CHECK(phiFromRawDensity(rmin*0.99, pp) == doctest::Approx(0.0));
  CHECK(phiFromRawDensity(rmin*1.01 + 0.05, pp) > 0.0);
}
```
- [ ] **Step 2: CMake에 test 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/physics/phasefield.h`:
```cpp
#pragma once
#include <cmath>
#include <algorithm>
struct PhaseParams {
  double rho_l = 1.0;        // liquid density (normalized)
  double rho_g = 0.01;       // gas density (ratio 100:1)
  double alpha_phi = 1.0;    // noise<->stiffness knob
  double rho_tilde_0 = 1.0;  // reference raw density of packed liquid (calibrated to 1)
};
inline double etaPhi(const PhaseParams& pp){ return std::log(pp.rho_l/pp.rho_g); }
// Eq.7
inline double phiFromRawDensity(double rt, const PhaseParams& pp){
  double rmin = etaPhi(pp)*pp.rho_g*pp.rho_tilde_0;
  if(rt < rmin) return 0.0;
  double v = std::sqrt(std::max(rt-rmin,0.0)/(pp.alpha_phi*pp.rho_tilde_0*pp.rho_l));
  return std::min(v, 1.0);
}
// density / pressure-coeff from phi
inline double densityFromPhi(double phi, const PhaseParams& pp){ return phi*pp.rho_l + (1.0-phi)*pp.rho_g; }
inline double betaFromPhi(double phi, const PhaseParams& pp){ return 1.0/densityFromPhi(phi, pp); }
```
- [ ] **Step 4: 빌드·테스트 PASS** — `cmake -S . -B build; cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure`
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: Eq.7 phase-field transform (Fig.7 validated)"`

---

## Task 2: cubic 커널(Eq.6) + 타입별 2상 P2G/G2P

**Files:** Create `src/transfer/transfer2d_tp.h`, `src/transfer/transfer2d_tp.cpp`, `tests/test_transfer_tp.cpp`; Modify `CMakeLists.txt` (cpp→library, test→unit_tests).

타입별 입자(0=liquid,1=gas), `m_p = ρ_type·V_p`. cubic 커널 Eq.6: `w=(max(1−(d/r)²,0))³` (반경 r=r0·dx, 기본 r0=1.0, 제곱거리 기반). 면 raw 밀도 = Σ w·m_p(=`mu/mv`). 면 속도 = Σ w·m_p·u / Σ w·m_p. G2P는 상별 α.

> Particles2D는 type이 없으므로 2상 전용 컨테이너를 쓴다. `src/particles/particles2d_tp.h` 추가:
```cpp
#pragma once
#include <vector>
#include "math/vec2.h"
struct Particles2DTP {
  std::vector<Vec2> pos, vel;
  std::vector<unsigned char> type;  // 0=liquid, 1=gas
  size_t size() const { return pos.size(); }
  void add(const Vec2& p, const Vec2& v, unsigned char t){ pos.push_back(p); vel.push_back(v); type.push_back(t); }
};
```

- [ ] **Step 1: 실패 테스트** `tests/test_transfer_tp.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d_tp.h"
#include "transfer/transfer2d_tp.h"
#include "physics/phasefield.h"
TEST_CASE("tp p2g momentum conserved (cubic kernel)") {
  UniformGrid2D g(6,6,1.0); PhaseParams pp; double Vp=1.0;
  Particles2DTP ps; ps.add({3.0,2.5},{4.0,0.0},0);  // liquid near u-faces
  p2g_tp(g, ps, pp, Vp);
  // total x-momentum over all u-faces equals m_p*vx (m_p=rho_l*Vp=1)
  double mom=0; for(int j=0;j<g.ny;++j) for(int i=0;i<=g.nx;++i) mom += g.u(i,j)*g.mu[i+(g.nx+1)*j];
  CHECK(mom == doctest::Approx(4.0).epsilon(1e-9));
}
TEST_CASE("tp p2g separates phases: liquid block -> phi~1, gas -> phi~0") {
  UniformGrid2D g(8,8,1.0); PhaseParams pp; double Vp=1.0;
  Particles2DTP ps;
  // fill bottom half with liquid (4 per cell), top half with gas
  for(int j=1;j<4;++j) for(int i=1;i<7;++i) for(int s=0;s<4;++s){
    double jit=0.25+0.5*(s%2); double jit2=0.25+0.5*(s/2);
    ps.add({i+jit, j+jit2},{0,0},0); }
  for(int j=4;j<7;++j) for(int i=1;i<7;++i) for(int s=0;s<4;++s){
    double jit=0.25+0.5*(s%2); double jit2=0.25+0.5*(s/2);
    ps.add({i+jit, j+jit2},{0,0},1); }
  // calibrate rho_tilde_0 so packed liquid -> raw density rho_l
  pp.rho_tilde_0 = calibrateRhoTilde0(pp, Vp);
  p2g_tp(g, ps, pp, Vp);
  // phi at a deep-liquid u-face (i=4,j=2) ~ 1, at deep-gas (i=4,j=5) ~ 0
  double phi_liq = phiFromRawDensity(g.mu[4+(g.nx+1)*2], pp);
  double phi_gas = phiFromRawDensity(g.mu[4+(g.nx+1)*5], pp);
  CHECK(phi_liq > 0.8);
  CHECK(phi_gas < 0.2);
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/transfer/transfer2d_tp.h`:
```cpp
#pragma once
struct UniformGrid2D;
struct Particles2DTP;
struct PhaseParams;
// raw-density of a fully packed liquid region with particle volume Vp, using the cubic kernel.
double calibrateRhoTilde0(const PhaseParams& pp, double Vp);
void p2g_tp(UniformGrid2D& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp);
void g2p_tp(const UniformGrid2D& g, Particles2DTP& ps, const UniformGrid2D& saved,
            double alpha_liquid, double alpha_gas);
double sampleU(const UniformGrid2D& g, double px, double py);   // reuse-compatible signatures
double sampleV(const UniformGrid2D& g, double px, double py);
```
`src/transfer/transfer2d_tp.cpp`:
```cpp
#include "transfer/transfer2d_tp.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"
#include <algorithm>
#include <cmath>

// Eq.6 cubic kernel on squared distance; r in grid units (cells).
static inline double kernel(double dx2_cells, double r){
  double q = dx2_cells/(r*r);
  double t = 1.0 - q;
  return (t>0.0) ? t*t*t : 0.0;
}
// splat with cubic kernel into a face field (continuous index gx,gy), support radius r (cells)
static void splatK(std::vector<double>& field, std::vector<double>& mass,
                   int sw,int W,int H, double gx,double gy, double mom,double m, double r){
  int rad = (int)std::ceil(r);
  int i0=(int)std::floor(gx), j0=(int)std::floor(gy);
  for(int dj=-rad; dj<=rad+1; ++dj) for(int di=-rad; di<=rad+1; ++di){
    int ii=i0+di, jj=j0+dj; if(ii<0||ii>=W||jj<0||jj>=H) continue;
    double ddx=(gx-ii), ddy=(gy-jj); double d2=ddx*ddx+ddy*ddy;
    double w=kernel(d2,r); if(w<=0.0) continue;
    int idx=ii+sw*jj; field[idx]+=w*mom; mass[idx]+=w*m;
  }
}
static const double KR = 1.5;  // kernel support radius in cells

double calibrateRhoTilde0(const PhaseParams& pp, double Vp){
  // measure raw density at the center face of a fully packed liquid block (4 particles/cell).
  UniformGrid2D g(8,8,1.0); std::vector<double>& f=g.ufield; std::vector<double>& m=g.mu;
  double mp = pp.rho_l*Vp;
  for(int j=0;j<8;++j) for(int i=0;i<8;++i) for(int s=0;s<4;++s){
    double x=i+0.25+0.5*(s%2), y=j+0.25+0.5*(s/2);
    splatK(f,m, g.nx+1,g.nx+1,g.ny, x, y-0.5, mp*0.0, mp, KR);
  }
  double raw = m[4+(g.nx+1)*4];          // center u-face raw density (= rho_tilde_0 * rho_l)
  return (raw>0)? raw/pp.rho_l : 1.0;
}
void p2g_tp(UniformGrid2D& g, const Particles2DTP& ps, const PhaseParams& pp, double Vp){
  std::fill(g.ufield.begin(),g.ufield.end(),0.0); std::fill(g.vfield.begin(),g.vfield.end(),0.0);
  std::fill(g.mu.begin(),g.mu.end(),0.0); std::fill(g.mv.begin(),g.mv.end(),0.0);
  for(size_t k=0;k<ps.size();++k){
    double rho = (ps.type[k]==0)? pp.rho_l : pp.rho_g; double mp = rho*Vp;
    double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    splatK(g.ufield,g.mu, g.nx+1,g.nx+1,g.ny, px, py-0.5, mp*ps.vel[k].x, mp, KR);
    splatK(g.vfield,g.mv, g.nx,  g.nx,g.ny+1, px-0.5, py, mp*ps.vel[k].y, mp, KR);
  }
  for(size_t i=0;i<g.ufield.size();++i) if(g.mu[i]>0.0) g.ufield[i]/=g.mu[i];
  for(size_t i=0;i<g.vfield.size();++i) if(g.mv[i]>0.0) g.vfield[i]/=g.mv[i];
}
static double triF(const std::vector<double>& f,int sw,int W,int H,double gx,double gy){
  int i0=(int)std::floor(gx),j0=(int)std::floor(gy); double fx=gx-i0,fy=gy-j0;
  auto get=[&](int ii,int jj){ ii=std::max(0,std::min(W-1,ii)); jj=std::max(0,std::min(H-1,jj)); return f[ii+sw*jj]; };
  return (1-fx)*(1-fy)*get(i0,j0)+fx*(1-fy)*get(i0+1,j0)+(1-fx)*fy*get(i0,j0+1)+fx*fy*get(i0+1,j0+1);
}
double sampleU(const UniformGrid2D& g,double px,double py){ return triF(g.ufield,g.nx+1,g.nx+1,g.ny,px,py-0.5); }
double sampleV(const UniformGrid2D& g,double px,double py){ return triF(g.vfield,g.nx,g.nx,g.ny+1,px-0.5,py); }
void g2p_tp(const UniformGrid2D& g, Particles2DTP& ps, const UniformGrid2D& saved, double aL, double aG){
  for(size_t k=0;k<ps.size();++k){
    double a = (ps.type[k]==0)? aL : aG;
    double px=(ps.pos[k].x-g.ox)/g.dx, py=(ps.pos[k].y-g.oy)/g.dx;
    double un=sampleU(g,px,py), vn=sampleV(g,px,py);
    double du=un-sampleU(saved,px,py), dv=vn-sampleV(saved,px,py);
    Vec2 pic{un,vn}; Vec2 flip{ps.vel[k].x+du, ps.vel[k].y+dv};
    ps.vel[k]=flip*a + pic*(1.0-a);
  }
}
```
> 주의: `sampleU/sampleV`는 Phase 0의 `transfer2d.cpp`에도 동일 이름이 있다. **링크 충돌을 피하기 위해** 2상 sample은 `transfer2d_tp.cpp` 내부 `static`로 두고 헤더에서 선언 제거 — 즉 위 헤더의 `sampleU/sampleV` 선언 두 줄을 삭제하고, cpp의 `triF`/`sampleU`/`sampleV`를 모두 `static`으로. advect는 Task 4에서 2상 전용으로 재구현.
- [ ] **Step 4: 빌드·테스트 PASS** (운동량 보존 + 위상 분리 phi_liq>0.8, phi_gas<0.2)
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: cubic-kernel two-phase P2G/G2P + rho_tilde_0 calibration"`

---

## Task 3: 가변계수 β Poisson + 투영

**Files:** Create `src/pressure/pressure2d_vc.h`, `src/pressure/pressure2d_vc.cpp`, `tests/test_pressure_vc.cpp`; Modify `CMakeLists.txt`.

면별 β=1/ρ(면 φ에서). 셀 c식: `(Δt/dx²)·Σ_face β_face·(p_c−p_n) = (div+c_div)_c`. applyA: diag=Σβ_face(비솔리드 면), off=Σβ_face·p_n(유체 이웃). 투영: `u −= Δt·β_face·(p_n−p_c)/dx`. 면 β는 호출자가 채운 `g.bu/g.bv`(신규 면 채널) 사용.

> UniformGrid2D에 면 β 채널 추가 필요. `uniform_grid2d.h`에 멤버 `std::vector<double> bu, bv;`를 추가하고 생성자에서 `bu((nx+1)*ny,1.0), bv(nx*(ny+1),1.0)` 초기화(기본 1 → 단상과 호환). (헤더 1줄 추가 + 생성자 init 2개. clear()에서는 건드리지 않음 — β는 매 스텝 재계산.)

- [ ] **Step 1: 실패 테스트** `tests/test_pressure_vc.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "pressure/pressure2d_vc.h"
#include <cmath>
TEST_CASE("VC projection removes divergence (uniform beta == constant case)") {
  UniformGrid2D g(8,8,1.0);
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) g.cell(i,j)=(i>=1&&i<7&&j>=1&&j<7)?Cell::FLUID:Cell::AIR;
  for(int j=0;j<g.ny;++j){g.cell(0,j)=Cell::SOLID;g.cell(7,j)=Cell::SOLID;}
  for(int i=0;i<g.nx;++i){g.cell(i,0)=Cell::SOLID;g.cell(i,7)=Cell::SOLID;}
  std::fill(g.bu.begin(),g.bu.end(),1.0); std::fill(g.bv.begin(),g.bv.end(),1.0);  // beta=1
  for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i) g.u(i,j)=(double)i;
  auto d0=divergenceVC(g);
  solvePressureVC(g,d0,1.0,500,1e-10);
  projectVC(g,1.0);
  auto d1=divergenceVC(g);
  double mx=0; for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) if(g.cell(i,j)==Cell::FLUID) mx=std::max(mx,std::abs(d1[i+g.nx*j]));
  CHECK(mx<1e-5);
}
TEST_CASE("hydrostatic two-phase column stays balanced") {
  // heavy bottom (beta small), light top (beta large); gravity in divergence source via c_div=0,
  // inject gravity into v then project -> resulting v should be ~0 (equilibrium), interface still.
  UniformGrid2D g(6,16,1.0);
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) g.cell(i,j)=(i>=1&&i<5&&j>=1&&j<15)?Cell::FLUID:Cell::AIR;
  for(int j=0;j<g.ny;++j){g.cell(0,j)=Cell::SOLID;g.cell(5,j)=Cell::SOLID;}
  for(int i=0;i<g.nx;++i){g.cell(i,0)=Cell::SOLID;g.cell(i,15)=Cell::SOLID;}
  // beta: bottom half rho=1 (beta=1), top half rho=0.01 (beta=100)
  for(int j=0;j<=g.ny;++j)for(int i=0;i<g.nx;++i){ double b=(j<8)?1.0:100.0; g.bv[i+g.nx*j]=b; }
  for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i){ double b=(j<8)?1.0:100.0; g.bu[i+(g.nx+1)*j]=b; }
  // apply gravity impulse to all interior v-faces, then project once
  double dt=0.1, gconst=-9.81;
  for(int j=1;j<g.ny;++j)for(int i=0;i<g.nx;++i) g.v(i,j)+=dt*gconst;
  auto d=divergenceVC(g); solvePressureVC(g,d,dt,1000,1e-10); projectVC(g,dt);
  // post-projection max |v| in interior should be small (hydrostatic balance), not growing
  double mv=0; for(int j=2;j<g.ny-1;++j)for(int i=1;i<g.nx-1;++i) mv=std::max(mv,std::abs(g.v(i,j)));
  CHECK(mv < 0.5);   // residual velocity bounded (not free-fall ~0.981)
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인** (also add `bu,bv` to grid header per note above; rebuild existing tests must still pass)
- [ ] **Step 3: 구현** `src/pressure/pressure2d_vc.h`:
```cpp
#pragma once
#include <vector>
struct UniformGrid2D;
std::vector<double> divergenceVC(const UniformGrid2D& g);
double solvePressureVC(UniformGrid2D& g, const std::vector<double>& div, double dt, int max_iter, double tol);
void projectVC(UniformGrid2D& g, double dt);
```
`src/pressure/pressure2d_vc.cpp`:
```cpp
#include "pressure/pressure2d_vc.h"
#include "grid/uniform_grid2d.h"
#include <cmath>
#include <algorithm>
std::vector<double> divergenceVC(const UniformGrid2D& g){
  std::vector<double> d(g.nx*g.ny,0.0);
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    double du=g.u(i+1,j)-g.u(i,j), dv=g.v(i,j+1)-g.v(i,j);
    d[i+g.nx*j]=(du+dv)/g.dx;
  }
  return d;
}
namespace {
inline bool isFluid(UniformGrid2D& g,int i,int j){ return g.inBounds(i,j)&&g.cell(i,j)==Cell::FLUID; }
inline bool isSolid(UniformGrid2D& g,int i,int j){ return !g.inBounds(i,j)||g.cell(i,j)==Cell::SOLID; }
// face betas: between (i-1,j)&(i,j) -> bu(i,j); between (i,j-1)&(i,j) -> bv(i,j)
inline double bU(UniformGrid2D& g,int i,int j){ return g.bu[i+(g.nx+1)*j]; }
inline double bV(UniformGrid2D& g,int i,int j){ return g.bv[i+g.nx*j]; }
void applyA(UniformGrid2D& g,double scale,const std::vector<double>& x,std::vector<double>& out){
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    int c=i+g.nx*j; out[c]=0.0; if(!isFluid(g,i,j)) continue;
    double diag=0,off=0;
    // +x face bU(i+1,j) to neighbor (i+1,j); -x face bU(i,j) to (i-1,j); etc.
    struct F{int ni,nj; double b;}; 
    F fs[4]={ {i+1,j,bU(g,i+1,j)}, {i-1,j,bU(g,i,j)}, {i,j+1,bV(g,i,j+1)}, {i,j-1,bV(g,i,j)} };
    for(auto& f: fs){ if(isSolid(g,f.ni,f.nj)) continue; diag+=f.b; if(isFluid(g,f.ni,f.nj)) off+=f.b*x[f.ni+g.nx*f.nj]; }
    out[c]=scale*(diag*x[c]-off);
  }
}
double diagOf(UniformGrid2D& g,double scale,int i,int j){
  double d=0; struct F{int ni,nj;double b;}; F fs[4]={ {i+1,j,bU(g,i+1,j)},{i-1,j,bU(g,i,j)},{i,j+1,bV(g,i,j+1)},{i,j-1,bV(g,i,j)} };
  for(auto& f:fs) if(!isSolid(g,f.ni,f.nj)) d+=f.b; return scale*d;
}
}
double solvePressureVC(UniformGrid2D& g,const std::vector<double>& div,double dt,int max_iter,double tol){
  int N=g.nx*g.ny; double scale=dt/(g.dx*g.dx);
  std::vector<double> x(N,0.0),r(N,0.0),z(N,0.0),pd(N,0.0),Ap(N,0.0);
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){int c=i+g.nx*j; r[c]=isFluid(g,i,j)?-div[c]:0.0;}
  auto precond=[&](const std::vector<double>& in,std::vector<double>& o){ for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){int c=i+g.nx*j; double d=isFluid(g,i,j)?diagOf(g,scale,i,j):0.0; o[c]=(d>0)?in[c]/d:0.0;} };
  auto dotp=[&](const std::vector<double>& a,const std::vector<double>& b){double s=0;for(int t=0;t<N;++t)s+=a[t]*b[t];return s;};
  double res0=0; for(int t=0;t<N;++t) res0=std::max(res0,std::abs(r[t])); if(res0<tol){g.pfield=x;return res0;}
  precond(r,z); pd=z; double rz=dotp(r,z),res=res0;
  for(int it=0;it<max_iter;++it){ applyA(g,scale,pd,Ap); double pAp=dotp(pd,Ap); if(std::abs(pAp)<1e-30) break;
    double al=rz/pAp; for(int t=0;t<N;++t){x[t]+=al*pd[t];r[t]-=al*Ap[t];}
    res=0; for(int t=0;t<N;++t) res=std::max(res,std::abs(r[t])); if(res<tol) break;
    precond(r,z); double rzn=dotp(r,z),be=rzn/rz; rz=rzn; for(int t=0;t<N;++t) pd[t]=z[t]+be*pd[t]; }
  g.pfield=x; return res;
}
void projectVC(UniformGrid2D& g,double dt){
  double s=dt/g.dx;
  for(int j=0;j<g.ny;++j)for(int i=1;i<g.nx;++i){ if(isSolid(g,i-1,j)||isSolid(g,i,j)){g.u(i,j)=0;continue;}
    bool a=isFluid(g,i-1,j),b=isFluid(g,i,j); if(a||b){ double pl=a?g.p(i-1,j):0.0,pr=b?g.p(i,j):0.0; g.u(i,j)-=s*bU(g,i,j)*(pr-pl); } }
  for(int j=1;j<g.ny;++j)for(int i=0;i<g.nx;++i){ if(isSolid(g,i,j-1)||isSolid(g,i,j)){g.v(i,j)=0;continue;}
    bool a=isFluid(g,i,j-1),b=isFluid(g,i,j); if(a||b){ double pb=a?g.p(i,j-1):0.0,pt=b?g.p(i,j):0.0; g.v(i,j)-=s*bV(g,i,j)*(pt-pb); } }
}
```
- [ ] **Step 4: 빌드·테스트 PASS** (β=1일 때 발산<1e-5; 정수압 잔류속도 유계). 기존 모든 테스트도 PASS(bu/bv 추가가 깨지 않음).
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: variable-coefficient (beta=1/rho) pressure Poisson + projection"`

---

## Task 4: 2상 Sim 드라이버 + dam-break 통합테스트

**Files:** Create `src/driver/sim2d_tp.h`, `src/driver/sim2d_tp.cpp`, `tests/test_sim_tp.cpp`; Modify `CMakeLists.txt`.

스텝: `markCells(양상=FLUID) → p2g_tp → 면 φ·β 계산 → saved → 중력(질량가중) → 벽 BC → divergenceVC → solvePressureVC → projectVC → g2p_tp(상별 α) → advect_tp`. 면 β: `bu[i,j]=betaFromPhi(phi(mu[i,j]))`, 같은 식 bv. (raw 밀도 = mu/mv는 p2g_tp가 채움.)

- [ ] **Step 1: 실패 테스트** `tests/test_sim_tp.cpp`:
```cpp
#include "doctest.h"
#include "driver/sim2d_tp.h"
#include <cmath>
TEST_CASE("two-phase dam break: stable, count conserved, heavy phase falls") {
  Sim2DTP sim(32,32,1.0);
  sim.initTwoPhaseDamBreak();   // liquid column + gas filling the rest
  size_t n0=sim.particles.size(); CHECK(n0>0);
  // mean y of LIQUID particles
  auto meanLiqY=[&](){ double s=0;int n=0; for(size_t k=0;k<sim.particles.size();++k) if(sim.particles.type[k]==0){s+=sim.particles.pos[k].y;++n;} return n?s/n:0.0; };
  double y0=meanLiqY();
  for(int s=0;s<50;++s) sim.step();
  CHECK(sim.particles.size()==n0);
  bool finite=true; for(size_t k=0;k<sim.particles.size();++k) if(!std::isfinite(sim.particles.pos[k].x)||!std::isfinite(sim.particles.pos[k].y)) finite=false;
  CHECK(finite);
  CHECK(meanLiqY() < y0 + 0.5);   // liquid did not levitate; fell or stayed (heavy phase sinks)
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/driver/sim2d_tp.h`:
```cpp
#pragma once
#include "grid/uniform_grid2d.h"
#include "particles/particles2d_tp.h"
#include "physics/phasefield.h"
struct Sim2DTP {
  UniformGrid2D grid;
  Particles2DTP particles;
  PhaseParams phase;
  double dt=0.02, gravity=-9.81, Vp=1.0;
  double alpha_liquid=0.95, alpha_gas=0.95;
  int cg_iters=400; double cg_tol=1e-7;
  Sim2DTP(int nx,int ny,double dx) : grid(nx,ny,dx) {}
  void initTwoPhaseDamBreak();
  void initRayleighTaylor();
  void step();
};
```
`src/driver/sim2d_tp.cpp`:
```cpp
#include "driver/sim2d_tp.h"
#include "transfer/transfer2d_tp.h"
#include "pressure/pressure2d_vc.h"
#include <cmath>
#include <algorithm>

static void seedCell(Particles2DTP& ps,int i,int j,double dx,unsigned char t){
  for(int s=0;s<4;++s){ double x=(i+0.25+0.5*(s%2))*dx, y=(j+0.25+0.5*(s/2))*dx; ps.add({x,y},{0,0},t); }
}
void Sim2DTP::initTwoPhaseDamBreak(){
  phase.rho_tilde_0 = calibrateRhoTilde0(phase, Vp);
  int wx=grid.nx*4/10, hy=grid.ny*7/10;
  for(int j=1;j<grid.ny-1;++j)for(int i=1;i<grid.nx-1;++i){
    bool liquid = (i<wx && j<hy);
    seedCell(particles,i,j,grid.dx, liquid?0:1);
  }
}
void Sim2DTP::initRayleighTaylor(){
  phase.rho_tilde_0 = calibrateRhoTilde0(phase, Vp);
  // heavy (liquid) on TOP, light (gas) on BOTTOM -> unstable. small interface perturbation.
  int mid=grid.ny/2;
  for(int j=1;j<grid.ny-1;++j)for(int i=1;i<grid.nx-1;++i){
    double pert = 1.0*std::cos(2*3.14159265*i/grid.nx);
    bool heavy = (double)j > (mid + pert);
    seedCell(particles,i,j,grid.dx, heavy?0:1);
  }
}
static void markCells(UniformGrid2D& g, const Particles2DTP& ps){
  for(auto& c:g.marker) c=Cell::AIR;
  for(int j=0;j<g.ny;++j){g.cell(0,j)=Cell::SOLID;g.cell(g.nx-1,j)=Cell::SOLID;}
  for(int i=0;i<g.nx;++i){g.cell(i,0)=Cell::SOLID;g.cell(i,g.ny-1)=Cell::SOLID;}
  for(size_t k=0;k<ps.size();++k){ int i=(int)((ps.pos[k].x-g.ox)/g.dx),j=(int)((ps.pos[k].y-g.oy)/g.dx);
    if(g.inBounds(i,j)&&g.cell(i,j)!=Cell::SOLID) g.cell(i,j)=Cell::FLUID; }
}
static void advect_tp(Particles2DTP& ps, UniformGrid2D& g, double dt){
  // RK2 using VC-projected face velocities; reuse simple sampling
  auto sU=[&](double px,double py){ int i0=(int)std::floor(px),j0=(int)std::floor(py-0.5);
    double fx=px-i0,fy=(py-0.5)-j0; auto gv=[&](int ii,int jj){ii=std::max(0,std::min(g.nx,ii));jj=std::max(0,std::min(g.ny-1,jj));return g.u(ii,jj);};
    return (1-fx)*(1-fy)*gv(i0,j0)+fx*(1-fy)*gv(i0+1,j0)+(1-fx)*fy*gv(i0,j0+1)+fx*fy*gv(i0+1,j0+1); };
  auto sV=[&](double px,double py){ int i0=(int)std::floor(px-0.5),j0=(int)std::floor(py);
    double fx=(px-0.5)-i0,fy=py-j0; auto gv=[&](int ii,int jj){ii=std::max(0,std::min(g.nx-1,ii));jj=std::max(0,std::min(g.ny,jj));return g.v(ii,jj);};
    return (1-fx)*(1-fy)*gv(i0,j0)+fx*(1-fy)*gv(i0+1,j0)+(1-fx)*fy*gv(i0,j0+1)+fx*fy*gv(i0+1,j0+1); };
  double lox=0.5*g.dx,hix=(g.nx-0.5)*g.dx,loy=0.5*g.dx,hiy=(g.ny-0.5)*g.dx;
  for(size_t k=0;k<ps.size();++k){ double px=ps.pos[k].x/g.dx,py=ps.pos[k].y/g.dx;
    double u1=sU(px,py),v1=sV(px,py); double mx=ps.pos[k].x+0.5*dt*u1,my=ps.pos[k].y+0.5*dt*v1;
    double u2=sU(mx/g.dx,my/g.dx),v2=sV(mx/g.dx,my/g.dx);
    ps.pos[k].x=std::max(lox,std::min(hix,ps.pos[k].x+dt*u2));
    ps.pos[k].y=std::max(loy,std::min(hiy,ps.pos[k].y+dt*v2)); }
}
void Sim2DTP::step(){
  markCells(grid, particles);
  p2g_tp(grid, particles, phase, Vp);
  // face phi -> beta
  for(size_t idx=0; idx<grid.mu.size(); ++idx){ double phi=phiFromRawDensity(grid.mu[idx],phase); grid.bu[idx]=betaFromPhi(phi,phase); }
  for(size_t idx=0; idx<grid.mv.size(); ++idx){ double phi=phiFromRawDensity(grid.mv[idx],phase); grid.bv[idx]=betaFromPhi(phi,phase); }
  UniformGrid2D saved = grid;
  // gravity on all mass-bearing v-faces (both phases feel gravity; buoyancy emerges from pressure)
  for(size_t idx=0; idx<grid.vfield.size(); ++idx) if(grid.mv[idx]>0.0) grid.vfield[idx]+=dt*gravity;
  for(int j=0;j<grid.ny;++j){grid.u(0,j)=0;grid.u(1,j)=0;grid.u(grid.nx-1,j)=0;grid.u(grid.nx,j)=0;}
  for(int i=0;i<grid.nx;++i){grid.v(i,0)=0;grid.v(i,1)=0;grid.v(i,grid.ny-1)=0;grid.v(i,grid.ny)=0;}
  auto div=divergenceVC(grid); solvePressureVC(grid,div,dt,cg_iters,cg_tol); projectVC(grid,dt);
  g2p_tp(grid, particles, saved, alpha_liquid, alpha_gas);
  advect_tp(particles, grid, dt);
}
```
- [ ] **Step 4: 빌드·테스트 PASS** (2상 dam-break: 안정·count 보존·유한·heavy 안뜸)
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: Sim2DTP two-phase phase-field FLIP driver"`

---

## Task 5: Rayleigh-Taylor 검증 + φ viz

**Files:** Create `src/driver/viz_phase.h`, `apps/run_rt2d.cpp`, `tests/test_rt.cpp`; Modify `CMakeLists.txt`.

φ viz: liquid 입자=파랑, gas=어둠. RT: 무거운 상이 위 → 불안정 → spike 하강. 정량 게이트: 40~80스텝 후 액체-기체 계면 진폭이 초기보다 증가(불안정 성장).

- [ ] **Step 1: 실패 테스트** `tests/test_rt.cpp`:
```cpp
#include "doctest.h"
#include "driver/sim2d_tp.h"
#include <cmath>
TEST_CASE("Rayleigh-Taylor instability grows (heavy-over-light)") {
  Sim2DTP sim(32,48,1.0);
  sim.initRayleighTaylor();
  // initial mean y of heavy(liquid) and light(gas)
  auto meanY=[&](unsigned char t){ double s=0;int n=0; for(size_t k=0;k<sim.particles.size();++k) if(sim.particles.type[k]==t){s+=sim.particles.pos[k].y;++n;} return n?s/n:0.0; };
  double hy0=meanY(0), gy0=meanY(1);
  CHECK(hy0 > gy0);                 // heavy starts on top
  for(int s=0;s<80;++s) sim.step();
  bool finite=true; for(size_t k=0;k<sim.particles.size();++k) if(!std::isfinite(sim.particles.pos[k].y)) finite=false;
  CHECK(finite);
  double hy1=meanY(0), gy1=meanY(1);
  CHECK(hy1 < hy0);                 // heavy phase sank (instability -> overturning)
  CHECK(gy1 > gy0);                 // light phase rose
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/driver/viz_phase.h`:
```cpp
#pragma once
#include <string>
#include <vector>
#include <fstream>
#include "driver/sim2d_tp.h"
inline void writePhasePPM(const Sim2DTP& sim, const std::string& path, int scale=8){
  int W=sim.grid.nx*scale,H=sim.grid.ny*scale; std::vector<unsigned char> img(W*H*3,12);
  for(size_t k=0;k<sim.particles.size();++k){
    int px=(int)(sim.particles.pos[k].x/sim.grid.dx*scale), py=(int)(sim.particles.pos[k].y/sim.grid.dx*scale); py=H-1-py;
    if(px<0||px>=W||py<0||py>=H) continue; int o=(px+W*py)*3;
    if(sim.particles.type[k]==0){ img[o]=50;img[o+1]=130;img[o+2]=235; } else { img[o]=40;img[o+1]=40;img[o+2]=46; }
  }
  std::ofstream f(path,std::ios::binary); f<<"P6\n"<<W<<" "<<H<<"\n255\n"; f.write((const char*)img.data(),img.size());
}
```
`apps/run_rt2d.cpp`:
```cpp
#include "driver/sim2d_tp.h"
#include "driver/viz_phase.h"
#include <cstdio>
int main(){ Sim2DTP sim(64,96,1.0); sim.initRayleighTaylor();
  for(int s=0;s<240;++s){ sim.step(); if(s%8==0){char n[64];std::snprintf(n,sizeof(n),"rt_%03d.ppm",s/8);writePhasePPM(sim,n);} }
  std::printf("done: %zu particles\n", sim.particles.size()); return 0; }
```
CMake: `add_executable(run_rt2d apps/run_rt2d.cpp)` + `target_link_libraries(run_rt2d pfflip2d)`.
- [ ] **Step 4: 빌드·테스트 PASS** (RT: heavy 하강·light 상승). 그 후 `run_rt2d` 실행 → rt_###.ppm 시퀀스 → controller가 φ viz 육안 확인(특징적 spike/mushroom).
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: Rayleigh-Taylor validation + phase-field viz"`

---

## Self-Review (작성자 점검)
- **Spec coverage (Phase 2):** Eq.7(T1), cubic 커널 Eq.6(T2), 가변계수 β=1/ρ Poisson Eq.8(T3), 상별 점성(T2 G2P/T4), 2상 드라이버·RT(T4·T5). ✅ escaped droplet·완전 c_div·1000:1·3D는 명시적 이월.
- **Placeholder scan:** 전 step 코드/명령. 없음. ✅
- **Type consistency:** `Particles2DTP`(`pos/vel/type`,`add(p,v,t)`), `PhaseParams`, 함수 `phiFromRawDensity/densityFromPhi/betaFromPhi/calibrateRhoTilde0/p2g_tp/g2p_tp/divergenceVC/solvePressureVC/projectVC`, grid 신규 면채널 `bu/bv`. 일관. `sampleU/V` 충돌은 T2에서 static화로 회피. ✅
- **검증 관문:** Fig.7 곡선(T1), 위상 분리 phi_liq>0.8/phi_gas<0.2(T2), β=1 발산<1e-5 + 정수압 유계(T3), 2상 dam-break(T4), RT 성장(T5).
- **리스크:** 가변계수 CG가 100:1에서 느릴 수 있음(cg_iters 여유). 미명시 상수(KR 커널반경·Vp·rho_tilde_0 calibration)는 정성 게이트로 검증, 정량 동치는 비목표.

## 다음
- **Phase 2b(선택):** escaped droplet/bubble 변환 + c_div 부피보존 + 고밀도비
- **Phase 3:** 2상 코어를 3D + MSBG로 (SPEC-1 마지막)
