#include "driver/sparse_sim2d_tp.h"
#include "driver/viz_sparse_tp.h"
#include <algorithm>
#include <cstdio>
int main(){ SparseSim2DTP sim(96,96,1.0);   // 12x12=144 blocks; water rows [1,48), bubble r=9
  sim.cg_iters = 800;                        // demo headroom at 96^2 (4.4k fluid cells)
  sim.initBubbleTank();
  size_t maxActive=0;
  for(int s=0;s<300;++s){ sim.step(); maxActive=std::max(maxActive,sim.grid.activeCellBlocks());
    if(s%5==0){ char n[64]; std::snprintf(n,sizeof(n),"spb_%03d.ppm",s/5); writeSparseTPPPM(sim,n); } }
  std::printf("done: %zu particles, max active blocks %zu/%zu\n", sim.particles.size(), maxActive, sim.grid.totalCellBlocks());
  return 0; }
