// Particle exporter for external "rough" rendering.
// Runs a 2D two-phase Rayleigh-Taylor and dumps per-frame particle data (x,y,type)
// as CSV, to be shaded by tools/rough_render.py.
#include "driver/sim2d_tp.h"
#include <cstdio>
#include <fstream>
int main(){
  Sim2DTP sim(72,108,1.0);
  sim.cg_iters = 250; sim.cg_tol = 1e-5; sim.dt = 0.025;
  sim.initRayleighTaylor();
  const int STEPS = 200, EVERY = 5;
  for(int s=0; s<STEPS; ++s){
    sim.step();
    if(s % EVERY == 0){
      char n[64]; std::snprintf(n, sizeof(n), "render_%03d.csv", s/EVERY);
      std::ofstream f(n);
      f << sim.grid.nx << " " << sim.grid.ny << " " << sim.grid.dx << "\n";
      for(size_t k=0;k<sim.particles.size();++k)
        f << sim.particles.pos[k].x << "," << sim.particles.pos[k].y << "," << (int)sim.particles.type[k] << "\n";
    }
  }
  std::printf("done: %zu particles, %d frames\n", sim.particles.size(), STEPS/EVERY);
  return 0;
}
