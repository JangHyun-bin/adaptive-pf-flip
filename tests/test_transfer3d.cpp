#include "doctest.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d.h"
#include "transfer/transfer3d.h"
TEST_CASE("p2g3d single particle at u-node gives vx") {
  UniformGrid3D g(4,4,4,1.0);
  Particles3D ps; ps.add({2.0,1.5,1.5},{3.0,-7.0,2.0});
  p2g(g, ps);
  CHECK(g.u(2,1,1) == doctest::Approx(3.0));
  CHECK(g.mu[g.uidx(2,1,1)] == doctest::Approx(1.0));
}
TEST_CASE("p2g3d conserves x-momentum across split") {
  UniformGrid3D g(4,4,4,1.0);
  Particles3D ps; ps.add({2.5,1.5,1.5},{4.0,0.0,0.0});
  p2g(g, ps);
  double mom = g.u(2,1,1)*g.mu[g.uidx(2,1,1)] + g.u(3,1,1)*g.mu[g.uidx(3,1,1)];
  CHECK(mom == doctest::Approx(4.0));
}
TEST_CASE("g2p3d PIC vs FLIP") {
  UniformGrid3D g(4,4,4,1.0), saved(4,4,4,1.0);
  std::fill(g.ufield.begin(),g.ufield.end(),5.0);
  std::fill(saved.ufield.begin(),saved.ufield.end(),2.0);
  Particles3D ps; ps.add({2.0,2.0,2.0},{10.0,0.0,0.0});
  g2p(g, ps, saved, 1.0);
  CHECK(ps.vel[0].x == doctest::Approx(13.0));
}
