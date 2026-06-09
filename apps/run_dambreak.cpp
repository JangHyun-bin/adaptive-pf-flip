#include "driver/sim2d.h"
#include "driver/viz_ppm.h"
#include <cstdio>
int main() {
  Sim2D sim(64,64,1.0);
  sim.initDamBreak();
  for (int s=0;s<120;++s) {
    sim.step();
    if (s%4==0) { char n[64]; std::snprintf(n,sizeof(n),"frame_%03d.ppm",s/4); writePPM(sim,n); }
  }
  std::printf("done: %zu particles\n", sim.particles.size());
  return 0;
}
