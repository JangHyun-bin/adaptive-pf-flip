#pragma once
#include <string>
#include <vector>
#include <fstream>
#include <cmath>
#include "driver/sim3d_tp.h"
#include "driver/sparse_sim3d_tp.h"
inline void writePhaseSlice(const Sim3DTP& sim,const std::string& path,int scale=8,double zhalf=0.12){
  int W=sim.grid.nx*scale,H=sim.grid.ny*scale; std::vector<unsigned char> img(W*H*3,12);
  double zc=sim.grid.nz*0.5*sim.grid.dx, band=zhalf*sim.grid.nz*sim.grid.dx;
  for(size_t k=0;k<sim.particles.size();++k){ if(std::abs(sim.particles.pos[k].z-zc)>band) continue;
    int px=(int)(sim.particles.pos[k].x/sim.grid.dx*scale),py=(int)(sim.particles.pos[k].y/sim.grid.dx*scale); py=H-1-py;
    if(px<0||px>=W||py<0||py>=H) continue; int o=(px+W*py)*3;
    if(sim.particles.type[k]==0){img[o]=50;img[o+1]=130;img[o+2]=235;} else {img[o]=40;img[o+1]=40;img[o+2]=46;} }
  std::ofstream f(path,std::ios::binary); f<<"P6\n"<<W<<" "<<H<<"\n255\n"; f.write((const char*)img.data(),img.size());
}

inline void writePhaseSlice(const SparseSim3DTP& sim,const std::string& path,int scale=8,double zhalf=0.12){
  int W=sim.grid.nx*scale,H=sim.grid.ny*scale; std::vector<unsigned char> img(W*H*3,12);
  double zc=sim.grid.nz*0.5*sim.grid.dx, band=zhalf*sim.grid.nz*sim.grid.dx;
  for(int b: sim.grid.pf.activeBlockIds()){ int bx,by,bz; sim.grid.pf.blockCoords(b,bx,by,bz);
    for(int ly=0;ly<4;++ly)for(int lx=0;lx<4;++lx){
      int i=bx*4+lx,j=by*4+ly,k=bz*4; if(i>=sim.grid.nx||j>=sim.grid.ny||k>=sim.grid.nz) continue;
      double z=sim.grid.oz+(k+0.5)*sim.grid.dx; if(std::abs(z-zc)>band) continue;
      int px=i*scale,py=H-1-j*scale;
      for(int yy=0;yy<scale;++yy)for(int xx=0;xx<scale;++xx){ int X=px+xx,Y=py-yy; if(X<0||X>=W||Y<0||Y>=H) continue; int o=(X+W*Y)*3; img[o]=18;img[o+1]=34;img[o+2]=24; }
    } }
  for(size_t k=0;k<sim.particles.size();++k){ if(std::abs(sim.particles.pos[k].z-zc)>band) continue;
    int px=(int)((sim.particles.pos[k].x-sim.grid.ox)/sim.grid.dx*scale),py=(int)((sim.particles.pos[k].y-sim.grid.oy)/sim.grid.dx*scale); py=H-1-py;
    if(px<0||px>=W||py<0||py>=H) continue; int o=(px+W*py)*3;
    if(sim.particles.type[k]==0){img[o]=50;img[o+1]=130;img[o+2]=235;} else {img[o]=235;img[o+1]=160;img[o+2]=60;} }
  std::ofstream f(path,std::ios::binary); f<<"P6\n"<<W<<" "<<H<<"\n255\n"; f.write((const char*)img.data(),img.size());
}
