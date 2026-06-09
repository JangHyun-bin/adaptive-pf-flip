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
