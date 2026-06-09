# PF-FLIP Phase 1 — 3D 확장 + 점성 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Phase 0의 2D 단상 FLIP을 **3D**로 확장하고, FLIP/PIC 혼합으로 제어되는 **물리 점성(Eq.13)**과 자유표면 근처 **속도 외삽**을 추가한다. 3D dam-break로 검증. (SPEC-1 Phase 1 = phase-field 2상(Phase 2)의 토대)

**Architecture:** 3D MAC 격자(u/v/w 면속도, p 셀압력). 구조는 검증된 2D 모듈과 평행 — 차원만 +1(z/w 추가, bilinear→trilinear, 5점→7점 라플라시안). 점성은 별도 확산 솔버 없이 α↔ν 매핑(Eq.13)으로. Phase 0 모듈은 그대로 두고 `*3d` 새 모듈을 추가(2D는 회귀 테스트로 보존).

**Tech Stack:** 기존 C++17/CMake/doctest 프로젝트에 3D 모듈 추가. branch `feat/phase1-3d-viscosity` (현재 HEAD = Phase 0 리뷰완료 `aea9da0`).

---

## File Structure

| 파일 | 책임 |
|---|---|
| `src/math/vec3.h` | 3D 벡터 (header-only) |
| `src/grid/uniform_grid3d.h` | 3D MAC 격자 (header-only) |
| `src/transfer/transfer3d.h`/`.cpp` | 3D P2G/G2P + trilinear 샘플 |
| `src/pressure/pressure3d.h`/`.cpp` | 3D 발산·7점 Poisson CG·투영 |
| `src/advect/advect3d.h`/`.cpp` | 속도 외삽 + 3D RK2 이류 |
| `src/physics/viscosity.h` | α↔ν 매핑 (Eq.13) |
| `src/particles/particles3d.h` | 3D 입자 (위치·속도·타입 hook) |
| `src/driver/sim3d.h`/`.cpp` | 3D 스텝 루프, 3D dam-break |
| `src/driver/viz_slice.h` | XY-슬라이스 PPM (육안용) |
| `apps/run_dambreak3d.cpp` | 3D 러너 |
| `tests/test_*3d.cpp` | 3D 회귀 테스트 |

**3D MAC 규약:** `nx,ny,nz,dx,ox,oy,oz`. cell idx `i+nx*(j+ny*k)`. u(x-면) size `(nx+1)*ny*nz`, idx `i+(nx+1)*(j+ny*k)`. v(y-면) size `nx*(ny+1)*nz`, idx `i+nx*(j+(ny+1)*k)`. w(z-면) size `nx*ny*(nz+1)`, idx `i+nx*(j+ny*k)`. u-면(i,j,k) 중심 연속인덱스 `(px, py-0.5, pz-0.5)`; v `(px-0.5, py, pz-0.5)`; w `(px-0.5, py-0.5, pz)` where `px=(x-ox)/dx` etc.

**라이브러리 등록:** 새 `.cpp`(transfer3d, pressure3d, advect3d, sim3d)를 `CMakeLists.txt`의 `pfflip2d` 라이브러리(이름 유지) 소스에 추가하고, 각 `tests/test_*3d.cpp`를 `unit_tests`에 추가.

---

## Task 1: Vec3 + Particles3D + UniformGrid3D

**Files:** Create `src/math/vec3.h`, `src/particles/particles3d.h`, `src/grid/uniform_grid3d.h`, `tests/test_grid3d.cpp`; Modify `CMakeLists.txt`.

- [ ] **Step 1: 실패 테스트** `tests/test_grid3d.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid3d.h"
TEST_CASE("grid3d sizes and access") {
  UniformGrid3D g(4,3,2,0.5);
  CHECK(g.u_size() == (4+1)*3*2);
  CHECK(g.v_size() == 4*(3+1)*2);
  CHECK(g.w_size() == 4*3*(2+1));
  CHECK(g.cell_size() == 4*3*2);
  g.u(2,1,1) = 7.0; CHECK(g.u(2,1,1) == doctest::Approx(7.0));
  g.w(3,2,2) = -1.5; CHECK(g.w(3,2,2) == doctest::Approx(-1.5));
  g.clear(); CHECK(g.u(2,1,1) == doctest::Approx(0.0));
}
```
- [ ] **Step 2: CMake에 `tests/test_grid3d.cpp` 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현**

