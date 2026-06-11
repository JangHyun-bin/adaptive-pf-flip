#include "doctest.h"
#include "driver/sparse_sim2d_tp.h"
#include <cmath>
#include <algorithm>
TEST_CASE("sparse bubble tank: gas rises by buoyancy, headspace blocks never allocated") {
  SparseSim2DTP sim(48,48,1.0);    // 6x6=36 cell-blocks
  sim.initBubbleTank();            // water rows [1,24), gas bubble circle, empty above
  size_t n0=sim.particles.size(); CHECK(n0>0);
  auto meanY=[&](unsigned char t){ double s=0;int n=0; for(size_t k=0;k<sim.particles.size();++k) if(sim.particles.type[k]==t){s+=sim.particles.pos[k].y;++n;} return n?s/n:0.0; };
  double gy0=meanY(1); CHECK(gy0>0.0);
  size_t maxActive=0;
  for(int s=0;s<60;++s){ sim.step(); maxActive=std::max(maxActive,sim.grid.activeCellBlocks()); }
  CHECK(sim.particles.size()==n0);
  bool fin=true; for(size_t k=0;k<sim.particles.size();++k) if(!std::isfinite(sim.particles.pos[k].x)||!std::isfinite(sim.particles.pos[k].y)) fin=false;
  CHECK(fin);
  CHECK(meanY(1) > gy0 + 0.5);                       // bubble rose
  CHECK(maxActive > 0);
  CHECK(maxActive < sim.grid.totalCellBlocks());     // headspace stayed unallocated (sparsity)
}
