#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "pressure/pressure2d_vc.h"
#include <cmath>
TEST_CASE("VC projection removes divergence (uniform beta == constant case)") {
  UniformGrid2D g(8,8,1.0);
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) g.cell(i,j)=(i>=1&&i<7&&j>=1&&j<7)?Cell::FLUID:Cell::AIR;
  for(int j=0;j<g.ny;++j){g.cell(0,j)=Cell::SOLID;g.cell(7,j)=Cell::SOLID;}
  for(int i=0;i<g.nx;++i){g.cell(i,0)=Cell::SOLID;g.cell(i,7)=Cell::SOLID;}
  std::fill(g.bu.begin(),g.bu.end(),1.0); std::fill(g.bv.begin(),g.bv.end(),1.0);
  for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i) g.u(i,j)=(double)i;
  auto d0=divergenceVC(g);
  solvePressureVC(g,d0,1.0,500,1e-10);
  projectVC(g,1.0);
  auto d1=divergenceVC(g);
  double mx=0; for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) if(g.cell(i,j)==Cell::FLUID) mx=std::max(mx,std::abs(d1[i+g.nx*j]));
  CHECK(mx<1e-5);
}
TEST_CASE("hydrostatic two-phase column: residual velocity bounded") {
  UniformGrid2D g(6,16,1.0);
  for(int j=0;j<g.ny;++j)for(int i=0;i<g.nx;++i) g.cell(i,j)=(i>=1&&i<5&&j>=1&&j<15)?Cell::FLUID:Cell::AIR;
  for(int j=0;j<g.ny;++j){g.cell(0,j)=Cell::SOLID;g.cell(5,j)=Cell::SOLID;}
  for(int i=0;i<g.nx;++i){g.cell(i,0)=Cell::SOLID;g.cell(i,15)=Cell::SOLID;}
  for(int j=0;j<=g.ny;++j)for(int i=0;i<g.nx;++i){ double b=(j<8)?1.0:100.0; g.bv[i+g.nx*j]=b; }
  for(int j=0;j<g.ny;++j)for(int i=0;i<=g.nx;++i){ double b=(j<8)?1.0:100.0; g.bu[i+(g.nx+1)*j]=b; }
  double dt=0.1, gconst=-9.81;
  for(int j=1;j<g.ny;++j)for(int i=0;i<g.nx;++i) g.v(i,j)+=dt*gconst;
  auto d=divergenceVC(g); solvePressureVC(g,d,dt,1000,1e-10); projectVC(g,dt);
  double mv=0; for(int j=2;j<g.ny-1;++j)for(int i=1;i<g.nx-1;++i) mv=std::max(mv,std::abs(g.v(i,j)));
  CHECK(mv < 0.5);
}