`src/math/vec3.h`:
```cpp
#pragma once
#include <cmath>
struct Vec3 {
  double x=0.0, y=0.0, z=0.0;
  Vec3 operator+(const Vec3& o) const { return {x+o.x,y+o.y,z+o.z}; }
  Vec3 operator-(const Vec3& o) const { return {x-o.x,y-o.y,z-o.z}; }
  Vec3 operator*(double s) const { return {x*s,y*s,z*s}; }
  Vec3& operator+=(const Vec3& o){ x+=o.x;y+=o.y;z+=o.z; return *this; }
  double length() const { return std::sqrt(x*x+y*y+z*z); }
};
inline Vec3 operator*(double s, const Vec3& v){ return {v.x*s,v.y*s,v.z*s}; }
inline double dot(const Vec3& a, const Vec3& b){ return a.x*b.x+a.y*b.y+a.z*b.z; }
```
`src/particles/particles3d.h`:
```cpp
#pragma once
#include <vector>
#include "math/vec3.h"
struct Particles3D {
  std::vector<Vec3> pos, vel;
  std::vector<unsigned char> type;   // 0=liquid (Phase2에서 사용); Phase1은 전부 0
  size_t size() const { return pos.size(); }
  void add(const Vec3& p, const Vec3& v, unsigned char t=0){ pos.push_back(p); vel.push_back(v); type.push_back(t); }
};
```
`src/grid/uniform_grid3d.h`:
```cpp
#pragma once
#include <vector>
#include <cstddef>
#include <algorithm>
enum class Cell3 : unsigned char { AIR=0, FLUID=1, SOLID=2 };
struct UniformGrid3D {
  int nx, ny, nz;
  double dx, ox=0.0, oy=0.0, oz=0.0;
  std::vector<double> ufield, vfield, wfield;   // face velocities
  std::vector<double> mu, mv, mw;               // face masses
  std::vector<double> pfield;                   // cell pressure
  std::vector<Cell3> marker;
  UniformGrid3D(int nx_,int ny_,int nz_,double dx_)
    : nx(nx_),ny(ny_),nz(nz_),dx(dx_),
      ufield((nx_+1)*ny_*nz_,0.0), vfield(nx_*(ny_+1)*nz_,0.0), wfield(nx_*ny_*(nz_+1),0.0),
      mu((nx_+1)*ny_*nz_,0.0), mv(nx_*(ny_+1)*nz_,0.0), mw(nx_*ny_*(nz_+1),0.0),
      pfield(nx_*ny_*nz_,0.0), marker(nx_*ny_*nz_,Cell3::AIR) {}
  size_t u_size() const { return ufield.size(); }
  size_t v_size() const { return vfield.size(); }
  size_t w_size() const { return wfield.size(); }
  size_t cell_size() const { return pfield.size(); }
  int uidx(int i,int j,int k) const { return i + (nx+1)*(j + ny*k); }
  int vidx(int i,int j,int k) const { return i + nx*(j + (ny+1)*k); }
  int widx(int i,int j,int k) const { return i + nx*(j + ny*k); }       // w: nz+1 in k but stride nx*ny
  int cidx(int i,int j,int k) const { return i + nx*(j + ny*k); }
  double& u(int i,int j,int k){ return ufield[uidx(i,j,k)]; }
  double& v(int i,int j,int k){ return vfield[vidx(i,j,k)]; }
  double& w(int i,int j,int k){ return wfield[widx(i,j,k)]; }
  double& p(int i,int j,int k){ return pfield[cidx(i,j,k)]; }
  Cell3& cell(int i,int j,int k){ return marker[cidx(i,j,k)]; }
  const double& u(int i,int j,int k) const { return ufield[uidx(i,j,k)]; }
  const double& v(int i,int j,int k) const { return vfield[vidx(i,j,k)]; }
  const double& w(int i,int j,int k) const { return wfield[widx(i,j,k)]; }
  const double& p(int i,int j,int k) const { return pfield[cidx(i,j,k)]; }
  const Cell3& cell(int i,int j,int k) const { return marker[cidx(i,j,k)]; }
  bool inBounds(int i,int j,int k) const { return i>=0&&i<nx&&j>=0&&j<ny&&k>=0&&k<nz; }
  void clear(){
    std::fill(ufield.begin(),ufield.end(),0.0); std::fill(vfield.begin(),vfield.end(),0.0);
    std::fill(wfield.begin(),wfield.end(),0.0); std::fill(mu.begin(),mu.end(),0.0);
    std::fill(mv.begin(),mv.end(),0.0); std::fill(mw.begin(),mw.end(),0.0);
    std::fill(pfield.begin(),pfield.end(),0.0);
  }
};
```
> w-면 idx는 stride `nx*ny`, k범위 [0,nz] (size nx*ny*(nz+1)). 확인: `widx(i,j,nz)=i+nx*(j+ny*nz)` 최대 = nx*ny*(nz+1)-1 ✓.
- [ ] **Step 4: 빌드·테스트 PASS** `cmake -S . -B build; cmake --build build --config Debug; ctest --test-dir build -C Debug --output-on-failure`
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: Vec3, Particles3D, UniformGrid3D MAC"`

---

## Task 2: 3D P2G/G2P + trilinear 샘플

**Files:** Create `src/transfer/transfer3d.h`, `src/transfer/transfer3d.cpp`, `tests/test_transfer3d.cpp`; Modify `CMakeLists.txt` (add cpp to library + test to unit_tests).

- [ ] **Step 1: 실패 테스트** `tests/test_transfer3d.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d.h"
#include "transfer/transfer3d.h"
TEST_CASE("p2g3d single particle at u-node gives vx") {
  UniformGrid3D g(4,4,4,1.0);
  Particles3D ps; ps.add({2.0,1.5,1.5},{3.0,-7.0,2.0});  // u-face(2,1,1) center=(2.0,1.5,1.5)
  p2g(g, ps);
  CHECK(g.u(2,1,1) == doctest::Approx(3.0));
  CHECK(g.mu[g.uidx(2,1,1)] == doctest::Approx(1.0));
}
TEST_CASE("p2g3d conserves x-momentum across split") {
  UniformGrid3D g(4,4,4,1.0);
  Particles3D ps; ps.add({2.5,1.5,1.5},{4.0,0.0,0.0});
  p2g(g, ps);
  double mom = g.u(2,1,1)*g.mu[g.uidx(2,1,1)] + g.u(3,1,1)*g.mu[g.uidx(3,1,1)];
  CHECK(mom == doctest::Approx(4.0));
}
TEST_CASE("g2p3d PIC vs FLIP") {
  UniformGrid3D g(4,4,4,1.0), saved(4,4,4,1.0);
  std::fill(g.ufield.begin(),g.ufield.end(),5.0);
  std::fill(saved.ufield.begin(),saved.ufield.end(),2.0);
  Particles3D ps; ps.add({2.0,2.0,2.0},{10.0,0.0,0.0});
  g2p(g, ps, saved, 1.0);  // FLIP: 10 + (5-2)
  CHECK(ps.vel[0].x == doctest::Approx(13.0));
}
```
- [ ] **Step 2: CMake 추가(라이브러리에 `transfer3d.cpp`, unit_tests에 test) → 빌드 FAIL 확인**
- [ ] **Step 3: 구현**

