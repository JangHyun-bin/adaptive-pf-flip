#include "driver/sparse_sim2d_tp.h"
#include "driver/sparse_ops2d_tp.h"
#include "transfer/transfer2d_tp.h"   // calibrateRhoTilde0_2d
#include <cmath>
#include <algorithm>

static void seedCell(Particles2DTP& ps,int i,int j,double dx,unsigned char t){
  for(int s=0;s<4;++s){ double x=(i+0.25+0.5*(s%2))*dx, y=(j+0.25+0.5*(s/2))*dx; ps.add({x,y},{0,0},t); }
}
void SparseSim2DTP::initRayleighTaylor(){
  phase.rho_tilde_0 = calibrateRhoTilde0_2d(phase, Vp);
  int mid=grid.ny/2;
  for(int j=1;j<grid.ny-1;++j)for(int i=1;i<grid.nx-1;++i){
    double pert = 1.0*std::cos(2*3.14159265*i/grid.nx);
    bool heavy = (double)j > (mid + pert);
    seedCell(particles,i,j,grid.dx, heavy?0:1);
  }
}
void SparseSim2DTP::initBubbleTank(){
  phase.rho_tilde_0 = calibrateRhoTilde0_2d(phase, Vp);
  int wl = grid.ny/2;                                  // water level: liquid rows [1, wl)
  double cx = grid.nx*0.5, cy = wl*0.375, r = grid.nx*0.09375;   // 48x48 -> cx=24, cy=9, r=4.5
  for(int j=1;j<wl;++j)for(int i=1;i<grid.nx-1;++i){
    double dxc=(i+0.5)-cx, dyc=(j+0.5)-cy;
    bool gas = (dxc*dxc+dyc*dyc) < r*r;
    seedCell(particles,i,j,grid.dx, gas?1:0);          // bubble=gas, pool=liquid; above wl: EMPTY (AIR)
  }
}
static void markCells(SparseMacGrid2D<8>& g, const Particles2DTP& ps){
  g.mkf.clear();
  for(int j=0;j<g.ny;++j){ g.setCell(0,j,2); g.setCell(g.nx-1,j,2); }
  for(int i=0;i<g.nx;++i){ g.setCell(i,0,2); g.setCell(i,g.ny-1,2); }
  for(size_t k=0;k<ps.size();++k){ int i=(int)(ps.pos[k].x/g.dx),j=(int)(ps.pos[k].y/g.dx);
    if(g.inBounds(i,j) && g.cell(i,j)!=2) g.setCell(i,j,1); }
}
void SparseSim2DTP::step(){
  markCells(grid, particles);
  spP2G_tp(grid, particles, phase, Vp);
  SparseMacGrid2D<8> saved = grid;                 // FLIP snapshot (pre-forces)
  for(int b: grid.mvf.activeBlocks()){ int bx,by; grid.mvf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>=grid.nx||j>grid.ny) continue;
      if(grid.gmv(i,j)>0) grid.v(i,j)=grid.gv(i,j)+(float)(dt*gravity); } }
  for(int j=0;j<grid.ny;++j){ grid.u(0,j)=0; grid.u(1,j)=0; grid.u(grid.nx-1,j)=0; grid.u(grid.nx,j)=0; }
  for(int i=0;i<grid.nx;++i){ grid.v(i,0)=0; grid.v(i,1)=0; grid.v(i,grid.ny-1)=0; grid.v(i,grid.ny)=0; }
  spProjectStepVC(grid, phase, dt, cg_iters, cg_tol);
  spG2P_tp(grid, particles, saved, alpha_liquid, alpha_gas);
  spAdvect_tp(particles, grid, dt);
}
