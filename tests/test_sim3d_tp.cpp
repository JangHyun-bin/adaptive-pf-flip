#include "doctest.h"
#include "driver/sim3d_tp.h"
#include <cmath>
TEST_CASE("3D Rayleigh-Taylor overturns (heavy over light)") {
  Sim3DTP sim(24,36,24,1.0);
  sim.initRayleighTaylor();
  auto meanY=[&](unsigned char t){ double s=0;int n=0; for(size_t k=0;k<sim.particles.size();++k) if(sim.particles.type[k]==t){s+=sim.particles.pos[k].y;++n;} return n?s/n:0.0; };
  double hy0=meanY(0), gy0=meanY(1); CHECK(hy0>gy0);
  for(int s=0;s<60;++s) sim.step();
  bool fin=true; for(size_t k=0;k<sim.particles.size();++k) if(!std::isfinite(sim.particles.pos[k].y)) fin=false;
  CHECK(fin); CHECK(meanY(0) < hy0); CHECK(meanY(1) > gy0);
}