`src/transfer/transfer3d.h`:
```cpp
#pragma once
struct UniformGrid3D;
struct Particles3D;
void p2g(UniformGrid3D& g, const Particles3D& ps);
void g2p(const UniformGrid3D& g, Particles3D& ps, const UniformGrid3D& saved, double alpha);
double sampleU(const UniformGrid3D& g, double px,double py,double pz);
double sampleV(const UniformGrid3D& g, double px,double py,double pz);
double sampleW(const UniformGrid3D& g, double px,double py,double pz);
```
`src/transfer/transfer3d.cpp`:
```cpp
#include "transfer/transfer3d.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d.h"
#include <algorithm>
#include <cmath>

// trilinear splat into an axis-faced field (w=dimX size, h=dimY, d=dimZ; idx = i + sw*(j + h*k))
static void splat3(std::vector<double>& field, std::vector<double>& mass,
                   int sw, int W,int H,int D, double gx,double gy,double gz, double mom,double m){
  int i0=(int)std::floor(gx), j0=(int)std::floor(gy), k0=(int)std::floor(gz);
  double fx=gx-i0, fy=gy-j0, fz=gz-k0;
  double wx[2]={1-fx,fx}, wy[2]={1-fy,fy}, wz[2]={1-fz,fz};
  for(int dk=0;dk<2;++dk)for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di){
    int ii=i0+di, jj=j0+dj, kk=k0+dk;
    if(ii<0||ii>=W||jj<0||jj>=H||kk<0||kk>=D) continue;
    double wgt=wx[di]*wy[dj]*wz[dk];
    int idx=ii + sw*(jj + H*kk);
    field[idx]+=wgt*mom; mass[idx]+=wgt*m;
  }
}
void p2g(UniformGrid3D& g, const Particles3D& ps){
  std::fill(g.ufield.begin(),g.ufield.end(),0.0); std::fill(g.vfield.begin(),g.vfield.end(),0.0);
  std::fill(g.wfield.begin(),g.wfield.end(),0.0);
  std::fill(g.mu.begin(),g.mu.end(),0.0); std::fill(g.mv.begin(),g.mv.end(),0.0); std::fill(g.mw.begin(),g.mw.end(),0.0);
  const double m_p=1.0;
  for(size_t kpt=0;kpt<ps.size();++kpt){
    double px=(ps.pos[kpt].x-g.ox)/g.dx, py=(ps.pos[kpt].y-g.oy)/g.dx, pz=(ps.pos[kpt].z-g.oz)/g.dx;
    splat3(g.ufield,g.mu, g.nx+1, g.nx+1,g.ny,g.nz, px, py-0.5, pz-0.5, m_p*ps.vel[kpt].x, m_p);
    splat3(g.vfield,g.mv, g.nx,   g.nx,g.ny+1,g.nz, px-0.5, py, pz-0.5, m_p*ps.vel[kpt].y, m_p);
    splat3(g.wfield,g.mw, g.nx,   g.nx,g.ny,g.nz+1, px-0.5, py-0.5, pz, m_p*ps.vel[kpt].z, m_p);
  }
  for(size_t i=0;i<g.ufield.size();++i) if(g.mu[i]>0.0) g.ufield[i]/=g.mu[i];
  for(size_t i=0;i<g.vfield.size();++i) if(g.mv[i]>0.0) g.vfield[i]/=g.mv[i];
  for(size_t i=0;i<g.wfield.size();++i) if(g.mw[i]>0.0) g.wfield[i]/=g.mw[i];
}
static double tri(const std::vector<double>& f,int sw,int W,int H,int D,double gx,double gy,double gz){
  int i0=(int)std::floor(gx), j0=(int)std::floor(gy), k0=(int)std::floor(gz);
  double fx=gx-i0, fy=gy-j0, fz=gz-k0;
  auto get=[&](int ii,int jj,int kk)->double{
    ii=std::max(0,std::min(W-1,ii)); jj=std::max(0,std::min(H-1,jj)); kk=std::max(0,std::min(D-1,kk));
    return f[ii+sw*(jj+H*kk)]; };
  double wx[2]={1-fx,fx},wy[2]={1-fy,fy},wz[2]={1-fz,fz}; double s=0;
  for(int dk=0;dk<2;++dk)for(int dj=0;dj<2;++dj)for(int di=0;di<2;++di)
    s+=wx[di]*wy[dj]*wz[dk]*get(i0+di,j0+dj,k0+dk);
  return s;
}
double sampleU(const UniformGrid3D& g,double px,double py,double pz){ return tri(g.ufield,g.nx+1,g.nx+1,g.ny,g.nz,px,py-0.5,pz-0.5); }
double sampleV(const UniformGrid3D& g,double px,double py,double pz){ return tri(g.vfield,g.nx,g.nx,g.ny+1,g.nz,px-0.5,py,pz-0.5); }
double sampleW(const UniformGrid3D& g,double px,double py,double pz){ return tri(g.wfield,g.nx,g.nx,g.ny,g.nz+1,px-0.5,py-0.5,pz); }
void g2p(const UniformGrid3D& g, Particles3D& ps, const UniformGrid3D& saved, double alpha){
  for(size_t kpt=0;kpt<ps.size();++kpt){
    double px=(ps.pos[kpt].x-g.ox)/g.dx, py=(ps.pos[kpt].y-g.oy)/g.dx, pz=(ps.pos[kpt].z-g.oz)/g.dx;
    double un=sampleU(g,px,py,pz), vn=sampleV(g,px,py,pz), wn=sampleW(g,px,py,pz);
    double du=un-sampleU(saved,px,py,pz), dv=vn-sampleV(saved,px,py,pz), dw=wn-sampleW(saved,px,py,pz);
    Vec3 pic{un,vn,wn}; Vec3 flip{ps.vel[kpt].x+du, ps.vel[kpt].y+dv, ps.vel[kpt].z+dw};
    ps.vel[kpt] = flip*alpha + pic*(1.0-alpha);
  }
}
```
- [ ] **Step 4: 빌드·테스트 PASS**
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: 3D P2G/G2P + trilinear sampling"`

