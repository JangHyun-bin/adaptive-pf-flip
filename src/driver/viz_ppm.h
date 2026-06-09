#pragma once
#include <string>
#include <vector>
#include <fstream>
#include "driver/sim2d.h"
inline void writePPM(const Sim2D& sim, const std::string& path, int scale=8) {
  int W = sim.grid.nx*scale, H = sim.grid.ny*scale;
  std::vector<unsigned char> img(W*H*3, 20);
  for (size_t k=0;k<sim.particles.size();++k) {
    int px=(int)((sim.particles.pos[k].x - sim.grid.ox)/sim.grid.dx*scale);
    int py=(int)((sim.particles.pos[k].y - sim.grid.oy)/sim.grid.dx*scale);
    py = H-1-py;
    if (px<0||px>=W||py<0||py>=H) continue;
    int o=(px+W*py)*3; img[o]=60; img[o+1]=140; img[o+2]=230;
  }
  std::ofstream f(path, std::ios::binary);
  f << "P6\n" << W << " " << H << "\n255\n";
  f.write((const char*)img.data(), img.size());
}
