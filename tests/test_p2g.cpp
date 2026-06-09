#include "doctest.h"
#include "grid/uniform_grid2d.h"
#include "particles/particles2d.h"
#include "transfer/transfer2d.h"
TEST_CASE("p2g single particle at u-node gives its vx") {
  UniformGrid2D g(4,4,1.0);
  Particles2D ps; ps.add({2.0,1.5}, {3.0,-7.0});  // u-face(2,1) center=(2.0,1.5)
  p2g(g, ps);
  CHECK(g.u(2,1) == doctest::Approx(3.0));
  CHECK(g.mu[2 + (g.nx+1)*1] == doctest::Approx(1.0));
}
TEST_CASE("p2g conserves momentum across two u-nodes") {
  UniformGrid2D g(4,4,1.0);
  Particles2D ps; ps.add({2.5,1.5}, {4.0,0.0});   // splits 50:50
  p2g(g, ps);
  double mom = g.u(2,1)*g.mu[2+5*1] + g.u(3,1)*g.mu[3+5*1];
  CHECK(mom == doctest::Approx(4.0));
}