---

## Task 3: 3D 발산 + 7점 Poisson CG + 투영

**Files:** Create `src/pressure/pressure3d.h`, `src/pressure/pressure3d.cpp`, `tests/test_pressure3d.cpp`; Modify `CMakeLists.txt`.

- [ ] **Step 1: 실패 테스트** `tests/test_pressure3d.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid3d.h"
#include "pressure/pressure3d.h"
#include <cmath>
TEST_CASE("projection removes 3D divergence in fluid") {
  UniformGrid3D g(8,8,8,1.0);
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i)
    g.cell(i,j,k) = (i>=2&&i<6&&j>=2&&j<6&&k>=2&&k<6)?Cell3::FLUID:Cell3::AIR;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i)
    if(i==0||i==g.nx-1||j==0||j==g.ny-1||k==0||k==g.nz-1) g.cell(i,j,k)=Cell3::SOLID;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i) g.u(i,j,k)=(double)i;
  auto d0=divergence(g);
  solvePressure(g,d0,1.0,1.0,1000,1e-9);
  project(g,1.0,1.0);
  auto d1=divergence(g);
  double maxdiv=0.0;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i)
    if(g.cell(i,j,k)==Cell3::FLUID) maxdiv=std::max(maxdiv,std::abs(d1[g.cidx(i,j,k)]));
  CHECK(maxdiv < 1e-5);
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현**

`src/pressure/pressure3d.h`:
```cpp
#pragma once
#include <vector>
struct UniformGrid3D;
std::vector<double> divergence(const UniformGrid3D& g);
double solvePressure(UniformGrid3D& g, const std::vector<double>& div, double dt,double rho,int max_iter,double tol);
void project(UniformGrid3D& g, double dt, double rho);
```
`src/pressure/pressure3d.cpp`:
```cpp
#include "pressure/pressure3d.h"
#include "grid/uniform_grid3d.h"
#include <cmath>
#include <algorithm>

