#include "driver/sim2d_tp.h"
#include "driver/viz_phase.h"
#include <cstdio>
int main(){ Sim2DTP sim(64,96,1.0); sim.initRayleighTaylor();
  for(int s=0;s<240;++s){ sim.step(); if(s%8==0){char n[64];std::snprintf(n,sizeof(n),"rt_%03d.ppm",s/8);writePhasePPM(sim,n);} }
  std::printf("done: %zu particles\n", sim.particles.size()); return 0; }
