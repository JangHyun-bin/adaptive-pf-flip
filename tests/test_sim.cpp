#include "doctest.h"
#include "driver/sim2d.h"
#include <cmath>
#include <algorithm>
TEST_CASE("dam break stable + particle count conserved + physically falls and spreads") {
  Sim2D sim(32,32,1.0);
  sim.initDamBreak();
  size_t n0 = sim.particles.size();
  CHECK(n0 > 0);
  double mx0=0, my0=0;
  for (size_t k=0;k<n0;++k){ mx0+=sim.particles.pos[k].x; my0+=sim.particles.pos[k].y; }
  mx0/=n0; my0/=n0;
  for (int s=0;s<60;++s) sim.step();
  CHECK(sim.particles.size() == n0);
  bool finite = true; double maxy = 0.0, mx1=0, my1=0;
  for (size_t k=0;k<sim.particles.size();++k) {
    if (!std::isfinite(sim.particles.pos[k].x) || !std::isfinite(sim.particles.pos[k].y)) finite=false;
    maxy = std::max(maxy, sim.particles.pos[k].y);
    mx1 += sim.particles.pos[k].x; my1 += sim.particles.pos[k].y;
  }
  mx1/=sim.particles.size(); my1/=sim.particles.size();
  CHECK(finite);
  CHECK(maxy < 32.0);
  CHECK(my1 < my0);   // fluid fell under gravity
  CHECK(mx1 > mx0);   // fluid spread rightward (dam collapse)
}
