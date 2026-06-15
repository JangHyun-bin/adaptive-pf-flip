#include "doctest.h"
#include "particles/particles2d.h"
#include "particles/particles3d_tp.h"
TEST_CASE("particles add/size") {
  Particles2D ps;
  CHECK(ps.size() == 0);
  ps.add({1.0,2.0}, {0.0,-1.0});
  ps.add({3.0,4.0}, {0.5,0.0});
  CHECK(ps.size() == 2);
  CHECK(ps.pos[1].x == doctest::Approx(3.0));
  CHECK(ps.vel[0].y == doctest::Approx(-1.0));
}

TEST_CASE("3D two-phase particles carry volume multipliers through erase") {
  Particles3DTP ps;
  ps.add({1.0, 2.0, 3.0}, {0.0, 0.0, 0.0}, 0, 2.5);
  ps.add({4.0, 5.0, 6.0}, {1.0, 0.0, 0.0}, 1, 0.25);

  CHECK(ps.size() == 2);
  CHECK(ps.volume[0] == doctest::Approx(2.5));
  CHECK(ps.volume[1] == doctest::Approx(0.25));

  ps.eraseIf([](size_t p) { return p == 0; });

  REQUIRE(ps.size() == 1);
  CHECK(ps.type[0] == 1);
  CHECK(ps.volume[0] == doctest::Approx(0.25));
}
