#include "doctest.h"
#include "driver/sparse_sim2d.h"
#include <cmath>
TEST_CASE("sparse dam-break: stable, count conserved, falls+spreads, SPARSE storage") {
  SparseSim2D sim(64,64,1.0);     // 8x8=64 cell-blocks total
  sim.initDamBreak();
  size_t n0=sim.particles.size(); CHECK(n0>0);
  double mx0=0,my0=0; for(size_t k=0;k<n0;++k){mx0+=sim.particles.pos[k].x;my0+=sim.particles.pos[k].y;} mx0/=n0;my0/=n0;
  size_t maxActive=0;
  for(int s=0;s<60;++s){ sim.step(); maxActive=std::max(maxActive,sim.grid.activeCellBlocks()); }
  CHECK(sim.particles.size()==n0);
  bool fin=true; double mx1=0,my1=0; for(size_t k=0;k<sim.particles.size();++k){ if(!std::isfinite(sim.particles.pos[k].x)||!std::isfinite(sim.particles.pos[k].y)) fin=false; mx1+=sim.particles.pos[k].x;my1+=sim.particles.pos[k].y;} mx1/=sim.particles.size();my1/=sim.particles.size();
  CHECK(fin); CHECK(my1<my0); CHECK(mx1>mx0);
  // SPARSITY payoff: never all 64 blocks active (fluid occupies a fraction)
  CHECK(maxActive < sim.grid.totalCellBlocks());
}
