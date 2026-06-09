#include "doctest.h"
#include "driver/sim2d_tp.h"
#include <cmath>
TEST_CASE("two-phase dam break: stable, count conserved, heavy phase does not levitate") {
  Sim2DTP sim(32,32,1.0);
  sim.initTwoPhaseDamBreak();
  size_t n0=sim.particles.size(); CHECK(n0>0);
  auto meanLiqY=[&](){ double s=0;int n=0; for(size_t k=0;k<sim.particles.size();++k) if(sim.particles.type[k]==0){s+=sim.particles.pos[k].y;++n;} return n?s/n:0.0; };
  double y0=meanLiqY();
  for(int s=0;s<50;++s) sim.step();
  CHECK(sim.particles.size()==n0);
  bool finite=true; for(size_t k=0;k<sim.particles.size();++k) if(!std::isfinite(sim.particles.pos[k].x)||!std::isfinite(sim.particles.pos[k].y)) finite=false;
  CHECK(finite);
  CHECK(meanLiqY() < y0 + 0.5);   // heavy phase did not levitate
}
