#include "doctest.h"
#include "driver/sparse_sim2d_tp.h"
#include <cmath>
TEST_CASE("sparse two-phase Rayleigh-Taylor overturns (heavy over light)") {
  SparseSim2DTP sim(32,48,1.0);
  sim.initRayleighTaylor();
  auto meanY=[&](unsigned char t){ double s=0;int n=0; for(size_t k=0;k<sim.particles.size();++k) if(sim.particles.type[k]==t){s+=sim.particles.pos[k].y;++n;} return n?s/n:0.0; };
  double hy0=meanY(0), gy0=meanY(1);
  CHECK(hy0 > gy0);                 // heavy starts on top
  size_t n0=sim.particles.size();
  for(int s=0;s<80;++s) sim.step();
  CHECK(sim.particles.size()==n0);
  bool fin=true; for(size_t k=0;k<sim.particles.size();++k) if(!std::isfinite(sim.particles.pos[k].x)||!std::isfinite(sim.particles.pos[k].y)) fin=false;
  CHECK(fin);
  CHECK(meanY(0) < hy0);            // heavy sank
  CHECK(meanY(1) > gy0);            // light rose
}