std::vector<double> divergence(const UniformGrid3D& g){
  std::vector<double> d(g.nx*g.ny*g.nz,0.0);
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    double du=g.u(i+1,j,k)-g.u(i,j,k), dv=g.v(i,j+1,k)-g.v(i,j,k), dw=g.w(i,j,k+1)-g.w(i,j,k);
    d[g.cidx(i,j,k)]=(du+dv+dw)/g.dx;
  }
  return d;
}
namespace {
inline bool isFluid(UniformGrid3D& g,int i,int j,int k){ return g.inBounds(i,j,k)&&g.cell(i,j,k)==Cell3::FLUID; }
inline bool isSolid(UniformGrid3D& g,int i,int j,int k){ return !g.inBounds(i,j,k)||g.cell(i,j,k)==Cell3::SOLID; }
const int DI[6]={1,-1,0,0,0,0}, DJ[6]={0,0,1,-1,0,0}, DK[6]={0,0,0,0,1,-1};
void applyA(UniformGrid3D& g,double scale,const std::vector<double>& x,std::vector<double>& out){
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    int c=g.cidx(i,j,k); out[c]=0.0;
    if(!isFluid(g,i,j,k)) continue;
    double diag=0,off=0;
    for(int n=0;n<6;++n){ int ni=i+DI[n],nj=j+DJ[n],nk=k+DK[n];
      if(isSolid(g,ni,nj,nk)) continue; diag+=1.0; if(isFluid(g,ni,nj,nk)) off+=x[g.cidx(ni,nj,nk)]; }
    out[c]=scale*(diag*x[c]-off);
  }
}
double diagOf(UniformGrid3D& g,double scale,int i,int j,int k){
  double d=0; for(int n=0;n<6;++n) if(!isSolid(g,i+DI[n],j+DJ[n],k+DK[n])) d+=1.0; return scale*d;
}
}
double solvePressure(UniformGrid3D& g,const std::vector<double>& div,double dt,double rho,int max_iter,double tol){
  int N=g.nx*g.ny*g.nz; double scale=dt/(rho*g.dx*g.dx);
  std::vector<double> x(N,0.0),r(N,0.0),z(N,0.0),pdir(N,0.0),Ap(N,0.0);
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){ int c=g.cidx(i,j,k); r[c]=isFluid(g,i,j,k)?-div[c]:0.0; }
  auto precond=[&](const std::vector<double>& in,std::vector<double>& outv){
    for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){ int c=g.cidx(i,j,k);
      double d=isFluid(g,i,j,k)?diagOf(g,scale,i,j,k):0.0; outv[c]=(d>0.0)?in[c]/d:0.0; } };
  auto dotp=[&](const std::vector<double>& a,const std::vector<double>& b){ double s=0; for(int t=0;t<N;++t) s+=a[t]*b[t]; return s; };
  double res0=0; for(int t=0;t<N;++t) res0=std::max(res0,std::abs(r[t]));
  if(res0<tol){ g.pfield=x; return res0; }
  precond(r,z); pdir=z; double rz=dotp(r,z), res=res0;
  for(int it=0;it<max_iter;++it){
    applyA(g,scale,pdir,Ap); double pAp=dotp(pdir,Ap); if(std::abs(pAp)<1e-30) break;
    double alpha=rz/pAp; for(int t=0;t<N;++t){ x[t]+=alpha*pdir[t]; r[t]-=alpha*Ap[t]; }
    res=0; for(int t=0;t<N;++t) res=std::max(res,std::abs(r[t])); if(res<tol) break;
    precond(r,z); double rzn=dotp(r,z), beta=rzn/rz; rz=rzn;
    for(int t=0;t<N;++t) pdir[t]=z[t]+beta*pdir[t];
  }
  g.pfield=x; return res;
}
void project(UniformGrid3D& g,double dt,double rho){
  double scale=dt/(rho*g.dx);
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=1;i<g.nx;++i){
    if(isSolid(g,i-1,j,k)||isSolid(g,i,j,k)){ g.u(i,j,k)=0.0; continue; }
    bool a=isFluid(g,i-1,j,k),b=isFluid(g,i,j,k); if(a||b){ double pl=a?g.p(i-1,j,k):0.0, pr=b?g.p(i,j,k):0.0; g.u(i,j,k)-=scale*(pr-pl); }
  }
  for(int k=0;k<g.nz;++k)for(int j=1;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    if(isSolid(g,i,j-1,k)||isSolid(g,i,j,k)){ g.v(i,j,k)=0.0; continue; }
    bool a=isFluid(g,i,j-1,k),b=isFluid(g,i,j,k); if(a||b){ double pb=a?g.p(i,j-1,k):0.0, pt=b?g.p(i,j,k):0.0; g.v(i,j,k)-=scale*(pt-pb); }
  }
  for(int k=1;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i){
    if(isSolid(g,i,j,k-1)||isSolid(g,i,j,k)){ g.w(i,j,k)=0.0; continue; }
    bool a=isFluid(g,i,j,k-1),b=isFluid(g,i,j,k); if(a||b){ double pd=a?g.p(i,j,k-1):0.0, pu=b?g.p(i,j,k):0.0; g.w(i,j,k)-=scale*(pu-pd); }
  }
}
```
- [ ] **Step 4: 빌드·테스트 PASS** (3D maxdiv < 1e-5)
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: 3D divergence + 7-point pressure CG + projection"`

---

## Task 4: 속도 외삽 + 3D RK2 이류

**Files:** Create `src/advect/advect3d.h`, `src/advect/advect3d.cpp`, `tests/test_advect3d.cpp`; Modify `CMakeLists.txt`.

자유표면 근처에서 입자가 air 셀의 무효 속도를 샘플하지 않도록, 질량 없는 면 속도를 유효 이웃에서 N회 sweep으로 외삽. 그 후 RK2 이류.

- [ ] **Step 1: 실패 테스트** `tests/test_advect3d.cpp`:
```cpp
#include "doctest.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d.h"
#include "advect/advect3d.h"
#include <algorithm>
TEST_CASE("advect3d linear motion") {
  UniformGrid3D g(10,10,10,1.0);
  std::fill(g.ufield.begin(),g.ufield.end(),2.0);
  Particles3D ps; ps.add({5.0,5.0,5.0},{2.0,0.0,0.0});
  advect(ps,g,0.5);
  CHECK(ps.pos[0].x == doctest::Approx(6.0));
}
TEST_CASE("extrapolate fills a zero-mass face from a valid neighbor") {
  UniformGrid3D g(4,4,4,1.0);
  // one valid u-face with mass, its +x neighbor has none
  g.u(1,1,1)=5.0; g.mu[g.uidx(1,1,1)]=1.0;
  extrapolateVelocity(g, 2);
  CHECK(g.u(2,1,1) == doctest::Approx(5.0));  // propagated
}
```
- [ ] **Step 2: CMake 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현**

