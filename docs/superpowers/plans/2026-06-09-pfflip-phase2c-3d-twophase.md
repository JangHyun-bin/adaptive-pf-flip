# PF-FLIP Phase 2c — 3D 2상 (3D air-water) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`).

**Goal:** Phase 1의 3D 단상 인프라에 Phase 2의 2상 phase-field를 결합해 **3D 공기-물 phase-field FLIP** 솔버를 만든다. 3D Rayleigh-Taylor로 검증. (검증된 2D 2상 + 3D 단상을 포팅 — 2D에서 발견된 버그 수정을 코드에 선반영.)

**Architecture:** 3D MAC + 면 raw 밀도 → Eq.7 φ → β=1/ρ(면 bu/bv/bw). cubic 커널(Eq.6, **2-pass 정규화**). 가변계수 6-이웃 Poisson(BC-aware 발산 + 순수 Neumann 핀). `phasefield.h`는 차원무관이라 재사용. 단상 3D 모듈 보존, 2상 3D는 `*3d_tp`/`*3d_vc` 신규.

**Tech Stack:** 기존 C++17/CMake/doctest. branch `feat/phase2c-3d-twophase`(from main). 밀도비 기본 100:1.

---

## File Structure (신규)
| 파일 | 책임 |
|---|---|
| `src/particles/particles3d_tp.h` | 3D 타입별 입자 |
| `src/transfer/transfer3d_tp.h`/`.cpp` | cubic(정규화) 3D 타입별 P2G/G2P + 캘리브레이션 |
| `src/pressure/pressure3d_vc.h`/`.cpp` | 3D 가변계수 β Poisson + 투영 |
| `src/driver/sim3d_tp.h`/`.cpp` | 3D 2상 드라이버 + RT/dam-break |
| `src/driver/viz_phase3d.h` | mid-z φ 슬라이스 viz |
| `apps/run_rt3d.cpp` | 3D RT 러너 |
| `tests/test_*3d_tp.cpp` | 3D 2상 테스트 |

**3D MAC:** u size `(nx+1)*ny*nz` idx `i+(nx+1)*(j+ny*k)`; v `nx*(ny+1)*nz` idx `i+nx*(j+(ny+1)*k)`; w `nx*ny*(nz+1)` idx `i+nx*(j+ny*k)`; cell `i+nx*(j+ny*k)`. 면 β 채널 `bu/bv/bw`(기본 1). 면 raw 밀도 = `mu/mv/mw`.

---

## Task 1: 3D 타입별 2상 P2G/G2P (cubic 정규화) + 캘리브레이션

**Files:** Create `src/particles/particles3d_tp.h`, `src/transfer/transfer3d_tp.h`, `src/transfer/transfer3d_tp.cpp`, `tests/test_transfer3d_tp.cpp`; Modify `CMakeLists.txt` (cpp→library, test→unit_tests).

`phasefield.h`(`PhaseParams`,`phiFromRawDensity`,`betaFromPhi`)는 기존 것 재사용. 3D 입자 8/cell(2³). cubic 커널 Eq.6 + **per-particle 2-pass 정규화**(partition-of-unity — 2D에서 이게 없으면 운동량 안 맞음). `static` 샘플 헬퍼(링크 충돌 회피).

