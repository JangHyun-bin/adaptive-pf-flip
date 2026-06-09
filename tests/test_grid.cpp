#include "doctest.h"
#include "grid/uniform_grid2d.h"
TEST_CASE("grid sizes and access") {
  UniformGrid2D g(4,3,0.5);
  CHECK(g.nx == 4); CHECK(g.ny == 3);
  CHECK(g.u_size() == (4+1)*3);
  CHECK(g.v_size() == 4*(3+1));
  CHECK(g.cell_size() == 4*3);
  g.u(2,1) = 7.0;  CHECK(g.u(2,1) == doctest::Approx(7.0));
  g.p(3,2) = -1.5; CHECK(g.p(3,2) == doctest::Approx(-1.5));
  g.clear();       CHECK(g.u(2,1) == doctest::Approx(0.0));
}
