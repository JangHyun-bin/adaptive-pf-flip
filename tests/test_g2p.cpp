#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d.h"
#include "transfer/transfer2d.h"
TEST_CASE("g2p PIC (alpha=0) takes grid velocity") {
  UniformGrid2D g(4,4,1.0), saved(4,4,1.0);
  std::fill(g.ufield.begin(), g.ufield.end(), 5.0);
  std::fill(saved.ufield.begin(), saved.ufield.end(), 0.0);
  Particles2D ps; ps.add({2.0,2.0}, {1.0,1.0});
  g2p(g, ps, saved, 0.0);
  CHECK(ps.vel[0].x == doctest::Approx(5.0));
}
TEST_CASE("g2p FLIP (alpha=1) adds delta") {
  UniformGrid2D g(4,4,1.0), saved(4,4,1.0);
  std::fill(g.ufield.begin(), g.ufield.end(), 5.0);
  std::fill(saved.ufield.begin(), saved.ufield.end(), 2.0);
  Particles2D ps; ps.add({2.0,2.0}, {10.0,0.0});
  g2p(g, ps, saved, 1.0);
  CHECK(ps.vel[0].x == doctest::Approx(13.0));  // 10 + (5-2)
}
