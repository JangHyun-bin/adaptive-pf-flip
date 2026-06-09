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