`src/advect/advect3d.h`:
```cpp
#pragma once
struct UniformGrid3D;
struct Particles3D;
void extrapolateVelocity(UniformGrid3D& g, int sweeps);
void advect(Particles3D& ps, const UniformGrid3D& g, double dt);
```
`src/advect/advect3d.cpp`:
```cpp
#include "advect/advect3d.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d.h"
#include "transfer/transfer3d.h"
#include <algorithm>
#include <vector>

// generic extrapolation on one axis field: faces with valid[idx]==0 get the average of valid neighbors; repeat.
static void extrapField(std::vector<double>& f, std::vector<char>& valid, int W,int H,int D,int sw,int sweeps){
  const int di[6]={1,-1,0,0,0,0},dj[6]={0,0,1,-1,0,0},dk[6]={0,0,0,0,1,-1};
  for(int s=0;s<sweeps;++s){
    std::vector<char> newly(valid.size(),0); std::vector<double> add(f.size(),0.0); std::vector<int> cnt(f.size(),0);
    for(int k=0;k<D;++k)for(int j=0;j<H;++j)for(int i=0;i<W;++i){
      int c=i+sw*(j+H*k); if(valid[c]) continue;
      double sum=0; int n=0;
      for(int t=0;t<6;++t){ int ii=i+di[t],jj=j+dj[t],kk=k+dk[t];
        if(ii<0||ii>=W||jj<0||jj>=H||kk<0||kk>=D) continue;
        int nc=ii+sw*(jj+H*kk); if(valid[nc]){ sum+=f[nc]; ++n; } }
      if(n>0){ f[c]=sum/n; newly[c]=1; }
    }
    for(size_t t=0;t<valid.size();++t) if(newly[t]) valid[t]=1;
  }
}
void extrapolateVelocity(UniformGrid3D& g, int sweeps){
  std::vector<char> vu(g.mu.size()),vv(g.mv.size()),vw(g.mw.size());
  for(size_t t=0;t<g.mu.size();++t) vu[t]=g.mu[t]>0.0; 
  for(size_t t=0;t<g.mv.size();++t) vv[t]=g.mv[t]>0.0;
  for(size_t t=0;t<g.mw.size();++t) vw[t]=g.mw[t]>0.0;
  extrapField(g.ufield,vu,g.nx+1,g.ny,g.nz,g.nx+1,sweeps);
  extrapField(g.vfield,vv,g.nx,g.ny+1,g.nz,g.nx,sweeps);
  extrapField(g.wfield,vw,g.nx,g.ny,g.nz+1,g.nx,sweeps);
}
void advect(Particles3D& ps, const UniformGrid3D& g, double dt){
  double lox=g.ox+0.5*g.dx, hix=g.ox+(g.nx-0.5)*g.dx;
  double loy=g.oy+0.5*g.dx, hiy=g.oy+(g.ny-0.5)*g.dx;
  double loz=g.oz+0.5*g.dx, hiz=g.oz+(g.nz-0.5)*g.dx;
  for(size_t kpt=0;kpt<ps.size();++kpt){
    double px=(ps.pos[kpt].x-g.ox)/g.dx, py=(ps.pos[kpt].y-g.oy)/g.dx, pz=(ps.pos[kpt].z-g.oz)/g.dx;
    double u1=sampleU(g,px,py,pz),v1=sampleV(g,px,py,pz),w1=sampleW(g,px,py,pz);
    double mx=ps.pos[kpt].x+0.5*dt*u1, my=ps.pos[kpt].y+0.5*dt*v1, mz=ps.pos[kpt].z+0.5*dt*w1;
    double mpx=(mx-g.ox)/g.dx,mpy=(my-g.oy)/g.dx,mpz=(mz-g.oz)/g.dx;
    double u2=sampleU(g,mpx,mpy,mpz),v2=sampleV(g,mpx,mpy,mpz),w2=sampleW(g,mpx,mpy,mpz);
    double nx_=ps.pos[kpt].x+dt*u2, ny_=ps.pos[kpt].y+dt*v2, nz_=ps.pos[kpt].z+dt*w2;
    ps.pos[kpt].x=std::max(lox,std::min(hix,nx_));
    ps.pos[kpt].y=std::max(loy,std::min(hiy,ny_));
    ps.pos[kpt].z=std::max(loz,std::min(hiz,nz_));
  }
}
```
- [ ] **Step 4: 빌드·테스트 PASS**
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: velocity extrapolation + 3D RK2 advection"`

---

## Task 5: 점성 α↔ν 매핑 (Eq.13)

**Files:** Create `src/physics/viscosity.h`, `tests/test_viscosity.cpp`; Modify `CMakeLists.txt`.

논문 Eq.13: `ν = (1−α)·Δx²/(6Δt)` → 목표 점성 ν에서 α를 역산: `α = 1 − 6νΔt/Δx²` (clamp [0,1]).

- [ ] **Step 1: 실패 테스트** `tests/test_viscosity.cpp`:
```cpp
#include "doctest.h"
#include "physics/viscosity.h"
TEST_CASE("alpha<->nu roundtrip (Eq.13)") {
  double dx=0.5, dt=0.01, alpha=0.9;
  double nu = numericalViscosity(alpha, dx, dt);
  CHECK(nu == doctest::Approx((1-alpha)*dx*dx/(6*dt)));
  CHECK(alphaForViscosity(nu, dx, dt) == doctest::Approx(alpha));
}
TEST_CASE("alphaForViscosity clamps") {
  CHECK(alphaForViscosity(1e9, 1.0, 1.0) == doctest::Approx(0.0));   // huge nu -> alpha 0
  CHECK(alphaForViscosity(0.0, 1.0, 1.0) == doctest::Approx(1.0));   // inviscid -> alpha 1
}
```
- [ ] **Step 2: CMake에 test 추가 → 빌드 FAIL 확인**
- [ ] **Step 3: 구현** `src/physics/viscosity.h`:
```cpp
#pragma once
#include <algorithm>
// Eq.13: nu = (1-alpha) * dx^2 / (6 dt)
inline double numericalViscosity(double alpha, double dx, double dt){
  return (1.0-alpha)*dx*dx/(6.0*dt);
}
// invert: alpha = 1 - 6 nu dt / dx^2, clamped to [0,1]
inline double alphaForViscosity(double nu, double dx, double dt){
  double a = 1.0 - 6.0*nu*dt/(dx*dx);
  return std::max(0.0, std::min(1.0, a));
}
```
- [ ] **Step 4: 빌드·테스트 PASS**
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: viscosity <-> FLIP alpha mapping (Eq.13)"`

