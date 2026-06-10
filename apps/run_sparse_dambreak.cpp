#include "driver/sparse_sim2d.h"
#include "driver/viz_sparse.h"
#include <algorithm>
#include <cstdio>
int main(){ SparseSim2D sim(128,96,1.0);   // 16x12=192 blocks
  sim.initDamBreak();
  size_t maxActive=0;
  for(int s=0;s<160;++s){ sim.step(); maxActive=std::max(maxActive,sim.grid.activeCellBlocks());
    if(s%5==0){ char n[64]; std::snprintf(n,sizeof(n),"sp_%03d.ppm",s/5); writeSparsePPM(sim,n); } }
  std::printf("done: %zu particles, max active blocks %zu/%zu\n", sim.particles.size(), maxActive, sim.grid.totalCellBlocks());
  return 0; }
