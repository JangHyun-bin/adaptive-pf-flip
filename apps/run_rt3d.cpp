#include "driver/sim3d_tp.h"
#include "driver/viz_phase3d.h"
#include <cstdio>
int main(){ Sim3DTP sim(48,64,48,1.0); sim.initRayleighTaylor();
  for(int s=0;s<200;++s){ sim.step(); if(s%8==0){char n[64];std::snprintf(n,sizeof(n),"rt3_%03d.ppm",s/8);writePhaseSlice(sim,n);} }
  std::printf("done: %zu particles\n", sim.particles.size()); return 0; }
