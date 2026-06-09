#include "pressure/pressure2d.h"
#include "grid/uniform_grid2d.h"
#include <cmath>
#include <algorithm>

std::vector<double> divergence(const UniformGrid2D& g) {
  UniformGrid2D& gm = const_cast<UniformGrid2D&>(g);
  std::vector<double> d(g.nx*g.ny, 0.0);
  for (int j=0;j<g.ny;++j) for (int i=0;i<g.nx;++i) {
    double du = gm.u(i+1,j) - gm.u(i,j);
    double dv = gm.v(i,j+1) - gm.v(i,j);
    d[i + g.nx*j] = (du + dv)/g.dx;
  }
  return d;
}
