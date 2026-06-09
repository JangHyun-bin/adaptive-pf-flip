#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "pressure/pressure2d.h"
TEST_CASE("divergence of linear u field") {
  UniformGrid2D g(2,2,0.5);
  for (int j=0;j<g.ny;++j) for (int i=0;i<=g.nx;++i) g.u(i,j) = (double)i;
  auto d = divergence(g);
  CHECK(d[0] == doctest::Approx(2.0));  // (u(i+1)-u(i))/dx = 1/0.5
  CHECK(d[3] == doctest::Approx(2.0));
}