- [ ] **Step 1: 실패 테스트** `tests/test_transfer3d_tp.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d_tp.h"
#include "transfer/transfer3d_tp.h"
#include "physics/phasefield.h"
TEST_CASE("3D tp p2g momentum conserved (normalized cubic)") {
  UniformGrid3D g(6,6,6,1.0); PhaseParams pp; double Vp=1.0;
  Particles3DTP ps; ps.add({3.0,2.5,2.5},{4.0,0.0,0.0},0);  // liquid, m_p=rho_l*Vp=1
  p2g_tp(g, ps, pp, Vp);
  double mom=0; for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i) mom+=g.u(i,j,k)*g.mu[g.uidx(i,j,k)];
  CHECK(mom == doctest::Approx(4.0).epsilon(1e-9));
}
TEST_CASE("3D tp p2g separates phases") {
  UniformGrid3D g(8,8,8,1.0); PhaseParams pp; double Vp=1.0;
  Particles3DTP ps;
  auto seed=[&](int i,int j,int k,unsigned char t){ for(int s=0;s<8;++s){ double x=i+0.25+0.5*(s&1), y=j+0.25+0.5*((s>>1)&1), z=k+0.25+0.5*((s>>2)&1); ps.add({x,y,z},{0,0,0},t);} };
  for(int k=1;k<7;++k)for(int j=1;j<4;++j)for(int i=1;i<7;++i) seed(i,j,k,0);  // liquid bottom
  for(int k=1;k<7;++k)for(int j=4;j<7;++j)for(int i=1;i<7;++i) seed(i,j,k,1);  // gas top
  pp.rho_tilde_0 = calibrateRhoTilde0(pp, Vp);
  p2g_tp(g, ps, pp, Vp);
  double phi_liq = phiFromRawDensity(g.mu[g.uidx(4,2,3)], pp);
  double phi_gas = phiFromRawDensity(g.mu[g.uidx(4,5,3)], pp);
  CHECK(phi_liq > 0.8);
  CHECK(phi_gas < 0.2);
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/particles/particles3d_tp.h`:
```cpp
#pragma once
#include <vector>
#include "math/vec3.h"
struct Particles3DTP {
  std::vector<Vec3> pos, vel;
  std::vector<unsigned char> type;  // 0=liquid,1=gas
  size_t size() const { return pos.size(); }
  void add(const Vec3& p, const Vec3& v, unsigned char t){ pos.push_back(p); vel.push_back(v); type.push_back(t); }
};
```
`src/transfer/transfer3d_tp.h`:
```cpp
#pragma once
struct UniformGrid3D;
struct Particles3DTP;
struct PhaseParams;
double calibrateRhoTilde0(const PhaseParams& pp, double Vp);
void p2g_tp(UniformGrid3D& g, const Particles3DTP& ps, const PhaseParams& pp, double Vp);
void g2p_tp(const UniformGrid3D& g, Particles3DTP& ps, const UniformGrid3D& saved, double aL, double aG);
```
`src/transfer/transfer3d_tp.cpp` (모든 샘플 헬퍼 static; 2-pass 정규화 splat):
```cpp
#include "transfer/transfer3d_tp.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d_tp.h"
#include "physics/phasefield.h"
#include <algorithm>
#include <cmath>
#include <vector>

static inline double kern(double d2_cells, double r){ double q=d2_cells/(r*r), t=1.0-q; return (t>0.0)? t*t*t : 0.0; }
static const double KR=1.5;
// normalized splat into one axis face field (sw stride x; W,H,D dims; idx=i+sw*(j+H*k))
static void splatN(std::vector<double>& field, std::vector<double>& mass, int sw,int W,int H,int D,
                   double gx,double gy,double gz, double mom,double m, double r){
  int rad=(int)std::ceil(r); int i0=(int)std::floor(gx),j0=(int)std::floor(gy),k0=(int)std::floor(gz);
  // pass 1: weight sum
  double wsum=0;
  for(int dk=-rad;dk<=rad+1;++dk)for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj,kk=k0+dk; if(ii<0||ii>=W||jj<0||jj>=H||kk<0||kk>=D) continue;
    double dx=gx-ii,dy=gy-jj,dz=gz-kk; wsum+=kern(dx*dx+dy*dy+dz*dz,r);
  }
  if(wsum<=0.0) return;
  // pass 2: normalized splat
  for(int dk=-rad;dk<=rad+1;++dk)for(int dj=-rad;dj<=rad+1;++dj)for(int di=-rad;di<=rad+1;++di){
    int ii=i0+di,jj=j0+dj,kk=k0+dk; if(ii<0||ii>=W||jj<0||jj>=H||kk<0||kk>=D) continue;
    double dx=gx-ii,dy=gy-jj,dz=gz-kk; double w=kern(dx*dx+dy*dy+dz*dz,r)/wsum; if(w<=0.0) continue;
    int idx=ii+sw*(jj+H*kk); field[idx]+=w*mom; mass[idx]+=w*m;
  }
}
double calibrateRhoTilde0(const PhaseParams& pp, double Vp){
  UniformGrid3D g(8,8,8,1.0); double mp=pp.rho_l*Vp;
  for(int k=0;k<8;++k)for(int j=0;j<8;++j)for(int i=0;i<8;++i)for(int s=0;s<8;++s){
    double x=i+0.25+0.5*(s&1), y=j+0.25+0.5*((s>>1)&1), z=k+0.25+0.5*((s>>2)&1);
    splatN(g.ufield,g.mu, g.nx+1,g.nx+1,g.ny,g.nz, x, y-0.5, z-0.5, 0.0, mp, KR);
  }
  double raw=g.mu[g.uidx(4,4,4)]; return (raw>0)? raw/pp.rho_l : 1.0;
}
void p2g_tp(UniformGrid3D& g, const Particles3DTP& ps, const PhaseParams& pp, double Vp){
  std::fill(g.ufield.begin(),g.ufield.end(),0.0);std::fill(g.vfield.begin(),g.vfield.end(),0.0);std::fill(g.wfield.begin(),g.wfield.end(),0.0);
  std::fill(g.mu.begin(),g.mu.end(),0.0);std::fill(g.mv.begin(),g.mv.end(),0.0);std::fill(g.mw.begin(),g.mw.end(),0.0);
  for(size_t p=0;p<ps.size();++p){
    double rho=(ps.type[p]==0)?pp.rho_l:pp.rho_g; double mp=rho*Vp;
    double px=(ps.pos[p].x-g.ox)/g.dx,py=(ps.pos[p].y-g.oy)/g.dx,pz=(ps.pos[p].z-g.oz)/g.dx;
    splatN(g.ufield,g.mu, g.nx+1,g.nx+1,g.ny,g.nz, px, py-0.5, pz-0.5, mp*ps.vel[p].x, mp, KR);
    splatN(g.vfield,g.mv, g.nx,  g.nx,g.ny+1,g.nz, px-0.5, py, pz-0.5, mp*ps.vel[p].y, mp, KR);
    splatN(g.wfield,g.mw, g.nx,  g.nx,g.ny,g.nz+1, px-0.5, py-0.5, pz, mp*ps.vel[p].z, mp, KR);
  }
  for(size_t i=0;i<g.ufield.size();++i) if(g.mu[i]>0) g.ufield[i]/=g.mu[i];
  for(size_t i=0;i<g.vfield.size();++i) if(g.mv[i]>0) g.vfield[i]/=g.mv[i];
  for(size_t i=0;i<g.wfield.size();++i) if(g.mw[i]>0) g.wfield[i]/=g.mw[i];
}
static double tri(const std::vector<double>& f,int sw,int W,int H,int D,double gx,double gy,double gz){
  int i0=(int)std::floor(gx),j0=(int)std::floor(gy),k0=(int)std::floor(gz); double fx=gx-i0,fy=gy-j0,fz=gz-k0;
  auto get=[&](int ii,int jj,int kk){ ii=std::max(0,std::min(W-1,ii));jj=std::max(0,std::min(H-1,jj));kk=std::max(0,std::min(D-1,kk)); return f[ii+sw*(jj+H*kk)]; };
  double wx[2]={1-fx,fx},wy[2]={1-fy,fy},wz[2]={1-fz,fz}; double s=0;
  for(int dk=0;dk<2;++dk)for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di) s+=wx[di]*wy[dj]*wz[dk]*get(i0+di,j0+dj,k0+dk);
  return s;
}
static double sU(const UniformGrid3D& g,double px,double py,double pz){return tri(g.ufield,g.nx+1,g.nx+1,g.ny,g.nz,px,py-0.5,pz-0.5);}
static double sV(const UniformGrid3D& g,double px,double py,double pz){return tri(g.vfield,g.nx,g.nx,g.ny+1,g.nz,px-0.5,py,pz-0.5);}
static double sW(const UniformGrid3D& g,double px,double py,double pz){return tri(g.wfield,g.nx,g.nx,g.ny,g.nz+1,px-0.5,py-0.5,pz);}
void g2p_tp(const UniformGrid3D& g, Particles3DTP& ps, const UniformGrid3D& saved, double aL, double aG){
  for(size_t p=0;p<ps.size();++p){ double a=(ps.type[p]==0)?aL:aG;
    double px=(ps.pos[p].x-g.ox)/g.dx,py=(ps.pos[p].y-g.oy)/g.dx,pz=(ps.pos[p].z-g.oz)/g.dx;
    double un=sU(g,px,py,pz),vn=sV(g,px,py,pz),wn=sW(g,px,py,pz);
    double du=un-sU(saved,px,py,pz),dv=vn-sV(saved,px,py,pz),dw=wn-sW(saved,px,py,pz);
    Vec3 pic{un,vn,wn}; Vec3 flip{ps.vel[p].x+du,ps.vel[p].y+dv,ps.vel[p].z+dw};
    ps.vel[p]=flip*a+pic*(1.0-a);
  }
}
```
- [ ] **Step 4: 빌드·테스트 PASS** (운동량=4.0; 위상분리 phi_liq>0.8, phi_gas<0.2). 분리 실패 시 KR/캘리브레이션 디버그(테스트 약화 금지).
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: 3D normalized-cubic two-phase P2G/G2P + calibration"`

