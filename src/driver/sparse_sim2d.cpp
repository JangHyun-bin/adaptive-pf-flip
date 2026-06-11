#include "driver/sparse_sim2d.h"
#include "driver/sparse_ops2d.h"
#include <vector>
void SparseSim2D::initDamBreak(){
  int wc=grid.nx*4/10,hr=grid.ny*7/10;
  for(int j=1;j<hr;++j)for(int i=1;i<wc;++i)for(int sj=0;sj<2;++sj)for(int si=0;si<2;++si){
    double x=(i+0.25+0.5*si)*grid.dx,y=(j+0.25+0.5*sj)*grid.dx; particles.add({x,y},{0,0}); }
}
static void markCells(SparseMacGrid2D<8>& g, const Particles2D& ps){
  g.mkf.clear();
  for(int j=0;j<g.ny;++j){ g.setCell(0,j,2); g.setCell(g.nx-1,j,2); }
  for(int i=0;i<g.nx;++i){ g.setCell(i,0,2); g.setCell(i,g.ny-1,2); }
  for(size_t k=0;k<ps.size();++k){ int i=(int)(ps.pos[k].x/g.dx),j=(int)(ps.pos[k].y/g.dx);
    if(g.inBounds(i,j) && g.cell(i,j)!=2) g.setCell(i,j,1); }
}
void SparseSim2D::step(){
  markCells(grid, particles);
  spP2G(grid, particles);
  SparseMacGrid2D<8> saved = grid;                 // copy for FLIP delta
  // gravity on active v-faces with mass
  for(int b: grid.mvf.activeBlocks()){ int bx,by; grid.mvf.blockCoords(b,bx,by);
    for(int ly=0;ly<8;++ly)for(int lx=0;lx<8;++lx){ int i=bx*8+lx,j=by*8+ly; if(i>=grid.nx||j>grid.ny) continue;
      if(grid.gmv(i,j)>0) grid.v(i,j)=grid.gv(i,j)+(float)(dt*gravity); } }
  // wall BC: zero normal velocity at the solid-interface faces (cols/rows 0,1,nx-1,nx ; 0,1,ny-1,ny)
  for(int j=0;j<grid.ny;++j){ grid.u(0,j)=0; grid.u(1,j)=0; grid.u(grid.nx-1,j)=0; grid.u(grid.nx,j)=0; }
  for(int i=0;i<grid.nx;++i){ grid.v(i,0)=0; grid.v(i,1)=0; grid.v(i,grid.ny-1)=0; grid.v(i,grid.ny)=0; }
  spProjectStep(grid, dt, cg_iters, cg_tol);
  spG2P(grid, particles, saved, alpha);
  spAdvect(particles, grid, dt);
}
