#pragma once
#include <algorithm>
#include <fstream>
#include <string>
#include <vector>
#include "driver/multires_sim2d_tp.h"
inline void writeMRTPPM(const MRSim2DTP& sim,const std::string& path,int scale=8){
  if(scale<1) scale=1;
  int W=sim.layout.nx*scale,H=sim.layout.ny*scale; std::vector<unsigned char> img(W*H*3,16);
  for(const MRBlockKey& b: sim.layout.leaves()){ int s=sim.layout.blockFineSize(b.level);
    int x0=std::max(0,b.bx*s),y0=std::max(0,b.by*s),x1=std::min(sim.layout.nx,b.bx*s+s),y1=std::min(sim.layout.ny,b.by*s+s);
    unsigned char r=b.level==0?24:28,g=b.level==0?40:32,bl=b.level==0?28:48;
    for(int j=y0;j<y1;++j)for(int i=x0;i<x1;++i){ int px=i*scale,py=H-1-j*scale;
      for(int yy=0;yy<scale;++yy)for(int xx=0;xx<scale;++xx){ int X=px+xx,Y=py-yy; if(X<0||X>=W||Y<0||Y>=H) continue; int o=(X+W*Y)*3; img[o]=r;img[o+1]=g;img[o+2]=bl; } } }
  for(size_t k=0;k<sim.particles.size();++k){ int px=(int)(sim.particles.pos[k].x/sim.layout.dx*scale),py=H-1-(int)(sim.particles.pos[k].y/sim.layout.dx*scale);
    if(px<0||px>=W||py<0||py>=H) continue; int o=(px+W*py)*3;
    if(sim.particles.type[k]==0){ img[o]=60;img[o+1]=140;img[o+2]=230; } else { img[o]=235;img[o+1]=160;img[o+2]=60; } }
  std::ofstream f(path,std::ios::binary); f<<"P6\n"<<W<<" "<<H<<"\n255\n"; f.write((const char*)img.data(),img.size());
}
