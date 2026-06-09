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
