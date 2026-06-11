#pragma once
#include <string>
#include <vector>
#include <fstream>
#include "driver/sparse_sim2d.h"
inline void writeSparsePPM(const SparseSim2D& sim,const std::string& path,int scale=8){
  int W=sim.grid.nx*scale,H=sim.grid.ny*scale; std::vector<unsigned char> img(W*H*3,16);
  // shade active blocks faintly
  for(int b: sim.grid.pf.activeBlocks()){ int bx,by; sim.grid.pf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>=sim.grid.nx||j>=sim.grid.ny) continue;
      int px=i*scale,py=H-1-j*scale; for(int yy=0;yy<scale;++yy)for(int xx=0;xx<scale;++xx){ int X=px+xx,Y=py-yy; if(X<0||X>=W||Y<0||Y>=H)continue; int o=(X+W*Y)*3; img[o]=24;img[o+1]=40;img[o+2]=28; } } }
  for(size_t k=0;k<sim.particles.size();++k){ int px=(int)(sim.particles.pos[k].x/sim.grid.dx*scale),py=H-1-(int)(sim.particles.pos[k].y/sim.grid.dx*scale);
    if(px<0||px>=W||py<0||py>=H) continue; int o=(px+W*py)*3; img[o]=60;img[o+1]=140;img[o+2]=230; }
  std::ofstream f(path,std::ios::binary); f<<"P6\n"<<W<<" "<<H<<"\n255\n"; f.write((const char*)img.data(),img.size());
}
