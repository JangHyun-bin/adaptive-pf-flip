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
