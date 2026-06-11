#include "driver/multires_sim2d_tp.h"
#include "driver/viz_multires_tp.h"
#include <cstdio>
int main(){ MRSim2DTP sim(96,96,1.0);
  sim.initBubbleTankInterfaceBand();
  for(int s=0;s<160;++s){ sim.step();
    if(s%5==0){ char n[64]; std::snprintf(n,sizeof(n),"mrb_%03d.ppm",s/5); writeMRTPPM(sim,n); } }
  int active=sim.activePressureCellCount(),full=sim.layout.nx*sim.layout.ny;
  std::printf("done: %zu particles, active pressure cells %d/%d\n", sim.particles.size(), active, full);
  return 0; }
