#include "doctest.h"
#include "particles/particles2d.h"
TEST_CASE("particles add/size") {
  Particles2D ps;
  CHECK(ps.size() == 0);
  ps.add({1.0,2.0}, {0.0,-1.0});
  ps.add({3.0,4.0}, {0.5,0.0});
  CHECK(ps.size() == 2);
  CHECK(ps.pos[1].x == doctest::Approx(3.0));
  CHECK(ps.vel[0].y == doctest::Approx(-1.0));
}