---

## Task 6: Sim3D 드라이버 + 3D dam-break 통합테스트 + 슬라이스 viz

**Files:** Create `src/driver/sim3d.h`, `src/driver/sim3d.cpp`, `src/driver/viz_slice.h`, `apps/run_dambreak3d.cpp`, `tests/test_sim3d.cpp`; Modify `CMakeLists.txt`.

스텝: `markCells → p2g → saved=grid → 중력(mv>0 면) → 솔리드 경계 → divergence → solvePressure → project → extrapolateVelocity → g2p → advect`. α는 목표 점성에서 `alphaForViscosity`로.

- [ ] **Step 1: 실패 통합 테스트** `tests/test_sim3d.cpp`:
```cpp
#include "doctest.h"
#include "driver/sim3d.h"
#include <cmath>
#include <algorithm>
TEST_CASE("3D dam break stable, conserves count, falls and spreads") {
  Sim3D sim(24,24,24,1.0);
  sim.initDamBreak();
  size_t n0=sim.particles.size(); CHECK(n0>0);
  double my0=0,mx0=0; for(size_t k=0;k<n0;++k){ my0+=sim.particles.pos[k].y; mx0+=sim.particles.pos[k].x; } my0/=n0; mx0/=n0;
  for(int s=0;s<40;++s) sim.step();
  CHECK(sim.particles.size()==n0);
  bool finite=true; double maxy=0,my1=0,mx1=0;
  for(size_t k=0;k<sim.particles.size();++k){
    if(!std::isfinite(sim.particles.pos[k].x)||!std::isfinite(sim.particles.pos[k].y)||!std::isfinite(sim.particles.pos[k].z)) finite=false;
    maxy=std::max(maxy,sim.particles.pos[k].y); my1+=sim.particles.pos[k].y; mx1+=sim.particles.pos[k].x;
  }
  my1/=sim.particles.size(); mx1/=sim.particles.size();
  CHECK(finite); CHECK(maxy<24.0); CHECK(my1<my0); CHECK(mx1>mx0);
}
```
- [ ] **Step 2: CMake 추가(라이브러리에 `sim3d.cpp`, unit_tests에 test) → 빌드 FAIL 확인**
- [ ] **Step 3: 구현**