---

## Task 2: 3D 가변계수 β Poisson + 투영

**Files:** Create `src/pressure/pressure3d_vc.h`, `src/pressure/pressure3d_vc.cpp`, `tests/test_pressure3d_vc.cpp`; Modify `src/grid/uniform_grid3d.h`(bu/bv/bw 추가), `CMakeLists.txt`.

**STEP A — 면 β 채널:** `uniform_grid3d.h`에 `std::vector<double> bu,bv,bw;` 멤버 추가 + 생성자 init `bu((nx+1)*ny*nz,1.0), bv(nx*(ny+1)*nz,1.0), bw(nx*ny*(nz+1),1.0)`. clear() 미변경. 기존 23+ 3D 테스트 PASS 확인.

**STEP B:** 6-이웃 가변계수. **2D에서 검증된 두 수정 선반영:** ① 발산은 solid-인접 면을 0으로 취급(투영과 일관), ② **순수 Neumann**(어떤 유체셀도 AIR 이웃이 없음)이면 첫 유체셀 압력을 핀(identity row).

- [ ] **Step 1: 실패 테스트** `tests/test_pressure3d_vc.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid3d.h"
#include "pressure/pressure3d_vc.h"
#include <cmath>
TEST_CASE("3D VC projection removes divergence (beta=1)") {
  UniformGrid3D g(8,8,8,1.0);
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i)
    g.cell(i,j,k)=(i>=2&&i<6&&j>=2&&j<6&&k>=2&&k<6)?Cell3::FLUID:Cell3::AIR;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i)
    if(i==0||i==g.nx-1||j==0||j==g.ny-1||k==0||k==g.nz-1) g.cell(i,j,k)=Cell3::SOLID;
  std::fill(g.bu.begin(),g.bu.end(),1.0);std::fill(g.bv.begin(),g.bv.end(),1.0);std::fill(g.bw.begin(),g.bw.end(),1.0);
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i) g.u(i,j,k)=(double)i;
  auto d0=divergenceVC(g); solvePressureVC(g,d0,1.0,1000,1e-10); projectVC(g,1.0);
  auto d1=divergenceVC(g); double mx=0;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i)
    if(g.cell(i,j,k)==Cell3::FLUID) mx=std::max(mx,std::abs(d1[g.cidx(i,j,k)]));
  CHECK(mx<1e-5);
}
TEST_CASE("3D hydrostatic two-phase: residual |v| bounded") {
  UniformGrid3D g(6,16,6,1.0);
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i)
    g.cell(i,j,k)=(i>=1&&i<5&&j>=1&&j<15&&k>=1&&k<5)?Cell3::FLUID:Cell3::AIR;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i)
    if(i==0||i==5||j==0||j==15||k==0||k==5) g.cell(i,j,k)=Cell3::SOLID;
  for(int k=0;k<=g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) g.bw[g.widx(i,j,k)]=(j<8)?1.0:100.0;
  for(int k=0;k<g.nz;++k)for(int j=0;j<=g.ny;++j)for(int i=0;i<g.nx;++i) g.bv[g.vidx(i,j,k)]=(j<8)?1.0:100.0;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i) g.bu[g.uidx(i,j,k)]=(j<8)?1.0:100.0;
  double dt=0.1,gc=-9.81; for(int k=0;k<g.nz;++k)for(int j=1;j<g.ny;++j)for(int i=0;i<g.nx;++i) g.v(i,j,k)+=dt*gc;
  auto d=divergenceVC(g); solvePressureVC(g,d,dt,2000,1e-10); projectVC(g,dt);
  double mv=0; for(int k=1;k<g.nz-1;++k)for(int j=2;j<g.ny-1;++j)for(int i=1;i<g.nx-1;++i) mv=std::max(mv,std::abs(g.v(i,j,k)));
  CHECK(mv<0.6);
}
```
- [ ] **Step 2: STEP A 적용(grid bu/bv/bw) → 기존 테스트 PASS 확인 → CMake에 새 cpp/test 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/pressure/pressure3d_vc.h`:
```cpp
#pragma once
#include <vector>
struct UniformGrid3D;
std::vector<double> divergenceVC(const UniformGrid3D& g);
double solvePressureVC(UniformGrid3D& g, const std::vector<double>& div, double dt, int max_iter, double tol);
void projectVC(UniformGrid3D& g, double dt);
```
`src/pressure/pressure3d_vc.cpp`:
```cpp
#include "pressure/pressure3d_vc.h"
#include "grid/uniform_grid3d.h"
#include <cmath>
#include <algorithm>
namespace {
inline bool isFluid(const UniformGrid3D& g,int i,int j,int k){ return g.inBounds(i,j,k)&&g.cell(i,j,k)==Cell3::FLUID; }
inline bool isSolid(const UniformGrid3D& g,int i,int j,int k){ return !g.inBounds(i,j,k)||g.cell(i,j,k)==Cell3::SOLID; }
inline double bU(const UniformGrid3D& g,int i,int j,int k){ return g.bu[g.uidx(i,j,k)]; }
inline double bV(const UniformGrid3D& g,int i,int j,int k){ return g.bv[g.vidx(i,j,k)]; }
inline double bW(const UniformGrid3D& g,int i,int j,int k){ return g.bw[g.widx(i,j,k)]; }
// returns true if pure-Neumann (no fluid cell touches AIR)
bool pureNeumann(const UniformGrid3D& g){
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) if(isFluid(g,i,j,k)){
    const int di[6]={1,-1,0,0,0,0},dj[6]={0,0,1,-1,0,0},dk[6]={0,0,0,0,1,-1};
    for(int n=0;n<6;++n){ int ni=i+di[n],nj=j+dj[n],nk=k+dk[n];
      if(g.inBounds(ni,nj,nk)&&g.cell(ni,nj,nk)==Cell3::AIR) return false; } }
  return true;
}
int firstFluid(const UniformGrid3D& g){ for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) if(isFluid(g,i,j,k)) return g.cidx(i,j,k); return -1; }
struct Face{int ni,nj,nk; double b;};
void faces(const UniformGrid3D& g,int i,int j,int k,Face f[6]){
  f[0]={i+1,j,k,bU(g,i+1,j,k)}; f[1]={i-1,j,k,bU(g,i,j,k)};
  f[2]={i,j+1,k,bV(g,i,j+1,k)}; f[3]={i,j-1,k,bV(g,i,j,k)};
  f[4]={i,j,k+1,bW(g,i,j,k+1)}; f[5]={i,j,k-1,bW(g,i,j,k)};
}
}
std::vector<double> divergenceVC(const UniformGrid3D& g){
  std::vector<double> d(g.nx*g.ny*g.nz,0.0);
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    // BC-aware: solid-adjacent faces count as 0 velocity (consistent with projection)
    double up = isSolid(g,i,j,k)||isSolid(g,i+1,j,k)? 0.0 : g.u(i+1,j,k);
    double um = isSolid(g,i,j,k)||isSolid(g,i-1,j,k)? 0.0 : g.u(i,j,k);
    double vp = isSolid(g,i,j,k)||isSolid(g,i,j+1,k)? 0.0 : g.v(i,j+1,k);
    double vm = isSolid(g,i,j,k)||isSolid(g,i,j-1,k)? 0.0 : g.v(i,j,k);
    double wp = isSolid(g,i,j,k)||isSolid(g,i,j,k+1)? 0.0 : g.w(i,j,k+1);
    double wm = isSolid(g,i,j,k)||isSolid(g,i,j,k-1)? 0.0 : g.w(i,j,k);
    d[g.cidx(i,j,k)]=((up-um)+(vp-vm)+(wp-wm))/g.dx;
  }
  return d;
}
double solvePressureVC(UniformGrid3D& g,const std::vector<double>& div,double dt,int max_iter,double tol){
  int N=g.nx*g.ny*g.nz; double scale=dt/(g.dx*g.dx);
  bool pin = pureNeumann(g); int pc = pin? firstFluid(g) : -1;
  std::vector<double> x(N,0.0),r(N,0.0),z(N,0.0),pd(N,0.0),Ap(N,0.0);
  auto applyA=[&](const std::vector<double>& xx,std::vector<double>& out){
    for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){ int c=g.cidx(i,j,k); out[c]=0.0;
      if(!isFluid(g,i,j,k)) continue;
      if(c==pc){ out[c]=xx[c]; continue; }                  // identity row pins pressure
      Face f[6]; faces(g,i,j,k,f); double diag=0,off=0;
      for(int n=0;n<6;++n){ if(isSolid(g,f[n].ni,f[n].nj,f[n].nk)) continue; diag+=f[n].b;
        if(isFluid(g,f[n].ni,f[n].nj,f[n].nk) && g.cidx(f[n].ni,f[n].nj,f[n].nk)!=pc) off+=f[n].b*xx[g.cidx(f[n].ni,f[n].nj,f[n].nk)]; }
      out[c]=scale*(diag*xx[c]-off);
    } };
  auto diagOf=[&](int i,int j,int k){ Face f[6]; faces(g,i,j,k,f); double d=0; for(int n=0;n<6;++n) if(!isSolid(g,f[n].ni,f[n].nj,f[n].nk)) d+=f[n].b; return scale*d; };
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){ int c=g.cidx(i,j,k); r[c]= isFluid(g,i,j,k)? (c==pc?0.0:-div[c]) : 0.0; }
  auto precond=[&](const std::vector<double>& in,std::vector<double>& o){ for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){ int c=g.cidx(i,j,k);
    double dd = isFluid(g,i,j,k)? (c==pc?1.0:diagOf(i,j,k)) : 0.0; o[c]=(dd>0)?in[c]/dd:0.0; } };
  auto dotp=[&](const std::vector<double>& a,const std::vector<double>& b){ double s=0; for(int t=0;t<N;++t) s+=a[t]*b[t]; return s; };
  double res0=0; for(int t=0;t<N;++t) res0=std::max(res0,std::abs(r[t])); if(res0<tol){g.pfield=x;return res0;}
  precond(r,z); pd=z; double rz=dotp(r,z),res=res0;
  for(int it=0;it<max_iter;++it){ applyA(pd,Ap); double pAp=dotp(pd,Ap); if(std::abs(pAp)<1e-30) break;
    double al=rz/pAp; for(int t=0;t<N;++t){x[t]+=al*pd[t];r[t]-=al*Ap[t];}
    res=0; for(int t=0;t<N;++t) res=std::max(res,std::abs(r[t])); if(res<tol) break;
    precond(r,z); double rzn=dotp(r,z),be=rzn/rz; rz=rzn; for(int t=0;t<N;++t) pd[t]=z[t]+be*pd[t]; }
  g.pfield=x; return res;
}
void projectVC(UniformGrid3D& g,double dt){
  double s=dt/g.dx;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=1;i<g.nx;++i){ if(isSolid(g,i-1,j,k)||isSolid(g,i,j,k)){g.u(i,j,k)=0;continue;}
    bool a=isFluid(g,i-1,j,k),b=isFluid(g,i,j,k); if(a||b){ double pl=a?g.p(i-1,j,k):0.0,pr=b?g.p(i,j,k):0.0; g.u(i,j,k)-=s*bU(g,i,j,k)*(pr-pl);} }
  for(int k=0;k<g.nz;++k)for(int j=1;j<g.ny;++j)for(int i=0;i<g.nx;++i){ if(isSolid(g,i,j-1,k)||isSolid(g,i,j,k)){g.v(i,j,k)=0;continue;}
    bool a=isFluid(g,i,j-1,k),b=isFluid(g,i,j,k); if(a||b){ double pb=a?g.p(i,j-1,k):0.0,pt=b?g.p(i,j,k):0.0; g.v(i,j,k)-=s*bV(g,i,j,k)*(pt-pb);} }
  for(int k=1;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){ if(isSolid(g,i,j,k-1)||isSolid(g,i,j,k)){g.w(i,j,k)=0;continue;}
    bool a=isFluid(g,i,j,k-1),b=isFluid(g,i,j,k); if(a||b){ double pd=a?g.p(i,j,k-1):0.0,pu=b?g.p(i,j,k):0.0; g.w(i,j,k)-=s*bW(g,i,j,k)*(pu-pd);} }
}
```
- [ ] **Step 4: 빌드·테스트 PASS** (β=1 발산<1e-5; 정수압 |v|<0.6; 기존 테스트 보존)
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: 3D variable-coefficient pressure Poisson (BC-aware, Neumann-pinned)"`

