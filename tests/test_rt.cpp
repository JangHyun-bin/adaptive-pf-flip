#include "doctest.h"
#include "driver/sim2d_tp.h"
#include <cmath>
TEST_CASE("Rayleigh-Taylor instability grows (heavy-over-light)") {
  Sim2DTP sim(32,48,1.0);
  sim.initRayleighTaylor();
  auto meanY=[&](unsigned char t){ double s=0;int n=0; for(size_t k=0;k<sim.particles.size();++k) if(sim.particles.type[k]==t){s+=sim.particles.pos[k].y;++n;} return n?s/n:0.0; };
  double hy0=meanY(0), gy0=meanY(1);
  CHECK(hy0 > gy0);                 // heavy starts on top
  for(int s=0;s<80;++s) sim.step();
  bool finite=true; for(size_t k=0;k<sim.particles.size();++k) if(!std::isfinite(sim.particles.pos[k].y)) finite=false;
  CHECK(finite);
  double hy1=meanY(0), gy1=meanY(1);
  CHECK(hy1 < hy0);                 // heavy phase sank (overturning)
  CHECK(gy1 > gy0);                 // light phase rose
}