`src/driver/sim3d.h`:
```cpp
#pragma once
#include "grid/uniform_grid3d.h"
#include "particles/particles3d.h"
struct Sim3D {
  UniformGrid3D grid;
  Particles3D particles;
  double dt=0.05, rho=1.0, gravity=-9.81;
  double target_nu=0.0;   // 0 -> alpha=1 (inviscid); set >0 for viscous
  int cg_iters=300; double cg_tol=1e-6; int extrap_sweeps=3;
  Sim3D(int nx,int ny,int nz,double dx) : grid(nx,ny,nz,dx) {}
  void initDamBreak();
  void step();
};
```
`src/driver/sim3d.cpp`:
```cpp
#include "driver/sim3d.h"
#include "transfer/transfer3d.h"
#include "pressure/pressure3d.h"
#include "advect/advect3d.h"
#include "physics/viscosity.h"

void Sim3D::initDamBreak(){
  int wx=grid.nx*4/10, hy=grid.ny*7/10, dz=grid.nz; // column: left 40% x, 70% y, full z (minus walls)
  for(int k=1;k<dz-1;++k)for(int j=1;j<hy;++j)for(int i=1;i<wx;++i)
    for(int sk=0;sk<2;++sk)for(int sj=0;sj<2;++sj)for(int si=0;si<2;++si){
      double x=grid.ox+(i+0.25+0.5*si)*grid.dx, y=grid.oy+(j+0.25+0.5*sj)*grid.dx, z=grid.oz+(k+0.25+0.5*sk)*grid.dx;
      particles.add({x,y,z},{0,0,0},0);
    }
}
static void markCells(UniformGrid3D& g, const Particles3D& ps){
  for(auto& c:g.marker) c=Cell3::AIR;
  for(int k=0;k<g.nz;++k)for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i)
    if(i==0||i==g.nx-1||j==0||j==g.ny-1||k==0||k==g.nz-1) g.cell(i,j,k)=Cell3::SOLID;
  for(size_t t=0;t<ps.size();++t){
    int i=(int)((ps.pos[t].x-g.ox)/g.dx), j=(int)((ps.pos[t].y-g.oy)/g.dx), k=(int)((ps.pos[t].z-g.oz)/g.dx);
    if(g.inBounds(i,j,k)&&g.cell(i,j,k)!=Cell3::SOLID) g.cell(i,j,k)=Cell3::FLUID;
  }
}
void Sim3D::step(){
  double alpha = alphaForViscosity(target_nu, grid.dx, dt);
  markCells(grid, particles);
  p2g(grid, particles);
  UniformGrid3D saved = grid;
  for(size_t idx=0; idx<grid.vfield.size(); ++idx) if(grid.mv[idx]>0.0) grid.vfield[idx]+=dt*gravity;
  // No-penetration BC at wall-interface faces (cells 0 and n-1 are SOLID)
  for(int k=0;k<grid.nz;++k)for(int j=0;j<grid.ny;++j){ grid.u(0,j,k)=0; grid.u(1,j,k)=0; grid.u(grid.nx-1,j,k)=0; grid.u(grid.nx,j,k)=0; }
  for(int k=0;k<grid.nz;++k)for(int i=0;i<grid.nx;++i){ grid.v(i,0,k)=0; grid.v(i,1,k)=0; grid.v(i,grid.ny-1,k)=0; grid.v(i,grid.ny,k)=0; }
  for(int j=0;j<grid.ny;++j)for(int i=0;i<grid.nx;++i){ grid.w(i,j,0)=0; grid.w(i,j,1)=0; grid.w(i,j,grid.nz-1)=0; grid.w(i,j,grid.nz)=0; }
  auto div = divergence(grid);
  solvePressure(grid, div, dt, rho, cg_iters, cg_tol);
  project(grid, dt, rho);
  extrapolateVelocity(grid, extrap_sweeps);
  g2p(grid, particles, saved, alpha);
  advect(particles, grid, dt);
}
```
`src/driver/viz_slice.h` (mid-z XY 슬라이스에 입자 투영):
```cpp
#pragma once
#include <string>
#include <vector>
#include <fstream>
#include <cmath>
#include "driver/sim3d.h"
inline void writeSlicePPM(const Sim3D& sim, const std::string& path, int scale=8, double zhalf=0.1){
  int W=sim.grid.nx*scale, H=sim.grid.ny*scale;
  std::vector<unsigned char> img(W*H*3,20);
  double zc = sim.grid.oz + sim.grid.nz*0.5*sim.grid.dx;
  double band = zhalf*sim.grid.nz*sim.grid.dx;
  for(size_t k=0;k<sim.particles.size();++k){
    if(std::abs(sim.particles.pos[k].z - zc) > band) continue;     // thin mid slice
    int px=(int)((sim.particles.pos[k].x-sim.grid.ox)/sim.grid.dx*scale);
    int py=(int)((sim.particles.pos[k].y-sim.grid.oy)/sim.grid.dx*scale); py=H-1-py;
    if(px<0||px>=W||py<0||py>=H) continue;
    int o=(px+W*py)*3; img[o]=60; img[o+1]=140; img[o+2]=230;
  }
  std::ofstream f(path,std::ios::binary); f<<"P6\n"<<W<<" "<<H<<"\n255\n"; f.write((const char*)img.data(),img.size());
}
```
`apps/run_dambreak3d.cpp`:
```cpp
#include "driver/sim3d.h"
#include "driver/viz_slice.h"
#include <cstdio>
int main(){
  Sim3D sim(48,48,48,1.0);
  sim.initDamBreak();
  for(int s=0;s<160;++s){ sim.step();
    if(s%5==0){ char n[80]; std::snprintf(n,sizeof(n),"slice_%03d.ppm",s/5); writeSlicePPM(sim,n); } }
  std::printf("done: %zu particles\n", sim.particles.size());
  return 0;
}
```
CMake: add `add_executable(run_dambreak3d apps/run_dambreak3d.cpp)` + `target_link_libraries(run_dambreak3d pfflip2d)`.
- [ ] **Step 4: 빌드·테스트 PASS** (3D dam-break: count 보존·유한·낙하·확산). 그 후 `run_dambreak3d` 실행해 mid-z 슬라이스 시퀀스 생성, controller가 육안 확인.
- [ ] **Step 5: Commit** — `git add -A; git commit -m "feat: Sim3D driver + 3D dam-break integration + slice viz"`

---

## Self-Review (작성자 점검)
- **Spec coverage (SPEC-1 Phase 1):** 3D 확장(T1–3,6), 점성 Eq.13(T5), 속도 외삽(T4), 3D dam-break(T6). ✅ Phase 0 2D 모듈은 미삭제 → 회귀 보존.
- **Placeholder scan:** 전 step 실제 코드/명령. 없음. ✅
- **Type consistency:** `UniformGrid3D`(`u/v/w/p/cell` + const, `uidx/vidx/widx/cidx`, `nx/ny/nz/dx/ox/oy/oz`), `Particles3D`(`pos/vel/type`,`add(p,v,t)`), 함수 `p2g/g2p/sampleU/V/W/divergence/solvePressure/project/extrapolateVelocity/advect/numericalViscosity/alphaForViscosity` 전 태스크 일관. w-면 stride=`nx*ny`, k∈[0,nz]. ✅
- **검증 관문:** 3D 압력 maxdiv<1e-5(T3), 외삽 전파(T4), Eq.13 왕복(T5), 3D dam-break 낙하·확산(T6).

## 다음 PLAN
- **PLAN-2 (Phase 2, ★권장 정지선):** phase-field 2상(Eq.7) + 가변계수 β=1/ρ Poisson(Eq.8) + cubic 커널(Eq.6) + escaped 분기 → "표면재구성 없는 2상"이라는 **논문 핵심**이 처음 등장.
