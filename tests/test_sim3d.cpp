#include "doctest.h"
#include "driver/sim3d.h"
#include <cmath>
#include <algorithm>
TEST_CASE("3D dam break stable, conserves count, falls and spreads") {
  Sim3D sim(24,24,24,1.0);
  sim.initDamBreak();
  size_t n0=sim.particles.size(); CHECK(n0>0);
  double my0=0,mx0=0; for(size_t k=0;k<n0;++k){ my0+=sim.particles.pos[k].y; mx0+=sim.particles.pos[k].x; } my0/=n0; mx0/=n0;
  for(int s=0;s<40;++s) sim.step();
  CHECK(sim.particles.size()==n0);
  bool finite=true; double maxy=0,my1=0,mx1=0;
  for(size_t k=0;k<sim.particles.size();++k){
    if(!std::isfinite(sim.particles.pos[k].x)||!std::isfinite(sim.particles.pos[k].y)||!std::isfinite(sim.particles.pos[k].z)) finite=false;
    maxy=std::max(maxy,sim.particles.pos[k].y); my1+=sim.particles.pos[k].y; mx1+=sim.particles.pos[k].x;
  }
  my1/=sim.particles.size(); mx1/=sim.particles.size();
  CHECK(finite); CHECK(maxy<24.0); CHECK(my1<my0); CHECK(mx1>mx0);
}
