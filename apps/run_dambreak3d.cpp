#include "driver/sim3d.h"
#include "driver/viz_slice.h"
#include <cstdio>
int main(){
  Sim3D sim(48,48,48,1.0);
  sim.initDamBreak();
  for(int s=0;s<160;++s){ sim.step();
    if(s%5==0){ char n[80]; std::snprintf(n,sizeof(n),"slice_%03d.ppm",s/5); writeSlicePPM(sim,n); } }
  std::printf("done: %zu particles\n", sim.particles.size());
  return 0;
}