---

## Task 3: 3D 2상 드라이버 + RT 검증 + 슬라이스 viz

**Files:** Create `src/driver/sim3d_tp.h`, `src/driver/sim3d_tp.cpp`, `src/driver/viz_phase3d.h`, `apps/run_rt3d.cpp`, `tests/test_sim3d_tp.cpp`; Modify `CMakeLists.txt`.

스텝: `markCells(양상=FLUID) → p2g_tp → 면 φ→β(bu/bv/bw) → saved → 중력(mv>0) → 벽 BC(u/v/w) → divergenceVC → solvePressureVC → projectVC → g2p_tp → advect_tp(3D RK2)`.

- [ ] **Step 1: 실패 테스트** `tests/test_sim3d_tp.cpp`:
```cpp
#include "doctest.h"
#include "driver/sim3d_tp.h"
#include <cmath>
TEST_CASE("3D Rayleigh-Taylor overturns (heavy over light)") {
  Sim3DTP sim(24,36,24,1.0);
  sim.initRayleighTaylor();
  auto meanY=[&](unsigned char t){ double s=0;int n=0; for(size_t k=0;k<sim.particles.size();++k) if(sim.particles.type[k]==t){s+=sim.particles.pos[k].y;++n;} return n?s/n:0.0; };
  double hy0=meanY(0), gy0=meanY(1); CHECK(hy0>gy0);
  for(int s=0;s<60;++s) sim.step();
  bool fin=true; for(size_t k=0;k<sim.particles.size();++k) if(!std::isfinite(sim.particles.pos[k].y)) fin=false;
  CHECK(fin); CHECK(meanY(0) < hy0); CHECK(meanY(1) > gy0);
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/driver/sim3d_tp.h`:
```cpp
#pragma once
#include "grid/uniform_grid3d.h"
#include "particles/particles3d_tp.h"
#include "physics/phasefield.h"
struct Sim3DTP {
  UniformGrid3D grid; Particles3DTP particles; PhaseParams phase;
  double dt=0.02, gravity=-9.81, Vp=1.0, alpha_liquid=0.95, alpha_gas=0.95;
  int cg_iters=600; double cg_tol=1e-7;
  Sim3DTP(int nx,int ny,int nz,double dx) : grid(nx,ny,nz,dx) {}
  void initTwoPhaseDamBreak();
  void initRayleighTaylor();
  void step();
};
```
`src/driver/sim3d_tp.cpp`:
```cpp
#include "driver/sim3d_tp.h"
#include "transfer/transfer3d_tp.h"
#include "pressure/pressure3d_vc.h"
#include <cmath>
#include <algorithm>
static void seed(Particles3DTP& ps,int i,int j,int k,double dx,unsigned char t){
  for(int s=0;s<8;++s){ double x=(i+0.25+0.5*(s&1))*dx,y=(j+0.25+0.5*((s>>1)&1))*dx,z=(k+0.25+0.5*((s>>2)&1))*dx; ps.add({x,y,z},{0,0,0},t);} }
void Sim3DTP::initTwoPhaseDamBreak(){
  phase.rho_tilde_0=calibrateRhoTilde0(phase,Vp);
  int wx=grid.nx*4/10,hy=grid.ny*7/10;
  for(int k=1;k<grid.nz-1;++k)for(int j=1;j<grid.ny-1;++j)for(int i=1;i<grid.nx-1;++i){ bool liq=(i<wx&&j<hy); seed(particles,i,j,k,grid.dx,liq?0:1); }
}
void Sim3DTP::initRayleighTaylor(){
  phase.rho_tilde_0=calibrateRhoTilde0(phase,Vp); int mid=grid.ny/2;
  for(int k=1;k<grid.nz-1;++k)for(int j=1;j<grid.ny-1;++j)for(int i=1;i<grid.nx-1;++i){
    double pert=1.0*std::cos(2*3.14159265*i/grid.nx)*std::cos(2*3.14159265*k/grid.nz);
    bool heavy=(double)j>(mid+pert); seed(particles,i,j,k,grid.dx,heavy?0:1); }
}
static void markCells(UniformGrid3D& g,const Particles3DTP& ps){
  for(auto& c:g.marker) c=Cell3::AIR;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) if(i==0||i==g.nx-1||j==0||j==g.ny-1||k==0||k==g.nz-1) g.cell(i,j,k)=Cell3::SOLID;
  for(size_t p=0;p<ps.size();++p){ int i=(int)((ps.pos[p].x-g.ox)/g.dx),j=(int)((ps.pos[p].y-g.oy)/g.dx),k=(int)((ps.pos[p].z-g.oz)/g.dx);
    if(g.inBounds(i,j,k)&&g.cell(i,j,k)!=Cell3::SOLID) g.cell(i,j,k)=Cell3::FLUID; }
}
static double sUg(UniformGrid3D& g,double px,double py,double pz){ int i0=(int)std::floor(px),j0=(int)std::floor(py-0.5),k0=(int)std::floor(pz-0.5);
  double fx=px-i0,fy=(py-0.5)-j0,fz=(pz-0.5)-k0; auto gv=[&](int i,int j,int k){i=std::max(0,std::min(g.nx,i));j=std::max(0,std::min(g.ny-1,j));k=std::max(0,std::min(g.nz-1,k));return g.u(i,j,k);};
  double wx[2]={1-fx,fx},wy[2]={1-fy,fy},wz[2]={1-fz,fz}; double s=0; for(int dk=0;dk<2;++dk)for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di) s+=wx[di]*wy[dj]*wz[dk]*gv(i0+di,j0+dj,k0+dk); return s; }
static double sVg(UniformGrid3D& g,double px,double py,double pz){ int i0=(int)std::floor(px-0.5),j0=(int)std::floor(py),k0=(int)std::floor(pz-0.5);
  double fx=(px-0.5)-i0,fy=py-j0,fz=(pz-0.5)-k0; auto gv=[&](int i,int j,int k){i=std::max(0,std::min(g.nx-1,i));j=std::max(0,std::min(g.ny,j));k=std::max(0,std::min(g.nz-1,k));return g.v(i,j,k);};
  double wx[2]={1-fx,fx},wy[2]={1-fy,fy},wz[2]={1-fz,fz}; double s=0; for(int dk=0;dk<2;++dk)for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di) s+=wx[di]*wy[dj]*wz[dk]*gv(i0+di,j0+dj,k0+dk); return s; }
static double sWg(UniformGrid3D& g,double px,double py,double pz){ int i0=(int)std::floor(px-0.5),j0=(int)std::floor(py-0.5),k0=(int)std::floor(pz);
  double fx=(px-0.5)-i0,fy=(py-0.5)-j0,fz=pz-k0; auto gv=[&](int i,int j,int k){i=std::max(0,std::min(g.nx-1,i));j=std::max(0,std::min(g.ny-1,j));k=std::max(0,std::min(g.nz,k));return g.w(i,j,k);};
  double wx[2]={1-fx,fx},wy[2]={1-fy,fy},wz[2]={1-fz,fz}; double s=0; for(int dk=0;dk<2;++dk)for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di) s+=wx[di]*wy[dj]*wz[dk]*gv(i0+di,j0+dj,k0+dk); return s; }
static void advect_tp(Particles3DTP& ps,UniformGrid3D& g,double dt){
  double lo=0.5*g.dx,hix=(g.nx-0.5)*g.dx,hiy=(g.ny-0.5)*g.dx,hiz=(g.nz-0.5)*g.dx;
  for(size_t p=0;p<ps.size();++p){ double px=ps.pos[p].x/g.dx,py=ps.pos[p].y/g.dx,pz=ps.pos[p].z/g.dx;
    double u1=sUg(g,px,py,pz),v1=sVg(g,px,py,pz),w1=sWg(g,px,py,pz);
    double mx=ps.pos[p].x+0.5*dt*u1,my=ps.pos[p].y+0.5*dt*v1,mz=ps.pos[p].z+0.5*dt*w1;
    double u2=sUg(g,mx/g.dx,my/g.dx,mz/g.dx),v2=sVg(g,mx/g.dx,my/g.dx,mz/g.dx),w2=sWg(g,mx/g.dx,my/g.dx,mz/g.dx);
    ps.pos[p].x=std::max(lo,std::min(hix,ps.pos[p].x+dt*u2));
    ps.pos[p].y=std::max(lo,std::min(hiy,ps.pos[p].y+dt*v2));
    ps.pos[p].z=std::max(lo,std::min(hiz,ps.pos[p].z+dt*w2)); }
}
void Sim3DTP::step(){
  markCells(grid,particles); p2g_tp(grid,particles,phase,Vp);
  for(size_t idx=0;idx<grid.mu.size();++idx) grid.bu[idx]=betaFromPhi(phiFromRawDensity(grid.mu[idx],phase),phase);
  for(size_t idx=0;idx<grid.mv.size();++idx) grid.bv[idx]=betaFromPhi(phiFromRawDensity(grid.mv[idx],phase),phase);
  for(size_t idx=0;idx<grid.mw.size();++idx) grid.bw[idx]=betaFromPhi(phiFromRawDensity(grid.mw[idx],phase),phase);
  UniformGrid3D saved=grid;
  for(size_t idx=0;idx<grid.vfield.size();++idx) if(grid.mv[idx]>0.0) grid.vfield[idx]+=dt*gravity;
  for(int k=0;k<grid.nz;++k)for(int j=0;j<grid.ny;++j){grid.u(0,j,k)=0;grid.u(1,j,k)=0;grid.u(grid.nx-1,j,k)=0;grid.u(grid.nx,j,k)=0;}
  for(int k=0;k<grid.nz;++k)for(int i=0;i<grid.nx;++i){grid.v(i,0,k)=0;grid.v(i,1,k)=0;grid.v(i,grid.ny-1,k)=0;grid.v(i,grid.ny,k)=0;}
  for(int j=0;j<grid.ny;++j)for(int i=0;i<grid.nx;++i){grid.w(i,j,0)=0;grid.w(i,j,1)=0;grid.w(i,j,grid.nz-1)=0;grid.w(i,j,grid.nz)=0;}
  auto div=divergenceVC(grid); solvePressureVC(grid,div,dt,cg_iters,cg_tol); projectVC(grid,dt);
  g2p_tp(grid,particles,saved,alpha_liquid,alpha_gas); advect_tp(particles,grid,dt);
}
```
`src/driver/viz_phase3d.h` (mid-z 슬라이스):
```cpp
#pragma once
#include <string>
#include <vector>
#include <fstream>
#include <cmath>
#include "driver/sim3d_tp.h"
inline void writePhaseSlice(const Sim3DTP& sim,const std::string& path,int scale=8,double zhalf=0.12){
  int W=sim.grid.nx*scale,H=sim.grid.ny*scale; std::vector<unsigned char> img(W*H*3,12);
  double zc=sim.grid.nz*0.5*sim.grid.dx, band=zhalf*sim.grid.nz*sim.grid.dx;
  for(size_t k=0;k<sim.particles.size();++k){ if(std::abs(sim.particles.pos[k].z-zc)>band) continue;
    int px=(int)(sim.particles.pos[k].x/sim.grid.dx*scale),py=(int)(sim.particles.pos[k].y/sim.grid.dx*scale); py=H-1-py;
    if(px<0||px>=W||py<0||py>=H) continue; int o=(px+W*py)*3;
    if(sim.particles.type[k]==0){img[o]=50;img[o+1]=130;img[o+2]=235;} else {img[o]=40;img[o+1]=40;img[o+2]=46;} }
  std::ofstream f(path,std::ios::binary); f<<"P6\n"<<W<<" "<<H<<"\n255\n"; f.write((const char*)img.data(),img.size());
}
```
`apps/run_rt3d.cpp`:
```cpp
#include "driver/sim3d_tp.h"
#include "driver/viz_phase3d.h"
#include <cstdio>
int main(){ Sim3DTP sim(48,64,48,1.0); sim.initRayleighTaylor();
  for(int s=0;s<200;++s){ sim.step(); if(s%8==0){char n[64];std::snprintf(n,sizeof(n),"rt3_%03d.ppm",s/8);writePhaseSlice(sim,n);} }
  std::printf("done: %zu particles\n", sim.particles.size()); return 0; }
```
CMake: `add_executable(run_rt3d apps/run_rt3d.cpp)` + `target_link_libraries(run_rt3d pfflip2d)`.
- [ ] **Step 4: 빌드·테스트 PASS** (3D RT 뒤집힘). 이후 `run_rt3d`를 `frames_rt3/`에서 실행 → mid-z 슬라이스 → controller 육안.
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: Sim3DTP 3D two-phase driver + 3D Rayleigh-Taylor + slice viz"`

---

## Self-Review
- **Coverage:** 3D 타입별 P2G(T1), 3D 가변계수 Poisson(T2), 3D 2상 드라이버+RT(T3). phasefield.h 재사용. ✅
- **선반영 버그수정:** 2-pass 정규화 splat(운동량), BC-aware divergenceVC, 순수 Neumann 핀. ✅
- **Type consistency:** `Particles3DTP`, `bu/bv/bw`+`uidx/vidx/widx`, `p2g_tp/g2p_tp/calibrateRhoTilde0/divergenceVC/solvePressureVC/projectVC` 3D 시그니처 일관. static 샘플로 단상 transfer3d와 충돌 회피. ✅
- **게이트:** 운동량/위상분리(T1), β=1 발산<1e-5 + 정수압(T2), 3D RT 뒤집힘(T3).

## 다음: Phase 3 (MSBG 통합) — SPEC-1 마지막.
