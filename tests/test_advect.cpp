#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d.h"
#include "advect/advect2d.h"
#include <algorithm>
TEST_CASE("advect moves particle linearly in uniform field") {
  UniformGrid2D g(10,10,1.0);
  std::fill(g.ufield.begin(), g.ufield.end(), 2.0);
  Particles2D ps; ps.add({5.0,5.0}, {2.0,0.0});
  advect(ps, g, 0.5);
  CHECK(ps.pos[0].x == doctest::Approx(6.0));
  CHECK(ps.pos[0].y == doctest::Approx(5.0));
}
TEST_CASE("advect clamps to domain") {
  UniformGrid2D g(10,10,1.0);
  std::fill(g.ufield.begin(), g.ufield.end(), 100.0);
  Particles2D ps; ps.add({9.0,5.0}, {100.0,0.0});
  advect(ps, g, 1.0);
  CHECK(ps.pos[0].x <= 10.0 - 0.5);
}
