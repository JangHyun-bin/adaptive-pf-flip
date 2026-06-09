#pragma once
#include <string>
#include <vector>
#include <fstream>
#include "driver/sim2d_tp.h"
inline void writePhasePPM(const Sim2DTP& sim, const std::string& path, int scale=8){
  int W=sim.grid.nx*scale,H=sim.grid.ny*scale; std::vector<unsigned char> img(W*H*3,12);
  for(size_t k=0;k<sim.particles.size();++k){
    int px=(int)(sim.particles.pos[k].x/sim.grid.dx*scale), py=(int)(sim.particles.pos[k].y/sim.grid.dx*scale); py=H-1-py;
    if(px<0||px>=W||py<0||py>=H) continue; int o=(px+W*py)*3;
    if(sim.particles.type[k]==0){ img[o]=50;img[o+1]=130;img[o+2]=235; } else { img[o]=40;img[o+1]=40;img[o+2]=46; }
  }
  std::ofstream f(path,std::ios::binary); f<<"P6\n"<<W<<" "<<H<<"\n255\n"; f.write((const char*)img.data(),img.size());
}
