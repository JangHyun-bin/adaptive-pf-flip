#include "doctest.h"
#include "grid/uniform_grid3d.h"
#include "particles/particles3d.h"
#include "advect/advect3d.h"
#include <algorithm>
TEST_CASE("advect3d linear motion") {
  UniformGrid3D g(10,10,10,1.0);
  std::fill(g.ufield.begin(),g.ufield.end(),2.0);
  Particles3D ps; ps.add({5.0,5.0,5.0},{2.0,0.0,0.0});
  advect(ps,g,0.5);
  CHECK(ps.pos[0].x == doctest::Approx(6.0));
}
TEST_CASE("extrapolate fills a zero-mass face from a valid neighbor") {
  UniformGrid3D g(4,4,4,1.0);
  g.u(1,1,1)=5.0; g.mu[g.uidx(1,1,1)]=1.0;
  extrapolateVelocity(g, 2);
  CHECK(g.u(2,1,1) == doctest::Approx(5.0));
}
